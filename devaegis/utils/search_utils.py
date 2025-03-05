import logging

import numpy as np
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def extract_keywords(text):
    return text.split()


def fusion_retrieval(vectorstore, query: str, k: int = 5, alpha: float = 0.5):
    """
    Perform fusion retrieval combining keyword-based (BM25) and vector-based search.

    Args:
    vectorstore (VectorStore): The vectorstore containing the documents.
    bm25 (BM25Okapi): Pre-computed BM25 index.
    query (str): The query string.
    k (int): The number of documents to retrieve.
    alpha (float): The weight for vector search scores (1-alpha will be the weight for BM25 scores).

    Returns:
    List[Document]: The top k documents based on the combined scores.
    """

    epsilon = 1e-8

    # Step 1: Get all documents from the vectorstore
    all_docs = vectorstore.similarity_search("", k=vectorstore.index.ntotal)

    # Step 2: Perform BM25 search
    # bm25_scores = bm25.get_scores(query.split())

    # Step 2: Keywords Similarity score
    keywords = extract_keywords(query)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([doc.page_content for doc in all_docs])
    query_vector = vectorizer.transform([" ".join(keywords)])
    bm25_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Step 3: Perform vector search
    vector_results = vectorstore.similarity_search_with_score(query, k=len(all_docs))

    # Step 4: Normalize scores
    vector_scores = np.array([score for _, score in vector_results])
    vector_scores = 1 - (vector_scores - np.min(vector_scores)) / (
        np.max(vector_scores) - np.min(vector_scores) + epsilon
    )

    bm25_scores = (bm25_scores - np.min(bm25_scores)) / (
        np.max(bm25_scores) - np.min(bm25_scores) + epsilon
    )

    # Step 5: Combine scores
    combined_scores = alpha * vector_scores + (1 - alpha) * bm25_scores

    # Step 6: Rank documents
    sorted_indices = np.argsort(combined_scores)[::-1]

    # Step 7: Return top k documents
    ret_docs = [all_docs[i] for i in sorted_indices[:k]]

    return ret_docs


class RatingScore(BaseModel):
    relevance_score: float = Field(
        ..., description="The relevance score of a document to a query."
    )


class JobTemplate(BaseModel):
    job_name: str = Field(..., description="The most matched job's name to a project.")
    job_path: str = Field(..., description="The most matched job's path to a project.")


def rerank_documents(query, docs, top_n=5):
    prompt_template = PromptTemplate(
        input_variables=["query", "doc"],
        template="""On a scale of 1-10, rate the relevance of the following CICD pipeline to the query. Consider the specific context and intent of the query, not just keyword matches.
        Query: {query}
        Document: {doc}
        Relevance Score:""",
    )
    llm = ChatOpenAI(model="gpt-4o")
    chain = prompt_template | llm.with_structured_output(RatingScore)

    scored_docs = []
    for doc in docs:
        score = chain.invoke({"query": query, "doc": doc}).relevance_score
        try:
            score = float(score)
        except ValueError:
            score = 0  # Default score if parsing fails
        scored_docs.append((doc, score))

    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in scored_docs[:top_n]]


def extract_attributes(page_content):
    import re

    attributes = {}

    # Define regex patterns for Path, Job Name, and Description
    patterns = {
        "Path": r"Path:\s*(.*)",
        "Job Name": r"Job Name:\s*(.*)",
        "Description": r"Description:\s*(.*)",
        "Job": r"Script:\s*(.*)",
    }

    # Search for each pattern in the page content
    for key, pattern in patterns.items():
        if key == "Job":
            match = re.search(pattern, page_content, re.DOTALL)
        else:
            match = re.search(pattern, page_content)
        if match:
            attributes[key] = match.group(1).strip()

    return attributes


def retrieve_relevant_template_with_project_info(template_list, project_info):
    prompt_template = PromptTemplate(
        input_variables=["template_list", "project_info"],
        template="""Based on the project info, find the most suitable CICD job template. Consider the specific context and intent of the query, not just keyword matches.
                    Do not just return job name, return full job script only.   
                    Project Info: {project_info}
                    Job Templates: {template_list}
                    Most matched template:""",
    )
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    chain = prompt_template | llm.with_structured_output(JobTemplate)
    job_details = chain.invoke(
        {"project_info": project_info, "template_list": template_list}
    )
    return {"job_name": job_details.job_name, "job_path": job_details.job_path}

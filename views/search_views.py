import logging
import pickle

import faiss
import psycopg2
from flask import Blueprint, current_app, jsonify, make_response, request

from utils.search_utils import (extract_attributes, fusion_retrieval,
                                rerank_documents)

blueprint = Blueprint("search_views", __name__)
logger = logging.getLogger(__name__)


@blueprint.route("/", methods=["POST"])
def filter_for_templates():
    """
    Filter top k templates
    """
    auth_header = request.headers.get("Authorization")
    if auth_header != current_app.config["AUTH_TOKEN"]:
        return make_response(jsonify({"details": "Permission denied."}), 401)

    user_query = request.form.get("user_query")
    limit = int(request.form.get("limit", 1))

    DB_PARAMS = {
        "host": current_app.config["POSTGRES_HOSTNAME"],
        "user": current_app.config["POSTGRES_USER"],
        "port": current_app.config["POSTGRES_PORT"],
        "dbname": current_app.config["POSTGRES_DB"],
        "password": current_app.config["POSTGRES_PASSWORD"],
    }

    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    # Retrieve the FAISS index
    cursor.execute(
        "SELECT index_data, docstore_data, index_to_docstore_id FROM faiss_index ORDER BY id DESC LIMIT 1"
    )
    index_data, docstore_data, index_to_docstore_id = cursor.fetchone()

    # Deserialize the index, docstore, index_to_docstore_id
    index = faiss.deserialize_index(pickle.loads(index_data))
    docstore = pickle.loads(docstore_data)
    index_to_docstore_id = {int(k): v for k, v in index_to_docstore_id.items()}

    # Close connection
    cursor.close()
    conn.close()

    # Recreate vector_store with loaded index
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings()

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )

    # Perform fusion retrieval
    top_docs = fusion_retrieval(vector_store, user_query, k=10, alpha=0.4)
    docs_content = [doc.page_content for doc in top_docs]

    reranked_docs = rerank_documents(user_query, docs_content, limit)

    result = [extract_attributes(doc) for doc in reranked_docs]

    return make_response(jsonify(result), 200)

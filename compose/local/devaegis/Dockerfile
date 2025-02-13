FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    bash \
    python3-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN python -m pip install --no-cache-dir --requirement /requirements.txt

# install kubectl for cloud service
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin

COPY ./compose/local/devaegis/entrypoint.sh /entrypoint.sh
RUN sed --in-place 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh


COPY . /app

WORKDIR /app

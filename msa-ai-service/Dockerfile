FROM python:3.10-slim

WORKDIR /app

# SSL 인증서와 필요한 툴 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# RUN python -c "from sentence_transformers import SentenceTransformer; \
#                SentenceTransformer('BM-K/KoSimCSE-roberta').save('./model')"


COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

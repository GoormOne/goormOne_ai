FROM python:3.10-slim

WORKDIR /app

# 시스템 기본 툴 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements 설치
COPY msa-ai-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# grpcio-tools 설치 (proto 컴파일용)
RUN pip install grpcio grpcio-tools

# proto 복사 & 컴파일 (생성 결과는 /app 루트에 위치)
COPY proto ./proto
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=. \
    --grpc_python_out=. \
    ./proto/model.proto

# 서비스 코드 복사
COPY msa-ai-service/app ./app

# PYTHONPATH 잡아주기
ENV PYTHONPATH=/app

# 기본 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]    


# FROM python:3.10-slim

# WORKDIR /app

# # SSL 인증서와 필요한 툴 설치
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ca-certificates \
#     curl \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*
    
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# # RUN python -c "from sentence_transformers import SentenceTransformer; \
# #                SentenceTransformer('BM-K/KoSimCSE-roberta').save('./model')"


# # 서비스 코드 복사
# COPY app ./app

# # proto 복사 (루트에서 proto만 가져옴)
# COPY ../proto ./proto

# # proto 파일 컴파일 (model.proto → model_pb2.py / model_pb2_grpc.py)
# RUN python -m grpc_tools.protoc \
#     -I. \
#     --python_out=. \
#     --grpc_python_out=. \
#     app/protos/model.proto

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

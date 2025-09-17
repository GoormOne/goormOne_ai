FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY model-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# proto 복사 & gRPC 코드 생성 → 루트(/app)에 생성
COPY proto ./proto
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=. \
    --grpc_python_out=. \
    ./proto/model.proto

# 서비스 코드 복사
COPY model-service/app ./app

# PYTHONPATH 설정
ENV PYTHONPATH=/app

# gRPC 서버 실행
CMD ["python", "-m", "app.main"]

import os
from dotenv import load_dotenv

# ENV 구분
ENV = os.getenv("ENV", "dev")

if ENV == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")

# Mongo
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
MONGODB_NAME = os.getenv("MONGODB_NAME", "ai_service_dev")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_REQUEST_STREAM = os.getenv("REDIS_REQUEST_STREAM", "chat:requests")
REDIS_RESPONSE_STREAM = os.getenv("REDIS_RESPONSE_STREAM", "chat:responses")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# gRPC
MODEL_SERVICE_HOST = os.getenv("MODEL_SERVICE_HOST", "model-service")
MODEL_SERVICE_PORT = int(os.getenv("MODEL_SERVICE_PORT", 50051))

# Vector Search (prod용)
VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "reviews_embedding_index")

# 라벨 정의
REVIEW_LABELS = ["quantity", "size", "sweet", "salty", "spicy", "deep", "sour"]
POLARITY_LABELS = ["POSITIVE", "NEGATIVE"]

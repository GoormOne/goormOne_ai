import os
from dotenv import load_dotenv

# 기본 ENV=dev
ENV = os.getenv("ENV", "dev")

if ENV == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")


MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_NAME = os.getenv("MONGODB_NAME", "ai_service_db")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_REQUEST_STREAM = os.getenv("REDIS_REQUEST_STREAM", "chat:requests")
REDIS_RESPONSE_STREAM = os.getenv("REDIS_RESPONSE_STREAM", "chat:responses")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

REVIEW_LABELS = ["quantity", "size", "sweet", "salty", "spicy", "deep", "sour"]
POLARITY_LABELS = ["POSITIVE", "NEGATIVE"]
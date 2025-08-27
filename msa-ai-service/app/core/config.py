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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

REVIEW_LABELS = ["quantity", "size", "sweet", "salty", "spicy", "deep"]
POLARITY_LABELS = ["POSITIVE", "NEGATIVE"]
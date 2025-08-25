# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017") # fallback용 
MONGODB_NAME = os.getenv("MONGODB_NAME", "ai_service_db")

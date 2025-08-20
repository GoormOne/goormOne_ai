# app/db/mongodb.py
from pymongo import MongoClient
from app.core.config import MONGODB_URI, MONGODB_NAME

client = MongoClient(MONGODB_URI)
db = client[MONGODB_NAME]

def get_collection(name: str):
    """지정된 컬렉션 반환"""
    return db[name]

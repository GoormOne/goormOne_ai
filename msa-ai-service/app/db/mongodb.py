from pymongo import MongoClient
from app.core.config import MONGODB_URI, MONGODB_NAME

client = MongoClient(MONGODB_URI)
db = client[MONGODB_NAME]

def get_collection(name: str):
    return db[name] # 지정된 콜렉션 반환

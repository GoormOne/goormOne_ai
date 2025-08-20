#FastAPI 연결 테스트

from pymongo import MongoClient
from core import config

client = MongoClient(config.MONGODB_URI)
db = client[config.MONGODB_NAME]

print("연결 성공:", db.name)
print("현재 콜렉션 목록:", db.list_collection_names())

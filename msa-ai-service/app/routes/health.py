# app/routes/health.py
from fastapi import APIRouter
from app.db.mongodb import get_collection

router = APIRouter()

@router.get("/health")
def health_check():
    col = get_collection("test_collection")
    doc_count = col.count_documents({})
    return {"status": "ok", "documents": doc_count}

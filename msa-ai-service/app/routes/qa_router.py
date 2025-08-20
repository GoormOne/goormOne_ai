 # 질문 → 답변 API (API endpoint)

from fastapi import APIRouter
from app.services.rag_service import run_rag

router = APIRouter()

@router.post("/ask/{request_id}")
async def ask_question(request_id: str):
    return await run_rag(request_id)

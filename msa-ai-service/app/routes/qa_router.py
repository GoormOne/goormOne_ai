 # 질문 → 답변 API (API endpoint)
# 질문을 DB에 채움
from fastapi import APIRouter
from app.services.rag_service import run_rag

router = APIRouter()

@router.post("/ask/{request_id}")
async def ask_question(request_id: str):
    return await run_rag(request_id)

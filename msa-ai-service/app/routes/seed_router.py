# 테스트용 파이프라인 재현 라우터

# app/routes/seed_router.py
from fastapi import APIRouter
from datetime import datetime, timezone
from app.db.mongodb import get_collection
from app.utils.helpers import gen_uuid
from app.services.embedding_service import get_embedding
from openai import OpenAI
import os

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/seed")
def seed_data():
    now = datetime.now(timezone.utc)

    # 1) 리뷰 (Spring 대신 임시로 직접 삽입)
    review_id = gen_uuid()
    menu_id = gen_uuid()
    review = {
        "_id": review_id,
        "menu_id": menu_id,
        "menu_name": "꿔바로우",
        "store_name": "신나라 마라탕",
        "text": "겉바속촉이라 바삭합니다.",
        "created_at": now,
        "updated_at": now
    }
    get_collection("reviews_denorm").insert_one(review)

    # 2) 질문 (사용자 질문 임의 입력)
    request_id = gen_uuid()
    query = {
        "_id": gen_uuid(),
        "request_id": request_id,
        "menu_id": menu_id,
        "question_raw": "겉바속촉인가요?",
        "created_at": now
    }
    get_collection("qa_queries").insert_one(query)

    # 3) 리뷰 임베딩 (실제 OpenAI 호출)
    review_embedding = {
        "_id": gen_uuid(),
        "review_id": review_id,
        "menu_id": menu_id,
        "text": review["text"],
        "embedding": get_embedding(review["text"]),  # OpenAI embedding
        "created_at": now,
        "updated_at": now
    }
    get_collection("reviews_embedding").insert_one(review_embedding)

    # 4) 답변 (실제 OpenAI 호출)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 리뷰 내용을 요약해서 질문에 답하는 도우미야."},
            {"role": "user", "content": f"리뷰: {review['text']}\n질문: {query['question_raw']}"}
        ]
    )
    answer_text = resp.choices[0].message.content

    answer = {
        "_id": gen_uuid(),
        "key_hash": gen_uuid(),
        "menu_id": menu_id,
        "norm_question": "CRISPY",
        "answer_text": answer_text,
        "evidence": [{"review_id": review_id, "snippet": review["text"]}],
        "generated_at": now
    }
    get_collection("qa_answers").insert_one(answer)

    return {
        "message": "seed data inserted",
        "review_id": review_id,
        "request_id": request_id,
        "answer": answer_text
    }

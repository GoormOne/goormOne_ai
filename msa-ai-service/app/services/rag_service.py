# RAG 로직 (질문 -> 검색 ->답변)
# 질문 콜렉션 조회 -> 메뉴 리뷰 가져옴 -> 리뷰 임베딩 저장 -> 질문 답변 생성 및 콜렉션에 저장
# 실제 운영에서 쓰임

# app/services/rag_service.py
from datetime import datetime
from app.db.mongodb import get_collection
from app.services.embedding_service import get_embedding
from app.utils.helpers import gen_uuid
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_rag(request_id: str):
    """질문 → 임베딩 검색 → 답변 생성 → MongoDB 저장"""

    query_col = get_collection("old_qa_queries")
    query = query_col.find_one({"request_id": request_id})
    if not query:
        return {"error": "query not found"}

    menu_id = query["menu_id"]
    question_text = query["question_raw"]

    # 1) 질문 임베딩
    q_emb = get_embedding(question_text)

    # 2) 리뷰 가져오기 (메뉴 기준 최신 1건)
    review_col = get_collection("old_reviews_denorm")
    review = review_col.find_one({"menu_id": menu_id}, sort=[("updated_at", -1)])
    if not review:
        return {"error": "no reviews found"}

    # 3) 리뷰 임베딩 생성 및 저장
    emb_col = get_collection("reviews_embedding")
    emb_doc = {
        "_id": gen_uuid(),
        "review_id": review["_id"],
        "menu_id": review["menu_id"],
        "text": review["text"],
        "embedding": get_embedding(review["text"]),  # 실제 OpenAI 호출
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    emb_col.insert_one(emb_doc)

    # 4) 답변 생성 (실제 OpenAI 호출)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 리뷰 내용을 요약해서 질문에 답하는 도우미야."},
            {"role": "user", "content": f"리뷰: {review['text']}\n질문: {question_text}"}
        ]
    )
    answer_text = resp.choices[0].message.content

    # 5) 답변 MongoDB 저장
    ans_col = get_collection("qa_answers")
    ans_doc = {
        "_id": gen_uuid(),
        "key_hash": gen_uuid(),
        "menu_id": menu_id,
        "norm_question": "CRISPY",
        "answer_text": answer_text,
        "evidence": [{"review_id": review["_id"], "snippet": review["text"]}],
        "generated_at": datetime.utcnow()
    }
    ans_col.insert_one(ans_doc)

    return {"answer": answer_text}

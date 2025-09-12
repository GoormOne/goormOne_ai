# 강제 수동 실행용 (Change Stream 대신)
# API 트리거 질문 -> 응답 처리 가능

"""
1. (Change Stream 또는 직접 호출 시) queries 문서 전체 읽기
2. 각 질문(request_id) 확인:
    queries_embedding에 없으면 → 새 질문 처리 시작
3. queries_embedding 생성 (label, polarity 포함)
4. answers에 같은 store_id + menu_id + label + polarity 답변이 있으면:
    answers.created_at < reviews.updated_at → 새로 생성
    아니면 재사용
5. 최종 답변 answers에 저장
"""

from fastapi import APIRouter
from datetime import datetime
from app.db.mongodb import get_collection
from app.services.embedding_service import embed_and_label_question
from app.services.rag_service import generate_answer_from_reviews

router = APIRouter()

queries_col = get_collection("queries")
queries_embedding_col = get_collection("queries_embedding")

@router.get("/process-queries")
async def process_queries(limit: int = 10):
    """
    수동으로 QA 파이프라인 실행 (Change Stream 대신 직접 확인할 때 사용)
    """
    results = []
    docs = queries_col.find().limit(limit)

    for doc in docs:
        store_id = doc["_id"]
        store_name = doc["store_name"]

        for menu in doc.get("menus", []):
            menu_id = menu["menu_id"]
            menu_name = menu["menu_name"]

            for q in menu.get("questions", []):
                request_id = q["request_id"]
                question = q["question"]

                # 이미 처리된 질문이면 skip
                queries_doc = queries_embedding_col.find_one({"_id": store_id})
                existing_ids = []
                if queries_doc:
                    for m in queries_doc["menus"]:
                        if m["menu_id"] == menu_id:
                            existing_ids = [qe["request_id"] for qe in m.get("questions_embedding", [])]
                if request_id in existing_ids:
                    continue

                # 질문 라벨링 + 임베딩
                label, polarity, embedding = embed_and_label_question(question)

                queries_embedding_col.update_one(
                    {"_id": store_id, "menus.menu_id": menu_id},
                    {
                        "$push": {
                            "menus.$.questions_embedding": {
                                "request_id": request_id,
                                "question": question,
                                "label": label,
                                "polarity": polarity,
                                "embedding": embedding,
                                "created_at": datetime.utcnow()
                            }
                        },
                        "$set": {"updated_at": datetime.utcnow(), "store_name": store_name}
                    },
                    upsert=True
                )

                # RAG 실행 (라벨 맞는 리뷰 통계로 응답 생성)
                answer_result = generate_answer_from_reviews(store_id, menu_id, question)

                results.append({
                    "request_id": request_id,
                    "answer": answer_result.get("answer"),
                    "reviews_used": answer_result.get("reviews_used", [])
                })

    return {"processed": len(results), "results": results}

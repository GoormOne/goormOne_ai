# MongoDB 이벤트 감시 후 자동 처리 트리거
"""
MongoDB Change Stream 이벤트 감시 서비스
- queries 변경 시: 새로운 질문 → queries_embedding 업데이트 + process_query 호출
- reviews 변경 시: 새로운 리뷰 → reviews_embedding 업데이트
"""
# app/services/change_stream_service.py
import threading
from datetime import datetime
from app.db.mongodb import get_collection
from app.services.embedding_service import embed_and_label_question, embed_and_label_review
from app.services.rag_service import process_query

queries_col = get_collection("queries")
reviews_col = get_collection("reviews")
queries_embedding_col = get_collection("queries_embedding")
reviews_embedding_col = get_collection("reviews_embedding")

# 새 질문 처리
def process_new_questions(change):
    print("🟢 New question change detected:", change)
    full_doc = change["fullDocument"]

    for menu in full_doc.get("menus", []):
        for q in menu.get("questions", []):
            # 이미 처리된 request_id 건너뛰기 ✅ (기존에도 있었음, 유지)
            queries_doc = queries_embedding_col.find_one({"_id": full_doc["_id"]})
            existing_ids = []
            if queries_doc:
                for m in queries_doc["menus"]:
                    if m["menu_id"] == menu["menu_id"]:
                        existing_ids = [qe["request_id"] for qe in m.get("questions_embedding", [])]
            if q["request_id"] in existing_ids:
                continue

            # 라벨링 + 임베딩
            label, polarity, embedding = embed_and_label_question(q["question"])

            # 메뉴 없으면 생성
            queries_embedding_col.update_one(
                {"_id": full_doc["_id"], "menus.menu_id": menu["menu_id"]},
                {
                    "$setOnInsert": {
                        "_id": full_doc["_id"],
                        "store_name": full_doc["store_name"],
                        "menus": [
                            {
                                "menu_id": menu["menu_id"],
                                "menu_name": menu["menu_name"],
                                "questions_embedding": []
                            }
                        ]
                    }
                },
                upsert=True
            )

            # 질문 추가
            queries_embedding_col.update_one(
                {"_id": full_doc["_id"], "menus.menu_id": menu["menu_id"]},
                {
                    "$push": {
                        "menus.$.questions_embedding": {
                            "request_id": q["request_id"],
                            "question": q["question"],
                            "label": label,
                            "polarity": polarity,
                            "embedding": embedding,
                            "created_at": datetime.utcnow()
                        }
                    },
                    "$set": {"updated_at": datetime.utcnow(), "store_name": full_doc["store_name"]}
                }
            )

            # RAG 실행 (answers 생성까지)
            query_emb = {
                "request_id": q["request_id"],
                "question": q["question"],
                "label": label,
                "polarity": polarity,
                "embedding": embedding
            }
            process_query(full_doc, menu, query_emb)


# 새 리뷰 처리
def process_new_reviews(change):
    print("🟢 New review change detected:", change)
    full_doc = change["fullDocument"]

    for menu in full_doc.get("menus", []):
        for r in menu.get("reviews", []):
            reviews_doc = reviews_embedding_col.find_one({"_id": full_doc["_id"]})
            existing_ids = []
            if reviews_doc:
                for m in reviews_doc["menus"]:
                    if m["menu_id"] == menu["menu_id"]:
                        existing_ids = [re["review_id"] for re in m.get("reviews_embedding", [])]
            if r["review_id"] in existing_ids:
                continue  # ✅ 리뷰 단위 비교 (updated_at 신뢰 안 함)

            # 라벨링 + 임베딩
            label, polarity, embedding = embed_and_label_review(r["text"])

            # 메뉴 없으면 생성
            reviews_embedding_col.update_one(
                {"_id": full_doc["_id"], "menus.menu_id": menu["menu_id"]},
                {
                    "$setOnInsert": {
                        "_id": full_doc["_id"],
                        "store_name": full_doc["store_name"],
                        "menus": [
                            {
                                "menu_id": menu["menu_id"],
                                "menu_name": menu["menu_name"],
                                "reviews_embedding": []
                            }
                        ]
                    }
                },
                upsert=True
            )

            # 리뷰 추가
            reviews_embedding_col.update_one(
                {"_id": full_doc["_id"], "menus.menu_id": menu["menu_id"]},
                {
                    "$push": {
                        "menus.$.reviews_embedding": {
                            "review_id": r["review_id"],
                            "text": r["text"],
                            "label": label,
                            "polarity": polarity,
                            "embedding": embedding,
                            "updated_at": datetime.utcnow()
                        }
                    },
                    "$set": {"updated_at": datetime.utcnow(), "store_name": full_doc["store_name"]}
                }
            )


# ✅ 추가: 서버 시작 시 bootstrap 함수들
def bootstrap_unanswered_questions():
    print("🚀 Bootstrap unanswered questions 실행")
    for full_doc in queries_col.find({}):
        for menu in full_doc.get("menus", []):
            for q in menu.get("questions", []):
                queries_doc = queries_embedding_col.find_one({"_id": full_doc["_id"]})
                existing_ids = []
                if queries_doc:
                    for m in queries_doc.get("menus", []):
                        if m["menu_id"] == menu["menu_id"]:
                            existing_ids = [qe["request_id"] for qe in m.get("questions_embedding", [])]
                if q["request_id"] in existing_ids:
                    continue

                label, polarity, embedding = embed_and_label_question(q["question"])

                queries_embedding_col.update_one(
                    {"_id": full_doc["_id"], "menus.menu_id": menu["menu_id"]},
                    {"$push": {"menus.$.questions_embedding": {
                        "request_id": q["request_id"],
                        "question": q["question"],
                        "label": label,
                        "polarity": polarity,
                        "embedding": embedding,
                        "created_at": datetime.utcnow()
                    }}},
                    upsert=True
                )

                query_emb = {
                    "request_id": q["request_id"],
                    "question": q["question"],
                    "label": label,
                    "polarity": polarity,
                    "embedding": embedding
                }
                process_query(full_doc, menu, query_emb)
    print("✅ Bootstrap unanswered questions 완료")


def bootstrap_reviews_embedding():
    print("🚀 Bootstrap reviews embedding 실행")
    for full_doc in reviews_col.find({}):
        for menu in full_doc.get("menus", []):
            for r in menu.get("reviews", []):
                reviews_doc = reviews_embedding_col.find_one({"_id": full_doc["_id"]})
                existing_ids = []
                if reviews_doc:
                    for m in reviews_doc.get("menus", []):
                        if m["menu_id"] == menu["menu_id"]:
                            existing_ids = [re["review_id"] for re in m.get("reviews_embedding", [])]
                if r["review_id"] in existing_ids:
                    continue

                # 라벨링 + 임베딩
                label, polarity, embedding = embed_and_label_review(r["text"])

                # 1. store 문서 없으면 생성
                reviews_embedding_col.update_one(
                    {"_id": full_doc["_id"]},
                    {
                        "$setOnInsert": {
                            "_id": full_doc["_id"],
                            "store_name": full_doc["store_name"],
                            "menus": []
                        }
                    },
                    upsert=True
                )

                # ✅ 2. 해당 menu_id 없으면 메뉴 추가
                reviews_embedding_col.update_one(
                    {"_id": full_doc["_id"], "menus.menu_id": {"$ne": menu["menu_id"]}},
                    {
                        "$push": {
                            "menus": {
                                "menu_id": menu["menu_id"],
                                "menu_name": menu["menu_name"],
                                "reviews_embedding": []
                            }
                        }
                    }
                )

                # 3. 이제 안전하게 리뷰 추가
                reviews_embedding_col.update_one(
                    {"_id": full_doc["_id"], "menus.menu_id": menu["menu_id"]},
                    {
                        "$push": {
                            "menus.$.reviews_embedding": {
                                "review_id": r["review_id"],
                                "text": r["text"],
                                "label": label,
                                "polarity": polarity,
                                "embedding": embedding,
                                "updated_at": datetime.utcnow()
                            }
                        },
                        "$set": {"updated_at": datetime.utcnow(), "store_name": full_doc["store_name"]}
                    }
                )
    print("✅ Bootstrap reviews embedding 완료")



# Change Stream 워처
def watch_queries():
    with queries_col.watch(full_document="updateLookup") as stream:
        for change in stream:
            if change["operationType"] in ("insert", "replace", "update"):
                process_new_questions(change)

def watch_reviews():
    with reviews_col.watch(full_document="updateLookup") as stream:
        for change in stream:
            if change["operationType"] in ("insert", "replace", "update"):
                process_new_reviews(change)

def start_watchers():
    bootstrap_unanswered_questions()
    bootstrap_reviews_embedding()

    threading.Thread(target=watch_queries, daemon=True).start()
    threading.Thread(target=watch_reviews, daemon=True).start()

# 응답 생성 로직 (실제 운영 파이프라인, LLM/RAG 호출)
"""
질문 임베딩과 리뷰 임베딩 비교
label + polarity 필터링
Top-K 리뷰 선택
답변 텍스트 생성 및 qa_answers 저장
"""

from datetime import datetime
from openai import OpenAI
import numpy as np
from app.db.mongodb import get_collection
from app.core.config import OPENAI_API_KEY
from app.services.embedding_service import embed_and_label_question

client = OpenAI(api_key=OPENAI_API_KEY)

# Mongo 컬렉션
queries_embedding_col = get_collection("queries_embedding")
reviews_embedding_col = get_collection("reviews_embedding")
qa_answers_col = get_collection("qa_answers")

# 코사인 유사도
def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# GPT 기반 답변 생성
def generate_answer(store_name, menu_name, question, label, reviews):
    review_texts = "\n".join([f"- {r['text']} ({r['polarity']})" for r in reviews])

    prompt = f"""
당신은 음식점 리뷰 분석기입니다.

질문: {question}
메뉴: {menu_name} @ {store_name}
리뷰 ({len(reviews)}건):
{review_texts}

규칙:
1. 반드시 위 리뷰만 사실 근거로 삼아 답변하세요.
2. {label} 속성에 해당하는 리뷰들 중, 긍정/부정 리뷰 개수를 세어라.
3. 다음 형식으로 요약하라:
   - {label} 관련 리뷰 {len(reviews)}건 중 X건은 긍정적이고, Y건은 부정적입니다."
   - 마지막에 결론을 붙여라. (예: "대체로 짜다고 합니다", "의견이 갈립니다", "비율이 비슷합니다", "너무 짜다고 합니다")
4. 긍정/부정이라는 단어는 쓰지 말고, {label} 속성에 맞는 자연스러운 한국어 서술형으로 풀어라.
   - 예: salty → "짜다" / "짜지 않다"
   - 예: quantity → "양이 많다" / "양이 적다"
   - 예: spicy → "맵다" / "안맵다"
   - 표현은 리뷰 맥락에 맞게 자연스럽게 변형해도 된다.
"""

    resp = client.chat.completions.create(
        model="gpt-41-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()

# Change Stream 자동 호출
def process_query(store_doc, menu, query_emb):
    """
    Change Stream에서 새로운 질문 들어왔을 때 실행되는 자동 응답 생성기
    """
    print("📌 process_query 진입:", store_doc["_id"], menu["menu_id"], query_emb["label"])

    reviews_doc = reviews_embedding_col.find_one({"_id": store_doc["_id"]})
    if not reviews_doc:
        return None

    target_menu = next((m for m in reviews_doc["menus"] if m["menu_id"] == menu["menu_id"]), None)
    if not target_menu or "reviews_embedding" not in target_menu:
        return None

    # 라벨 맞는 리뷰만 (긍/부정 포함)
    candidate_reviews = [r for r in target_menu["reviews_embedding"] if r["label"] == query_emb["label"]]
    print("후보 리뷰 개수:", len(candidate_reviews))
    if not candidate_reviews:
        return None

    # 유사도 top-5
    scored = [(cosine_similarity(query_emb["embedding"], r["embedding"]), r) for r in candidate_reviews]
    scored = sorted(scored, key=lambda x: x[0], reverse=True)[:5]
    selected_reviews = [r for _, r in scored]

    # GPT 답변 생성
    answer_text = generate_answer(
        store_doc["store_name"],
        menu["menu_name"],
        query_emb["question"],
        query_emb["label"],
        selected_reviews
    )
    print("qa_answers 저장 시도:", query_emb["request_id"]) 
    # qa_answers 저장
    qa_answers_col.update_one(
        {"_id": query_emb["request_id"]},
        {"$set": {
            "store_id": store_doc["_id"],
            "store_name": store_doc["store_name"],
            "menu_id": menu["menu_id"],
            "menu_name": menu["menu_name"],
            "answer": answer_text,
            "label": query_emb["label"],
            "polarity": query_emb["polarity"],
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

    return answer_text

# 수동 API 호출
def generate_answer_from_reviews(store_id: str, menu_id: str, question: str):
    reviews_doc = reviews_embedding_col.find_one({"_id": store_id})
    if not reviews_doc:
        return {"error": "no reviews_embedding found"}

    target_menu = next((m for m in reviews_doc["menus"] if m["menu_id"] == menu_id), None)
    if not target_menu or "reviews_embedding" not in target_menu:
        return {"error": "no reviews for this menu"}

    # 질문 임베딩 + 라벨링
    label, polarity, embedding = embed_and_label_question(question)

    candidate_reviews = [r for r in target_menu["reviews_embedding"] if r["label"] == label]
    if not candidate_reviews:
        return {"error": "no matching reviews"}

    scored = [(cosine_similarity(embedding, r["embedding"]), r) for r in candidate_reviews]
    scored = sorted(scored, key=lambda x: x[0], reverse=True)[:5]
    selected_reviews = [r for _, r in scored]

    answer_text = generate_answer(
        reviews_doc["store_name"],
        target_menu["menu_name"],
        question,
        label,
        selected_reviews
    )

    qa_answers_col.update_one(
        {"_id": question},
        {"$set": {
            "store_id": store_id,
            "store_name": reviews_doc["store_name"],
            "menu_id": menu_id,
            "menu_name": target_menu["menu_name"],
            "answer": answer_text,
            "label": label,
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

    return {"answer": answer_text, "reviews_used": [r["text"] for r in selected_reviews]}

# 질문/리뷰를 임베딩으로 변환

"""
질문 / 리뷰 임베딩 + 라벨링 서비스
- OpenAI GPT를 사용하여 label / polarity 분류
- OpenAI Embedding API를 사용하여 벡터 생성
- 결과를 MongoDB queries_embedding / reviews_embedding 에 반영
"""

from datetime import datetime
from openai import OpenAI
import json
from app.db.mongodb import get_collection
from app.core.config import OPENAI_API_KEY, REVIEW_LABELS, POLARITY_LABELS

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# MongoDB 컬렉션 핸들
qa_queries_col = get_collection("qa_queries")
reviews_denorm_col = get_collection("reviews_denorm")
queries_embedding_col = get_collection("queries_embedding")
reviews_embedding_col = get_collection("reviews_embedding")

# 질문 라벨링 + 임베딩
def embed_and_label_question(question: str):
    prompt = f"""
    너는 리뷰 분석기야. 질문 문장을 보고 아래 후보 중 라벨과 polarity를 정해줘.
    라벨 후보: {", ".join(REVIEW_LABELS)}
    폴라리티 후보: {", ".join(POLARITY_LABELS)}
    출력 형식: JSON {{ "label": "...", "polarity": "..." }}
    질문: {question}
    """
    resp = client.chat.completions.create(
        model="gpt-41-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    # 최신 SDK에서는 .content 안에 JSON string 들어옴
    parsed = json.loads(resp.choices[0].message.content)
    label = parsed["label"]
    polarity = parsed["polarity"]

    # OpenAI Embedding API 호출
    embed_resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    embedding = embed_resp.data[0].embedding

    return label, polarity, embedding


# 리뷰 라벨링 + 임베딩
def embed_and_label_review(text: str):
    prompt = f"""
    너는 리뷰 분석기야. 리뷰 문장을 보고 아래 후보 중 라벨과 polarity를 정해줘.
    라벨 후보: {", ".join(REVIEW_LABELS)}
    폴라리티 후보: {", ".join(POLARITY_LABELS)}
    출력 형식: JSON {{ "label": "...", "polarity": "..." }}
    리뷰: {text}
    """
    resp = client.chat.completions.create(
        model="gpt-41-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    parsed = json.loads(resp.choices[0].message.content)
    label = parsed["label"]
    polarity = parsed["polarity"]

    embed_resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    embedding = embed_resp.data[0].embedding

    return label, polarity, embedding


# (옵션) 필요시: 임베딩 문서 업데이트 로직도 여기에 넣을 수 있음
# ex) queries_embedding_col.update_one(...) / reviews_embedding_col.update_one(...)
# 하지만 실제 업데이트는 change_stream_service.py에서 수행

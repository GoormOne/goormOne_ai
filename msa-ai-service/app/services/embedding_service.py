
import grpc
import model_pb2, model_pb2_grpc  # gRPC proto에서 생성된 코드

class EmbeddingService:
    def __init__(self, host="model-service", port=50051):
        channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = model_pb2_grpc.ModelServiceStub(channel)

    def embed_and_label(self, text, meta):
        request = model_pb2.EmbeddingRequest(text=text, meta=meta)
        response = self.stub.GetEmbedding(request)
        return response.status




############# 수정 단계 코드 #############
# # 질문/리뷰에서 임베딩 + 라벨링 추출
# # 임베딩: kosimCSE
# # 라벨링: OpenAI API

# """
# 질문 / 리뷰 임베딩 + 라벨링 서비스
# - OpenAI GPT를 사용하여 label / polarity 분류
# - OpenAI Embedding API를 사용하여 벡터 생성
# - 결과를 MongoDB queries_embedding / reviews_embedding 에 반영
# """

# from openai import OpenAI
# import json
# from app.core.config import OPENAI_API_KEY, REVIEW_LABELS, POLARITY_LABELS
# from app.ml.embedding_model import embedding_model
# import requests
# from app.core.config import MODEL_SERVICE_URL

# # OpenAI 클라이언트 초기화
# client = OpenAI(api_key=OPENAI_API_KEY)

# # # MongoDB 컬렉션 핸들
# # queries_col = get_collection("queries")
# # reviews_col = get_collection("reviews")
# # queries_embedding_col = get_collection("queries_embedding")
# # reviews_embedding_col = get_collection("reviews_embedding")


# def get_embedding(text: str):
#     response = requests.post(MODEL_SERVICE_URL, json={"text": text})
#     response.raise_for_status()
#     return response.json()["embedding"]


# def embed_and_label(text: str, mode: str):
#     """
#     텍스트(리뷰/질문)를 라벨링 + 임베딩으로 변환
#     mode: "review" 또는 "question"
#     """
#     target_word = "리뷰" if mode == "review" else "질문"
#     prompt = f"""
#     너는 리뷰 분석기야. {target_word} 문장을 보고 아래 후보 중 라벨과 polarity를 정해줘.
#     라벨 후보: {", ".join(REVIEW_LABELS)}
#     폴라리티 후보: {", ".join(POLARITY_LABELS)}
#     출력 형식: JSON {{ "label": "...", "polarity": "..." }}
#     {target_word}: {text}
#     """

#     # 라벨링
#     resp = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=[{"role": "user", "content": prompt}],
#         response_format={"type": "json_object"}
#     )
#     parsed = json.loads(resp.choices[0].message.content)
#     label = parsed["label"]
#     polarity = parsed["polarity"]

#     # 임베딩
#     embedding = get_embedding(text)
#     # embedding = embedding_model.encode([text])[0]

#     return label, polarity, embedding









##### 코드 리팩토링 전 (완전 옛날)#####
# 질문 라벨링 + 임베딩
# def embed_and_label_question(question: str):
#     prompt = f"""
#     너는 리뷰 분석기야. 질문 문장을 보고 아래 후보 중 라벨과 polarity를 정해줘.
#     라벨 후보: {", ".join(REVIEW_LABELS)}
#     폴라리티 후보: {", ".join(POLARITY_LABELS)}
#     출력 형식: JSON {{ "label": "...", "polarity": "..." }}
#     질문: {question}
#     """
#     resp = client.chat.completions.create(
#         model="gpt-41-mini",
#         messages=[{"role": "user", "content": prompt}],
#         response_format={"type": "json_object"}
#     )

#     # 최신 SDK에서는 .content 안에 JSON string 들어옴
#     parsed = json.loads(resp.choices[0].message.content)
#     label = parsed["label"]
#     polarity = parsed["polarity"]

#     # 임베딩 추출
#     embedding = embedding_model.encode([question])[0]

#     return label, polarity, embedding


# # 리뷰 라벨링 + 임베딩
# def embed_and_label_review(text: str):
#     # 라벨링
#     prompt = f"""
#     너는 리뷰 분석기야. 리뷰 문장을 보고 아래 후보 중 라벨과 polarity를 정해줘.
#     라벨 후보: {", ".join(REVIEW_LABELS)}
#     폴라리티 후보: {", ".join(POLARITY_LABELS)}
#     출력 형식: JSON {{ "label": "...", "polarity": "..." }}
#     리뷰: {text}
#     """
#     resp = client.chat.completions.create(
#         model="gpt-41-mini",
#         messages=[{"role": "user", "content": prompt}],
#         response_format={"type": "json_object"}
#     )

#     parsed = json.loads(resp.choices[0].message.content)
#     label = parsed["label"]
#     polarity = parsed["polarity"]
    
#     # 임베딩 (로컬 모델)
#     embedding = embedding_model.encode([text])[0]

#     return label, polarity, embedding


# (옵션) 필요시: 임베딩 문서 업데이트 로직도 여기에 넣을 수 있음
# ex) queries_embedding_col.update_one(...) / reviews_embedding_col.update_one(...)
# 하지만 실제 업데이트는 change_stream_service.py에서 수행

# Huggingface로 모델 로드하기

from sentence_transformers import SentenceTransformer
from typing import List
import os

class LocalEmbeddingModel:
    def __init__(self, model_name: str = None):
        # 환경변수에서 모델 경로/이름 불러오기 (없으면 기본값)
        model_name = model_name or os.getenv("EMBEDDING_MODEL", "BM-K/KoSimCSE-roberta")
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> List[List[float]]:
        """여러 문장을 벡터로 변환"""
        return self.model.encode(texts, convert_to_numpy=True).tolist()

# 싱글톤 객체 생성 (앱 전체에서 공유)
embedding_model = LocalEmbeddingModel()

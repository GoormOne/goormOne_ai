# Pydantic 스키마 (queries, answers)
# Swagger 문서화/타입 검증용 샘플

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QueryItem(BaseModel):
    query_id: str
    query: str


class MenuQueries(BaseModel):
    menu_id: str
    queries: List[QueryItem] = []


class QueryDocument(BaseModel):
    id: str = Field(..., alias="_id")   # store_id
    menus: List[MenuQueries] = []
    updated_at: datetime


class AnswerDocument(BaseModel):
    id: str = Field(..., alias="_id")   # question_id
    store_id: str
    store_name: str
    menu_id: str
    menu_name: str
    answer: str
    label: str
    created_at: datetime


class QueryEmbeddingDocument(BaseModel):
    id: str = Field(..., alias="_id")   # request_id
    menu_id: str
    query: str
    label: str
    embedding: List[float]
    created_at: datetime

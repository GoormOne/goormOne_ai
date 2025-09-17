# Pydantic 스키마 (reviews, reviews_embedding)

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ReviewItem(BaseModel):
    review_id: str
    text: str
    created_at: datetime


class MenuReviews(BaseModel):
    menu_id: str
    menu_name: str
    reviews: List[ReviewItem] = []


class ReviewDocument(BaseModel):
    id: str = Field(..., alias="_id")   # store_id
    store_name: str
    menus: List[MenuReviews] = []
    updated_at: datetime


class ReviewEmbeddingDocument(BaseModel):
    id: str = Field(..., alias="_id")   # review_id
    store_id: str
    menu_id: str
    review: str
    label: str
    polarity: str
    embedding: List[float]
    updated_at: datetime

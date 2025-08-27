# Pydantic 스키마 (reviews, reviews_embedding)

from pydantic import BaseModel
from datetime import datetime
from typing import List

class Review(BaseModel):
    review_id: str
    text: str
    created_at: datetime

class Menu(BaseModel):
    menu_id: str
    menu_name: str
    reviews: List[Review] = []

class StoreReview(BaseModel):
    _id: str
    store_name: str
    menus: List[Menu]
    updated_at: datetime

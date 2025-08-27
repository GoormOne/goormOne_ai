# Pydantic 스키마 (qa_queries, qa_answers)
# Swagger 문서화/타입 검증용 샘플

from pydantic import BaseModel
from datetime import datetime

class QAQuery(BaseModel):
    request_id: str
    menu_id: str
    question: str

class QAAnswer(BaseModel):
    request_id: str
    store_id: str
    store_name: str
    menu_id: str
    menu_name: str
    answer: str
    label: str
    polarity: str
    created_at: datetime

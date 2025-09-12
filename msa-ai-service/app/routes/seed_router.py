# app/routes/seed_router.py
# 로컬 테스트용 -> 스프링 API 역할 대신 질문/리뷰 더미 데이터 넣어주는 라우터

from fastapi import APIRouter
from app.db.mongodb import get_collection
from datetime import datetime
import uuid

router = APIRouter()

queries_col = get_collection("queries")
reviews_col = get_collection("reviews")

# 고정 UUID 생성 (매번 실행해도 동일한 ID 유지)
STORE_IDS = {
    "고봉밥상": str(uuid.uuid5(uuid.NAMESPACE_DNS, "고봉밥상")),
    "엽기떡볶이": str(uuid.uuid5(uuid.NAMESPACE_DNS, "엽기떡볶이")),
    "네모디저트": str(uuid.uuid5(uuid.NAMESPACE_DNS, "네모디저트")),
}
MENU_IDS = {
    "된장찌개": str(uuid.uuid5(uuid.NAMESPACE_DNS, "된장찌개")),
    "떡볶이": str(uuid.uuid5(uuid.NAMESPACE_DNS, "떡볶이")),
    "치즈케이크": str(uuid.uuid5(uuid.NAMESPACE_DNS, "치즈케이크")),
}

# 매장/메뉴/질문/리뷰 정의
stores = [
    {
        "store_name": "고봉밥상",
        "menu_name": "된장찌개",
        "questions": ["짜지 않나요?", "국물 맛이 깊나요?", "양이 충분한가요?"],
        "reviews": [
            "국물이 너무 짜요.",
            "간이 세서 목이 메여요.",
            "싱거워서 맛이 없어요.",
            "양이 부족해요.",
            "국물 맛이 텁텁해요.",
            "짠맛이 강하지만 깊은 맛은 있어요.",
            "국물이 깔끔해서 좋습니다.",
            "된장이 진해서 좋아요.",
            "양이 많아 든든합니다.",
            "국물이 따뜻하고 구수해요.",
        ],
    },
    {
        "store_name": "엽기떡볶이",
        "menu_name": "떡볶이",
        "questions": ["맵나요?", "양이 많나요?", "맛이 자극적이지는 않나요?"],
        "reviews": [
            "매콤하고 맛있어요.",
            "양이 많아서 만족스러워요.",
            "매운맛이 강렬하고 중독적이에요.",
            "양념이 진하고 달콤해요.",
            "치즈랑 어울려서 좋아요.",
            "너무 매워서 먹기 힘들어요.",
            "양이 적어서 아쉬워요.",
            "국물이 너무 짜요.",
            "개매움.",
            "조금 달아서 느끼해요.",
        ],
    },
    {
        "store_name": "네모디저트",
        "menu_name": "치즈케이크",
        "questions": ["크기가 크나요?", "달콤한가요?", "느끼하지는 않나요?"],
        "reviews": [
            "조각이 커서 배부릅니다.",
            "달콤하고 부드러워요.",
            "치즈 맛이 진하고 깊어요.",
            "크리미해서 입안에서 녹아요.",
            "양이 넉넉해서 좋아요.",
            "너무 달아서 목이 멕혀요.",
            "조각이 작아서 아쉬워요.",
            "치즈 맛이 안남.",
            "양이 부족합니다.",
            "맛이 조금 밋밋해요.",
        ],
    },
]


@router.post("/init")
async def init_dummy_data():
    results = []

    for store in stores:
        store_id = STORE_IDS[store["store_name"]]
        menu_id = MENU_IDS[store["menu_name"]]

        # 질문 준비
        questions = [
            {"request_id": str(uuid.uuid4()), "question": q}
            for q in store["questions"]
        ]

        # queries 전체 교체 (replace_one)
        queries_col.replace_one(
            {"_id": store_id},
            {
                "_id": store_id,
                "store_name": store["store_name"],
                "menus": [
                    {
                        "menu_id": menu_id,
                        "menu_name": store["menu_name"],
                        "questions": questions,
                    }
                ],
                "updated_at": datetime.utcnow(),
            },
            upsert=True,
        )

        # 리뷰 준비
        reviews = [
            {
                "review_id": str(uuid.uuid4()),
                "text": r,
                "created_at": datetime.utcnow(),
            }
            for r in store["reviews"]
        ]

        # reviews 전체 교체 (replace_one)
        reviews_col.replace_one(
            {"_id": store_id},
            {
                "_id": store_id,
                "store_name": store["store_name"],
                "menus": [
                    {
                        "menu_id": menu_id,
                        "menu_name": store["menu_name"],
                        "reviews": reviews,
                    }
                ],
                "updated_at": datetime.utcnow(),
            },
            upsert=True,
        )

        results.append(
            {
                "store_id": store_id,
                "store_name": store["store_name"],
                "menu": store["menu_name"],
                "question_count": len(questions),
                "review_count": len(reviews),
            }
        )

    return {"msg": "Dummy data inserted", "stores": results}

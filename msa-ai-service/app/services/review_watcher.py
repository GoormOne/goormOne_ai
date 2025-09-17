import asyncio
import logging
from bson import ObjectId
from datetime import datetime
from app.db.mongodb import get_collection
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

reviews_col = get_collection("reviews")
reviews_embedding_col = get_collection("reviews_embedding")

embedding_svc = EmbeddingService()

async def watch_reviews():
    """
    MongoDB Change Stream으로 reviews 컬렉션 감시
    """
    pipeline = [{"$match": {"operationType": "insert"}}]

    try:
        with reviews_col.watch(pipeline) as stream:
            for change in stream:
                full_doc = change["fullDocument"]

                store_id = str(full_doc["_id"])
                for menu in full_doc.get("menus", []):
                    menu_id = menu["menu_id"]

                    for review in menu.get("reviews", []):
                        review_id = review["review_id"]
                        text = review["text"]

                        # 중복 체크
                        exists = reviews_embedding_col.find_one({"_id": review_id})
                        if exists:
                            logger.info(f"⚠️ Review {review_id} already embedded, skipping")
                            continue

                        # gRPC 호출 (model-service)
                        meta = {
                            "type": "review",
                            "review_id": review_id,
                            "store_id": store_id,
                            "menu_id": menu_id,
                        }
                        status = embedding_svc.embed_and_label(text, meta)
                        logger.info(f"✅ Embedded review {review_id}, status={status}")

    except Exception as e:
        logger.error(f"❌ Change Stream stopped: {e}")
        await asyncio.sleep(5)
        await watch_reviews()  # 재시작

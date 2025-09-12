# 임시테스트요오오오

import asyncio
import logging
import redis
import socket
from app.db.mongodb import get_collection
from datetime import datetime
from app.core.config import (
    REDIS_HOST, REDIS_PORT,
    REDIS_REQUEST_STREAM, REDIS_RESPONSE_STREAM, MONGODB_NAME
)

logger = logging.getLogger(__name__)

r = redis.Redis(
                host=REDIS_HOST, 
                port=REDIS_PORT, 
                decode_responses=True, 
                encoding='utf-8')

GROUP_NAME = "ai-service"
CONSUMER_NAME = "fastapi-worker"    # CONSUMER_NAME = f"fastapi-{socket.gethostname()}"
queries_col = get_collection("queries")

# ---------------------------
# Consumer 역할
# ---------------------------

def init_consumer_group():
    """Redis Consumer Group 초기화"""
    try:
        r.xgroup_create(
                        REDIS_REQUEST_STREAM, 
                        GROUP_NAME, 
                        id="0", 
                        mkstream=True
                        )
        logger.info("✅ Redis consumer group created")

    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            logger.info("ℹ️ Consumer group already exists")
        else:
            raise


def read_request():
    """Redis Stream에서 요청 읽기"""
    msgs = r.xreadgroup(
                        GROUP_NAME, 
                        CONSUMER_NAME, 
                        {REDIS_REQUEST_STREAM: ">"}, 
                        count=1, 
                        block=5000)
    
    if not msgs:
        return None
    
    _, elements = msgs[0]
    for msg_id, fields in elements:
        r.xack(REDIS_REQUEST_STREAM, GROUP_NAME, msg_id)
        return fields


# ---------------------------
# Producer 역할
# ---------------------------
def add_request(request_id: str, store_id: str, menu_id: str, query: str):
    """
    FastAPI에서 직접 Redis 요청 스트림에 메시지 추가 (테스트/내부용)
    """
    return r.xadd(REDIS_REQUEST_STREAM, {
        "request_id": request_id,
        "store_id": store_id,
        "menu_id": menu_id,
        "query": query
    })


def add_response(request_id: str, answer: str, source: str = "generated"):
    """
    FastAPI가 생성한 응답을 Redis 응답 스트림에 push
    """
    return r.xadd(REDIS_RESPONSE_STREAM, {
        "request_id": request_id,
        "answer": answer
    })
    logger.info(f"✅ Response pushed for {request_id}")


async def worker_loop():
    """Redis Worker Loop"""
    while True:
        msg = read_request()
        if msg:
            logger.info(f"📥 Received: {msg}")

            request_id = msg["request_id"]
            store_id = msg["store_id"]
            menu_id = msg["menu_id"]
            query = msg.get("query")


 # 1. 기존 store + menu 찾고 질문 push
            result = queries_col.update_one(
                {"_id": store_id, "menus.menu_id": menu_id},
                {
                    "$push": {
                        "menus.$.queries": {
                            "query_id": request_id,
                            "query": query
                        }
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

            # 2. store_id 문서가 없거나 menu_id가 없을 때 → 새로 생성
            if result.matched_count == 0:
                queries_col.update_one(
                    {"_id": store_id},
                    {
                        "$push": {
                            "menus": {
                                "menu_id": menu_id,
                                "queries": [
                                    {
                                        "query_id": request_id,
                                        "query": query
                                    }
                                ]
                            }
                        },
                        "$set": {"updated_at": datetime.utcnow()}
                    },
                    upsert=True
                )

            logger.info(f"✅ Saved to MongoDB: store={store_id}, menu={menu_id}, request={request_id}", {MONGODB_NAME})

            # 👉 간단히 확인만: 받은 질문 그대로 응답
            answer = f"'{query}'에 대한 임시 응답입니다."
            add_response(request_id, answer)

        await asyncio.sleep(0.1)


def start_redis_consumer():
    """FastAPI lifespan에서 호출"""
    init_consumer_group()
    asyncio.create_task(worker_loop())
    logger.info("🚀 Redis consumer started")
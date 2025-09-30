import asyncio
import logging
import redis
import socket
from datetime import datetime
from app.db.mongodb import get_collection
from app.core.config import (
    REDIS_HOST, REDIS_PORT,
    REDIS_REQUEST_STREAM, REDIS_RESPONSE_STREAM, MONGODB_NAME
)
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RagService

logger = logging.getLogger(__name__)

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    encoding='utf-8'
)

GROUP_NAME = "ai-service"
CONSUMER_NAME = "fastapi-worker"
# CONSUMER_NAME = f"fastapi-{socket.gethostname()}"

queries_col = get_collection("queries")

embedding_svc = EmbeddingService()
rag_svc = RagService()


# ---------------------------
# Consumer 역할
# ---------------------------
def init_consumer_group():
    """Redis Consumer Group 초기화"""
    try:
        r.xgroup_create(
            REDIS_REQUEST_STREAM,
            GROUP_NAME,
            id="$",
            mkstream=True
        )
        logger.info("✅ Redis consumer group created")

    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            logger.info("ℹ️ Consumer group already exists")
        else:
            raise


def read_request():
    """Redis Stream에서 새 요청 읽기"""
    msgs = r.xreadgroup(
        GROUP_NAME,
        CONSUMER_NAME,
        {REDIS_REQUEST_STREAM: ">"},
        count=1,
        block=5000
    )

    logger.info(f"📦 Raw msgs: {msgs}")

    if not msgs:
        return None, None

    stream, elements = msgs[0]
    for msg_id, fields in elements:
        logger.info(f"📥 Received from {stream}: id={msg_id}, fields={fields}")
        return msg_id, fields

    return None, None


# ---------------------------
# Producer 역할
# ---------------------------
def add_request(request_id: str, store_id: str, menu_id: str, query: str):
    """FastAPI에서 직접 Redis 요청 스트림에 메시지 추가"""
    return r.xadd(REDIS_REQUEST_STREAM, {
        "request_id": request_id,
        "store_id": store_id,
        "menu_id": menu_id,
        "query": query
    })


def add_response(request_id: str, answer: str, source: str = "generated"):
    """FastAPI가 생성한 응답을 Redis 응답 스트림에 push"""
    r.xadd(REDIS_RESPONSE_STREAM, {
        "request_id": request_id,
        "answer": answer,
        "source": source
    })
    logger.info(f"✅ Response pushed for {request_id}")


# ---------------------------
# Worker Loop
# ---------------------------
async def worker_loop():
    """Redis Worker Loop"""
    while True:
        msg_id, msg = read_request()
        if msg:
            try:
                logger.info(f"📥 Processing message: {msg}")

                request_id = msg["request_id"]
                store_id = msg["store_id"]
                menu_id = msg["menu_id"]
                query = msg.get("query")

                # 1. MongoDB 저장
                result = queries_col.update_one(
                    {"_id": store_id, "menus.menu_id": menu_id},
                    {
                        "$push": {"menus.$.queries": {
                            "query_id": request_id,
                            "query": query
                        }},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )

                if result.matched_count == 0:
                    queries_col.update_one(
                        {"_id": store_id},
                        {
                            "$push": {
                                "menus": {
                                    "menu_id": menu_id,
                                    "queries": [{
                                        "query_id": request_id,
                                        "query": query
                                    }]
                                }
                            },
                            "$set": {"updated_at": datetime.utcnow()}
                        },
                        upsert=True
                    )
                    logger.info(f"🆕 New menu created: store={store_id}, menu={menu_id}")
                else:
                    logger.info(f"➕ Query pushed: store={store_id}, menu={menu_id}")

                logger.info(
                    f"✅ Saved to MongoDB: store={store_id}, menu={menu_id}, request={request_id}, db={MONGODB_NAME}"
                )

                # 2. gRPC로 model-service 호출 → 임베딩/라벨링
                meta = {"type": "query", "query_id": request_id, "store_id": store_id, "menu_id": menu_id}
                embedding_svc.embed_and_label(query, meta)

                # 3. RAG 실행 → answers 저장
                answer = rag_svc.run_rag(request_id, store_id, menu_id)

                # 4. Redis 응답 스트림 push
                add_response(request_id, answer)

                # ✅ 모든 작업 성공 후 ack
                r.xack(REDIS_REQUEST_STREAM, GROUP_NAME, msg_id)
                logger.info(f"👍 Acked message {msg_id}")

            except Exception as e:
                logger.error(f"❌ Worker 처리 실패: {e}", exc_info=True)

        await asyncio.sleep(0.1)


def start_redis_consumer():
    """FastAPI lifespan에서 호출"""
    init_consumer_group()
    asyncio.create_task(worker_loop())
    logger.info("🚀 Redis consumer started")


# # 레디스 컨슈머 + 프로듀서
# # 임시테스트 완료

# import asyncio
# import logging
# import redis
# import socket
# from datetime import datetime
# from app.db.mongodb import get_collection
# from app.core.config import (
#     REDIS_HOST, REDIS_PORT,
#     REDIS_REQUEST_STREAM, REDIS_RESPONSE_STREAM, MONGODB_NAME
# )
# from app.services.embedding_service import EmbeddingService
# from app.services.rag_service import RagService

# logger = logging.getLogger(__name__)

# r = redis.Redis(
#                 host=REDIS_HOST, 
#                 port=REDIS_PORT, 
#                 decode_responses=True, 
#                 encoding='utf-8')

# GROUP_NAME = "ai-service"
# CONSUMER_NAME = "fastapi-worker"    
# # CONSUMER_NAME = f"fastapi-{socket.gethostname()}"

# queries_col = get_collection("queries")

# embedding_svc = EmbeddingService()
# rag_svc = RagService()


# # ---------------------------
# # Consumer 역할
# # ---------------------------
# last_id = "0"
# def init_consumer_group():
#     """Redis Consumer Group 초기화"""
#     try:
#         r.xgroup_create(
#                         REDIS_REQUEST_STREAM, 
#                         GROUP_NAME, 
#                         id="$", 
#                         mkstream=True
#                         )
#         logger.info("✅ Redis consumer group created")

#     except redis.exceptions.ResponseError as e:
#         if "BUSYGROUP" in str(e):
#             logger.info("ℹ️ Consumer group already exists")
#         else:
#             raise
# def read_request():
#     msgs = r.xreadgroup(
#         GROUP_NAME,
#         CONSUMER_NAME,
#         {REDIS_REQUEST_STREAM: ">"},  # backlog 포함 전부 읽기
#         count=1,
#         block=5000
#     )

#     logger.info(f"📦 Raw msgs: {msgs}")

#     if not msgs:
#         return None

#     stream, elements = msgs[0]
#     for msg_id, fields in elements:
#         logger.info(f"📥 Received from {stream}: id={msg_id}, fields={fields}")
#         r.xack(REDIS_REQUEST_STREAM, GROUP_NAME, msg_id)
#         return fields

# """
# def read_request():
#     global last_id

#     msgs = r.xreadgroup(
#         GROUP_NAME,
#         CONSUMER_NAME,
#         {REDIS_REQUEST_STREAM: last_id},
#         count=1,
#         block=5000
#     )

#     logger.info(f"📦 Raw msgs: {msgs}")  # 무조건 찍기

#     if not msgs:
#         return None

#     stream, elements = msgs[0]
#     if not elements:
#         return None

#     msg_id, fields = elements[0]
#     logger.info(f"📦 Read from stream: id={msg_id}, fields={fields}")
#     r.xack(REDIS_REQUEST_STREAM, GROUP_NAME, msg_id)

#     if last_id == "0":
#         last_id = ">"

#     return fields

# """

# # def read_request():
# #     msgs = r.xreadgroup(
# #         GROUP_NAME,
# #         CONSUMER_NAME,
# #         {REDIS_REQUEST_STREAM: ">"},
# #         count=1,
# #         block=5000
# #     )
# #     logger.info(f"📦 Raw msgs: {msgs}")  

# #     if not msgs:
# #         return None
# #     msg_id, fields = msgs[0][1][0]

# #     # _, elements = msgs[0]
# #     # msg_id, fields = elements[0]
# #     logger.info(f"📦 Read from stream: id={msg_id}, fields={fields}")
# #     r.xack(REDIS_REQUEST_STREAM, GROUP_NAME, msg_id)
# #     return fields

# # def read_request(process_old = False):
# #     """Redis Stream에서 요청 읽기"""
# #     last_id = "0" if process_old else ">"
# #     msgs = r.xreadgroup(
# #                         GROUP_NAME, 
# #                         CONSUMER_NAME, 
# #                         {REDIS_REQUEST_STREAM: "last_id"}, # >로 해보기 
# #                         count=1, 
# #                         block=5000)
    
# #     if not msgs:
# #         logger.debug("⏳ No new messages")
# #         return None
    
# #     _, elements = msgs[0]
# #     for msg_id, fields in elements:
# #         logger.info(f"📦 Read from stream: id={msg_id}, fields={fields}")
# #         r.xack(REDIS_REQUEST_STREAM, GROUP_NAME, msg_id)
# #         yield fields


# # ---------------------------
# # Producer 역할
# # ---------------------------
# def add_request(request_id: str, store_id: str, menu_id: str, query: str):
#     """
#     FastAPI에서 직접 Redis 요청 스트림에 메시지 추가 (테스트/내부용)
#     """
#     return r.xadd(REDIS_REQUEST_STREAM, {
#         "request_id": request_id,
#         "store_id": store_id,
#         "menu_id": menu_id,
#         "query": query
#     })


# def add_response(request_id: str, answer: str, source: str = "generated"):
#     """
#     FastAPI가 생성한 응답을 Redis 응답 스트림에 push
#     """
#     return r.xadd(REDIS_RESPONSE_STREAM, {
#         "request_id": request_id,
#         "answer": answer
#     })
#     logger.info(f"✅ Response pushed for {request_id}")



# # ---------------------------
# # Worker Loop
# # ---------------------------
# async def worker_loop():
#     """Redis Worker Loop"""
#     while True:
#         msg = read_request()
#         if msg:
#             logger.info(f"📥 Received: {msg}")

#             request_id = msg["request_id"]
#             store_id = msg["store_id"]
#             menu_id = msg["menu_id"]
#             query = msg.get("query")


#             # 1. 기존 store + menu 찾고 질문 push
#             result = queries_col.update_one(
#                 {"_id": store_id, "menus.menu_id": menu_id},
#                 {
#                     "$push": {
#                         "menus.$.queries": {
#                             "query_id": request_id,
#                             "query": query
#                         }
#                     },
#                     "$set": {"updated_at": datetime.utcnow()}
#                 }
#             )

#             # 1-2. store_id 문서가 없거나 menu_id가 없을 때 → 새로 생성
#             if result.matched_count == 0:
#                 queries_col.update_one(
#                     {"_id": store_id},
#                     {
#                         "$push": {
#                             "menus": {
#                                 "menu_id": menu_id,
#                                 "queries": [
#                                     {
#                                         "query_id": request_id,
#                                         "query": query
#                                     }
#                                 ]
#                             }
#                         },
#                         "$set": {"updated_at": datetime.utcnow()}
#                     },
#                     upsert=True
#                 )

#             logger.info(f"✅ Saved to MongoDB: store={store_id}, menu={menu_id}, request={request_id}, db={MONGODB_NAME}")


#             # 2. gRPC로 model-service 호출 → 임베딩/라벨링 + queries_embedding 저장
#             meta = {"type": "query", "query_id": request_id, "store_id": store_id, "menu_id": menu_id}
#             embedding_svc.embed_and_label(query, meta)

#             # 3. RAG 실행 → answers 저장
#             answer = rag_svc.run_rag(request_id, store_id, menu_id)

#             # 4. Redis 응답 스트림 push (Spring이 사용자한테 전달)
#             add_response(request_id, answer)

            
#             # # 👉 간단히 확인만: 받은 질문 그대로 응답
#             # answer = f"'{query}'에 대한 임시 응답입니다."
#             # add_response(request_id, answer)

#         await asyncio.sleep(0.1)


# def start_redis_consumer():
#     """FastAPI lifespan에서 호출"""
#     init_consumer_group()
#     asyncio.create_task(worker_loop())
#     logger.info("🚀 Redis consumer started")
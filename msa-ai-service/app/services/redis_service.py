# Redis 연결 및 Stream 헬퍼 함수 모음
# Redis Stream에서 질문 읽고, 몽고디비 저장, rag_service 호출, 응답 redis stream에 push

import redis
import os

# 싱글톤 Redis 클라이언트
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

REQUEST_STREAM = "chat:requests"
RESPONSE_STREAM = "chat:responses"

def add_request(request_id: str, user_id: str, question: str):
    return r.xadd(REQUEST_STREAM, {
        "request_id": request_id,
        "user_id": user_id,
        "question": question
    })

def read_requests(group: str, consumer: str, count: int = 1, block: int = 5000):
    try:
        return r.xreadgroup(group, consumer, {REQUEST_STREAM: ">"}, count=count, block=block)
    except redis.exceptions.ResponseError as e:
        # 그룹 없을 때 최초 생성
        if "NOGROUP" in str(e):
            r.xgroup_create(REQUEST_STREAM, group, id="$", mkstream=True)
        return []

def add_response(request_id: str, reply: str, source: str = "generated"):
    return r.xadd(RESPONSE_STREAM, {
        "request_id": request_id,
        "reply": reply,
        "source": source
    })

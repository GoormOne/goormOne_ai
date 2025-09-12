# 임시테스트요오오
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import sys
from app.routes import health
from app.core.config import ENV
from app.services.redis_service import start_redis_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis Consumer 시작
    start_redis_consumer()
    yield


app = FastAPI(title="MSA AI Service", lifespan=lifespan)

# 공통 라우터
app.include_router(health.router, prefix="/ai", tags=["health"])

# dev 환경일 때만 seed_router 등록
if ENV == "dev":
    from app.routes import seed_router
    app.include_router(seed_router.router, prefix="/ai", tags=["seed"])


# # (Spring + Mongo + Redis Stream 자동 실행)

# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# from app.routes import health, qa_router
# from app.core.config import ENV
# if ENV == "dev": from app.routes import seed_router
# import logging
# import sys
# from app.services.redis_service import start_redis_consumer
# from app.services.redis_service import read_request, add_response
# import asyncio


# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)-5s %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     stream=sys.stdout,
# )
# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
    
#     # Redis Consumer 시작
#     start_redis_consumer()
#     yield

# app = FastAPI(title="MSA AI Service", lifespan=lifespan)

# # 공통 라우터
# app.include_router(health.router, prefix="/ai", tags=["health"])
# app.include_router(qa_router.router, prefix="/ai", tags=["qa"])

# # dev 환경일 때만 seed_router 등록
# if ENV == "dev":
#     app.include_router(seed_router.router, prefix="/ai", tags=["seed"])

# (Spring + Mongo + Change Stream 자동 실행)

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import health, qa_router, seed_router
from app.services.change_stream_service import start_watchers
from app.core.config import ENV
if ENV == "dev": from app.routes import seed_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Mongo Change Stream 시작
    start_watchers()
    yield

app = FastAPI(title="MSA AI Service", lifespan=lifespan)

# 공통 라우터
app.include_router(health.router, prefix="/ai", tags=["health"])
app.include_router(qa_router.router, prefix="/ai", tags=["qa"])

# dev 환경일 때만 seed_router 등록
if ENV == "dev":
    app.include_router(seed_router.router, prefix="/ai", tags=["seed"])

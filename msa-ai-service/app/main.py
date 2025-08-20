from fastapi import FastAPI
from app.routes import health, seed_router, qa_router

app = FastAPI(title="MSA AI Service")

app.include_router(health.router, prefix="/ai", tags=["health"])
app.include_router(seed_router.router, prefix="/ai", tags=["seed"])
app.include_router(qa_router.router, prefix="/ai", tags=["qa"])

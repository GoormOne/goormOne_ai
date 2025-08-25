import logging
import sys
from fastapi import FastAPI
from app.routes import health, seed_router, qa_router
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


app = FastAPI(title="MSA AI Service")


app.include_router(health.router, prefix="/ai", tags=["health"])
app.include_router(seed_router.router, prefix="/ai", tags=["seed"])
app.include_router(qa_router.router, prefix="/ai", tags=["qa"])

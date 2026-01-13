from fastapi import APIRouter
from app.api.endpoints import ingestion, query, health

router = APIRouter()

router.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])
router.include_router(query.router, prefix="/query", tags=["query"])
router.include_router(health.router, prefix="/health", tags=["health"])

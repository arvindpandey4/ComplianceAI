from fastapi import APIRouter
from app.api.endpoints import ingestion, query, health, auth

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])
router.include_router(query.router, prefix="/query", tags=["query"])
router.include_router(health.router, prefix="/health", tags=["health"])

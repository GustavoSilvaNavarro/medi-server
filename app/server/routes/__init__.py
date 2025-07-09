from fastapi import APIRouter

from .check import router as redis_routes
from .monitoring import router as monitoring_router
from .quotes import router as quotes_router

router = APIRouter()

router.include_router(monitoring_router)
router.include_router(redis_routes)
router.include_router(quotes_router, prefix="/quotes", tags=["Quotes"])

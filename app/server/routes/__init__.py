from fastapi import APIRouter

from .monitoring import router as monitoring_router
from .quotes import router as quotes_router

router = APIRouter()

router.include_router(monitoring_router)
router.include_router(quotes_router, prefix="/quotes")

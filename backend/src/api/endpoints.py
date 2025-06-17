import fastapi

from src.api.routes.authentication import router as auth_router
from src.api.routes.market import router as market_router

router = fastapi.APIRouter()

router.include_router(router=market_router)
router.include_router(router=auth_router)

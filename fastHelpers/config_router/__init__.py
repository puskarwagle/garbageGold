# fastHelpers/config_router/__init__.py
from fastapi import APIRouter

# Create the main API router WITHOUT auth dependency
router = APIRouter(
    prefix="/api",
    tags=["config"]
    # REMOVED: dependencies=[Depends(auth_manager.verify_laravel_token)]
)

# Import and include all sub-routers
from .personals import router as personals_router
from .secrets import router as secrets_router
from .questions import router as questions_router
from .search import router as search_router
from .settings import router as settings_router

# Include all sub-routers
router.include_router(personals_router)
router.include_router(secrets_router)
router.include_router(questions_router)
router.include_router(search_router)
router.include_router(settings_router)
from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
from typing import Dict, Any
import shutil

from fastHelpers.auth import auth_manager
from fastHelpers.config_updater import ConfigUpdater

# Create the main API router with global auth dependency
router = APIRouter(
    prefix="/api",
    tags=["config"],
    dependencies=[Depends(auth_manager.verify_laravel_token)]
)

# Shared config handlers used by all sub-routers
def get_shared_handlers():
    config_updater = ConfigUpdater()

    async def handle_config_update(config_type: str, data: Dict[str, Any]):
        try:
            backup_path = config_updater.backup_config(config_type)
            result = config_updater.update_config(config_type, data)
            if result["status"] == "success":
                return {
                    "success": True,
                    "message": result["message"],
                    "backup_created": backup_path,
                    "file_path": result["file_path"]
                }
            raise HTTPException(status_code=500, detail=result["message"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    async def handle_config_get(config_type: str):
        try:
            config_data = config_updater.read_config(config_type)
            if "error" in config_data:
                raise HTTPException(status_code=404, detail=config_data["error"])
            return {"success": True, "data": config_data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    async def handle_config_restore(config_type: str):
        try:
            config_path = Path(__file__).parent.parent.parent / "config"
            source_backup = config_path / "backup" / f"{config_type}.py.backup"
            target_file = config_path / f"{config_type}.py"
            if not source_backup.exists():
                raise HTTPException(status_code=404, detail=f"No backup file found for {config_type}")
            shutil.copy2(source_backup, target_file)
            return {
                "success": True,
                "message": f"{config_type}.py restored from backup successfully"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")

    return handle_config_update, handle_config_get, handle_config_restore

# Inject shared handlers into each module on import
handle_config_update, handle_config_get, handle_config_restore = get_shared_handlers()

# Sub-route modules
from .personals import router as personals_router
from .secrets import router as secrets_router
from .questions import router as questions_router
from .search import router as search_router
from .settings import router as settings_router

router.include_router(personals_router)
router.include_router(secrets_router)
router.include_router(questions_router)
router.include_router(search_router)
router.include_router(settings_router)

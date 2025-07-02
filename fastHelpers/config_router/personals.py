from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil
from fastHelpers.config_updater import ConfigUpdater

router = APIRouter()
config_updater = ConfigUpdater()

class PersonalsData(BaseModel):
    first_name: str
    middle_name: str = ""
    last_name: str
    phone_number: str
    current_city: str = ""
    street: str = ""
    state: str = ""
    zipcode: str = ""
    country: str = ""
    ethnicity: str = ""
    gender: str = ""
    disability_status: str = ""
    veteran_status: str = ""

@router.post("/update-personals")
async def update_personals(data: PersonalsData):
    return await handle_config_update("personals", data.dict())

@router.get("/get-personals")
async def get_current_personals():
    return await handle_config_get("personals")

@router.post("/restore-personals-backup")
async def restore_personals_backup():
    return await handle_config_restore("personals")

# You can optionally factor shared helpers like these into a `shared.py`
async def handle_config_update(config_type: str, data: dict):
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
            raise HTTPException(status_code=404, detail=f"No backup found for {config_type}")
        shutil.copy2(source_backup, target_file)
        return {
            "success": True,
            "message": f"{config_type}.py restored from backup"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")

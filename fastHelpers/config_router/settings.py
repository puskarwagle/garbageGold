from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Union

from fastHelpers.config_router import (
    handle_config_update,
    handle_config_get,
    handle_config_restore,
)

router = APIRouter()

class SettingsData(BaseModel):
    close_tabs: Optional[bool] = False
    follow_companies: Optional[bool] = False
    run_non_stop: Optional[bool] = False
    alternate_sortby: Optional[bool] = False
    cycle_date_posted: Optional[bool] = False
    stop_date_cycle_at_24hr: Optional[bool] = False
    generated_resume_path: Optional[str] = ""
    file_name: Optional[str] = "applied_jobs"
    failed_file_name: Optional[str] = "failed_jobs"
    logs_folder_path: Optional[str] = "logs"
    click_gap: Optional[Union[int, float]] = 1
    run_in_background: Optional[bool] = False
    disable_extensions: Optional[bool] = False
    safe_mode: Optional[bool] = False
    smooth_scroll: Optional[bool] = False
    keep_screen_awake: Optional[bool] = False
    stealth_mode: Optional[bool] = False
    showAiErrorAlerts: Optional[bool] = True

@router.post("/update-settings")
async def update_settings(data: SettingsData):
    return await handle_config_update("settings", data.dict())

@router.get("/get-settings")
async def get_settings():
    return await handle_config_get("settings")

@router.post("/restore-settings-backup")
async def restore_settings_backup():
    return await handle_config_restore("settings")

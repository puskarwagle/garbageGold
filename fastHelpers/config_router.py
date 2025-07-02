# fastHelpers/config_router.py
from fastapi import APIRouter, Depends, HTTPException
from fastHelpers.auth import auth_manager
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from .config_updater import ConfigUpdater
import shutil
from pathlib import Path

# Pydantic models for each config type
class PersonalsData(BaseModel):
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    phone_number: str
    current_city: Optional[str] = ""
    street: Optional[str] = ""
    state: Optional[str] = ""
    zipcode: Optional[str] = ""
    country: Optional[str] = ""
    ethnicity: Optional[str] = ""
    gender: Optional[str] = ""
    disability_status: Optional[str] = ""
    veteran_status: Optional[str] = ""

class SecretsData(BaseModel):
    username: Optional[str] = ""
    password: Optional[str] = ""
    use_AI: Optional[bool] = False
    ai_provider: Optional[str] = "deepseek"
    deepseek_api_url: Optional[str] = "https://api.deepseek.com"
    deepseek_api_key: Optional[str] = ""
    deepseek_model: Optional[str] = "deepseek-chat"
    llm_api_url: Optional[str] = "https://api.openai.com/v1/"
    llm_api_key: Optional[str] = ""
    llm_model: Optional[str] = "gpt-3.5-turbo"
    llm_spec: Optional[str] = "openai"
    stream_output: Optional[bool] = False

class QuestionsData(BaseModel):
    default_resume_path: Optional[str] = ""
    years_of_experience: Optional[str] = ""
    require_visa: Optional[str] = ""
    website: Optional[str] = ""
    linkedIn: Optional[str] = ""
    us_citizenship: Optional[str] = ""
    desired_salary: Optional[Union[int, str]] = 0
    current_ctc: Optional[Union[int, str]] = 0
    notice_period: Optional[Union[int, str]] = 0
    linkedin_headline: Optional[str] = ""
    linkedin_summary: Optional[str] = ""
    cover_letter: Optional[str] = ""
    user_information_all: Optional[str] = ""
    recent_employer: Optional[str] = ""
    confidence_level: Optional[str] = ""
    pause_before_submit: Optional[bool] = False
    pause_at_failed_question: Optional[bool] = False
    overwrite_previous_answers: Optional[bool] = False

class SearchData(BaseModel):
    search_terms: Optional[List[str]] = []
    search_location: Optional[str] = ""
    switch_number: Optional[int] = 1
    randomize_search_order: Optional[bool] = False
    sort_by: Optional[str] = ""
    date_posted: Optional[str] = ""
    salary: Optional[str] = ""
    easy_apply_only: Optional[bool] = True
    experience_level: Optional[List[str]] = []
    job_type: Optional[List[str]] = []
    on_site: Optional[List[str]] = []
    companies: Optional[List[str]] = []
    location: Optional[List[str]] = []
    industry: Optional[List[str]] = []
    job_function: Optional[List[str]] = []
    job_titles: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    commitments: Optional[List[str]] = []
    under_10_applicants: Optional[bool] = False
    in_your_network: Optional[bool] = False
    fair_chance_employer: Optional[bool] = False
    pause_after_filters: Optional[bool] = False
    about_company_bad_words: Optional[List[str]] = []
    about_company_good_words: Optional[List[str]] = []
    bad_words: Optional[List[str]] = []
    security_clearance: Optional[bool] = False
    did_masters: Optional[bool] = False
    current_experience: Optional[str] = ""

class SettingsData(BaseModel):
    # LinkedIn settings
    close_tabs: Optional[bool] = False
    follow_companies: Optional[bool] = False
    run_non_stop: Optional[bool] = False
    alternate_sortby: Optional[bool] = False
    cycle_date_posted: Optional[bool] = False
    stop_date_cycle_at_24hr: Optional[bool] = False
    # Resume generator
    generated_resume_path: Optional[str] = ""
    # Global settings
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

# Initialize unified config updater
config_updater = ConfigUpdater()

# Create router
router = APIRouter(
    prefix="/api",
    tags=["config"],
    dependencies=[Depends(auth_manager.require_auth())]  # 🔒 all routes locked
)

# Generic helper functions
async def handle_config_update(config_type: str, data: Dict[str, Any]):
    """Generic config update handler"""
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
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

async def handle_config_get(config_type: str):
    """Generic config get handler"""
    try:
        config_data = config_updater.read_config(config_type)
        
        if "error" in config_data:
            raise HTTPException(status_code=404, detail=config_data["error"])
        
        return {"success": True, "data": config_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

async def handle_config_restore(config_type: str):
    """Generic config restore handler"""
    try:
        config_path = Path(__file__).parent.parent / "config"
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

# ============ PERSONALS ROUTES ============
@router.post("/update-personals")
async def update_personals(data: PersonalsData):
    """Update personals.py with form data"""
    return await handle_config_update("personals", data.dict())

@router.get("/get-personals")
async def get_current_personals():
    """Get current personals.py configuration"""
    return await handle_config_get("personals")

@router.post("/restore-personals-backup")
async def restore_personals_backup():
    """Restore personals.py from backup"""
    return await handle_config_restore("personals")

# ============ SECRETS ROUTES ============
@router.post("/update-secrets")
async def update_secrets(data: SecretsData):
    """Update secrets.py with form data"""
    return await handle_config_update("secrets", data.dict())

@router.get("/get-secrets")
async def get_current_secrets():
    """Get current secrets.py configuration"""
    return await handle_config_get("secrets")

@router.post("/restore-secrets-backup")
async def restore_secrets_backup():
    """Restore secrets.py from backup"""
    return await handle_config_restore("secrets")

# ============ QUESTIONS ROUTES ============
@router.post("/update-questions")
async def update_questions(data: QuestionsData):
    """Update questions.py with form data"""
    return await handle_config_update("questions", data.dict())

@router.get("/get-questions")
async def get_current_questions():
    """Get current questions.py configuration"""
    return await handle_config_get("questions")

@router.post("/restore-questions-backup")
async def restore_questions_backup():
    """Restore questions.py from backup"""
    return await handle_config_restore("questions")

# ============ SEARCH ROUTES ============
@router.post("/update-search")
async def update_search(data: SearchData):
    """Update search.py with form data"""
    return await handle_config_update("search", data.dict())

@router.get("/get-search")
async def get_current_search():
    """Get current search.py configuration"""
    return await handle_config_get("search")

@router.post("/restore-search-backup")
async def restore_search_backup():
    """Restore search.py from backup"""
    return await handle_config_restore("search")

# ============ SETTINGS ROUTES ============
@router.post("/update-settings")
async def update_settings(data: SettingsData):
    """Update settings.py with form data"""
    return await handle_config_update("settings", data.dict())

@router.get("/get-settings")
async def get_current_settings():
    """Get current settings.py configuration"""
    return await handle_config_get("settings")

@router.post("/restore-settings-backup")
async def restore_settings_backup():
    """Restore settings.py from backup"""
    return await handle_config_restore("settings")

# ============ BULK OPERATIONS ============
@router.get("/get-all-configs")
async def get_all_configs():
    """Get all configuration files at once"""
    try:
        all_configs = {}
        config_types = ["personals", "secrets", "questions", "search", "settings"]
        
        for config_type in config_types:
            config_data = config_updater.read_config(config_type)
            all_configs[config_type] = config_data
        
        return {"success": True, "data": all_configs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/backup-all-configs")
async def backup_all_configs():
    """Create backups of all configuration files"""
    try:
        config_types = ["personals", "secrets", "questions", "search", "settings"]
        backup_paths = {}
        
        for config_type in config_types:
            backup_path = config_updater.backup_config(config_type)
            backup_paths[config_type] = backup_path
        
        return {
            "success": True,
            "message": "All config files backed up successfully",
            "backup_paths": backup_paths
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")
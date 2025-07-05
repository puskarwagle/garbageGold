# fastHelpers/confit_router/settings.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Union
import shutil

router = APIRouter()  # <- Remove the duplicate

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

def generate_settings_template(data: dict) -> str:
    """Generate settings.py content from form data"""
    clean_data = {}
    for key, value in data.items():
        if isinstance(value, bool):
            clean_data[key] = str(value)
        elif isinstance(value, (int, float)):
            clean_data[key] = value
        else:
            clean_data[key] = f'"{value}"'
    
    return '''###################################################### CONFIGURE YOUR BOT HERE ######################################################

# >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<< #
close_tabs = {close_tabs}
follow_companies = {follow_companies}
run_non_stop = {run_non_stop}
alternate_sortby = {alternate_sortby}
cycle_date_posted = {cycle_date_posted}
stop_date_cycle_at_24hr = {stop_date_cycle_at_24hr}

# >>>>>>>>>>> RESUME GENERATOR (Experimental & In Development) <<<<<<<<<
generated_resume_path = {generated_resume_path}

# >>>>>>>>>>> Global Settings <<<<<<<<<
file_name = {file_name}
failed_file_name = {failed_file_name}
logs_folder_path = {logs_folder_path}
click_gap = {click_gap}
run_in_background = {run_in_background}
disable_extensions = {disable_extensions}
safe_mode = {safe_mode}
smooth_scroll = {smooth_scroll}
keep_screen_awake = {keep_screen_awake}
stealth_mode = {stealth_mode}
showAiErrorAlerts = {showAiErrorAlerts}
'''.format(**clean_data)

async def write_settings_file(data: dict) -> dict:
    """Write settings.py file"""
    try:
        # Adjust path based on your actual structure
        config_path = Path(__file__).parent.parent.parent / "config"
        settings_file = config_path / "settings.py"
        
        # Backup existing file
        if settings_file.exists():
            backup_dir = config_path / "backup"
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(settings_file, backup_dir / "settings.py.backup")
        
        # Write new content
        content = generate_settings_template(data)
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "message": "Settings updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def read_settings_file() -> dict:
    """Read existing settings.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        settings_file = config_path / "settings.py"
        
        if not settings_file.exists():
            return {"error": "settings.py not found"}
        
        config_vars = {}
        with open(settings_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    var_name, var_value = line.split('=', 1)
                    var_name = var_name.strip()
                    var_value = var_value.strip().strip('"').strip("'")
                    
                    # Convert to proper types
                    if var_value.lower() in ['true', 'false']:
                        var_value = var_value.lower() == 'true'
                    elif var_value.isdigit():
                        var_value = int(var_value)
                    elif var_value.replace('.', '', 1).isdigit():
                        var_value = float(var_value)
                    
                    config_vars[var_name] = var_value
        
        return config_vars
    except Exception as e:
        return {"error": f"Failed to read settings.py: {str(e)}"}

@router.post("/update-settings")
async def update_settings(data: SettingsData):
    result = await write_settings_file(data.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.post("/update-bot-config")  # <- Laravel endpoint
async def update_bot_config(data: SettingsData):
    return await update_settings(data)

@router.get("/get-settings")
async def get_settings():
    result = await read_settings_file()
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}
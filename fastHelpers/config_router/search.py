# fastHelpers/config_router/search.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Union, List
import shutil
import json

router = APIRouter()

class SearchData(BaseModel):
    search_terms: Optional[List[str]] = []
    search_location: Optional[str] = ""
    switch_number: Optional[int] = 1
    randomize_search_order: Optional[bool] = False
    sort_by: Optional[str] = "Most recent"
    date_posted: Optional[str] = "Any time"
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

def generate_search_template(data: dict) -> str:
    """Generate search.py content from form data"""
    clean_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            clean_data[key] = json.dumps(value)
        elif isinstance(value, bool):
            clean_data[key] = str(value)
        elif isinstance(value, int):
            clean_data[key] = value
        else:
            # Escape quotes in string values
            clean_value = str(value).replace('"', '\\"').replace("'", "\\'")
            clean_data[key] = f'"{clean_value}"'
    
    return '''###################################################### LINKEDIN SEARCH PREFERENCES ######################################################

search_terms = {search_terms}
search_location = {search_location}
switch_number = {switch_number}
randomize_search_order = {randomize_search_order}

# >>>>>>>>>>> Job Search Filters <<<<<<<<<<<

sort_by = {sort_by}
date_posted = {date_posted}
salary = {salary}
easy_apply_only = {easy_apply_only}

experience_level = {experience_level}
job_type = {job_type}
on_site = {on_site}
companies = {companies}
location = {location}
industry = {industry}
job_function = {job_function}
job_titles = {job_titles}
benefits = {benefits}
commitments = {commitments}

under_10_applicants = {under_10_applicants}
in_your_network = {in_your_network}
fair_chance_employer = {fair_chance_employer}

# >>>>>>>>>>> RELATED SETTING <<<<<<<<<<<

pause_after_filters = {pause_after_filters}

# >>>>>>>>>>> SKIP IRRELEVANT JOBS <<<<<<<<<<<

about_company_bad_words = {about_company_bad_words}
about_company_good_words = {about_company_good_words}
bad_words = {bad_words}

security_clearance = {security_clearance}
did_masters = {did_masters}
current_experience = {current_experience}
'''.format(**clean_data)

async def write_search_file(data: dict) -> dict:
    """Write search.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        search_file = config_path / "search.py"
        
        # Backup existing file
        if search_file.exists():
            backup_dir = config_path / "backup"
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(search_file, backup_dir / "search.py.backup")
        
        # Write new content
        content = generate_search_template(data)
        with open(search_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "message": "Search updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def read_search_file() -> dict:
    """Read existing search.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        search_file = config_path / "search.py"
        
        if not search_file.exists():
            return {"error": "search.py not found"}
        
        config_vars = {}
        with open(search_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    var_name, var_value = line.split('=', 1)
                    var_name = var_name.strip()
                    var_value = var_value.strip()
                    
                    # Remove inline comments
                    if '#' in var_value:
                        var_value = var_value.split('#')[0].strip()
                    
                    # Handle different data types
                    if var_value.startswith('[') and var_value.endswith(']'):
                        # List/array
                        try:
                            var_value = json.loads(var_value)
                        except json.JSONDecodeError:
                            var_value = []
                    elif var_value.lower() in ['true', 'false']:
                        # Boolean
                        var_value = var_value.lower() == 'true'
                    elif var_value.isdigit():
                        # Integer
                        var_value = int(var_value)
                    elif var_value.replace('.', '', 1).isdigit():
                        # Float
                        var_value = float(var_value)
                    else:
                        # String - remove quotes
                        var_value = var_value.strip('"').strip("'")
                    
                    config_vars[var_name] = var_value
        
        return config_vars
    except Exception as e:
        return {"error": f"Failed to read search.py: {str(e)}"}

@router.post("/update-search")
async def update_search(data: SearchData):
    result = await write_search_file(data.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/get-search")
async def get_search():
    result = await read_search_file()
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}
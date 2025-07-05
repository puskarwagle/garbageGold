# fastHelpers/config_router/personals.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import shutil

router = APIRouter()

class PersonalsData(BaseModel):
    first_name: Optional[str] = ""
    middle_name: Optional[str] = ""
    last_name: Optional[str] = ""
    phone_number: Optional[str] = ""
    current_city: Optional[str] = ""
    street: Optional[str] = ""
    state: Optional[str] = ""
    zipcode: Optional[str] = ""
    country: Optional[str] = ""
    ethnicity: Optional[str] = ""
    gender: Optional[str] = ""
    disability_status: Optional[str] = ""
    veteran_status: Optional[str] = ""

def generate_personals_template(data: dict) -> str:
    """Generate personals.py content from form data"""
    clean_data = {}
    for key, value in data.items():
        # Escape quotes in string values
        clean_value = str(value).replace('"', '\\"').replace("'", "\\'")
        clean_data[key] = clean_value
    
    return '''# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Your legal name
first_name = "{first_name}"                 # Your first name in quotes Eg: "First", "Sai"
middle_name = "{middle_name}"            # Your name in quotes Eg: "Middle", "Vignesh", ""
last_name = "{last_name}"                # Your last name in quotes Eg: "Last", "Golla"

# Phone number (required), make sure it's valid.
phone_number = "{phone_number}"        # Enter your 10 digit number in quotes Eg: "9876543210"

# What is your current city?
current_city = "{current_city}"                  # Los Angeles, San Francisco, etc.
\'''
Note: If left empty as "", the bot will fill in location of jobs location.
\'''

# Address, not so common question but some job applications make it required!
street = "{street}"
state = "{state}"
zipcode = "{zipcode}"
country = "{country}"

## US Equal Opportunity questions
# What is your ethnicity or race? If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
ethnicity = "{ethnicity}"              # "Decline", "Hispanic/Latino", "American Indian or Alaska Native", "Asian", "Black or African American", "Native Hawaiian or Other Pacific Islander", "White", "Other"

# How do you identify yourself? If left empty as "", tool will not answer the question. However, note that some companies make compulsory to be answered
gender = "{gender}"                 # "Male", "Female", "Other", "Decline" or ""

# Are you physically disabled or have a history/record of having a disability? If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
disability_status = "{disability_status}"      # "Yes", "No", "Decline"

veteran_status = "{veteran_status}"         # "Yes", "No", "Decline"
##


\'''
For string variables followed by comments with options, only use the answers from given options.
Some valid examples are:
* variable1 = "option1"         # "option1", "option2", "option3" or ("" to not select). Answers are case sensitive.#
* variable2 = ""                # "option1", "option2", "option3" or ("" to not select). Answers are case sensitive.#

Other variables are free text. No restrictions other than compulsory use of quotes.
Some valid examples are:
* variable3 = "Random Answer 5"         # Enter your answer. Eg: "Answer1", "Answer2"

Invalid inputs will result in an error!
\'''
'''.format(**clean_data)

async def write_personals_file(data: dict) -> dict:
    """Write personals.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        personals_file = config_path / "personals.py"
        
        # Backup existing file
        if personals_file.exists():
            backup_dir = config_path / "backup"
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(personals_file, backup_dir / "personals.py.backup")
        
        # Write new content
        content = generate_personals_template(data)
        with open(personals_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "message": "Personals updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def read_personals_file() -> dict:
    """Read existing personals.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        personals_file = config_path / "personals.py"
        
        if not personals_file.exists():
            return {"error": "personals.py not found"}
        
        config_vars = {}
        with open(personals_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#') and not line.startswith("'''"):
                    var_name, var_value = line.split('=', 1)
                    var_name = var_name.strip()
                    var_value = var_value.strip().strip('"').strip("'")
                    
                    # Remove inline comments
                    if '#' in var_value:
                        var_value = var_value.split('#')[0].strip().strip('"').strip("'")
                    
                    config_vars[var_name] = var_value
        
        return config_vars
    except Exception as e:
        return {"error": f"Failed to read personals.py: {str(e)}"}

@router.post("/update-personals")
async def update_personals(data: PersonalsData):
    result = await write_personals_file(data.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/get-personals")
async def get_personals():
    result = await read_personals_file()
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}
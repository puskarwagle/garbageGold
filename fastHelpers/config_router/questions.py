# fastHelpers/config_router/questions.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Union
import shutil

router = APIRouter()

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

def generate_questions_template(data: dict) -> str:
    """Generate questions.py content from form data"""
    clean_data = {}
    for key, value in data.items():
        # Handle numeric fields without quotes
        if key in ["desired_salary", "current_ctc", "notice_period"]:
            clean_data[key] = value if value not in [None, "", "None"] else 0
        # Handle boolean fields
        elif isinstance(value, bool):
            clean_data[key] = str(value)
        else:
            # Escape quotes in string values
            clean_value = str(value).replace('"', '\\"').replace("'", "\\'")
            clean_data[key] = clean_value
    
    return '''default_resume_path = "{default_resume_path}"
years_of_experience = "{years_of_experience}"
require_visa = "{require_visa}"
website = "{website}"
linkedIn = "{linkedIn}"
us_citizenship = "{us_citizenship}"

desired_salary = {desired_salary}
current_ctc = {current_ctc}

notice_period = {notice_period}
linkedin_headline = "{linkedin_headline}"
linkedin_summary = """{linkedin_summary}"""
cover_letter = """{cover_letter}"""
user_information_all = """{user_information_all}"""
recent_employer = "{recent_employer}"
confidence_level = "{confidence_level}"

# >>>>>>>>>>> RELATED SETTINGS <<<<<<<<<<<

pause_before_submit = {pause_before_submit}
pause_at_failed_question = {pause_at_failed_question}
overwrite_previous_answers = {overwrite_previous_answers}
'''.format(**clean_data)

async def write_questions_file(data: dict) -> dict:
    """Write questions.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        questions_file = config_path / "questions.py"
        
        # Backup existing file
        if questions_file.exists():
            backup_dir = config_path / "backup"
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(questions_file, backup_dir / "questions.py.backup")
        
        # Write new content
        content = generate_questions_template(data)
        with open(questions_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "message": "Questions updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def read_questions_file() -> dict:
    """Read existing questions.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        questions_file = config_path / "questions.py"
        
        if not questions_file.exists():
            return {"error": "questions.py not found"}
        
        config_vars = {}
        with open(questions_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if '=' in line and not line.startswith('#'):
                    var_name, var_value = line.split('=', 1)
                    var_name = var_name.strip()
                    var_value = var_value.strip()
                    
                    # Handle triple-quoted strings
                    if var_value.startswith('"""'):
                        if var_value.endswith('"""') and len(var_value) > 6:
                            # Single line triple quote
                            var_value = var_value[3:-3]
                        else:
                            # Multi-line triple quote
                            var_value = var_value[3:]  # Remove opening """
                            i += 1
                            while i < len(lines) and not lines[i].strip().endswith('"""'):
                                var_value += '\n' + lines[i]
                                i += 1
                            if i < len(lines):
                                var_value += '\n' + lines[i].strip()[:-3]  # Remove closing """
                    else:
                        # Regular value
                        var_value = var_value.strip('"').strip("'")
                        
                        # Remove inline comments
                        if '#' in var_value:
                            var_value = var_value.split('#')[0].strip().strip('"').strip("'")
                        
                        # Convert to proper types
                        if var_value.lower() in ['true', 'false']:
                            var_value = var_value.lower() == 'true'
                        elif var_value.isdigit():
                            var_value = int(var_value)
                        elif var_value.replace('.', '', 1).isdigit():
                            var_value = float(var_value)
                    
                    config_vars[var_name] = var_value
                i += 1
        
        return config_vars
    except Exception as e:
        return {"error": f"Failed to read questions.py: {str(e)}"}

@router.post("/update-questions")
async def update_questions(data: QuestionsData):
    result = await write_questions_file(data.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/get-questions")
async def get_questions():
    result = await read_questions_file()
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Union

from fastHelpers.config_router import (
    handle_config_update,
    handle_config_get,
    handle_config_restore,
)

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

@router.post("/update-questions")
async def update_questions(data: QuestionsData):
    return await handle_config_update("questions", data.dict())

@router.get("/get-questions")
async def get_questions():
    return await handle_config_get("questions")

@router.post("/restore-questions-backup")
async def restore_questions_backup():
    return await handle_config_restore("questions")

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from fastHelpers.config_router import (
    handle_config_update,
    handle_config_get,
    handle_config_restore,
)

router = APIRouter()

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

@router.post("/update-search")
async def update_search(data: SearchData):
    return await handle_config_update("search", data.dict())

@router.get("/get-search")
async def get_search():
    return await handle_config_get("search")

@router.post("/restore-search-backup")
async def restore_search_backup():
    return await handle_config_restore("search")

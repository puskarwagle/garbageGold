from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from fastHelpers.config_router import (
    handle_config_update,
    handle_config_get,
    handle_config_restore,
)

router = APIRouter()

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

@router.post("/update-secrets")
async def update_secrets(data: SecretsData):
    return await handle_config_update("secrets", data.dict())

@router.get("/get-secrets")
async def get_secrets():
    return await handle_config_get("secrets")

@router.post("/restore-secrets-backup")
async def restore_secrets_backup():
    return await handle_config_restore("secrets")

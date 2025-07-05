# fastHelpers/config_router/secrets.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Union
import shutil

router = APIRouter()

class SecretsData(BaseModel):
    username: Optional[str] = ""
    password: Optional[str] = ""
    use_AI: Optional[bool] = False
    ai_provider: Optional[str] = "openai"
    deepseek_api_url: Optional[str] = ""
    deepseek_api_key: Optional[str] = ""
    deepseek_model: Optional[str] = "deepseek-chat"
    llm_api_url: Optional[str] = ""
    llm_api_key: Optional[str] = ""
    llm_model: Optional[str] = ""
    llm_spec: Optional[str] = "openai"
    stream_output: Optional[bool] = False

def generate_secrets_template(data: dict) -> str:
    """Generate secrets.py content from form data"""
    clean_data = {}
    for key, value in data.items():
        if isinstance(value, bool):
            clean_data[key] = str(value)
        elif isinstance(value, (int, float)):
            clean_data[key] = value
        else:
            # Escape quotes in string values
            clean_value = str(value).replace('"', '\\"').replace("'", "\\'")
            clean_data[key] = clean_value
    
    return '''###################################################### CONFIGURE YOUR TOOLS HERE ######################################################
# Login Credentials for LinkedIn (Optional)
username = "{username}" # Enter your username in the quotes
password = "{password}" # Enter your password in the quotes
## Artificial Intelligence (Beta Not-Recommended)
# Use AI
use_AI = {use_AI} # True or False, Note: True or False are case-sensitive
\'''
Note: Set it as True only if you want to use AI, and If you either have a
1. Local LLM model running on your local machine, with it's APIs exposed. Example softwares to achieve it are:
 a. Ollama - https://ollama.com/
 b. llama.cpp - https://github.com/ggerganov/llama.cpp
 c. LM Studio - https://lmstudio.ai/ (Recommended)
 d. Jan - https://jan.ai/
2. OR you have a valid OpenAI API Key, and money to spare, and you don't mind spending it.
CHECK THE OPENAI API PIRCES AT THEIR WEBSITE (https://openai.com/api/pricing/).
\'''
##> ------ Yang Li : MARKYangL - Feature ------
# Select AI Provider
ai_provider = "{ai_provider}" # "openai", "deepseek"
\'''
Note: Select your AI provider.
* "openai" - OpenAI API (GPT models)
* "deepseek" - DeepSeek API (DeepSeek models)
\'''
# DeepSeek Configuration
deepseek_api_url = "{deepseek_api_url}" # Examples: "https://api.deepseek.com", "https://api.deepseek.com/v1"
\'''
Note: DeepSeek API URL.
This URL is compatible with OpenAI interface. The full endpoint will be {{deepseek_api_url}}/chat/completions.
\'''
deepseek_api_key = "{deepseek_api_key}" # Enter your DeepSeek API key in the quotes
\'''
Note: Enter your DeepSeek API key here. Leave it empty as "" or "not-needed" if not needed.
\'''
deepseek_model = "{deepseek_model}" # Examples: "deepseek-chat", "deepseek-reasoner"
\'''
Note: DeepSeek model selection
* "deepseek-chat" - DeepSeek-V3, general conversation model
* "deepseek-reasoner" - DeepSeek-R1, reasoning model
\'''
##<
# Your Local LLM url or other AI api url and port
llm_api_url = "{llm_api_url}" # Examples: "https://api.openai.com/v1/", "http://127.0.0.1:1234/v1/", "http://localhost:1234/v1/"
\'''
Note: Don't forget to add / at the end of your url
\'''
# Your Local LLM API key or other AI API key
llm_api_key = "{llm_api_key}" # Enter your API key in the quotes, make sure it's valid, if not will result in error.
\'''
Note: Leave it empyt as "" or "not-needed" if not needed. Else will result in error!
\'''
# Your local LLM model name or other AI model name
llm_model = "{llm_model}" # Examples: "gpt-3.5-turbo", "gpt-4o", "llama-3.2-3b-instruct"
#
llm_spec = "{llm_spec}" # Examples: "openai", "openai-like", "openai-like-github", "openai-like-mistral"
\'''
Note: Currently "openai" and "openai-like" api endpoints are supported.
\'''
# # Yor local embedding model name or other AI Embedding model name
# llm_embedding_model = "nomic-embed-text-v1.5"
# Do you want to stream AI output?
stream_output = {stream_output} # Examples: True or False. (False is recommended for performance, True is recommended for user experience!)
\'''
Set `stream_output = True` if you want to stream AI output or `stream_output = False` if not.
\'''
##
'''.format(**clean_data)

async def write_secrets_file(data: dict) -> dict:
    """Write secrets.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        secrets_file = config_path / "secrets.py"
        
        # Backup existing file
        if secrets_file.exists():
            backup_dir = config_path / "backup"
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(secrets_file, backup_dir / "secrets.py.backup")
        
        # Write new content
        content = generate_secrets_template(data)
        with open(secrets_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "message": "Secrets updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def read_secrets_file() -> dict:
    """Read existing secrets.py file"""
    try:
        config_path = Path(__file__).parent.parent.parent / "config"
        secrets_file = config_path / "secrets.py"
        
        if not secrets_file.exists():
            return {"error": "secrets.py not found"}
        
        config_vars = {}
        with open(secrets_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#') and not line.startswith("'''"):
                    var_name, var_value = line.split('=', 1)
                    var_name = var_name.strip()
                    var_value = var_value.strip().strip('"').strip("'")
                    
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
        
        return config_vars
    except Exception as e:
        return {"error": f"Failed to read secrets.py: {str(e)}"}

@router.post("/update-secrets")
async def update_secrets(data: SecretsData):
    result = await write_secrets_file(data.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/get-secrets")
async def get_secrets():
    result = await read_secrets_file()
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}
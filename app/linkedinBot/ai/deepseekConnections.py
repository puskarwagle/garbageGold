from config.secrets import *
from config.settings import showAiErrorAlerts
from utils.helpers import convert_to_json
from utils.logger import log, log_error
from ai.prompts import *

from pyautogui import confirm
from openai import OpenAI
from openai.types.model import Model
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Iterator, Literal

def deepseek_create_client() -> OpenAI | None:
    try:
        log("Creating DeepSeek client...")
        if not use_AI:
            raise ValueError("AI is not enabled! Please set `use_AI = True` in config/secrets.py")

        base_url = deepseek_api_url.rstrip("/")
        client = OpenAI(base_url=base_url, api_key=deepseek_api_key)

        log("✅ DeepSeek client created")
        log(f"🔗 API URL: {base_url}")
        log(f"🧠 Model: {deepseek_model}")
        return client

    except Exception as e:
        msg = "❌ Error while creating DeepSeek client. Check your API settings."
        log_error(msg, e)
        if showAiErrorAlerts:
            if "Pause AI error alerts" == confirm(f"{msg}\n{str(e)}", "DeepSeek Connection Error", ["Pause AI error alerts", "Okay Continue"]):
                showAiErrorAlerts = False
        return None


def deepseek_model_supports_temperature(model_name: str) -> bool:
    return model_name in ["deepseek-chat", "deepseek-reasoner"]


def deepseek_completion(client: OpenAI, messages: list[dict], response_format: dict = None, temperature: float = 0, stream: bool = stream_output) -> dict | ValueError:
    if not client:
        raise ValueError("DeepSeek client is missing")

    params = {
        "model": deepseek_model,
        "messages": messages,
        "stream": stream,
        "timeout": 30
    }

    if deepseek_model_supports_temperature(deepseek_model):
        params["temperature"] = temperature

    if response_format:
        params["response_format"] = response_format

    try:
        log(f"📡 Requesting DeepSeek completion with model: {deepseek_model} | messages: {len(messages)}")

        completion = client.chat.completions.create(**params)
        result = ""

        if stream:
            log("📥 Streaming response...")
            for chunk in completion:
                if chunk.model_extra and chunk.model_extra.get("error"):
                    raise ValueError(f'DeepSeek API error: {chunk.model_extra.get("error")}')
                chunk_msg = chunk.choices[0].delta.content
                if chunk_msg:
                    result += chunk_msg
                    print(chunk_msg, end="", flush=True)
            log("\n✅ Stream complete")
        else:
            if completion.model_extra and completion.model_extra.get("error"):
                raise ValueError(f'DeepSeek API error: {completion.model_extra.get("error")}')
            result = completion.choices[0].message.content

        if response_format:
            result = convert_to_json(result)

        log("✅ DeepSeek response received")
        return result

    except Exception as e:
        log_error("❌ DeepSeek API request failed", e)
        if hasattr(e, 'response'):
            log_error("🔎 API Response:", e.response.text if hasattr(e.response, 'text') else e.response)

        if "Connection" in str(e):
            log_error("⚠️ Connection issue. Check your internet or firewall settings.")
        elif "401" in str(e):
            log_error("🔐 Unauthorized. Your API key may be invalid.")
        elif "404" in str(e):
            log_error("📭 Endpoint not found. Check your API URL or model name.")
        elif "429" in str(e):
            log_error("🚫 Rate limit hit. Wait before retrying.")

        raise ValueError(f"DeepSeek API error: {str(e)}")


def deepseek_extract_skills(client: OpenAI, job_description: str, stream: bool = stream_output) -> dict | ValueError:
    try:
        log("🔍 Extracting skills from job description...")
        prompt = deepseek_extract_skills_prompt.format(job_description)
        messages = [{"role": "user", "content": prompt}]
        result = deepseek_completion(client, messages, {"type": "json_object"}, stream=stream)
        return convert_to_json(result) if isinstance(result, str) else result
    except Exception as e:
        log_error("❌ Failed to extract skills from job description", e)
        return {"error": str(e)}


def deepseek_answer_question(
    client: OpenAI,
    question: str, options: list[str] | None = None,
    question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text',
    job_description: str = None, about_company: str = None, user_information_all: str = None,
    stream: bool = stream_output
) -> dict | ValueError:
    try:
        log(f"🗨️ Answering question: {question}")
        user_info = user_information_all or ""
        prompt = ai_answer_prompt.format(user_info, question)

        if options and question_type in ['single_select', 'multiple_select']:
            opts = "\n".join([f"- {opt}" for opt in options])
            prompt += f"\n\nOPTIONS:\n{opts}"
            prompt += "\n\nSelect ONE." if question_type == 'single_select' else "\n\nSelect MULTIPLE if needed."

        if job_description:
            prompt += f"\n\nJOB DESCRIPTION:\n{job_description}"
        if about_company:
            prompt += f"\n\nABOUT COMPANY:\n{about_company}"

        messages = [{"role": "user", "content": prompt}]
        return deepseek_completion(client, messages, temperature=0.1, stream=stream)

    except Exception as e:
        log_error("❌ Failed to answer question with DeepSeek", e)
        return {"error": str(e)}

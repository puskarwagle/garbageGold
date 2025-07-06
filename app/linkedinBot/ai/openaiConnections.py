from config.secrets import *
from config.settings import showAiErrorAlerts
from config.personals import ethnicity, gender, disability_status, veteran_status
from config.questions import *
from config.search import security_clearance, did_masters

from utils.helpers import log_error, convert_to_json
from utils.logger import log, log_error

from app.linkedinBot.ai.prompts import *

from pyautogui import confirm
from openai import OpenAI
from openai.types.model import Model
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Iterator, Literal


apiCheckInstructions = """

1. Make sure your AI API connection details like url, key, model names, etc are correct.
2. If you're using an local LLM, please check if the server is running.
3. Check if appropriate LLM and Embedding models are loaded and running.

Open `secret.py` in `/config` folder to configure your AI API connections.

ERROR:
"""

# Function to show an AI error alert
def ai_error_alert(message: str, stackTrace: str, title: str = "AI Connection Error") -> None:
    """
    Function to show an AI error alert and log it.
    """
    global showAiErrorAlerts
    if showAiErrorAlerts:
        if "Pause AI error alerts" == confirm(f"{message}{stackTrace}\n", title, ["Pause AI error alerts", "Okay Continue"]):
            showAiErrorAlerts = False
    log_error(message, stackTrace)


# Function to check if an error occurred
def ai_check_error(response: ChatCompletion | ChatCompletionChunk) -> None:
    """
    Function to check if an error occurred.
    * Takes in `response` of type `ChatCompletion` or `ChatCompletionChunk`
    * Raises a `ValueError` if an error is found
    """
    if response.model_extra and response.model_extra.get("error"):
        error_msg = f'Error occurred with API: "{response.model_extra.get("error")}"'
        log_error(error_msg)
        raise ValueError(error_msg)


# Function to create an OpenAI client
def ai_create_openai_client() -> OpenAI | None:
    """
    Function to create an OpenAI client.
    * Takes no arguments
    * Returns an `OpenAI` object or None if failed
    """
    try:
        log("Creating OpenAI client...")
        
        if not use_AI:
            error_msg = "AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder."
            log_error(error_msg)
            raise ValueError(error_msg)
        
        if not llm_api_url or not llm_api_key:
            error_msg = "Missing API URL or API key in configuration"
            log_error(error_msg)
            raise ValueError(error_msg)
        
        if not llm_model:
            error_msg = "Missing model name in configuration"
            log_error(error_msg)
            raise ValueError(error_msg)
        
        client = OpenAI(base_url=llm_api_url, api_key=llm_api_key)

        models = ai_get_models_list(client)
        if isinstance(models, list) and len(models) >= 2 and models[0] == "error":
            error_msg = f"Failed to get models list: {models[1]}"
            log_error(error_msg)
            raise ValueError(error_msg)
        
        if not models or len(models) == 0:
            error_msg = "No models are available!"
            log_error(error_msg)
            raise ValueError(error_msg)
        
        if llm_model not in [model.id for model in models]:
            error_msg = f"Model `{llm_model}` is not found!"
            log_error(error_msg)
            raise ValueError(error_msg)
        
        log("---- SUCCESSFULLY CREATED OPENAI CLIENT! ----")
        log(f"Using API URL: {llm_api_url}")
        log(f"Using Model: {llm_model}")
        log("Check './config/secrets.py' for more details.")
        log("---------------------------------------------")

        return client
        
    except Exception as e:
        ai_error_alert(f"Error occurred while creating OpenAI client. {apiCheckInstructions}", str(e))
        return None


# Function to close an OpenAI client
def ai_close_openai_client(client: OpenAI) -> bool:
    """
    Function to close an OpenAI client.
    * Takes in `client` of type `OpenAI`
    * Returns True if successful, False otherwise
    """
    try:
        if client:
            log("Closing OpenAI client...")
            client.close()
            log("OpenAI client closed successfully")
            return True
        else:
            log_error("No client provided to close")
            return False
    except Exception as e:
        ai_error_alert("Error occurred while closing OpenAI client.", str(e))
        return False


# Function to get list of models available in OpenAI API
def ai_get_models_list(client: OpenAI) -> list[Model] | list[str]:
    """
    Function to get list of models available in OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Returns a `list` of models or ["error", error_message]
    """
    try:
        log("Getting AI models list...")
        
        if not client:
            error_msg = "Client is not available!"
            log_error(error_msg)
            raise ValueError(error_msg)
            
        models = client.models.list()
        ai_check_error(models)
        
        log("Available models:")
        for model in models.data:
            log(f"- {model.id}")
            
        return models.data
        
    except Exception as e:
        log_error("Error occurred while getting models list!", str(e))
        return ["error", str(e)]


def model_supports_temperature(model_name: str) -> bool:
    """
    Checks if the specified model supports the temperature parameter.
    
    Args:
        model_name (str): The name of the AI model.
    
    Returns:
        bool: True if the model supports temperature adjustments, otherwise False.
    """
    if not model_name:
        log_error("model_supports_temperature: Empty model_name provided")
        return False
        
    supported_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]
    return model_name in supported_models


# Function to get chat completion from OpenAI API
def ai_completion(client: OpenAI, messages: list[dict], response_format: dict = None, temperature: float = 0, stream: bool = stream_output) -> dict | str | None:
    """
    Function that completes a chat and prints and formats the results of the OpenAI API calls.
    * Takes in `client` of type `OpenAI`
    * Takes in `messages` of type `list[dict]`. Example: `[{"role": "user", "content": "Hello"}]`
    * Takes in `response_format` of type `dict` for JSON representation, default is `None`
    * Takes in `temperature` of type `float` for temperature, default is `0`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call or not
    * Returns a `dict` object representing JSON response, will try to convert to JSON if `response_format` is given
    """
    if not client:
        error_msg = "Client is not available!"
        log_error(error_msg)
        raise ValueError(error_msg)
    
    if not messages:
        error_msg = "Messages list is empty!"
        log_error(error_msg)
        raise ValueError(error_msg)

    try:
        params = {"model": llm_model, "messages": messages, "stream": stream}

        if model_supports_temperature(llm_model):
            params["temperature"] = temperature
        if response_format and llm_spec in ["openai", "openai-like"]:
            params["response_format"] = response_format

        log(f"Making AI completion request with model: {llm_model}")
        completion = client.chat.completions.create(**params)

        result = ""
        
        # Log response
        if stream:
            log("--STREAMING STARTED")
            try:
                for chunk in completion:
                    ai_check_error(chunk)
                    chunkMessage = chunk.choices[0].delta.content
                    if chunkMessage is not None:
                        result += chunkMessage
                    log(chunkMessage, end="", flush=True)
                log("\n--STREAMING COMPLETE")
            except Exception as e:
                log_error(f"Error during streaming: {str(e)}")
                raise
        else:
            ai_check_error(completion)
            result = completion.choices[0].message.content
        
        if response_format:
            try:
                result = convert_to_json(result)
            except Exception as e:
                log_error(f"Failed to convert response to JSON: {str(e)}")
                raise ValueError(f"Failed to convert response to JSON: {str(e)}")
        
        log("\nAI Answer to Question:")
        log(result)
        return result
        
    except Exception as e:
        log_error(f"Error in ai_completion: {str(e)}")
        raise


def ai_extract_skills(client: OpenAI, job_description: str, stream: bool = stream_output) -> dict | None:
    """
    Function to extract skills from job description using OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `dict` object representing JSON response or None if failed
    """
    log("-- EXTRACTING SKILLS FROM JOB DESCRIPTION")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not job_description or job_description.strip() == "":
        log_error("Job description is empty!")
        return None
    
    try:        
        prompt = extract_skills_prompt.format(job_description)

        messages = [{"role": "user", "content": prompt}]
        result = ai_completion(client, messages, response_format=extract_skills_response_format, stream=stream)
        
        log("Successfully extracted skills from job description")
        return result
        
    except Exception as e:
        ai_error_alert(f"Error occurred while extracting skills from job description. {apiCheckInstructions}", str(e))
        return None


def ai_answer_question(
    client: OpenAI, 
    question: str, options: list[str] | None = None, question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text', 
    job_description: str = None, about_company: str = None, user_information_all: str = None,
    stream: bool = stream_output
) -> str | None:
    """
    Function to generate AI-based answers for questions in a form.
    
    Parameters:
    - `client`: OpenAI client instance.
    - `question`: The question being answered.
    - `options`: List of options (for `single_select` or `multiple_select` questions).
    - `question_type`: Type of question (text, textarea, single_select, multiple_select) It is restricted to one of four possible values.
    - `job_description`: Optional job description for context.
    - `about_company`: Optional company details for context.
    - `user_information_all`: information about you, AI can use to answer question eg: Resume-like user information.
    - `stream`: Whether to use streaming AI completion.
    
    Returns:
    - `str`: The AI-generated answer or None if failed.
    """

    log("-- ANSWERING QUESTION using AI")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not question or question.strip() == "":
        log_error("Question is empty!")
        return None
    
    valid_question_types = ['text', 'textarea', 'single_select', 'multiple_select']
    if question_type not in valid_question_types:
        log_error(f"Invalid question_type: {question_type}. Must be one of {valid_question_types}")
        return None
    
    try:
        prompt = ai_answer_prompt.format(user_information_all or "N/A", question)
        
        # Append optional details if provided
        if job_description and job_description != "Unknown":
            prompt += f"\nJob Description:\n{job_description}"
        if about_company and about_company != "Unknown":
            prompt += f"\nAbout the Company:\n{about_company}"
        if options:
            prompt += f"\nAvailable options: {', '.join(options)}"

        messages = [{"role": "user", "content": prompt}]
        log(f"Question type: {question_type}")
        log(f"Question: {question}")
        
        response = ai_completion(client, messages, stream=stream)
        
        log("Successfully generated answer for question")
        return response
        
    except Exception as e:
        ai_error_alert(f"Error occurred while answering question. {apiCheckInstructions}", str(e))
        return None


def ai_gen_experience(
    client: OpenAI, 
    job_description: str, about_company: str, 
    required_skills: dict, user_experience: dict,
    stream: bool = stream_output
) -> dict | None:
    """
    Function to generate experience based on job requirements.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `about_company` of type `str`
    * Takes in `required_skills` of type `dict`
    * Takes in `user_experience` of type `dict`
    * Takes in `stream` of type `bool`
    * Returns a `dict` object or None if failed
    """
    log("-- GENERATING EXPERIENCE")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not job_description or not about_company or not required_skills or not user_experience:
        log_error("Missing required parameters for experience generation")
        return None
    
    try:
        # Implementation would go here
        log("Experience generation not yet implemented")
        return None
    except Exception as e:
        ai_error_alert(f"Error occurred while generating experience. {apiCheckInstructions}", str(e))
        return None


def ai_generate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    stream: bool = stream_output
) -> dict | None:
    '''
    Function to generate resume. Takes in user experience and template info from config.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `about_company` of type `str`
    * Takes in `required_skills` of type `dict`
    * Takes in `stream` of type `bool`
    * Returns a `dict` object or None if failed
    '''
    log("-- GENERATING RESUME")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not job_description or not about_company or not required_skills:
        log_error("Missing required parameters for resume generation")
        return None
    
    try:
        # Implementation would go here
        log("Resume generation not yet implemented")
        return None
    except Exception as e:
        ai_error_alert(f"Error occurred while generating resume. {apiCheckInstructions}", str(e))
        return None


def ai_generate_coverletter(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    stream: bool = stream_output
) -> dict | None:
    '''
    Function to generate cover letter. Takes in user experience and template info from config.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `about_company` of type `str`
    * Takes in `required_skills` of type `dict`
    * Takes in `stream` of type `bool`
    * Returns a `dict` object or None if failed
    '''
    log("-- GENERATING COVER LETTER")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not job_description or not about_company or not required_skills:
        log_error("Missing required parameters for cover letter generation")
        return None
    
    try:
        # Implementation would go here
        log("Cover letter generation not yet implemented")
        return None
    except Exception as e:
        ai_error_alert(f"Error occurred while generating cover letter. {apiCheckInstructions}", str(e))
        return None


# Evaluation Agents
def ai_evaluate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    resume: str,
    stream: bool = stream_output
) -> dict | None:
    """
    Function to evaluate resume against job requirements.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `about_company` of type `str`
    * Takes in `required_skills` of type `dict`
    * Takes in `resume` of type `str`
    * Takes in `stream` of type `bool`
    * Returns a `dict` object or None if failed
    """
    log("-- EVALUATING RESUME")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not job_description or not about_company or not required_skills or not resume:
        log_error("Missing required parameters for resume evaluation")
        return None
    
    try:
        # Implementation would go here
        log("Resume evaluation not yet implemented")
        return None
    except Exception as e:
        ai_error_alert(f"Error occurred while evaluating resume. {apiCheckInstructions}", str(e))
        return None


def ai_evaluate_coverletter(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    cover_letter: str,
    stream: bool = stream_output
) -> dict | None:
    """
    Function to evaluate cover letter against job requirements.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `about_company` of type `str`
    * Takes in `required_skills` of type `dict`
    * Takes in `cover_letter` of type `str`
    * Takes in `stream` of type `bool`
    * Returns a `dict` object or None if failed
    """
    log("-- EVALUATING COVER LETTER")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not job_description or not about_company or not required_skills or not cover_letter:
        log_error("Missing required parameters for cover letter evaluation")
        return None
    
    try:
        # Implementation would go here
        log("Cover letter evaluation not yet implemented")
        return None
    except Exception as e:
        ai_error_alert(f"Error occurred while evaluating cover letter. {apiCheckInstructions}", str(e))
        return None


def ai_check_job_relevance(
    client: OpenAI, 
    job_description: str, about_company: str,
    stream: bool = stream_output
) -> dict | None:
    """
    Function to check job relevance against user profile.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `about_company` of type `str`
    * Takes in `stream` of type `bool`
    * Returns a `dict` object or None if failed
    """
    log("-- CHECKING JOB RELEVANCE")
    
    if not client:
        log_error("Client is not available!")
        return None
        
    if not job_description or not about_company:
        log_error("Missing required parameters for job relevance check")
        return None
    
    try:
        # Implementation would go here
        log("Job relevance check not yet implemented")
        return None
    except Exception as e:
        ai_error_alert(f"Error occurred while checking job relevance. {apiCheckInstructions}", str(e))
        return None
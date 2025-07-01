# fastHelpers/config_updater.py

import os
import json
from typing import Dict, Any, List
from pathlib import Path

class ConfigUpdater:
    def __init__(self, config_base_path: str = None):
        """Initialize with path to config directory"""
        if config_base_path is None:
            # Assume we're in fastHelpers/ and config is ../config/
            self.config_path = Path(__file__).parent.parent / "config"
        else:
            self.config_path = Path(config_base_path)
        
        # Define config templates for each file type
        self.config_templates = {
            "personals": self._get_personals_template,
            "questions": self._get_questions_template,
            "search": self._get_search_template,
            "settings": self._get_settings_template,
            "secrets": self._get_secrets_template
        }
    
    def update_config(self, config_type: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Generic method to update any config file"""
        try:
            if config_type not in self.config_templates:
                return {
                    "status": "error",
                    "message": f"Unknown config type: {config_type}"
                }
            
            config_file = self.config_path / f"{config_type}.py"
            
            # Generate the Python file content using the appropriate template
            content = self.config_templates[config_type](data)
            
            # Write to file
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"{config_type}.py updated successfully at {config_file}",
                "file_path": str(config_file)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to update {config_type}.py: {str(e)}"
            }
    
    def read_config(self, config_type: str) -> Dict[str, Any]:
        """Generic method to read any config file"""
        try:
            config_file = self.config_path / f"{config_type}.py"
            
            if not config_file.exists():
                return {"error": f"{config_type}.py not found"}
            
            config_vars = {}
            
            with open(config_file, 'r', encoding='utf-8') as f:
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
            return {"error": f"Failed to read {config_type}.py: {str(e)}"}
    
    def backup_config(self, config_type: str) -> str:
        """Create backup of any config file"""
        try:
            filename = f"{config_type}.py"
            source_file = self.config_path / filename
            backup_dir = self.config_path / "backup"
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"{filename}.backup"
            
            if source_file.exists():
                import shutil
                shutil.copy2(source_file, backup_file)
                return str(backup_file)
            
            return "Source file not found"
            
        except Exception as e:
            return f"Backup failed: {str(e)}"
    
    def _clean_form_data(self, data: Dict[str, Any], expected_fields: List[str]) -> Dict[str, str]:
        """Clean and validate form data for any config type"""
        
        # Default empty values for all expected fields
        cleaned = {field: "" for field in expected_fields}
        
        # Update with actual form data, escaping quotes
        for key, value in data.items():
            if key in cleaned:
                # Convert to string and escape quotes
                clean_value = str(value).replace('"', '\\"').replace("'", "\\'")
                cleaned[key] = clean_value
        
        return cleaned
    
    # Template generators for each config type
    def _get_personals_template(self, data: Dict[str, Any]) -> str:
        expected_fields = [
            "first_name", "middle_name", "last_name", "phone_number", "current_city",
            "street", "state", "zipcode", "country", "ethnicity", "gender", 
            "disability_status", "veteran_status"
        ]
        clean_data = self._clean_form_data(data, expected_fields)
        
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
    
    def _get_secrets_template(self, data: Dict[str, Any]) -> str:
        expected_fields = [
            "username", "password", "use_AI", "ai_provider", "deepseek_api_url", 
            "deepseek_api_key", "deepseek_model", "llm_api_url", "llm_api_key", 
            "llm_model", "llm_spec", "stream_output"
        ]
        clean_data = self._clean_form_data(data, expected_fields)
        
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
    
    def _get_questions_template(self, data: Dict[str, Any]) -> str:
        expected_fields = [
            "default_resume_path", "years_of_experience", "require_visa", "website", "linkedIn",
            "us_citizenship", "desired_salary", "current_ctc", "notice_period", "linkedin_headline",
            "linkedin_summary", "cover_letter", "user_information_all", "recent_employer",
            "confidence_level", "pause_before_submit", "pause_at_failed_question", "overwrite_previous_answers"
        ]
        clean_data = self._clean_form_data(data, expected_fields)

        # Patch for boolean + int values (do not quote them)
        for key in ["desired_salary", "current_ctc", "notice_period",
                    "pause_before_submit", "pause_at_failed_question", "overwrite_previous_answers"]:
            if key in data:
                val = data[key]
                # Handle empty/None values for numeric fields
                if key in ["desired_salary", "current_ctc", "notice_period"]:
                    clean_data[key] = val if val not in [None, "", "None"] else 0
                else:
                    clean_data[key] = val if isinstance(val, (int, bool)) else val.strip('"').strip("'")
                    
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

    def _get_search_template(self, data: Dict[str, Any]) -> str:
        expected_fields = [
            "search_terms", "search_location", "switch_number", "randomize_search_order",
            "sort_by", "date_posted", "salary", "easy_apply_only", "experience_level", "job_type",
            "on_site", "companies", "location", "industry", "job_function", "job_titles", "benefits",
            "commitments", "under_10_applicants", "in_your_network", "fair_chance_employer",
            "pause_after_filters", "about_company_bad_words", "about_company_good_words", "bad_words",
            "security_clearance", "did_masters", "current_experience"
        ]

        clean_data = self._clean_form_data(data, expected_fields)

        # Fix formatting for non-string types: bools, ints, lists
        for key in expected_fields:
            val = data.get(key, "")
            if isinstance(val, list):
                clean_data[key] = json.dumps(val)
            elif isinstance(val, bool):
                clean_data[key] = str(val)
            elif isinstance(val, int):
                clean_data[key] = val
            elif isinstance(val, str) and val.startswith("[") and val.endswith("]"):
                # probably already a JSON array string
                clean_data[key] = val

        return '''###################################################### LINKEDIN SEARCH PREFERENCES ######################################################

    search_terms = {search_terms}
    search_location = "{search_location}"
    switch_number = {switch_number}
    randomize_search_order = {randomize_search_order}

    # >>>>>>>>>>> Job Search Filters <<<<<<<<<<<

    sort_by = "{sort_by}"
    date_posted = "{date_posted}"
    salary = "{salary}"
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

    def _get_settings_template(self, data: Dict[str, Any]) -> str:
        expected_fields = [
            # LinkedIn settings
            "close_tabs", "follow_companies", "run_non_stop", "alternate_sortby",
            "cycle_date_posted", "stop_date_cycle_at_24hr",

            # Resume generator
            "generated_resume_path",

            # Global settings
            "file_name", "failed_file_name", "logs_folder_path", "click_gap",
            "run_in_background", "disable_extensions", "safe_mode", "smooth_scroll",
            "keep_screen_awake", "stealth_mode", "showAiErrorAlerts"
            # Note: `use_resume_generator` is commented out in original config
        ]

        clean_data = self._clean_form_data(data, expected_fields)

        for key in expected_fields:
            val = data.get(key, "")
            if isinstance(val, bool):
                clean_data[key] = str(val)
            elif isinstance(val, int):
                clean_data[key] = val
            elif isinstance(val, str) and val.startswith("[") and val.endswith("]"):
                clean_data[key] = val  # already formatted
            else:
                clean_data[key] = f'"{val}"' if isinstance(val, str) else val

        return '''###################################################### CONFIGURE YOUR BOT HERE ######################################################

    # >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<< #

    close_tabs = {close_tabs}
    follow_companies = {follow_companies}
    run_non_stop = {run_non_stop}
    alternate_sortby = {alternate_sortby}
    cycle_date_posted = {cycle_date_posted}
    stop_date_cycle_at_24hr = {stop_date_cycle_at_24hr}


    # >>>>>>>>>>> RESUME GENERATOR (Experimental & In Development) <<<<<<<<<<<

    generated_resume_path = {generated_resume_path}


    # >>>>>>>>>>> Global Settings <<<<<<<<<<<

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

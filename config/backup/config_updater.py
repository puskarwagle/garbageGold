# fastHelpers/config_updater.py

import os
import json
from typing import Dict, Any
from pathlib import Path

class ConfigUpdater:
    def __init__(self, config_base_path: str = None):
        """Initialize with path to config directory"""
        if config_base_path is None:
            # Assume we're in fastHelpers/ and config is ../config/
            self.config_path = Path(__file__).parent.parent / "config"
        else:
            self.config_path = Path(config_base_path)
    
    def update_personals(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Update personals.py with form data"""
        try:
            personals_file = self.config_path / "personals.py"
            
            # Generate the Python file content
            content = self._generate_personals_content(data)
            
            # Write to file
            with open(personals_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"personals.py updated successfully at {personals_file}",
                "file_path": str(personals_file)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to update personals.py: {str(e)}"
            }
    
    def _generate_personals_content(self, data: Dict[str, Any]) -> str:
        """Generate the Python file content from form data"""
        
        # Clean and prepare data
        clean_data = self._clean_form_data(data)
        
        content = """# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Your legal name
first_name = "{first_name}"                 # Your first name in quotes Eg: "First", "Sai"
middle_name = "{middle_name}"            # Your name in quotes Eg: "Middle", "Vignesh", ""
last_name = "{last_name}"                # Your last name in quotes Eg: "Last", "Golla"

# Phone number (required), make sure it's valid.
phone_number = "{phone_number}"        # Enter your 10 digit number in quotes Eg: "9876543210"

# What is your current city?
current_city = "{current_city}"                  # Los Angeles, San Francisco, etc.
'''
Note: If left empty as "", the bot will fill in location of jobs location.
'''

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


'''
For string variables followed by comments with options, only use the answers from given options.
Some valid examples are:
* variable1 = "option1"         # "option1", "option2", "option3" or ("" to not select). Answers are case sensitive.#
* variable2 = ""                # "option1", "option2", "option3" or ("" to not select). Answers are case sensitive.#

Other variables are free text. No restrictions other than compulsory use of quotes.
Some valid examples are:
* variable3 = "Random Answer 5"         # Enter your answer. Eg: "Answer1", "Answer2"

Invalid inputs will result in an error!
'''
""".format(**clean_data)
        
        return content
    
    def _clean_form_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Clean and validate form data"""
        
        # Default empty values for all fields
        cleaned = {
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "phone_number": "",
            "current_city": "",
            "street": "",
            "state": "",
            "zipcode": "",
            "country": "",
            "ethnicity": "",
            "gender": "",
            "disability_status": "",
            "veteran_status": ""
        }
        
        # Update with actual form data, escaping quotes
        for key, value in data.items():
            if key in cleaned:
                # Convert to string and escape quotes
                clean_value = str(value).replace('"', '\\"').replace("'", "\\'")
                cleaned[key] = clean_value
        
        return cleaned
    
    def read_current_personals(self) -> Dict[str, Any]:
        """Read current personals.py file and return as dict"""
        try:
            personals_file = self.config_path / "personals.py"
            
            if not personals_file.exists():
                return {"error": "personals.py not found"}
            
            # This is a simple parser - in production you might want something more robust
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
    
    def backup_config(self, filename: str) -> str:
        """Create backup of config file"""
        try:
            source_file = self.config_path / filename
            backup_file = self.config_path / f"{filename}.backup"
            
            if source_file.exists():
                import shutil
                shutil.copy2(source_file, backup_file)
                return str(backup_file)
            
            return "Source file not found"
            
        except Exception as e:
            return f"Backup failed: {str(e)}"
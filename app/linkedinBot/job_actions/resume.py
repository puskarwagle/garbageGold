import os
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from config.questions import default_resume_path

def upload_resume(modal: WebElement, resume: str) -> tuple[bool, str]:
    try:
        modal.find_element(By.NAME, "file").send_keys(os.path.abspath(resume))
        return True, os.path.basename(default_resume_path)
    except: return False, "Previous resume"

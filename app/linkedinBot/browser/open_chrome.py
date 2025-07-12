# open_chrome.py
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from utils.helpers import make_directories, find_default_profile_directory
from utils.logger import log, log_error

if stealth_mode:
    import undetected_chromedriver as uc
else:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

# Global variables to store single instance
_driver = None
_wait = None
_actions = None

def launch_browser():
    global _driver, _wait, _actions
    
    # Return existing instance if already created
    if _driver is not None:
        return _driver, _wait, _actions
    
    try:
        make_directories([file_name, failed_file_name, logs_folder_path + "/screenshots", default_resume_path, generated_resume_path + "/temp"])
        options = uc.ChromeOptions() if stealth_mode else Options()
        
        if run_in_background:
            options.add_argument("--headless")
        if disable_extensions:
            options.add_argument("--disable-extensions")
            
        log("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM!")
        
        if safe_mode:
            log("SAFE MODE: Using guest profile, no history saved!")
        else:
            profile_dir = find_default_profile_directory()
            if profile_dir:
                options.add_argument(f"--user-data-dir={profile_dir}")
            else:
                log("Default profile directory not found. Falling back to guest.")
        
        if stealth_mode:
            log("Downloading undetected Chrome Driver...")
            _driver = uc.Chrome(options=options)
        else:
            _driver = webdriver.Chrome(options=options)
            
        _driver.maximize_window()
        _wait = WebDriverWait(_driver, 5)
        _actions = ActionChains(_driver)
        
        return _driver, _wait, _actions
        
    except Exception as e:
        msg = 'Detailed error message omitted here for brevity...'
        if isinstance(e, TimeoutError):
            msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
        log(msg)
        log_error("In Opening Chrome", e)
        try:
            from pyautogui import alert
            alert(msg, "Error in opening chrome")
        except ImportError:
            pass
        try:
            if _driver:
                _driver.quit()
        except:
            pass
        return None, None, None

# Initialize singleton instance
driver, wait, actions = launch_browser()
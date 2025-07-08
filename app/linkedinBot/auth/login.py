from utils.logger import log, log_error
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from browser.clickers_and_finders import text_input_by_ID, find_by_class
from utils.helpers import manual_login_retry
from auth.session import is_logged_in_LN
from config.secrets import username, password
from browser.open_chrome import driver, wait

def login_LN() -> None:
    '''
    Function to login for LinkedIn
    * Tries to login using given `username` and `password` from `secrets.py`
    * If failed, tries to login using saved LinkedIn profile button if available
    * If both failed, asks user to login manually
    '''
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            text_input_by_ID(driver, "username", username, 1)
        except Exception as e:
            log_error("Couldn't find username field.")
            # log(e)
        try:
            text_input_by_ID(driver, "password", password, 1)
        except Exception as e:
            log_error("Couldn't find password field.")
            # log(e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception as e2:
            # log(e1, e2)
            log_error("Couldn't Login!")

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/")) # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        return log("Login successful!")
    except Exception as e:
        log_error("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
        # log(e)
        manual_login_retry(is_logged_in_LN, 2)
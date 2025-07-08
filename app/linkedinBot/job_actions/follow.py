from selenium.webdriver.chrome.webdriver import WebDriver
from browser.open_chrome import driver
from browser.clickers_and_finders import try_xp
from config.settings import follow_companies
from utils.logger import log_error

def follow_company(modal: WebDriver) -> None:
    '''
    Function to follow or un-follow easy applied companies based on `follow_companies`
    '''
    try:
        follow_checkbox_input = try_xp(modal, ".//input[@id='follow-company-checkbox' and @type='checkbox']", False)
        if follow_checkbox_input and follow_checkbox_input.is_selected() != follow_companies:
            try_xp(modal, ".//label[@for='follow-company-checkbox']")
    except Exception as e:
        log_error("Failed to update follow companies checkbox!", e)
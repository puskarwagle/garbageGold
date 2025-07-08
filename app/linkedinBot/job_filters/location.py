from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException
from time import sleep
from browser.open_chrome import driver, actions
from browser.clickers_and_finders import try_xp, text_input
from config.search import search_location
from utils.logger import log, log_error

def set_search_location() -> None:
    '''
    Function to set search location
    '''
    if search_location.strip():
        try:
            log(f'Setting search location as: "{search_location.strip()}"')
            search_location_ele = try_xp(driver, ".//input[@aria-label='City, state, or zip code'and not(@disabled)]", False) #  and not(@aria-hidden='true')]")
            text_input(actions, search_location_ele, search_location, "Search Location")
        except ElementNotInteractableException:
            try_xp(driver, ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']")
            actions.send_keys(Keys.TAB, Keys.TAB).perform()
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(search_location.strip()).perform()
            sleep(2)
            actions.send_keys(Keys.ENTER).perform()
            try_xp(driver, ".//button[@aria-label='Cancel']")
        except Exception as e:
            try_xp(driver, ".//button[@aria-label='Cancel']")
            log_error("Failed to update search location, continuing with default location!", e)

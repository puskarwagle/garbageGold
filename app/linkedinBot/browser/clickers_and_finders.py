from config.settings import click_gap, smooth_scroll
from utils.helpers import buffer, sleep
from utils.logger import log, log_error
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException

# Click Functions
def wait_span_click(driver: WebDriver, text: str, time: float=5.0, click: bool=True, scroll: bool=True, scrollTop: bool=False) -> WebElement | bool:
    '''
    Finds the span element with the given `text`.
    - Returns `WebElement` if found, else `False` if not found.
    - Clicks on it if `click = True`.
    - Will spend a max of `time` seconds in searching for each element.
    - Will scroll to the element if `scroll = True`.
    - Will scroll to the top if `scrollTop = True`.
    '''
    if not text:
        log_error("wait_span_click: Empty text provided")
        return False
        
    try:
        button = WebDriverWait(driver, time).until(
            EC.element_to_be_clickable((By.XPATH, f'.//span[normalize-space(.)="{text}"]'))
        )
        
        if scroll:  
            scroll_to_view(driver, button, scrollTop)
            
        if click:
            button.click()
            buffer(click_gap)
            log(f"Successfully clicked span with text: '{text}'")
            
        return button
        
    except TimeoutException:
        log_error(f"Timeout: Could not find span with text '{text}' within {time} seconds")
        return False
    except (ElementNotInteractableException, StaleElementReferenceException) as e:
        log_error(f"Element interaction failed for span '{text}': {str(e)}")
        return False
    except Exception as e:
        log_error(f"Unexpected error clicking span '{text}': {str(e)}")
        return False

def multi_sel(driver: WebDriver, texts: list, time: float=5.0) -> None:
    '''
    - For each text in the `texts`, tries to find and click `span` element with that text.
    - Will spend a max of `time` seconds in searching for each element.
    '''
    if not texts:
        log_error("multi_sel: Empty texts list provided")
        return
        
    successful_clicks = []
    failed_clicks = []
    
    for text in texts:
        try:
            button = WebDriverWait(driver, time).until(
                EC.element_to_be_clickable((By.XPATH, f'.//span[normalize-space(.)="{text}"]'))
            )
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
            successful_clicks.append(text)
            
        except TimeoutException:
            log_error(f"Timeout: Could not find span with text '{text}' within {time} seconds")
            failed_clicks.append(text)
        except (ElementNotInteractableException, StaleElementReferenceException) as e:
            log_error(f"Element interaction failed for span '{text}': {str(e)}")
            failed_clicks.append(text)
        except Exception as e:
            log_error(f"Unexpected error clicking span '{text}': {str(e)}")
            failed_clicks.append(text)
    
    log(f"multi_sel completed - Success: {len(successful_clicks)}, Failed: {len(failed_clicks)}")
    if failed_clicks:
        log_error(f"Failed to click: {failed_clicks}")

def multi_sel_noWait(driver: WebDriver, texts: list, actions: ActionChains = None) -> None:
    '''
    - For each text in the `texts`, tries to find and click `span` element with that class.
    - If `actions` is provided, bot tries to search and Add the `text` to this filters list section.
    - Won't wait to search for each element, assumes that element is rendered.
    '''
    if not texts:
        log_error("multi_sel_noWait: Empty texts list provided")
        return
        
    successful_clicks = []
    failed_clicks = []
    
    for text in texts:
        try:
            button = driver.find_element(By.XPATH, f'.//span[normalize-space(.)="{text}"]')
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
            successful_clicks.append(text)
            
        except NoSuchElementException:
            if actions: 
                company_search_click(driver, actions, text)
                log(f"Attempted company search for: '{text}'")
            else:   
                log_error(f"Could not find span with text '{text}'")
                failed_clicks.append(text)
        except (ElementNotInteractableException, StaleElementReferenceException) as e:
            log_error(f"Element interaction failed for span '{text}': {str(e)}")
            failed_clicks.append(text)
        except Exception as e:
            log_error(f"Unexpected error clicking span '{text}': {str(e)}")
            failed_clicks.append(text)
    
    log(f"multi_sel_noWait completed - Success: {len(successful_clicks)}, Failed: {len(failed_clicks)}")

def boolean_button_click(driver: WebDriver, actions: ActionChains, text: str) -> bool:
    '''
    Tries to click on the boolean button with the given `text` text.
    Returns True if successful, False otherwise.
    '''
    if not text:
        log_error("boolean_button_click: Empty text provided")
        return False
        
    try:
        list_container = driver.find_element(By.XPATH, f'.//h3[normalize-space()="{text}"]/ancestor::fieldset')
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(driver, button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
        log(f"Successfully clicked boolean button for: '{text}'")
        return True
        
    except NoSuchElementException:
        log_error(f"Could not find boolean button for text '{text}'")
        return False
    except (ElementNotInteractableException, StaleElementReferenceException) as e:
        log_error(f"Element interaction failed for boolean button '{text}': {str(e)}")
        return False
    except Exception as e:
        log_error(f"Unexpected error clicking boolean button '{text}': {str(e)}")
        return False

# Find functions
def find_by_class(driver: WebDriver, class_name: str, time: float=5.0) -> WebElement | None:
    '''
    Waits for a max of `time` seconds for element to be found, and returns `WebElement` if found, else `None` if not found.
    '''
    if not class_name:
        log_error("find_by_class: Empty class_name provided")
        return None
        
    try:
        element = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        log(f"Successfully found element with class: '{class_name}'")
        return element
    except TimeoutException:
        log_error(f"Timeout: Could not find element with class '{class_name}' within {time} seconds")
        return None
    except Exception as e:
        log_error(f"Unexpected error finding element with class '{class_name}': {str(e)}")
        return None

# Scroll functions
def scroll_to_view(driver: WebDriver, element: WebElement, top: bool = False, smooth_scroll: bool = smooth_scroll) -> bool:
    '''
    Scrolls the `element` to view.
    - `smooth_scroll` will scroll with smooth behavior.
    - `top` will scroll to the `element` to top of the view.
    Returns True if successful, False otherwise.
    '''
    if not element:
        log_error("scroll_to_view: No element provided")
        return False
        
    try:
        if top:
            driver.execute_script('arguments[0].scrollIntoView();', element)
        else:
            behavior = "smooth" if smooth_scroll else "instant"
            driver.execute_script(f'arguments[0].scrollIntoView({{block: "center", behavior: "{behavior}" }});', element)
        return True
    except StaleElementReferenceException:
        log_error("scroll_to_view: Element reference is stale")
        return False
    except Exception as e:
        log_error(f"Error scrolling to element: {str(e)}")
        return False

# Enter input text functions
def text_input_by_ID(driver: WebDriver, id: str, value: str, time: float=5.0) -> bool:
    '''
    Enters `value` into the input field with the given `id` if found.
    - `time` is the max time to wait for the element to be found.
    Returns True if successful, False otherwise.
    '''
    if not id or not value:
        log_error("text_input_by_ID: Empty id or value provided")
        return False
        
    try:
        username_field = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))
        username_field.send_keys(Keys.CONTROL + "a")
        username_field.send_keys(value)
        log(f"Successfully entered text into field with ID: '{id}'")
        return True
    except TimeoutException:
        log_error(f"Timeout: Could not find input field with ID '{id}' within {time} seconds")
        return False
    except (ElementNotInteractableException, StaleElementReferenceException) as e:
        log_error(f"Element interaction failed for input field '{id}': {str(e)}")
        return False
    except Exception as e:
        log_error(f"Unexpected error entering text into field '{id}': {str(e)}")
        return False

def try_xp(driver: WebDriver, xpath: str, click: bool=True) -> WebElement | bool:
    '''
    Tries to find element by xpath and optionally click it.
    Returns element if found (and click=False), True if clicked successfully, False otherwise.
    '''
    if not xpath:
        log_error("try_xp: Empty xpath provided")
        return False
        
    try:
        element = driver.find_element(By.XPATH, xpath)
        if click:
            element.click()
            log(f"Successfully clicked element with xpath: '{xpath}'")
            return True
        else:
            log(f"Successfully found element with xpath: '{xpath}'")
            return element
    except NoSuchElementException:
        log_error(f"Could not find element with xpath: '{xpath}'")
        return False
    except (ElementNotInteractableException, StaleElementReferenceException) as e:
        log_error(f"Element interaction failed for xpath '{xpath}': {str(e)}")
        return False
    except Exception as e:
        log_error(f"Unexpected error with xpath '{xpath}': {str(e)}")
        return False

def try_linkText(driver: WebDriver, linkText: str) -> WebElement | bool:
    '''
    Tries to find element by link text.
    Returns element if found, False otherwise.
    '''
    if not linkText:
        log_error("try_linkText: Empty linkText provided")
        return False
        
    try:
        element = driver.find_element(By.LINK_TEXT, linkText)
        log(f"Successfully found link with text: '{linkText}'")
        return element
    except NoSuchElementException:
        log_error(f"Could not find link with text: '{linkText}'")
        return False
    except Exception as e:
        log_error(f"Unexpected error finding link '{linkText}': {str(e)}")
        return False

def try_find_by_classes(driver: WebDriver, classes: list[str]) -> WebElement | None:
    '''
    Tries to find element by any of the provided class names.
    Returns first found element or None if none found.
    '''
    if not classes:
        log_error("try_find_by_classes: Empty classes list provided")
        return None
        
    for cla in classes:
        try:
            element = driver.find_element(By.CLASS_NAME, cla)
            log(f"Successfully found element with class: '{cla}'")
            return element
        except NoSuchElementException:
            continue
        except Exception as e:
            log_error(f"Error finding element with class '{cla}': {str(e)}")
            continue
    
    log_error(f"Could not find element with any of the provided classes: {classes}")
    return None

def company_search_click(driver: WebDriver, actions: ActionChains, companyName: str) -> bool:
    '''
    Tries to search and Add the company to company filters list.
    Returns True if successful, False otherwise.
    '''
    if not companyName:
        log_error("company_search_click: Empty companyName provided")
        return False
        
    try:
        # Try to click "Add a company" button
        if not wait_span_click(driver, "Add a company", 1):
            log_error("Could not find 'Add a company' button")
            return False
            
        # Find and interact with search field
        search = driver.find_element(By.XPATH, "(.//input[@placeholder='Add a company'])[1]")
        search.send_keys(Keys.CONTROL + "a")
        search.send_keys(companyName)
        buffer(3)
        
        actions.send_keys(Keys.DOWN).perform()
        actions.send_keys(Keys.ENTER).perform()
        
        log(f'Successfully searched and added company: "{companyName}"')
        return True
        
    except NoSuchElementException:
        log_error(f"Could not find company search field for: '{companyName}'")
        return False
    except Exception as e:
        log_error(f"Error searching for company '{companyName}': {str(e)}")
        return False

def text_input(actions: ActionChains, textInputEle: WebElement | bool, value: str, textFieldName: str = "Text") -> bool:
    '''
    Enters text into the provided element.
    Returns True if successful, False otherwise.
    '''
    if not value:
        log_error(f"text_input: Empty value provided for {textFieldName}")
        return False
        
    if not textInputEle:
        log_error(f'{textFieldName} input element was not provided!')
        return False
        
    try:
        sleep(1)
        textInputEle.clear()
        textInputEle.send_keys(value.strip())
        sleep(2)
        actions.send_keys(Keys.ENTER).perform()
        log(f"Successfully entered text into {textFieldName} field")
        return True
        
    except (ElementNotInteractableException, StaleElementReferenceException) as e:
        log_error(f"Element interaction failed for {textFieldName}: {str(e)}")
        return False
    except Exception as e:
        log_error(f"Unexpected error entering text into {textFieldName}: {str(e)}")
        return False
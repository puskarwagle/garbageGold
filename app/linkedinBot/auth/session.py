from browser.open_chrome import driver
from browser.clickers_and_finders import try_linkText, try_xp
from utils.logger import log, log_error

def is_logged_in_LN() -> bool:
    '''
    Function to check if user is logged-in in LinkedIn
    * Returns: `True` if user is logged-in or `False` if not
    '''
    if driver.current_url == "https://www.linkedin.com/feed/": return True
    if try_linkText(driver, "Sign in"): return False
    if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):  return False
    if try_linkText(driver, "Join now"): return False
    log("Didn't find Sign in link, so assuming user is logged in!")
    return True
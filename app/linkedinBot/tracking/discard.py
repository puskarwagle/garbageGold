from selenium.webdriver.common.keys import Keys
from browser.open_chrome import driver, wait, actions
from browser.clickers_and_finders import wait_span_click

def discard_job() -> None:
    actions.send_keys(Keys.ESCAPE).perform()
    wait_span_click(driver, 'Discard', 2)


import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait



def get_html_by_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # headless has smaller window size, need to adjust for better display
    chrome_options.add_argument('window-size=1920,1080')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


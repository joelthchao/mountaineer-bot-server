from enum import Enum

import imgkit
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class ErrorCode(Enum):
    SUCCESS = 0
    ERR_NETWORK = 1
    ERR_MISSING = 2
    ERR_UNKNOWN = 3


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


def df2img(title, df, img_file):
    style = """
    <style>
    h3 {
        text-align: center;
    }
    .mystyle {
        font-size: 11pt;
        font-family: Arial;
        border-collapse: collapse;
        border: 1px solid silver;
        width: 600px;
    }
    .mystyle td, th {
        padding: 5px;
        text-align: center;
    }
    .mystyle tr:nth-child(even) {
        background: #E0E0E0;
    }
    .mystyle tr:hover {
        background: silver;
        cursor: pointer;
    }
    </style>
    """

    html_template = """
    <html>
      <head>
        {style}
      </head>
      <body>
        <h3>{title}</h3>
        {table}
      </body>
    </html>
    """
    html = html_template.format(
        style=style, title=title, table=df.to_html(index_names=False, classes='mystyle'))
    # print(df.to_html())
    options = {
        'width': 620,
        'disable-smart-width': '',
        'encoding': 'UTF-8',
        'quiet': '',
    }
    imgkit.from_string(html, img_file, options=options)

from enum import Enum
import re
import sys

import imgkit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from mtn_bot_server import config


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
        <meta charset="UTF-8">
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
    # it requires xvfb package on linux.
    if sys.platform != 'darwin':
        options['xvfb'] = ''
    imgkit.from_string(html, img_file, options=options)


def parse_intention(text):
    if '訂閱' in text or 'subscribe' in text:
        return config.SUBSCRIBE_INTENTION
    else:
        return config.QUERY_INTENTION


weather_query_re = re.compile(r'查?(.*[^的])的?(天氣|預報)')


def parse_query_request(text):
    match = weather_query_re.match(text)
    return match.group(1).strip()

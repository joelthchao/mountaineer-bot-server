# -*- coding: utf-8 -*-
"""
Utility function
"""
from enum import Enum
import re
import sys

import imgkit
from linebot import LineBotApi
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from mtn_bot_server import config
from mtn_bot_server.log import get_logger


logger = get_logger(__name__)
if config.LINE_CHANNEL_ACCESS_TOKEN is not None:
    line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
else:
    logger.warning('Linebot service requires access token to enable')


class ParseError(Exception):
    pass


class SqliteDBError(Exception):
    pass


class NotSupportError(Exception):
    pass


class SeleniumError(Exception):
    pass


class CWBParseError(Exception):
    pass


class MeteoblueParseError(Exception):
    pass


class ImageGenerateError(Exception):
    pass


class ErrorCode(Enum):
    """Error Code"""
    SUCCESS = 0
    ERR_NETWORK = 1
    ERR_MISSING = 2
    ERR_UNKNOWN = 3


def get_html_by_selenium(url, cookies=None):
    """Scrap html by selenium"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # headless has smaller window size, need to adjust for better display
    chrome_options.add_argument('window-size=1920,1080')
    driver = webdriver.Chrome(config.CHROMEDRIVER_PATH, options=chrome_options)
    if cookies is not None:
        driver.get(url)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


def df2img(title, df, img_file):
    """Transform pandas dataframe table to table image"""
    style = """
    <style>
    h4 {
        text-align: center;
    }
    .mystyle {
        font-size: 7pt;
        font-family: Arial;
        border-collapse: collapse;
        border: 1px solid silver;
        width: 360px;
    }
    .mystyle td, th {
        padding: 3px;
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
        <h4>{title}</h4>{table}
      </body>
    </html>
    """
    html = html_template.format(
        style=style, title=title, table=df.to_html(index_names=False, classes='mystyle'))
    options = {
        'width': 380,
        'disable-smart-width': '',
        'encoding': 'UTF-8',
        'quiet': '',
        'quality': config.IMAGE_QUALITY,
    }
    # it requires xvfb package on linux.
    if sys.platform != 'darwin':
        options['xvfb'] = ''
    imgkit.from_string(html, img_file, options=options)


def parse_intention(text):
    """parse message intention"""
    if '訂閱' in text or 'subscribe' in text:
        return config.SUBSCRIBE_INTENTION
    elif '天氣' in text:
        return config.QUERY_INTENTION
    else:
        return config.UNKNOWN_INTENTION


weather_query_re = re.compile(r'查?(.*[^的])的?(天氣|預報)')


def parse_query_request(text):
    """parse weather query"""
    try:
        match = weather_query_re.match(text)
        return match.group(1).strip()
    except (AttributeError, IndexError):
        raise ParseError('Fail to parse query request')


def push_line_message(user_id, message):
    """push line message"""
    line_bot_api.push_message(user_id, message)

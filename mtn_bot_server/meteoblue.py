# -*- coding: utf-8 -*-
"""
Query meteoblue weather (meteoblue.com)
"""
import os

import arrow
from bs4 import BeautifulSoup
import pandas as pd

from mtn_bot_server import config
from mtn_bot_server.utils import (
    get_html_by_selenium,
    ErrorCode,
)


mapping = pd.read_csv('resources/coordinates.csv').set_index('name').to_dict()['coordinate']


def query_meteoblue_forecast(location):
    """query meteoblue weather forecast for a location"""
    ts = arrow.now()
    output_name = '{}-{}-meteoblue.txt'.format(location, ts.format('YYYYMMDDTHH'))
    output_file = os.path.join(config.CACHE_PATH, output_name)
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            image_url = next(f).strip()
        return {
            'errno': ErrorCode.SUCCESS.value,
            'errmsg': 'Success',
            'data': {
                'location': location,
                'time': 'cached',
                'image_url': image_url,
            }
        }

    # compose meteoblue query url
    try:
        url = make_meteoblue_url(location)
    except KeyError:
        return {
            'errno': ErrorCode.ERR_MISSING.value,
            'errmsg': 'Location not found in coordinate mapping ({})'.format(location),
            'data': {},
        }

    # retrive html content by selenium
    try:
        html = get_html_by_selenium(url)
    except:
        return {
            'errno': ErrorCode.ERR_NETWORK.value,
            'errmsg': 'Encounter network issue ({})'.format(url),
            'data': {},
        }

    # parse data
    try:
        image_url = parse_image_url(html)
    except:
        return {
            'errno': ErrorCode.ERR_UNKNOWN.value,
            'errmsg': 'Encounter parse issue ({})'.format(url),
            'data': {},
        }

    with open(output_file, 'w') as f:
        print(image_url, file=f)

    return {
        'errno': ErrorCode.SUCCESS.value,
        'errmsg': 'Success',
        'data': {
            'location': location,
            'time': ts.format('YYYY-MM-DDTHH:mm:ssZZ'),
            'image_url': image_url,
        }
    }


def make_meteoblue_url(location):
    """compose meteoblue url"""
    coordinate = mapping[location]
    url = 'https://www.meteoblue.com/en/weather/week/{}'.format(coordinate)
    return url


def parse_image_url(html):
    """scrap image link from website"""
    soup = BeautifulSoup(html, features='html.parser')
    container = soup.find('div', attrs={'class': 'bloo_content'})
    img = container.find('img')
    img_url = 'https:' + img.attrs['data-original']
    return img_url

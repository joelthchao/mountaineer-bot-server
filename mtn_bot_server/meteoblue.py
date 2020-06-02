import os
from urllib.parse import urlparse

import arrow
from bs4 import BeautifulSoup
import pandas as pd

from mtn_bot_server.utils import get_html_by_selenium


mapping = pd.read_csv('resources/coordinates.csv').set_index('name').to_dict()['coordinate']


def query_meteoblue_forecast(name):
    try:
        coordinate = mapping[name]
    except KeyError:
        return {
            'errno': 1,
            'errmsg': 'Name not found in coordinate mapping ({})'.format(name),
            'image_url': '',
        }

    ts = arrow.now()
    url = 'https://www.meteoblue.com/en/weather/week/{}'.format(coordinate)
    html = get_html_by_selenium(url)
    image_url = parse_image_url(html)

    return {
        'errno': 0,
        'errmsg': 'success',
        'data': {
            'location': name,
            'time': ts.format('YYYY-MM-DDTHH:mm:ssZZ'),
            'image_url': image_url,
        }
    }


def parse_image_url(html):
    soup = BeautifulSoup(html, features='html.parser')
    container = soup.find('div', attrs={'class': 'bloo_content'})
    img = container.find('img')
    img_url = 'https:' + img.attrs['data-original']
    return img_url


if __name__ == '__main__':
    print(query_meteoblue_forecast('南湖大山'))

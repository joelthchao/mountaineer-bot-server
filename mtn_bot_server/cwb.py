# -*- coding: utf-8 -*-
"""
Query CWB weather (cwb.gov.tw)
"""
import base64
import os

import arrow
from bs4 import BeautifulSoup
import pandas as pd

from mtn_bot_server import config
from mtn_bot_server.log import get_logger
from mtn_bot_server.utils import (
    get_html_by_selenium,
    df2img,
    NotSupportError,
    SeleniumError,
    CWBParseError,
    ImageGenerateError,
)


logger = get_logger(__name__)
mapping = pd.read_csv('resources/codes.csv').set_index('name').to_dict()['code']


def query_cwb_forecast(location):
    """query cwb weather forecast for a location"""
    ts = arrow.now()
    # encode utf-8 characters for url safety
    location_key = base64.b64encode(location.encode('utf-8')).decode('utf-8')
    image_name = '{}-{}-cwb.jpg'.format(location_key, ts.format('YYYYMMDDTHH'))
    output_file = os.path.join(config.CWB_IMAGE_PATH, image_name)
    if os.path.exists(output_file):
        logger.info('Use cache: %s', output_file)
        return {
            'location': location,
            'query_time': 'cached',
            'image_name': image_name,
        }

    # compose cwb query url
    try:
        url = make_cwb_url(location)
    except KeyError:
        logger.error('Fail to compose cwb query url')
        raise NotSupportError('Location not found in coordinate mapping ({})'.format(location))

    # retrive html content by selenium
    try:
        html = get_html_by_selenium(url)
    except:
        logger.error('Fail to retrive html content by selenium')
        raise SeleniumError('Fail to retrive html content by selenium')

    # parse data
    try:
        title, df = parse_cwb_hourly_forcast(html)
    except:
        logger.error('Fail to parse data')
        raise CWBParseError('Encounter parse issue ({})'.format(url))

    # convert to photo
    try:
        df2img(title, df, output_file)
    except:
        logger.error('Fail to convert to photo')
        raise ImageGenerateError('Encounter image conversion issue ({})'.format(url))

    return {
        'location': location,
        'query_time': ts.format('YYYY-MM-DDTHH:mm:ssZZ'),
        'image_name': image_name,
    }


def make_cwb_url(location):
    """compose cwb url"""
    url_template = 'https://www.cwb.gov.tw/V8/C/L/Mountain/Mountain.html?PID={}'
    code = mapping[location]
    url = url_template.format(code)
    return url


def parse_cwb_hourly_forcast(html):
    """scrap information from website"""
    soup = BeautifulSoup(html, features='html.parser')
    title = soup.find('h2', attrs={'class': 'main-title'}).find('span').text.strip()
    table = soup.find('div', attrs={'id': 'PC_hr'}).find('table', attrs={'class': 'table'})
    rows = list(table.find_all('tr'))
    times = parse_cwb_time_row(rows[0])
    temps = parse_cwb_temp_row(rows[3])
    rains = parse_cwb_rain_row(rows[5])
    feels = parse_cwb_feel_row(rows[7])
    humids = parse_cwb_humid_row(rows[9])
    winds = parse_cwb_wind_row(rows[11])
    descs = parse_cwb_desc_row(rows[13])
    df = pd.DataFrame({
        'time': times,
        'temp': temps,
        'rain': rains,
        'feel': feels,
        'humid': humids,
        'wind': winds,
        'desc': descs,
    })
    df = df.set_index('time')
    return title, df


def parse_cwb_time_row(row):
    """parse time"""
    times = []
    for th in row.find_all('th'):
        spans = th.find_all('span')
        times.append('{} {}'.format(spans[1].text.strip(), spans[0].text.strip()))
    return times


def parse_cwb_temp_row(row):
    """parse temperature"""
    temps = [td.find('span').text.strip() for td in row.find_all('td')]
    return temps


def parse_cwb_rain_row(row):
    """parse rain"""
    rains = []
    for td in row.find_all('td'):
        rains.append(td.text.strip())
        # some rain value across two columns
        if td.get('colspan') == '2':
            rains.append(td.text.strip())
    return rains


def parse_cwb_feel_row(row):
    """parse feel temperature"""
    feels = [td.find('span').text.strip() for td in row.find_all('td')]
    return feels


def parse_cwb_humid_row(row):
    """parse humid"""
    humids = [td.text.strip() for td in row.find_all('td')]
    return humids


def parse_cwb_wind_row(row):
    """parse wind"""
    winds = [span.text.strip() for span in row.find_all('span', attrs={'class': 'wind_1'})]
    return winds


def parse_cwb_desc_row(row):
    """parse description"""
    descs = [p.text.strip() for p in row.find_all('p')]
    return descs

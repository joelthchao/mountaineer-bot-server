import os

import arrow
from bs4 import BeautifulSoup
import pandas as pd

from mtn_bot_server import config
from mtn_bot_server.utils import (
    get_html_by_selenium,
    df2img,
    ErrorCode,
)


mapping = pd.read_csv('resources/codes.csv').set_index('name').to_dict()['code']


def query_cwb_forecast(location):
    ts = arrow.now()
    image_name = '{}-{}-cwb.png'.format(location, ts.format('YYYYMMDDTHH'))
    output_file = os.path.join(config.CWB_IMAGE_PATH, image_name)
    if os.path.exists(output_file):
        return {
            'errno': ErrorCode.SUCCESS.value,
            'errmsg': 'Success',
            'data': {
                'location': location,
                'query_time': 'cached',
                'image_name': image_name,
            }
        }

    # compose cwb query url
    try:
        url = make_cwb_url(location)
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
        title, df = parse_cwb_hourly_forcast(html)
    except:
        return {
            'errno': ErrorCode.ERR_UNKNOWN.value,
            'errmsg': 'Encounter parse issue ({})'.format(url),
            'data': {},
        }

    # convert to photo
    try:
        df2img(title, df, output_file)
    except:
        return {
            'errno': ErrorCode.ERR_UNKNOWN.value,
            'errmsg': 'Encounter image conversion issue ({})'.format(url),
            'data': {},
        }

    return {
        'errno': ErrorCode.SUCCESS.value,
        'errmsg': 'Success',
        'data': {
            'location': location,
            'query_time': ts.format('YYYY-MM-DDTHH:mm:ssZZ'),
            'image_name': image_name,
        }
    }


def make_cwb_url(location):
    url_template = 'https://www.cwb.gov.tw/V8/C/L/Mountain/Mountain.html?PID={}'
    code = mapping[location]
    url = url_template.format(code)
    return url


def parse_cwb_hourly_forcast(html):
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
    times = []
    for th in row.find_all('th'):
        spans = th.find_all('span')
        times.append('{} {}'.format(spans[1].text.strip(), spans[0].text.strip()))
    return times


def parse_cwb_temp_row(row):
    temps = [td.find('span').text.strip() for td in row.find_all('td')]
    return temps


def parse_cwb_rain_row(row):
    rains = []
    for td in row.find_all('td'):
        rains.append(td.text.strip())
        # some rain value across two columns
        if td.get('colspan') == '2':
            rains.append(td.text.strip())
    return rains


def parse_cwb_feel_row(row):
    feels = [td.find('span').text.strip() for td in row.find_all('td')]
    return feels


def parse_cwb_humid_row(row):
    humids = [td.text.strip() for td in row.find_all('td')]
    return humids


def parse_cwb_wind_row(row):
    winds = [span.text.strip() for span in row.find_all('span', attrs={'class': 'wind_1'})]
    return winds


def parse_cwb_desc_row(row):
    descs = [p.text.strip() for p in row.find_all('p')]
    return descs


if __name__ == '__main__':
    print(query_cwb_forecast('南湖大山'))

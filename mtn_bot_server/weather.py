import os

from mtn_bot_server import config
from mtn_bot_server.cwb import query_cwb_forecast
from mtn_bot_server.meteoblue import query_meteoblue_forecast
from mtn_bot_server.utils import ErrorCode


def query_weather(location, user='anonymous'):
    cwb_res = query_cwb_forecast(location)
    meteoblue_res = query_meteoblue_forecast(location)

    data = {}
    if cwb_res['errno'] == ErrorCode.SUCCESS.value:
        data['cwb'] = cwb_res['data']
    else:
        print('Fail to query CWB: {}'.format(cwb_res))

    if meteoblue_res['errno'] == ErrorCode.SUCCESS.value:
        data['meteoblue'] = meteoblue_res['data']
    else:
        print('Fail to query Meteoblue: {}'.format(meteoblue_res))

    return data

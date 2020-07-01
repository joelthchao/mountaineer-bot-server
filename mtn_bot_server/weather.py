# -*- coding: utf-8 -*-
"""
Query weather from internet
"""
from mtn_bot_server.cwb import query_cwb_forecast
from mtn_bot_server.meteoblue import query_meteoblue_forecast
from mtn_bot_server.log import get_logger
from mtn_bot_server.utils import ErrorCode


logger = get_logger(__name__)


def query_weather(location):
    """query weather from cwb and meteoblue"""
    cwb_res = query_cwb_forecast(location)
    meteoblue_res = query_meteoblue_forecast(location)

    data = {'location': location}
    if cwb_res['errno'] == ErrorCode.SUCCESS.value:
        data['cwb'] = cwb_res['data']
    else:
        logger.error('Fail to query CWB: %s', cwb_res)

    if meteoblue_res['errno'] == ErrorCode.SUCCESS.value:
        data['meteoblue'] = meteoblue_res['data']
    else:
        logger.error('Fail to query Meteoblue: %s', meteoblue_res)

    return data

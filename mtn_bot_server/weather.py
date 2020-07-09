# -*- coding: utf-8 -*-
"""
Query weather from internet
"""
from mtn_bot_server.cwb import query_cwb_forecast
from mtn_bot_server.meteoblue import query_meteoblue_forecast
from mtn_bot_server.log import get_logger


logger = get_logger(__name__)


def query_weather(location):
    """query weather from cwb and meteoblue"""
    cwb_res = query_cwb_forecast(location)
    meteoblue_res = query_meteoblue_forecast(location)
    return {
        'location': location,
        'cwb': cwb_res,
        'meteoblue': meteoblue_res,
    }

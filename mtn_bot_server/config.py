# -*- coding: utf-8 -*-
"""
Configuration
"""
import os
import pathlib

# static
CWB_IMAGE_PATH = 'mtn_bot_server/static'
os.makedirs(CWB_IMAGE_PATH, exist_ok=True)

# cache
CACHE_PATH = 'cache'
os.makedirs(CACHE_PATH, exist_ok=True)

# linebot
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

# https
HOST = 'gcp-mtn-linebot.mtn-linebot.nctu.me'
PORT = 5050
IMAGE_ROUTE = 'image'
SSL_CRT = os.environ.get('SSL_CRT')
SSL_PRIVATE_KEY = os.environ.get('SSL_PRIVATE_KEY')

# intention
QUERY_INTENTION = 'query'
SUBSCRIBE_INTENTION = 'subscribe'
UNKNOWN_INTENTION = 'unknown'

# DB
DB_PATH = 'subscribe.sqlite3'
DB_NAME = 'subscribes'

# path
PROJECT_PATH = pathlib.Path(__file__).parent.parent.absolute()
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

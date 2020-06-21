import os

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
PORT = 5050
IMAGE_ROUTE = 'image'
SSL_CRT = os.environ.get('SSL_CRT')
SSL_PRIVATE_KEY = os.environ.get('SSL_PRIVATE_KEY')

# intention
QUERY_INTENTION = 'query'
SUBSCRIBE_INTENTION = 'subscribe'

# DB
DB_PATH = 'subscribe.sqlite3'
DB_NAME = 'subscribes'

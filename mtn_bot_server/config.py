import os


CWB_IMAGE_PATH = 'mtn_bot_server/static'
os.makedirs(CWB_IMAGE_PATH, exist_ok=True)

IMAGE_ROUTE = 'image'
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

PORT = 5050
SSL_CRT = os.environ.get('SSL_CRT')
SSL_PRIVATE_KEY = os.environ.get('SSL_PRIVATE_KEY')

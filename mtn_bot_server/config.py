import os


CWB_IMAGE_PATH = 'mtn_bot_server/static'
os.makedirs(CWB_IMAGE_PATH, exist_ok=True)

IMAGE_ROUTE = 'image'
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

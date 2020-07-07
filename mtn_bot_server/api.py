# -*- coding: utf-8 -*-
"""
Http service for linebot webhook and image hosting
"""
import argparse
import ast

from flask import (
    Flask,
    request,
    abort,
    send_from_directory,
)
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    ImageSendMessage,
)

from mtn_bot_server import config
from mtn_bot_server.log import get_logger
from mtn_bot_server.weather import query_weather
from mtn_bot_server.subscribe import (
    process_subscribe,

)
from mtn_bot_server.utils import (
    parse_intention,
    parse_query_request,
    ParseError,
    SqliteDBError,
    NotSupportError,
    SeleniumError,
    CWBParseError,
    MeteoblueParseError,
    ImageGenerateError,
)


app = Flask(__name__)
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)
logger = get_logger(__name__)


@app.route("/callback", methods=['POST'])
def callback():
    """line bot webhook entry"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logger.info('Request body: %s', body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.exception(
            'Invalid signature. Please check your channel access token/channel secret.')
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """line bot webhook handler"""
    intention = parse_intention(event.message.text)
    if intention == config.QUERY_INTENTION:
        handle_query_weather_message(event)
    elif intention == config.SUBSCRIBE_INTENTION:
        handle_subscribe_message(event)
    else:
        handle_unknown_message(event)


def handle_query_weather_message(event):
    """query weather reply logic"""
    try:
        location = parse_query_request(event.message.text)
    except ParseError:
        message = TextSendMessage(text='天氣查詢請求格式錯誤!')

    try:
        data = query_weather(location)
        message = make_weather_message(data)
    except NotSupportError:
        message = TextSendMessage(text='地點不存在!')
    except SeleniumError:
        message = TextSendMessage(text='抓取網站失敗!')
    except CWBParseError:
        message = TextSendMessage(text='中央氣象局天氣分析錯誤!')
    except MeteoblueParseError:
        message = TextSendMessage(text='Meteoblue天氣分析錯誤!')
    except ImageGenerateError:
        message = TextSendMessage(text='天氣圖片生成失敗!')
    except Exception:
        message = TextSendMessage(text='系統未知錯誤!')
    line_bot_api.reply_message(event.reply_token, message)


def make_weather_message(data):
    """compose weather message"""
    text_message = TextSendMessage(text='以下是"{}"的天氣預報'.format(data['location']))
    cwb_image_url = 'https://{}:{}/{}/{}'.format(
        config.HOST, config.PORT, config.IMAGE_ROUTE, data['cwb']['image_name'])
    cwb_image_message = ImageSendMessage(
        original_content_url=cwb_image_url, preview_image_url=cwb_image_url)

    meteoblue_image_url = data['meteoblue']['image_url']
    meteoblue_image_message = ImageSendMessage(
        original_content_url=meteoblue_image_url, preview_image_url=meteoblue_image_url)
    messages = [text_message, cwb_image_message, meteoblue_image_message]

    return messages


def handle_subscribe_message(event):
    """subscribe reply logic"""
    try:
        data = process_subscribe(event.source.user_id, event.message.text)
        text_message = TextSendMessage(text='預計於 {} 發送 {} 的天氣預報'.format(
            data['data']['time'].format('YYYY/MM/DD HH:mm'), data['data']['location']))
    except ParseError:
        text_message = TextSendMessage(text='訂閱請求格式錯誤!')
    except SqliteDBError:
        text_message = TextSendMessage(text='系統資料庫錯誤!')
    except Exception:
        text_message = TextSendMessage(text='系統未知錯誤!')

    line_bot_api.reply_message(event.reply_token, text_message)


def handle_unknown_message(event):
    """unknown intention reply logic"""
    text_message = TextSendMessage(text='無法理解此訊息: "{}"'.format(event.message.text))
    line_bot_api.reply_message(event.reply_token, text_message)


@app.route('/image/<path:path>')
def image(path):
    """image hosting"""
    response = send_from_directory(app.static_folder, path, mimetype='image/png')
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline')
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mountaineer Bot API')
    parser.add_argument('--https', type=ast.literal_eval, default=True)
    arguments = parser.parse_args()
    if arguments.https:
        app.run('0.0.0.0', port=config.PORT, ssl_context=(config.SSL_CRT, config.SSL_PRIVATE_KEY))
    else:
        app.run('0.0.0.0', port=config.PORT)

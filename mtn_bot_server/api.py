import json
import os

from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    ImageSendMessage,
)

from mtn_bot_server import config
from mtn_bot_server.weather import query_weather
from mtn_bot_server.utils import parse_query_request


app = Flask(__name__)
line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    location = parse_query_request(event.message.text)
    data = query_weather(location)

    text_message = TextSendMessage(text='以下是"{}"的天氣預報'.format(location))
    cwb_image_url = os.path.join(
        'https://', request.host, config.IMAGE_ROUTE, data['cwb']['image_name'])
    cwb_image_message = ImageSendMessage(
        original_content_url=cwb_image_url, preview_image_url=cwb_image_url)

    meteoblue_image_url = data['meteoblue']['image_url']
    meteoblue_image_message = ImageSendMessage(
        original_content_url=meteoblue_image_url, preview_image_url=meteoblue_image_url)
    messages = [text_message, cwb_image_message, meteoblue_image_message]

    line_bot_api.reply_message(event.reply_token, messages)


@app.route('/image/<path:path>')
def image(path):
    response = send_from_directory(app.static_folder, path, mimetype='image/png')
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline')
    return response


if __name__ == '__main__':
    app.run()

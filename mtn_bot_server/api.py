import os

from flask import (
    Flask,
    request,
    send_from_directory,
)

from mtn_bot_server import config
from mtn_bot_server.cwb import query_cwb_forecast
from mtn_bot_server.meteoblue import query_meteoblue_forecast
from mtn_bot_server.utils import ErrorCode


app = Flask(__name__)


@app.route('/query', methods=['GET'])
def query():
    # args
    user = request.args.get('user', 'anonymous')
    location = request.args['location']

    cwb_res = query_cwb_forecast(location)
    meteoblue_res = query_meteoblue_forecast(location)

    data = {}
    if cwb_res['errno'] == ErrorCode.SUCCESS.value:
        cwb_res['data']['image_url'] = os.path.join(
            request.host, config.IMAGE_ROUTE, cwb_res['data']['image_name'])
        data['cwb'] = cwb_res['data']

    if meteoblue_res['errno'] == ErrorCode.SUCCESS.value:
        data['meteoblue'] = meteoblue_res['data']

    return data


@app.route('/image/<path:path>')
def image(path):
    response = send_from_directory(app.static_folder, path, mimetype='image/png')
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline')
    return response

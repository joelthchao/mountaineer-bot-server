import re

import arrow

from mtn_bot_server.utils import ErrorCode


def process_subscribe(text):
    data = parse_subscribe(text)
    # TODO: subscribe function
    return {
        'errno': ErrorCode.SUCCESS.value,
        'errmsg': 'Success',
        'data': data,
    }


subscribe_re = re.compile(r'(訂閱|subscribe)\s*(\d{8})\s*(\d{4})?\s*([^的]+)的?(天氣|預報)')


def parse_subscribe(text):
    match = subscribe_re.match(text)
    date = match.group(2)
    hour = match.group(3)
    location = match.group(4)
    # fixme: timezone issue
    ts = arrow.get(date + hour, 'YYYYMMDDhhmm').replace(tzinfo='+08:00')
    res = {
        'time': ts,
        'location': location,
    }
    return res

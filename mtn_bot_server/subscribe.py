import re
import sqlite3

import arrow

from mtn_bot_server import config
from mtn_bot_server.utils import ErrorCode


def process_subscribe(user_id, text):
    data = parse_subscribe(text)
    db = SubscribeDB()
    db.insert_record(user_id, data['time'].timestamp, data['location'])
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


class SubscribeDB:
    def __init__(self, db_path=config.DB_PATH, db_name=config.DB_NAME):
        self.conn = sqlite3.connect(db_path)
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS {}
            (user_id TEXT, ts INTEGER, location TEXT)'''.format(self.db_name)
        self.conn.execute(query)
        self.conn.commit()

    def insert_record(self, user_id, ts, location):
        query = '''INSERT INTO {} VALUES ('{}', {}, '{}')'''.format(
            self.db_name, user_id, ts, location)
        self.conn.execute(query)
        self.conn.commit()

    def query_by_ts(self, ts):
        query = '''SELECT user_id, location FROM {} WHERE ts={}'''.format(self.db_name, ts)
        res = self.conn.execute(query)
        return list(res)

    def query_by_user(self, user_id):
        query = '''SELECT ts, location FROM {} WHERE user_id={}'''.format(self.db_name, user_id)
        res = self.conn.execute(query)
        return list(res)

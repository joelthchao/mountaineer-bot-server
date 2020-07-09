# -*- coding: utf-8 -*-
"""
Subscribe weather notification
"""
import re
import sqlite3

import arrow

from mtn_bot_server import config
from mtn_bot_server.utils import (
    ErrorCode,
    ParseError,
    SqliteDBError,
)


def process_subscribe(user_id, text):
    """process a subscribe request"""
    data = parse_subscribe(text)
    insert_record(user_id, data['time'].timestamp, data['location'])
    return {
        'errno': ErrorCode.SUCCESS.value,
        'errmsg': 'Success',
        'data': data,
    }


subscribe_re = re.compile(r'(訂閱|subscribe)\s*(\d{8})\s*(\d{4})?\s*([^的]+)的?(天氣|預報)')


def parse_subscribe(text):
    """parse subscribe message"""
    try:
        match = subscribe_re.match(text)
        date = match.group(2)
        hour = match.group(3)
        location = match.group(4)
    except (AttributeError, IndexError):
        raise ParseError('Fail to parse subscribe request')
    # fixme: timezone issue (maybe we can get timezone from line?)
    ts = arrow.get(date + hour, 'YYYYMMDDhhmm').replace(tzinfo='+08:00')
    data = {
        'time': ts,
        'location': location,
    }
    return data


def insert_record(user_id, ts, location):
    """insert subscribe record into sqlite3"""
    try:
        db = SubscribeDB()
        db.insert_record(user_id, ts, location)
    except sqlite3.Error:
        raise SqliteDBError('Encounter database error')


class SubscribeDB:
    """database to store subscribes"""
    def __init__(self, db_path=config.DB_PATH, db_name=config.DB_NAME):
        """use sqlite3"""
        self.conn = sqlite3.connect(db_path)
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        """create database table"""
        query = '''
            CREATE TABLE IF NOT EXISTS {}
            (user_id TEXT, ts INTEGER, location TEXT)'''.format(self.db_name)
        self.conn.execute(query)
        self.conn.commit()

    def insert_record(self, user_id, ts, location):
        """insert a subscribe to table"""
        query = '''INSERT INTO {} VALUES ('{}', {}, '{}')'''.format(
            self.db_name, user_id, ts, location)
        self.conn.execute(query)
        self.conn.commit()

    def query_by_ts(self, start_ts, end_ts):
        """query subscribe by time range"""
        query = '''SELECT user_id, location FROM {} WHERE ts >= {} AND ts <= {}'''.format(
            self.db_name, start_ts, end_ts)
        res = self.conn.execute(query)
        return list(res)

    def query_by_user(self, user_id):
        """query subscribe by user"""
        query = '''SELECT ts, location FROM {} WHERE user_id={}'''.format(self.db_name, user_id)
        res = self.conn.execute(query)
        return list(res)

# -*- coding: utf-8 -*-
"""
Cronjob for subscribe notification.
Periodicly check subscription and send notification if required.
"""
import argparse
from collections import defaultdict

import arrow
from crontab import CronTab

from mtn_bot_server import config
from mtn_bot_server.api import make_weather_message
from mtn_bot_server.log import get_logger
from mtn_bot_server.weather import query_weather
from mtn_bot_server.subscribe import SubscribeDB
from mtn_bot_server.utils import push_line_message


logger = get_logger(__name__)


def setup():
    """setup system crontab"""
    cron = CronTab(user='joelthchao')
    job = cron.new(command=(
        'cd {} && '
        'python -m mtn_bot_server.cronjob --mode run '
        '>> cronjob.log 2>&1').format(config.PROJECT_PATH))
    job.minute.on(0, 10, 20, 30, 40, 50)
    cron.write()


def run():
    """run subscribe notification job"""
    db = SubscribeDB()
    locations = set()
    user_locs = defaultdict(list)
    ts = arrow.now()
    start_ts = ts.shift(minutes=-10).timestamp
    end_ts = ts.timestamp
    for user_id, location in db.query_by_ts(start_ts, end_ts):
        user_locs[user_id].append(location)
        locations.add(location)

    loc_msg = {}
    for i, location in enumerate(locations):
        logger.info('Query %s weather (%d/%d) ...', location, i + 1, len(locations))
        data = query_weather(location)
        message = make_weather_message(data)
        loc_msg[location] = message

    for user_id, locations in user_locs.items():
        logger.info('Send message to user %s', user_id)
        for location in locations:
            push_line_message(user_id, loc_msg[location])


def main(args):
    """main function"""
    if args.mode == 'run':
        run()
    elif args.mode == 'setup':
        setup()
    else:
        raise Exception('Unknown mode: "{}"'.format(args.mode))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mountaineer Bot cronjob')
    parser.add_argument('--mode', type=str, default='run')
    arguments = parser.parse_args()
    main(arguments)

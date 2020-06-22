import argparse
from collections import defaultdict

import arrow
from crontab import CronTab

from mtn_bot_server import config
from mtn_bot_server.api import make_weather_message
from mtn_bot_server.weather import query_weather
from mtn_bot_server.subscribe import SubscribeDB
from mtn_bot_server.utils import push_line_message


def setup():
    cron = CronTab(user='joelthchao')
    job = cron.new(command='cd {} && python -m mtn_bot_server.cronjob --mode run'.format(
        config.PROJECT_PATH))
    job.minute.on(0, 10, 20, 30, 40, 50)
    cron.write()


def run():
    db = SubscribeDB()
    locations = set()
    user_locs = defaultdict(list)
    ts = arrow.now()
    start_ts = ts.shift(minute=-10).timestamp
    end_ts = ts.timestamp
    for user_id, location in db.query_by_ts(start_ts, end_ts):
        user_locs[user_id].append(location)
        locations.add(location)

    loc_msg = {}
    for i, location in enumerate(locations):
        print('Query {} weather ({}/{}) ...'.format(location, i + 1, len(locations)))
        data = query_weather(location)
        message = make_weather_message(data)
        loc_msg[location] = message

    for user_id, locations in user_locs.items():
        print('Send message to user {}'.format(user_id))
        messages = []
        for location in locations:
            messages.extend(loc_msg[location])
        push_line_message(user_id, messages)


def main(args):
    if args.mode == 'run':
        run()
    elif args.mode == 'setup':
        setup()
    else:
        raise Exception('Unknown mode: "{}"'.format(args.mode))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mountaineer-bot')
    parser.add_argument('--mode', type=str, default='run')
    arguments = parser.parse_args()
    main(arguments)

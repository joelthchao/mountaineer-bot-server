import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time

from mtn_bot_server import config


LOGGERS = {}
DEFAULT_FORMAT = '%(levelname)s: %(asctime)s.%(msecs)03d: %(filename)s:%(lineno)d %(message)s'


def get_logger(name, level=logging.INFO):
    if name not in LOGGERS:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        logger.addHandler(console_handler)
        LOGGERS[name] = logger
    return LOGGERS[name]


class MultiProcessingTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Logger handler suit for multi processing with time rotate"""
    def doRollover(self):
        """Overwrite doRollover"""
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if not os.path.exists(dfn):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            # find the oldest log file and delete it
            for s in self.getFilesToDelete():
                os.remove(s)
        self.mode = 'a'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                # DST kicks in before next rollover,
                # so we need to deduct an hour
                if not dstNow:
                    newRolloverAt = newRolloverAt - 3600
                # DST bows out before next rollover, so we need to add an hour
                else:
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt

    def computeRollover(self, currentTime):
        if self.when[0] == 'W' or self.when == 'MIDNIGHT':
            # use existing computation
            return super(MultiProcessingTimedRotatingFileHandler, self).computeRollover(currentTime)
        # round time up to nearest next multiple of the interval
        return (currentTime // self.interval) * self.interval


root_logger = logging.getLogger()
running_handler = MultiProcessingTimedRotatingFileHandler(
    config.RUNNING_LOG_FILE, when='MIDNIGHT', interval=1, backupCount=30,
    encoding='utf-8')
running_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
running_handler.setLevel(logging.DEBUG)
root_logger.addHandler(running_handler)

important_handler = MultiProcessingTimedRotatingFileHandler(
    config.IMPORTANT_LOG_FILE, when='MIDNIGHT', interval=1, backupCount=30,
    encoding='utf-8')
important_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
important_handler.setLevel(logging.WARNING)
root_logger.addHandler(important_handler)

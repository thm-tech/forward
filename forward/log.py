# -*- coding: utf-8 -*-

import logging
import logging.handlers
import sys
import os

from ndict import ndict

from config import CONFIG


def timed_roating_file_handler(name):
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(CONFIG.LOGGER.OUTPUT_DIRECTORY, name + '.log'), when='midnight', interval=1,
        backupCount=7, encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter(CONFIG.LOGGER.FORMAT))
    handler.setLevel(CONFIG.LOGGER.LEVEL)
    return handler


root_log = logging.getLogger()
root_log.setLevel(CONFIG.LOGGER.LEVEL)

root_stream_handler = logging.StreamHandler(sys.stdout)
root_stream_handler.setFormatter(logging.Formatter(CONFIG.LOGGER.FORMAT))
root_stream_handler.setLevel(CONFIG.LOGGER.LEVEL)

root_timed_roating_file_handler = timed_roating_file_handler('root')

root_log.addHandler(root_stream_handler)
root_log.addHandler(root_timed_roating_file_handler)


def _create_successor_logger(name):
    logger = logging.getLogger('root.' + name)
    time_rotating_file_handler = timed_roating_file_handler('root.' + name)
    logger.addHandler(time_rotating_file_handler)
    return logger


# DEFINE YOUR LOGGERS
orm_log = _create_successor_logger('orm')
http_log = _create_successor_logger('http')
fd_log = _create_successor_logger('fd')
auth_log = _create_successor_logger('auth')
user_log = _create_successor_logger('user')
mt_log = _create_successor_logger('mt')
chat_log = _create_successor_logger('chat')
mq_log = _create_successor_logger('mq')
# DEFINE YOUR LOGGERS ENDS


def echo_config(dict, prefix='CONFIG'):
    for item in dict.items():
        if isinstance(item[1], type(ndict())):
            echo_config(item[1], prefix + '.' + item[0])
        else:
            root_log.debug(prefix + '.' + str(item[0] + ': ' + str(item[1])))


root_log.info('Config Choose: %s' % CONFIG.NAME)
echo_config(CONFIG)
root_log.info('Loggers: %s' % list(logging.Logger.manager.loggerDict.keys()))

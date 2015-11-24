# coding:UTF-8

import os.path
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options
import tornado.web
import tornado.log


sys.path.append(os.path.abspath(".."))

from url import *
from config import CONFIG

define("port", default=CONFIG.TORNADO.PORT, help="run on the given port", type=int)

options.log_file_prefix = os.path.join(CONFIG.LOGGER.OUTPUT_DIRECTORY, 'mmx.log')
options.log_file_max_size = 1048576
options.log_file_num_backups = 10


class Application(tornado.web.Application):
    def __init__(self):
        handlers = URL_SETTINGS
        settings = CONFIG.TORNADO.SETTINGS
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

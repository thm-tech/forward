# -*- encoding: utf-8 -*-

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
from tornado.web import *
import tornado.websocket
import os.path
import uuid
import json
import time

from tornado.options import define, options

define("port", default=8889, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/chat/", ChatSocketHandler),
            (r"/", BaseHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #xsrf_cookies=True,
            login_url="/login"
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.add_header("Access-Control-Allow-Origin", 'http://www.lameleg.com:9000')
        self.add_header("Access-Control-Allow-Credentials", 'true')
        self.add_header("Access-Control-Allow-Methods", 'GET,POST,OPTIONS,PUT,DELETE')
        self.add_header("Access-Control-Allow-Headers", 
        'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type')

    def options(self):
        pass

       
class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "open"

    def on_close(self):
        print "on close"

    def on_message(self, message):
        s = 'you say:' + message
        print message
        self.write_message(s)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

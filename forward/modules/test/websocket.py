#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import thread

from tornado.options import define, options

define("port", default=8989, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/chatsocket", ChatSocketHandler),
            (r"/push", PushToPos),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class PushToPos(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><body><form action="/push" method="POST">'
                '<input type="text" name="shop_id">'
                '<input type="text" name="pos_id">'
                '<input type="text" name="message">'
                '<input type="submit" value="Submit">'
                '</form></body></html>')

    def post(self):
        """docstring for po"""
        shop_id = self.get_argument("shop_id")
        pos_id = self.get_argument("pos_id")
        message = self.get_argument("message")
        print shop_id,pos_id,message

        ChatSocketHandler.pushPos(shop_id,pos_id,message)

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    #key: shop_id + pos_id value:self point 
    pos_self = {}


    def open(self):
        self.shop_id = self.get_argument("shop_id")
        self.pos_id = self.get_argument("pos_id")

        print self.shop_id, self.pos_id

        self.pos_self[self.shop_id + self.pos_id] = self
        print "open"

    def on_close(self):
        del self.pos_self[self.shop_id + self.pos_id]
        print "close"

    def on_message(self, message):
        print self.shop_id, self.pos_id,message

        self.write_message(message)

    @staticmethod
    def pushPos(shop_id,pos_id,message):
        """docstring for pushPos"""
        try:
            ChatSocketHandler.pos_self[shop_id + pos_id].write_message(message)
        except:
            print "key error"



def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

# -*- encoding: utf-8 -*-

import logging
import tornado.escape
import tornado.ioloop
from tornado.httpclient import *
import tornado.options
from tornado import gen
from tornado.web import *
import tornado.websocket
import os.path
import uuid
import json
import time
from chat_processor import ChatProcessor

from tornado.options import define, options
from user_ws_session import UserSession
from settings import * 


import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)



class ChatBaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.add_header("Access-Control-Allow-Origin", 'http://api.immbear.com')
        self.add_header("Access-Control-Allow-Credentials", 'true')
        self.add_header("Access-Control-Allow-Methods", 'GET,POST,OPTIONS,PUT,DELETE')
        self.add_header("Access-Control-Allow-Headers", 
        'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type')

    def options(self):
        pass

       
class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    @gen.coroutine
    def auth(self):
        request = HTTPRequest(AUTH_URL, 'POST', body = json.dumps({'accID':self.user,
                                'password':self.passwd}))
        http = AsyncHTTPClient()
        res = yield http.fetch(request)
        raise gen.Return(json.loads(res.body))

    @gen.coroutine
    def userOnline(self):
        self.user = unicode(self.get_argument("u", None))
        self.passwd = self.get_argument("p", None)

        res = yield self.auth()
        if res['err']:
            print "auth failed"
            self.close()
            raise gen.Return(res)

        old_session = UserSession.getSession(self.user)
        if old_session:
            msg = json.dumps({
                'c':'CHANGE_DEVICE',
                'time':time.time(),
                'msg':'',
            })
            try:
                old_session.write_message(msg)
            except:
                pass

        UserSession.addSession(self.user, self)
        processor = ChatProcessor(self.user)
        processor.userOnline()

        print "user online:", self.user,type(self.user)


    @gen.coroutine
    def open(self):
        yield self.userOnline()

    def on_close(self):
        if hasattr(self, 'user'):
            UserSession.clearUserSession(self)
            print "on close", self.user
        #print UserSession.users
        #print 'on close'

    def on_message(self, message):
        CHAT_LOG.debug("got message:%s",unicode(message))
        processor = ChatProcessor(self.user, message)
        if processor:
            processor.process()
        else:
            CHAT_LOG.error("init processor failed")


"""
def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
"""

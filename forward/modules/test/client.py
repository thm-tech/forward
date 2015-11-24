from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.gen import coroutine
from tornado.web import asynchronous
from forward.httpbase import HttpBaseHandler
from forward.mq.mq import MQInterface as mq
from forward.config import PORT
import json
from forward.common.tools import *
from forward.common.encrypt import *

from forward.log.fdlog import log
import base64
import time

from forward.common.auth import *

COMMAND_URL_DICT = {
        "0x00010001":["/auth/auth", "POST"],
        "0x00020001":["/user/login", "POST"],
        "0x00020002":["/user/loginex", "POST"],
        "0x00020003":["/user/logout", "POST"],
        "0x00020004":["/user/register", "POST"],
    }


class Test(HttpBaseHandler):   
    log = log.getLogger("fd")

class Client(Test):
    def get(self):
        """here for test ,act as a client"""
        self.write('<html><body><form action="/test/client" method="POST">'
                '<textarea rows="20" cols="100" name="json_msg"></textarea> '
                '<input style="width:100px;height:100px;" type="submit" value="Submit">'
                '</form></body></html>')

    @coroutine
    def post(self):
  
        json_str = self.get_argument("json_msg")
        #print "json_str: ",json_str
        value_obj = json.loads(json_str)

        com_val = COMMAND_URL_DICT[value_obj["command"]]
        com_url = com_val[0]
        com_func = com_val[1]
        url = "http://115.28.143.67:" + str(PORT)  + com_url
        print "---------------------------------------"
        print "request url: " + url
        print "request json: " + json_str
        print "---------------------------------------"

        if "GET" == com_func :
            request = HTTPRequest(url, 'GET')
            http = AsyncHTTPClient()
            response = yield http.fetch(request)
            print "---------------------------------------"
            print "response json: " + response.body
            print "---------------------------------------"
            self.write(response.body)
        elif "POST" == com_func:
            request = HTTPRequest(url,'POST',body=json_str)
            http = AsyncHTTPClient()
            response = yield http.fetch(request)
            print "---------------------------------------"
            print "response json: " + response.body
            print "---------------------------------------"
            self.write(response.body)
        else:
            pass

class CoroutineDb(Test):
    def db_test(self):
        print "db_test start"
        time.sleep(10)
        print "db_test end"

        return None

    @coroutine
    def get(self):
        print "get start"
        yield self.db_test()
        print "get end"
        

class WebClient(Test):
    def get(self):
        self.write('<html><body><form action="/test/web/client" method="POST">'
                '<textarea rows="20" cols="100" name="json_msg"></textarea> <br />'
                '<label>url</label><input type="text" name="url" > <br />'
                '<label>method</label><input type="text" name="method" > <br />'
                '<input style="width:100px;height:100px;" type="submit" value="Submit">'
                '</form></body></html>')


    @coroutine
    #@showHttpPackage
    #@showHttpBody
    def post(self):
        json_str = self.get_argument("json_msg")
        url = self.get_argument("url")
        method = self.get_argument("method")

        url = "http://115.28.143.67:" + str(PORT) + url

        print "------request url: " + url + "-----method:" + method

        if method == "POST" or method == "PUT":
            request = HTTPRequest(url,method,body=json_str)
            http = AsyncHTTPClient()
            response = yield http.fetch(request)

            print "------response json: " + response.body

            self.write(response.body)

        if method == "DELETE":
            request = HTTPRequest(url,method)
            http = AsyncHTTPClient()
            response = yield http.fetch(request)

            print "------response json: " + response.body

            self.write(response.body)





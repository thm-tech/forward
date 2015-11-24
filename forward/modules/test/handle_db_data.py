from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.gen import coroutine
from tornado.web import asynchronous
from forward.httpbase import HttpBaseHandler
from forward.mq.mq import MQInterface as mq
from forward.config import PORT
from tornado.escape import json_encode, utf8

from forward.log.fdlog import log as log_base

from forward.db.db_base import *

from url_json_define import *

class Test(HttpBaseHandler):   
    log = log_base.getLogger("fd")


class GetDbData(Test):
    def get(self):
        self.render("get_db_data.html")


    @coroutine
    def post(self):

        for req in GET_DATA:
            url = "http://121.199.9.187:" + str(PORT) + req['url']
            self.log.info(url)

            request = HTTPRequest(url, 'GET')

            http = AsyncHTTPClient()
            response = yield http.fetch(request)
            print '--------------------------'
            print response
            print '--------------------------'

            f = open('output_josn.txt', 'a+')
            s = 'url:------------------\n' + url  \
                    + '\nresponse:------------------\n' + response.body
            f.write(s)
            f.close()

            self.write(s)

            self.log.info('response is:%s', response.body)


class DeleteDbData(Test):
    def get(self):
        self.write('<html><body><form action="/test/d/db/data" method="POST">'
                '<input style="width:100px;height:100px;" type="submit" value="delete db data">'
                '</form></body></html>')


    @coroutine
    def post(self):

        for req in DELETE_DATA:
            url = "http://121.199.9.187:" + str(PORT) + req['url']
            self.log.info(url)

            request = HTTPRequest(url, 'DELETE')

            http = AsyncHTTPClient()
            response = yield http.fetch(request)
            print '--------------------------'
            print response
            print '--------------------------'
            self.log.info('response is:%s', response.body)


class UpdateDbData(Test):
    def get(self):
        self.write('<html><body><form action="/test/u/db/data" method="POST">'
                '<input style="width:100px;height:100px;" type="submit" value="update db data">'
                '</form></body></html>')


    @coroutine
    def post(self):

        for req in UPDATE_DATA:
            url = "http://121.199.9.187:" + str(PORT) + req['url']
            self.log.info(url)

            for data in req['datas']:
                json_str = json_encode(data)
                request = HTTPRequest(url, 'PUT', body=json_str)

                http = AsyncHTTPClient()
                response = yield http.fetch(request)
                print '--------------------------'
                print response
                print '--------------------------'
                self.log.info('response is:%s', response.body)


class InsertDbData(Test):
    def get(self):
        self.write('<html><body><form action="/test/p/db/data" method="POST">'
                '<input style="width:100px;height:100px;" type="submit" value="insert db data">'
                '</form></body></html>')


    @coroutine
    def post(self):

        for req in INSERT_DATA:
            url = "http://121.199.9.187:" + str(PORT) + req['url']
            self.log.info(url)

            for data in req['datas']:
                json_str = json_encode(data)
                request = HTTPRequest(url, 'POST', body=json_str)

                http = AsyncHTTPClient()
                response = yield http.fetch(request)
                print '--------------------------'
                print response
                print '--------------------------'
                self.log.info('response is:%s', response.body)


def queryShopCodesByMerchantId_(self, merchant_id):
    shop_codes = []

    def wapper(self, merchant_id):
        if self.merchant_type == 1 or self.merchant_type == 2:
            for child in self.children:
                wapper(child, child.merchant_id)
        elif self.merchant_type == 3:
            shop_codes.append(self.shop_code)
        else:
            return

    wapper(self, merchant_id)

    return shop_codes



class MerchantShops(Test):
    def get(self):
        merchant_id = self.get_argument("mid", None)

        session = DBSession()

        m = session.query(FD_T_MerchantArch).\
                filter(FD_T_MerchantArch.merchant_id == merchant_id).one()

        self.write({"shopCodes":queryShopCodesByMerchant(m)})

        

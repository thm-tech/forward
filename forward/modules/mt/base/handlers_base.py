# -*- encoding: utf-8 -*-
import requests
from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPClient

__author__ = 'Mohanson'

from forward.httpbase import HttpBaseHandler
from .db_base import *
from forward.common.tools import tornado_argument
from forward.modules.mt.shenhe import shenhe, shenhe_all
from forward.common.tools import tornado_route
from tornado.gen import coroutine
import json

base_urls = []


@tornado_route(r'/base/newid', base_urls)
class NewIdHandler(HttpBaseHandler):
    @tornado_argument('_type')
    def get(self):
        if self.arg.type == 'account':
            self.write(dict(account_id=get_newaccountid()))
        elif self.arg.type == 'image':
            self.write(dict(image_id=get_newimageid()))
        elif self.arg.type == 'good':
            self.write(dict(goods_id=get_newgoodsid()))


@tornado_route(r'/base/admin/shenhe', base_urls)
class ShopService(HttpBaseHandler):
    @tornado_argument('_id', '_token')
    def get(self):
        assert self.arg.token == 'miumiu'
        if self.arg.id == 'all':
            r = shenhe_all()
        elif self.arg.id.isdigit():
            r = shenhe(self.arg.id)
        self.write({'is_success': True})


@tornado_route(r'/img/info', base_urls)
class ImgInfo(HttpBaseHandler):

    @coroutine
    def get(self):

        r = []

        urls = self.get_arguments('url')
        for url in urls:
            http_client = HTTPClient()
            response = http_client.fetch(url + "@infoexif")
            r.append(json.loads(response.body))
        self.write({'info': r})
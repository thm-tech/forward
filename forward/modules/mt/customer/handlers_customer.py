# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import tornado.web

from forward.httpbase import HttpBaseHandler
from forward.modules.mt.customer.db_customer import *
from forward.common.tools import tornado_route


urls = []


@tornado_route(r'/customer/(\d*)/shop/(\d*)/info', urls)
class CustomerHandler(HttpBaseHandler):
    @tornado.web.authenticated
    def get(self, user_id, shop_id):
        """
        :return:{"user_favorite_num": 4,
        "goods": [{"price": 12.5, "promotion_price": 10.5, "pic_url_list": "/fdimage/shopimage/47.jpg, /fdimage/shopimage/47.jpg", "goods_id": 1, "description": "desc1"}, {"price": 22.0, "promotion_price": -1.0, "pic_url_list": "/fdimage/shopimage/47.jpg, /fdimage/shopimage/47.jpg", "goods_id": 2, "description": "desc2"}, {"price": 25.0, "promotion_price": -1.0, "pic_url_list": "/fdimage/shopimage/47.jpg, /fdimage/shopimage/47.jpg", "goods_id": 3, "description": "desc3"}, {"price": 2.5, "promotion_price": -1.0, "pic_url_list": "/fdimage/shopimage/47.jpg, /fdimage/shopimage/47.jpg", "goods_id": 4, "description": "desc4"}],
        "user_name": "339",
        "user_visit_num": 1,
        "last_visit_time": "2015-05-12 15:15:53:000000"}
        """
        response = get_fans_all_msg(shop_id, user_id)
        self.write(response)
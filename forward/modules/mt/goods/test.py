# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import unittest
import json
import hashlib

import requests



FORWARD_URL = 'http://127.0.0.1:8887'
# FORWARD_URL = 'http://115.28.143.67:8887'


class Goods(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()
        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('root').hexdigest(),
        })
        self.session.post(FORWARD_URL + '/merchant/login', data=data)

    def tearDown(self):
        self.session.close()

    def test_goods_category(self):
        response = self.session.get(FORWARD_URL + '/goods/category/2')
        print(response.text)

    def test_goods_publish(self):
        data = json.dumps(dict(
            shop_id=10061,
            category_id=1,
            description='description',
            bar_code='asdfasdf',
            price=1,
            promotion_price=-1,
            brand_name='1111',
            basic_info='Hello',
            is_sendall=True,
        ))
        response = self.session.post(FORWARD_URL + '/goods', data=data)
        print(response.text)

    def test_get_goods_list_by_shop(self):
        params = {
            'shop_id': 10061,
            'offset': 0,
            'limit': 10,
            'status': '2',
        }
        response = self.session.get(FORWARD_URL + '/goods', params=params)
        print(response.text)
        print(len(json.loads(response.text)['goods']))

    def test_delete_goods(self):
        response = self.session.delete(FORWARD_URL + '/goods/75')
        print(response.text)

    def test_get_goods_info(self):
        response = self.session.get(FORWARD_URL + '/goods/1')
        print(response.text)

    def test_put_goods_info(self):
        data = json.dumps(dict(
            goods_name='goods_name',
            description='description',
            price=1,
            promotion_price=-1,
            brand_name='1111',
            basic_info='Hello',
            status=-1,
        ))
        response = self.session.put(FORWARD_URL + '/goods/75', data=data)
        print(response.text)

    def test_get_goods_img(self):
        response = self.session.get(FORWARD_URL + '/goods/1/image')
        print(response.text)

    def test_put_goods_img(self):
        data = json.dumps({
            'pic_url_list': '1,2,3,4,5'
        })
        response = self.session.put(FORWARD_URL + '/goods/1/image', data=data)
        print(response.text)

    def test_get_goods_favorite(self):
        response = self.session.get(FORWARD_URL + '/goods/1/favorite')
        print(response.text)

    def test_get_goods_fans(self):
        params = {
            'details': True,
            'offset': 0,
            'limit': 1,
        }
        response = self.session.get(FORWARD_URL + '/goods/75/fans', params=params)
        print(response.text)

    def test_add_goods_standard(self):
        data = json.dumps({
            'stand_key': 'size',
            'stand_value': 'big',
            'price': '1',
            'promotion_price': '0.5',
        })
        response = self.session.post(FORWARD_URL + '/goods/1/standard', data=data)
        print(response.text)

    def test_get_goods_standards(self):
        response = self.session.get(FORWARD_URL + '/goods/1/standard')
        print(response.text)

    def test_modify_goods_standards(self):
        data = json.dumps({
            'stand_key': 'size',
            'stand_value': 'small',
            'price': '1',
            'promotion_price': '2',
        })
        response = self.session.put(FORWARD_URL + '/goods/1/standard/1', data=data)
        print(response.text)

    def test_delete_goods_standards(self):
        response = self.session.delete(FORWARD_URL + '/goods/1/standard/2')
        print(response.text)

    def test_modify_goods_status(self):
        data = json.dumps({
            'ids': '58,59',
            'status': 2
        })
        response = self.session.put(FORWARD_URL + '/goods/status', data=data)
        print(response.text)



if __name__ == '__main__':
    unittest.main()
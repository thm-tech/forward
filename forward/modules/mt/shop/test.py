# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import unittest
import json
import datetime
import time
import requests
import hashlib


FORWARD_URL = 'http://127.0.0.1:8887'
# FORWARD_URL = 'http://115.28.143.67:8887'


class Shop(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()
        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('111111').hexdigest(),
        })
        self.session.post(FORWARD_URL + '/merchant/login', data=data)

    def tearDown(self):
        self.session.close()

    def test_sign_shop(self):
        data = json.dumps({
            'shop_id': 12000,
            'shop_name': '包头子',
            'brand_name': '小芳',
        })
        response = self.session.post(FORWARD_URL + '/shops', data=data)
        print(response.text)

    def test_get_shops(self):
        params = {
            'offset': 1,
            'limit': 2,
        }
        response = self.session.get(FORWARD_URL + '/shop', params=params)
        print(response.text)

    def test_get_shop_info(self):
        response = self.session.get(FORWARD_URL + '/shop/10061')
        print(response.text)

    def test_modify_shop_info(self):
        data = json.dumps({
            # 'shop_name': '妹子你这是坏掉了么',
            # 'brand_name': 'nihao',
            # 'business_hours': 'ss',
            # 'telephone_no': 'ss',
            # 'city_id': 12,
            # 'district_id': 12,
            # 'business_area': 'ss',
            # 'address': 'ss',
            # 'longitude': 12,
            # 'latitude': 12,
            'category_list': '202'
        })
        response = self.session.put(FORWARD_URL + '/shop/10061', data=data)
        print(response.text)

    def test_modify_shop_introduction(self):
        data = json.dumps({
            'shop_id': 10061,
            'introduction': '24333',
        })
        response = self.session.put(FORWARD_URL + '/shop/10061/introduction', data=data)
        print(response.text)

    def test_get_shop_introduction(self):
        response = self.session.get(FORWARD_URL + '/shop/10061/introduction')
        print(response.text)

    def test_put_shop_image(self):
        data = json.dumps({
            'pic_url_list': 'http://mmx-img-public.oss-cn-hangzhou.aliyuncs.com/sdfsdf/asdfasdf/1.txt'
        })
        response = self.session.put(FORWARD_URL + '/shop/10061/image', data=data)
        print(response.text)

    def test_get_shop_image(self):
        response = self.session.get(FORWARD_URL + '/shop/10061/image')
        print(response.text)

    def test_publish_activity(self):
        for i in range(100):
            data = json.dumps({
                'act_title': '买一送10',
                'act_content': '浙江温州最大皮革厂江南皮鞋厂倒闭了，王八蛋老板，黄鹤，吃喝嫖赌，欠下3.7个亿，带着小姨子跑了，我们没有办法，拿着钱包抵工资，原价200多，300多的钱包，现在只要20块。只要20块。黄鹤，你不是人，你个王八蛋，我们辛辛苦苦给你干了大半年，你不发工资，还我血汗钱! ',
                'begin_time': '2005-10-10',
                'end_time': '2015-10-10'
            })
            response = self.session.post(FORWARD_URL + '/shop/10061/activities', data=data)
            print(response.text)

    def test_get_shop_activities(self):
        params = {
            'offset': 0,
            'limit': 2,
        }
        response = requests.get(FORWARD_URL + '/shop/10061/activities', params=params)
        print(response.text)

    def test_get_shop_fans(self):
        params = {
            'offset': 0,
            'limit': 100000,
        }
        response = requests.get(FORWARD_URL + '/shop/10061/fans', params=params)
        print(response.text)
        print(len(json.loads(response.text)['fans']))

    def test_get_shop_user_favorite_goods(self):
        response = requests.get(FORWARD_URL + '/shop/10061/user/10039/favorite')
        print(response.text)

    def test_post_shop_fans_message(self):
        data = json.dumps({
            'userids': '1, 2, 3',
            'message': 'hello'
        })
        response = self.session.post(FORWARD_URL + '/shop/10061/fansmessage', data=data)
        print(response.text)

    def test_is_user_a_shop_fans(self):
        response = self.session.get(FORWARD_URL + '/shop/10061/fans/7')
        print(response.text)

if __name__ == '__main__':
    unittest.main()

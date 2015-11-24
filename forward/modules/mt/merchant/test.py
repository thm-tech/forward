# -*- encoding: utf-8 -*-
__author__ = 'Mohanson'

import unittest
import json
import hashlib
import requests


FORWARD_URL = 'http://127.0.0.1:8887'
# FORWARD_URL = 'http://115.28.143.67:8887'


class Merchant(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()
        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('root').hexdigest(),
        })
        self.session.post(FORWARD_URL + '/merchant/login', data=data)

    def tearDown(self):
        self.session.close()

    def test_get_merchant_basic_info(self):

        response = self.session.get(FORWARD_URL + '/merchant/10061/info')
        print(response.text)

    def test_modify_merchant_basic_info(self):
        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('root').hexdigest(),
        })
        self.session.post(FORWARD_URL + '/merchant/login', data=data)

        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('root').hexdigest(),
        })
        self.session.post(FORWARD_URL + '/merchant/login', data=data)

        data = json.dumps({
            'contact_name': '花随月',
        })
        response = self.session.post(FORWARD_URL + '/merchant/10061/info', data=data)
        print(response.text)

    def test_get_merchant_service_info(self):
        response = self.session.get(FORWARD_URL + '/merchant/10061/serviceinfo')
        print(response.text)

    def test_is_merchant_exist(self):
        params = {
            'account': '小明',
        }
        response = self.session.get(FORWARD_URL + '/merchant/isexist', params=params)
        print(response.text)

    def test_sign_merchant(self):
        data2 = {"account": "你好小苹果",
                 "password": "63a9f0ea7bb98050796b649e85481845",
                 "contact_name": "1",
                 "contact_phone_no": "1",
                 "brand_name": "1",
                 "category_list": "1",
                 "shop_name": "1",
                 "business_hours": "1,1",
                 "telephone_no": "1",
                 "city_id": 1,
                 "district_id": 1,
                 "business_area": "1",
                 "address": "1",
                 "longitude": "1",
                 "latitude": "1"}
        data2 = json.dumps(data2)

        response = self.session.post(FORWARD_URL + '/merchant', data=data2)
        print(response.text)

    def test_modify_password(self):
        data = json.dumps({
            'old_password': '63a9f0ea7bb98050796b649e85481845',
            'new_password': 'root',
        })
        response = self.session.put(FORWARD_URL + '/merchant/10061/password', data=data)
        print(response.text)

    def test_login(self):
        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('111111').hexdigest(),
        })
        response = self.session.post(FORWARD_URL + '/merchant/login', data=data)
        print(response.text)
        print(self.session.cookies)

    def test_get_shop_msgconfig(self):
        response = self.session.get(FORWARD_URL + '/merchant/10061/msgconfig')
        print(response.text)

    def test_desc_shop_msgconfig(self):
        data = json.dumps({
            'type': 'desc_remain',
            'cate': 'mass',
        })
        response = self.session.put(FORWARD_URL + '/merchant/10061/msgconfig', data=data)
        print(response.text)

    def test_is_account_or_password_exist(self):
        params = {
            'step': 'is_account_exist',
            'type': 'account',
            'acc_or_pho': '18756967287',
        }
        response = self.session.get(FORWARD_URL + '/merchant/forgetpassword', params=params)
        print(response.text)

    def test_get_phone_captcha(self):
        params = {
            'step': 'get_phone_captcha',
            'phone': '18756967287',
        }
        response = self.session.get(FORWARD_URL + '/merchant/forgetpassword', params=params)
        print(response.text)

    def test_validate_phone_captcha(self):
        data = json.dumps({
            'step': 'validate_phone_captcha',
            'phone_captcha': 727713,
            'phone': '18756967287',
        })
        response = self.session.post(FORWARD_URL + '/merchant/forgetpassword', data=data)
        print(response.text)

    def test_reset_password(self):
        data = json.dumps({
            'shop_id': '10173',
            'step': 'reset_password',
            'new_password': '63a9f0ea7bb98050796b649e85481845',
        })
        response = self.session.post(FORWARD_URL + '/merchant/forgetpassword', data=data)
        print(response.text)


class Merchant3Test(unittest.TestCase):

    def setUp(self):
        self.session = requests.session()
        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('root').hexdigest(),
        })
        self.session.post(FORWARD_URL + '/merchant/login', data=data)

    def tearDown(self):
        self.session.close()

    def test_sign_merchant(self):
        data = json.dumps({
            'account': 'rootdmin2',
            'password': hashlib.md5('root').hexdigest(),
        })
        response = self.session.post(FORWARD_URL + '/merchants', data=data)
        print(response.text)


if __name__ == '__main__':
    unittest.main()

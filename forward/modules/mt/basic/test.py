# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import unittest
import json

import requests

from forward.modules.mt.basic.db_basic import *


FORWARD_URL = 'http://127.0.0.1:8887'
# FORWARD_URL = 'http://115.28.143.67:8887'
FORWARD_URL = 'http://api.immbear.com'

class Basic(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()

    def tearDown(self):
        self.session.close()

    def test_get_companyinfo(self):
        response = self.session.get(FORWARD_URL + '/basic/companyinfo')
        print(response.text)

    def test_get_countries(self):
        response = self.session.get(FORWARD_URL + '/basic/countries')
        print(response.text)

    def test_get_provinces(self):
        print(get_provinces(1, 1))

        params = {
            'all': 1
        }
        response = self.session.get(url=FORWARD_URL + '/basic/provinces', params=params)
        print(response.text)

    def test_get_cities(self):
        params = {
            'province_id': 16,
            'all': 1
        }
        response = self.session.get(url=FORWARD_URL + '/basic/cities', params=params)
        print(response.text)

    def test_get_districts(self):
        params = {
            'country_id': 1,
            'province_id': 2,
            'city_id': 5,
        }
        response = self.session.get(url=FORWARD_URL + '/basic/districts', params=params)
        print(response.text)

    def test_get_goodscategories(self):
        params = {
            # 'parent_id': 3,
            'type': 'all',
        }
        response = self.session.get(url=FORWARD_URL + '/basic/goodscategories', params=params)
        print(response.text)

    def test_get_goodscategories_all(self):
        params = {
            'type': 'all',
        }
        response = self.session.get(url=FORWARD_URL + '/basic/goodscategories', params=params)
        print(response.text)

    def test_captcha(self):
        params = {
            'rnd': 0.154654,
        }
        response = self.session.get(url=FORWARD_URL + '/basic/captcha', params=params)
        print('captcha', response.status_code)

    def test_validate_captcha(self):
        data = json.dumps({
            'rnd': 0.154654,
            'captcha_str': 'KgS2'
        })
        response = self.session.post(url=FORWARD_URL + '/basic/captcha', data=data)
        print('captcha', response.text)

    def test_send_phone_validate(self):
        response = self.session.get(url=FORWARD_URL + '/basic/phonevalidate/18756967287')
        print(response.text)

    def test_validate_phone_validate(self):
        data = json.dumps({
            'code': '313168'
        })
        response = self.session.post(url=FORWARD_URL + '/basic/phonevalidate/18756967287', data=data)
        print(response.text)

    def test_get_joinshops(self):
        params = {
            'offset': 0,
            'limit': 9,
        }
        response = self.session.get(url=FORWARD_URL + '/basic/joinshops', params=params)
        print(response.text)


if __name__ == '__main__':
    unittest.main()
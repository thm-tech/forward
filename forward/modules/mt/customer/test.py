# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import unittest
import json
import hashlib
import requests


FORWARD_URL = 'http://127.0.0.1:8887'
# FORWARD_URL = 'http://115.28.143.67:8887'
# FORWARD_URL = 'http://www.lameleg.com:8887'
FORWARD_URL = 'http://api.immbear.com'

class Customer(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()
        data = json.dumps({
            'account': 'root',
            'password': hashlib.md5('root').hexdigest(),
        })
        self.session.post(FORWARD_URL + '/merchant/login', data=data)


    def tearDown(self):
        self.session.close()

    def test_customer(self):
        response = self.session.get(FORWARD_URL + '/customer/10039/shop/10061/info')


if __name__ == '__main__':
    unittest.main()
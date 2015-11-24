# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import unittest
import json

import requests



# from forward.modules.user.db_shop import DBShop
# from forward.modules.user.db_user_web import *


host = 'http://api.immbear.com'
host = 'http://127.0.0.1:8887'


class MyTest(unittest.TestCase):
    def setUp(self):
        self.session = requests.session()
        self.session.post(host + '/user/login',
                          data=json.dumps(
                              {"mode": 2, "phone": "18756967287", "password": "96e79218965eb72c92a549dd5a330112",
                               "type": "4",
                               "dev": "223.240.72.10"}))

    def tearDown(self):
        self.session.close()


    def test_get_favorite_goods(self):
        params = {
            'offset': 0,
            'limit': 2,
        }
        response = self.session.get(host + '/userweb/10303/favorites', params=params)
        print(response.text)


    def test_get_user_info_by_miumiu_or_phone(self):
        response = self.session.get(host + '/userweb/search/m10039')
        print(response.text)

    def test_get_fans_shops(self):
        data = json.dumps({
            'shopIDs': [],
        })
        response = self.session.post(host + '/user/fans/diff', data=data)
        print(response.text)

    def test_fucn(self):
        response = self.session.get(host + '/user/fans/info?sid=10061&sid=10250&sid=10251')
        print(response.text)

    def test_god_save_me(self):
        data = json.dumps({
            'sid': 10061
        })
        response = self.session.post(host + '/user/shop/concern?sid=10061', data=data)
        print(response.text)

    def test_help(self):
        data = json.dumps({
            'mode': 1,
            'phone': '54654645645654654654',
            'remark': '1',
        })
        response = self.session.post(host + '/user/friend/invite', data=data)
        print(response.text)

    def test_1(self):
        from forward.modules.user.db_shop import *

        r = DBShop().queryFansShopInfoList(10039, [10229, 10237, 10230, 10061])
        print(r)

    def test_modify_friend_remark(self):
        data = json.dumps({
            'friend_id': 10051,
            'remark': 'nihao'
        })
        print(data)
        response = self.session.post(host + '/userweb/10039/friend/remark', data=data)
        print(response.text)

    def test_invite_friend(self):
        data = json.dumps({
            'mode': 1,
            'phone': '13625510905',
            'remark': 'Hello'
        })
        response = self.session.post(host + '/user/friend/invite', data=data)
        print(response.text)

    def test_login(self):
        data = json.dumps({
            'mode': 5,
            'type': 4,
            'openID': '12121212',
            'dev': '1'
        })
        response = self.session.post(host + '/user/loginex', data=data)
        print(response.text)

    def test_upload_file(self):
        pic_url = 'http://img.immbear.com/27af60c48555d8df9f5b31133fe2f67d.jpeg'
        pic_content = requests.get(pic_url).content
        h = b'-----------------------------311092004222736\r\nContent-Disposition: form-data; name="file"; filename="logo1.png"\r\nContent-Type: image/png\r\n\r\n'
        f = b'\r\n-----------------------------297391254920134--\r\n'
        r = requests.post('http://115.28.143.67:8889/file/uploader', data=h + pic_content + f)
        print(r.text)
        import json

        j = json.loads(r.text)
        print(j['url'], j['md5'] + '.png')

    def test_i_dont_know(self):
        r = requests.post('http://127.0.0.1:8887/userweb/selectphones', data=json.dumps({
            'phone': 18756967287,
            'phone_list': [18756967287, 11111111111, 12345678999]
        }))
        print(r.text)

    def test_only_god_know_what_i_am_doing_now(self):
        r = requests.post('http://127.0.0.1:8887/userweb/sendinvite', data=json.dumps({
            'phone': 18756967287,
            'name': 'Hello',
            'remark': '中文'
        }))
        print(r.text)

    def test_q(self):
        self.session = requests.session()
        login = self.session.post(host + '/user/login',
                                  data=json.dumps(
                                      {"mode": 2, "phone": "18756967287",
                                       "password": "96e79218965eb72c92a549dd5a330112",
                                       "type": "4",
                                       "dev": "223.240.72.10"}))
        print(login.text)
        r = self.session.get('http://api.immbear.com/user/setting/private')
        print(r.text)

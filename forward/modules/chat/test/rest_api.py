# -*- encoding: utf-8 -*-
import unittest

import requests
import json


FORWARD_URL = 'http://127.0.0.1:8889'
session = requests.session()

class REST_api(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_userEnterShop(self):
        print "\n----------user enter shop----------"
        #data = '{"phone": "13811112222","password": "123456"}'
        response = session.post(FORWARD_URL + '/chat/user/123/shop/456')
        print(response.text)

    def test_queryShopUsersAndNum(self):
        print "\n----------query shop users and num----------"
        response = session.get(FORWARD_URL + '/chat/shop/456/users')
        print(response.text)

    def test_queryShopUsersList(self):
        print "\n----------query shop users and num----------"
        response = session.get(FORWARD_URL + '/chat/shop/456/userslist')
        print(response.text)

    def test_queryShopsUsernum(self):
        print "\n----------query shops user num----------"
        response = session.get(FORWARD_URL + '/chat/shops/usernum?shop_id=456&shop_id=789')
        print(response.text)

    def test_queryShopUserNum(self):
        print "\n----------query shop user num----------"
        response = session.get(FORWARD_URL + '/chat/shop/456/userstotalnum')
        print(response.text)

    def test_inviteFriend(self):
        print "\n----------invite friend----------"
        data = {
            'invitor_id':1,
            'invitor_name': 'kit',
            'invitor_portrait': '/mmx/image/user/1.jpg',
            'remark': 'i am kit',
            'receivor_id': 2
        }
        response = session.post(FORWARD_URL + '/chat/friend/invite/123/to/456',data=json.dumps(data))
        print(response.text)

    def test_confirmFriend(self):
        print "\n----------confirm friend----------"
        data = {
            'invitor_id':1,
            'receivor_id': 2,
            'receivor_name':'hel',
            'receivor_portrait':'/mmx/image/user/1.jpg'
        }
        response = session.post(FORWARD_URL + '/chat/friend/confirm/123/to/345',data=json.dumps(data))
        print(response.text)

    def test_ckedit_uploader(self):
        print "\n----------ck edit uploader----------"
        data = {
            'invitor_id':1,
            'receivor_id': 2,
            'receivor_name':'hel',
            'receivor_portrait':'/mmx/image/user/1.jpg'
        }
        response = session.post(FORWARD_URL + '/ck/file/uploader?CKEditorFuncNum=1',data=json.dumps(data))
        print(response.text)

    def test_add_update_room_info(self):
        print "\n----------add or update room info----------"
        data = {
            'roomName':'kendeji',        #options
            'roomImg':'http://img.immbear.com/lll.png', #options
            'owner':'10237',   #options
        }
        response = session.post(FORWARD_URL + '/chat/room/shop_10237/info',data=json.dumps(data))
        print(response.text)

    def test_get_room_info(self):
        print "\n----------get room info----------"
        response = session.get(FORWARD_URL + '/chat/room/shop_10237/info')
        """
        {
            'gname':'shop_10237',
            'roomName':'kendeji',       
            'roomImg':'http://img.immbear.com/lll.png', 
            'owner':'10237',  
        }
        """
        print(response.text)

if __name__ == '__main__':
    unittest.main()

# -*- encoding: utf-8 -*-
__author__ = 'Jilin Yin'

import unittest

import requests


FORWARD_URL = 'http://127.0.0.1:7188'
FORWARD_URL = 'http://127.0.0.1:8887'
session = requests.session()


class Passport(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_1_register(self):
        print "\n----------test_1_register----------"
        data = '{"phone": "13811112222","password": "123456"}'
        response = session.post(FORWARD_URL + '/user/register', data=data)
        print(response.text)

    def test_2_login_exist(self):
        print "\n----------test_2_login_exist----------"
        data = '{"mode":2, "phone":"15812345677", "password":"111222", "dev":"IMEI123456"}'
        print "req cookie:", session.cookies
        response = session.post(FORWARD_URL + '/user/login', data=data)
        print "rep cookie:", session.cookies
        print(response.text)

    def test_3_logout(self):
        print "\n----------test_3_logout----------"
        data = '{}'
        response = session.post(FORWARD_URL + '/user/logout', data=data)
        print(response.text)

    def test_4_login_unexist(self):
        print "\n-----test_4_login_unexist----------"
        data = '{"mode":2, "phone":"15812347777", "password":"123456", "dev":"IMEI123456"}'
        print "req cookie:", session.cookies
        response = session.post(FORWARD_URL + '/user/login', data=data)
        print "rep cookie:", session.cookies
        print(response.text)

    def test_5_login_3rd_exist(self):
        print "\n-----test_5_login_3rd_exist----------"
        data = '{"mode":4, "openID":"qq123456789abcd", "dev":"IMEI123456"}'
        print "req cookie:", session.cookies
        response = session.post(FORWARD_URL + '/user/loginex', data=data)
        print "rep cookie:", session.cookies
        print(response.text)

    def test_6_generate_phone_verify_code(self):
        print "\n-----test_6_generate_phone_verify_code----------"
        data = '{"phone":"15855193773"}'
        response = session.post(FORWARD_URL + '/user/gencode', data=data)
        print(response.text)

    def test_7_verify_phone_code(self):
        print "\n-----test_7_verify_phone_code----------"
        data = '{"phone":"15855193773", "code":"568427"}'
        response = session.post(FORWARD_URL + '/user/vercode', data=data)
        print(response.text)

    def test_8_reset_password(self):
        print "\n-----test_8_reset_password----------"
        data = '{"phone":"15812345677", "password":"111222"}'
        response = session.post(FORWARD_URL + '/user/resetpw', data=data)
        print(response.text)


class Personal(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_1_query_personal_info(self):
        print "\n-----test_1_query_personal_info----------"
        response = session.get(FORWARD_URL + '/user/info')
        print(response.text)

    def test_2_modify_personal_info_name(self):
        print "\n-----test_2_modify_personal_info_name----------"
        data = '{"attr":1, "name":"mmxu1"}'
        response = session.post(FORWARD_URL + '/user/info', data=data)
        print(response.text)

    def test_3_modify_personal_info_portrait(self):
        print "\n-----test_3_modify_personal_info_portrait----------"
        data = '{"attr":2, "portrait":"/mmx/image/portrait/mmxu1.jpg"}'
        response = session.post(FORWARD_URL + '/user/info', data=data)
        print(response.text)

    def test_4_modify_personal_info_gender(self):
        print "\n-----test_4_modify_personal_info_gender----------"
        data = '{"attr":3, "gender":1}'
        response = session.post(FORWARD_URL + '/user/info', data=data)
        print(response.text)

    def test_5_modify_personal_info_city(self):
        print "\n-----test_5_modify_personal_info_city----------"
        data = '{"attr":4, "city":12345678}'
        response = session.post(FORWARD_URL + '/user/info', data=data)
        print(response.text)

    def test_6_query_user_address(self):
        print "\n-----test_6_query_user_address----------"
        response = session.get(FORWARD_URL + '/user/address')
        print(response.text)

    def test_7_modify_user_address(self):
        print "\n-----test_7_modify_user_address----------"
        data = '{"addrID":9, "name":"zhangsan", "phone":"13611112222", "address":"huangshanglufeixilu"}'
        response = session.post(FORWARD_URL + '/user/address', data=data)
        print(response.text)

    def test_8_add_user_address(self):
        print "\n-----test_8_add_user_address----------"
        data = '{"name":"zhangsan", "phone":"13611113333", "address":"huangshanglufeixilu", "postcode":"230031"}'
        response = session.put(FORWARD_URL + '/user/address', data=data)
        print(response.text)

    def test_9_delete_user_address(self):
        print "\n-----test_9_delete_user_address----------"
        data = '{"addrID":10}'
        response = session.delete(FORWARD_URL + '/user/address', data=data)
        print(response.text)


class Shopping(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_1_query_recommend(self):
        print "\n-----test_1_query_recommend----------"
        response = session.get(FORWARD_URL + '/user/shop/recommend?city=111')
        print(response.text)

    def test_2_query_shops_by_category(self):
        print "\n-----test_2_query_shops_by_categorys----------"
        response = session.get(FORWARD_URL + '/user/shop?category=123&city=1&long=123.45&lat=35.55&offset=0&count=5')
        print(response.text)

    def test_3_query_shop_name(self):
        print "\n-----test_3_query_shop_name----------"
        response = session.get(FORWARD_URL + '/user/shop/name?sid=10061')
        print(response.text)

    def test_4_visit_shop(self):
        print "\n-----test_4_visit_shop----------"
        response = session.post(FORWARD_URL + '/user/shop/enter?sid=10061')
        print(response.text)

    def test_5_query_goods_by_shop(self):
        print "\n----test_5_query_goods_by_shop---------"
        response = session.get(FORWARD_URL + '/user/goods?sid=10061&offset=0&count=5')
        print(response.text)

    def test_6_query_activity(self):
        print "\n----test_6_query_activity---------"
        response = session.get(FORWARD_URL + '/user/shop/activity?sid=10061')
        print(response.text)

    def test_7_query_shop_info(self):
        print "\n----test_7_query_shop_info---------"
        response = session.get(FORWARD_URL + '/user/shop/info?sid=10061')
        print(response.text)

    def test_8_query_goods_detail(self):
        print "\n----test_8_query_goods_detail---------"
        response = session.get(FORWARD_URL + '/user/goods/info?gid=1')
        print(response.text)

    def test_9_query_customer_fitting(self):
        print "\n----test_9_query_customer_fitting---------"
        response = session.get(FORWARD_URL + '/user/goods/fit?gid=1&offset=1&count=3')
        print(response.text)

    def test_10_query_matched_shaker(self):
        print "\n----test_10_query_matched_shaker---------"
        response = session.get(FORWARD_URL + '/user/shaker')
        print(response.text)

    def test_11_query_visited_shops(self):
        print "\n----test_11_query_visited_shops---------"
        response = session.get(FORWARD_URL + '/user/shop/visit?time=1431399663&direct=2&count=5')
        print(response.text)

    def test_12_query_category(self):
        print "\n-----test_12_query_category----------"
        response = session.get(FORWARD_URL + '/user/category')
        print(response.text)

    def test_13_search_shops_by_name(self):
        print "\n-----test_13_search_shops_by_name----------"
        HS = u'黄山'
        response = session.get(
            FORWARD_URL + '/user/shop/search?name=' + HS + '&city=1048577&long=123.45&lat=35.55&offset=0&count=5')
        print(response.text)


class Friend(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_1_query_friends_difference(self):
        print "\n----test_1_query_friends_difference---------"
        data = '{"frdIDs":[10041,10042,10045]}'
        response = session.post(FORWARD_URL + '/user/friend/diff', data=data)
        print(response.text)

    def test_2_query_friend_info(self):
        print "\n----test_2_query_friend_info---------"
        response = session.get(FORWARD_URL + '/user/friend?uid=10040&uid=10041')
        print(response.text)

    def test_3_modify_friend_remark_name(self):
        print "\n----test_3_modify_friend_remark_name---------"
        data = '{"frdID":10041, "rmkName":"mmoo"}'
        response = session.post(FORWARD_URL + '/user/friend/name', data=data)
        print(response.text)

    def test_4_query_friend_private_setting(self):
        print "\n----test_4_query_friend_private_setting---------"
        response = session.get(FORWARD_URL + '/user/friend/private?uid=10040')
        print(response.text)

    def test_5_query_friend_favorite_goods(self):
        print "\n----test_5_query_friend_favorite_goods---------"
        response = session.get(FORWARD_URL + '/user/friend/favorite?uid=10040&offset=3&count=3')
        print(response.text)

    def test_6_query_friend_fans_shop(self):
        print "\n----test_6_query_friend_fans_shop---------"
        response = session.get(FORWARD_URL + '/user/friend/fans?uid=10040&offset=3&count=3')
        print(response.text)

    def test_7_query_friend_visited_shop(self):
        print "\n----test_7_query_friend_visited_shop---------"
        response = session.get(FORWARD_URL + '/user/friend/visit?uid=10040&offset=0&count=3')
        print(response.text)

    def test_8_invite_adding_friend(self):
        print "\n----test_8_invite_adding_friend---------"
        data = '{"mode":3, "userID":10050, "remark":"i am mick"}'
        response = session.post(FORWARD_URL + '/user/friend/invite', data=data)
        print(response.text)

    def test_9_accept_adding_friend(self):
        print "\n----test_9_accept_adding_friend---------"
        response = session.post(FORWARD_URL + '/user/friend/accept?uid=10050')
        print(response.text)

    def test_10_query_user_info(self):
        print "\n----test_10_query_user_info---------"
        response = session.get(FORWARD_URL + '/user/info?uid=10040')
        print(response.text)


class Fans(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_1_query_fans_shop_difference(self):
        print "\n----test_1_query_fans_shop_difference---------"
        data = '{"shopIDs":[10023,10024,10060]}'
        response = session.post(FORWARD_URL + '/user/fans/diff', data=data)
        print(response.text)

    def test_2_query_fans_shop_info(self):
        print "\n----test_2_query_fans_shop_info---------"
        response = session.get(FORWARD_URL + '/user/fans/info?sid=10061&sid=10123')
        print(response.text)

    def test_3_query_fans_shop_news(self):
        print "\n----test_3_query_fans_shop_news---------"
        response = session.get(FORWARD_URL + '/user/fans/news?sid=10061&sid=10123')
        print(response.text)

    def test_4_concern_shop(self):
        print "\n----test_4_concern_shop---------"
        response = session.post(FORWARD_URL + '/user/shop/concern?sid=10060')
        print(response.text)

    def test_5_unconcern_shop(self):
        print "\n----test_5_unconcern_shop---------"
        response = session.delete(FORWARD_URL + '/user/shop/concern?sid=10060')
        print(response.text)


class Favorite(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_1_query_favorite_difference(self):
        print "\n----test_1_query_favorite_difference---------"
        data = '{"goodsIDs":[1,3,5]}'
        response = session.post(FORWARD_URL + '/user/favorite/diff', data=data)
        print(response.text)

    def test_2_query_favorite_info(self):
        print "\n----test_2_query_favorite_info---------"
        response = session.get(FORWARD_URL + '/user/favorite/info?gid=1&gid=2')
        print(response.text)

    def test_3_concern_goods(self):
        print "\n----test_3_concern_goods---------"
        response = session.post(FORWARD_URL + '/user/goods/concern?gid=5')
        print(response.text)

    def test_4_unconcern_goods(self):
        print "\n----test_4_unconcern_goods---------"
        response = session.delete(FORWARD_URL + '/user/goods/concern?gid=5')
        print(response.text)

    def test_5_query_goods_promotion(self):
        print "\n----test_5_query_goods_promotion---------"
        response = session.get(FORWARD_URL + '/user/goods/promot?gid=1&gid=2')
        print(response.text)


class Setting(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        session.close()

    def test_1_query_support_city(self):
        print "\n----test_1_query_support_city---------"
        response = session.get(FORWARD_URL + '/user/city')
        print(response.text)

    def test_2_query_private_setting(self):
        print "\n----test_2_query_private_setting---------"
        response = session.get(FORWARD_URL + '/user/setting/private')
        print(response.text)

    def test_3_modify_private_setting(self):
        print "\n----test_3_modify_private_setting---------"
        data = '{"favoriteEnable":1, "fansEnable":0, "visitEnable":0}'
        response = session.post(FORWARD_URL + '/user/setting/private', data=data)
        print(response.text)

    def test_4_modify_message_setting(self):
        print "\n----test_4_modify_message_setting---------"
        data = '{"shopID":10061, "msgEnable":0}'
        response = session.post(FORWARD_URL + '/user/setting/message', data=data)
        print(response.text)

    def test_5_feedback(self):
        print "\n----test_5_feedback---------"
        data = '{"feedback":"miaomiaoxiong is a very good product"}'
        response = session.post(FORWARD_URL + '/user/feedback', data=data)
        print(response.text)

    def test_6_query_latest_version(self):
        print "\n----test_6_query_latest_version---------"
        response = session.get(FORWARD_URL + '/user/version?sys=1')
        print(response.text)

    def test_7(self):
        import requests
        import json
        session = requests.session()
        data = '{"mode":2, "phone":"18756967287", "password":"96e79218965eb72c92a549dd5a330112", "dev":"IMEI123456", "type":4}'
        response = session.post('http://localhost:8887/user/login', data=data)
        print(response.text)
        response = session.delete('http://localhost:8887/user/friend/delete', params={'uid': 10003})
        print(response.text)


if __name__ == '__main__':
    unittest.main()

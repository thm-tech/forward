# -*- encoding: utf-8 -*-
import hashlib
import json
import os
import random
import re

import requests
from tornado.template import Loader
from tornado.escape import url_unescape

from forward.common.send_message import send_invite_friend_download_app
from forward.modules.cache.base import cache
from forward.common.tools import tornado_route, tornado_argument, tornado_argument_json
from forward.modules.user.db_user_web import *
from forward.modules.user.db_personal import DBPersonal
from forward.common.define import OSS_URL_PRIFIX
from forward.config import CONFIG
from forward.modules.user.db_passport import DBPassport
from forward.httpbase import HttpBaseHandler


__author__ = 'Mohanson'

urls = []

loader = Loader(os.path.join(CONFIG.PROJECT_PATH, 'modules', 'user'))
dbpassport = DBPassport()


@tornado_route(r'/userweb/(\w+)/friends', urls)
class CustomerHandler(HttpBaseHandler):
    def get(self, user_id):
        friends = get_user_friends_by_initial_words(user_id)
        self.write(friends)


@tornado_route(r'/userweb/(\w+)/favorites', urls)
class Favorites(HttpBaseHandler):
    @tornado_argument('_offset', '_limit')
    def get(self, user_id):
        goods = get_user_favorite_goods(user_id=user_id, offset=int(self.arg.offset), limit=int(self.arg.limit))
        self.write(goods)


@tornado_route(r'/userweb/shopgoods/(.*)', urls)
class UWShopGoods(HttpBaseHandler):
    @cache(3600)
    @tornado_argument('count')
    def get(self, shop_ids):
        if self.arg.count:
            count = int(self.arg.count)
        else:
            count = 6
        ret = get_goods_by_shops(shop_ids, 0, count)
        self.write(ret)


@tornado_route(r'/userweb/search/(.*)', urls)
class UsersSearch(HttpBaseHandler):
    def get(self, num):
        try:
            ret = get_user_info_by_miumiu_or_phone(str(num))
        except Exception, e:
            self.write({'is_success': False, 'des': str(e)})
        else:
            self.write(ret)


@tornado_route(r'/userweb/(.*)/friend/remark', urls)
class FriendRemark(HttpBaseHandler):
    def get(self):
        pass

    @tornado_argument_json('_friend_id', '_remark')
    def post(self, user_id):
        r = modify_friend_remark(user_id, self.arg.friend_id, self.arg.remark)
        self.write(r)


@tornado_route(r'/userweb/qqinfo/(\w+)', urls)
class QQInfoHandler(HttpBaseHandler):
    def get(self, access_token):
        # get open_id
        r = requests.get(r'https://graph.qq.com/oauth2.0/me', params={
            'access_token': access_token
        }).text
        rule = re.compile(r'"client_id":"(?P<client_id>\d+)","openid":"(?P<openid>(\w+))"')
        client_id = rule.search(r).group('client_id')
        openid = rule.search(r).group('openid')
        r = requests.post(r'https://graph.qq.com/user/get_user_info', {
            'access_token': access_token,
            'oauth_consumer_key': CONFIG.THIRDLOGIN.QQ_APP_KEY,
            'openid': openid,
            'format': 'json'
        }).text
        self.write(r)


@tornado_route(r'/userweb/weiboinfo/(\w+)', urls)
class WeiboInfoHandler(HttpBaseHandler):
    def get(self, code):
        r = requests.post(r'https://api.weibo.com/oauth2/access_token', {
            'client_id': CONFIG.THIRDLOGIN.WEIBO_APP_KEY,
            'client_secret': CONFIG.THIRDLOGIN.WEIBO_APP_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://www.immbear.com'
        }).text
        r = json.loads(r)
        access_token = r['access_token']
        uid = r['uid']
        # print(access_token, uid)
        r = requests.get(r'https://api.weibo.com/2/users/show.json', {
            'access_token': access_token,
            'uid': uid
        }).text
        self.write(r)


@tornado_route(r'/user/goods/promot/news', urls)
class GoodsNewsHandler(HttpBaseHandler):
    def get(self):
        gids = self.get_arguments('gid')
        r = query_favorite_goods_news(gids)
        self.write(r)


@tornado_route(r'/userweb/activity/(.*)', urls)
class ActivityInfoHandler(HttpBaseHandler):
    def get(self, act_id):
        info = get_activity_info(act_id)
        self.write(info)


@tornado_route(r'/userweb/imgupload', urls)
class ImageUploadHandler(HttpBaseHandler):
    @tornado_argument('_url')
    def get(self):
        pic_content = requests.get(self.arg.url).content
        h = b'-----------------------------311092004222736\r\nContent-Disposition: form-data; name="file"; filename="logo1.png"\r\nContent-Type: image/png\r\n\r\n'
        f = b'\r\n-----------------------------297391254920134--\r\n'
        try:
            r = requests.post(CONFIG.FD_CHAT_SERVER + '/file/uploader', data=h + pic_content + f)
            j = json.loads(r.text)
            self.write({'is_success': True, 'url': OSS_URL_PRIFIX + '/' + j['md5'] + '.png'})
        except Exception as e:
            self.write({'is_success': False, 'err': str(e)})


@tornado_route(r'/userweb/quickmodifyimg', urls)
class QuickImageHandler(HttpBaseHandler):
    @tornado_argument_json('_user_id', '_url')
    def put(self):
        pic_content = requests.get(url_unescape(self.arg.url)).content
        h = b'-----------------------------311092004222736\r\nContent-Disposition: form-data; name="file"; filename="logo1.png"\r\nContent-Type: image/png\r\n\r\n'
        f = b'\r\n-----------------------------297391254920134--\r\n'
        try:
            response = requests.post(CONFIG.FD_CHAT_SERVER + '/file/uploader', data=h + pic_content + f)
            j = json.loads(response.text)
            img = j['md5'] + '.png'
            r = DBPersonal().modifyPersonalInfo(self.arg.user_id, 2, None, img, None, None)
            self.write({'is_success': r, 'url': img})
        except Exception as e:
            self.write({'is_success': False, 'err': str(e)})


@tornado_route(r'/userweb/qq/logincallback', urls)
class QQLoginCallBack(HttpBaseHandler):
    def get(self):
        self.write(loader.load('qqlogin.html').generate())


@tornado_route(r'/userweb/qq/openid', urls)
class QQLoginOpenId(HttpBaseHandler):
    @tornado_argument('_access_token')
    def get(self):
        # http_client = httpclient.HTTPClient()
        # try:
        # response = http_client.fetch("https://graph.qq.com/oauth2.0/me?access_token=%s" % self.arg.access_token)
        # print(response.body)
        # except httpclient.HTTPError as e:
        # print("Error: " + str(e))
        # except Exception as e:
        # print("Error: " + str(e))
        # http_client.close()

        # get open_id, client_id
        response = requests.get('https://graph.qq.com/oauth2.0/me', params={'access_token': self.arg.access_token},
                                verify=False).text
        rule1 = re.compile('"client_id":"(?P<client_id>\w+)"')
        rule2 = re.compile('"openid":"(?P<openid>\w+)"')
        client_id = rule1.search(response).group('client_id')
        open_id = rule2.search(response).group('openid')
        self.write({
            'client_id': client_id,
            'open_id': open_id
        })


@tornado_route(r'/userweb/qq/userinfo', urls)
class QQLoginUserInfo(HttpBaseHandler):
    @tornado_argument('_access_token', '_openid')
    def get(self):
        # https://graph.qq.com/user/get_user_info?access_token=YOUR_ACCESS_TOKEN&oauth_consumer_key=YOUR_APP_ID&openid=YOUR_OPENID
        response = requests.get('https://graph.qq.com/user/get_user_info', params={
            'access_token': self.arg.access_token,
            'oauth_consumer_key': CONFIG.THIRDLOGIN.QQ_APP_KEY,
            'openid': self.arg.openid
        }, verify=False).text
        self.write(json.loads(response))


@tornado_route(r'/userweb/selectphones', urls)
class PhoneTypeList(HttpBaseHandler):
    @tornado_argument_json('_phone', '_phone_list')
    def post(self):
        response = select_phone_type_list(self.arg.phone, self.arg.phone_list)
        self.write(response)


@tornado_route(r'/userweb/sendinvite', urls)
class SendInviteHandler(HttpBaseHandler):
    @tornado_argument_json('_phone', '_name', '_remark')
    def post(self):
        response = send_invite_friend_download_app(self.arg.phone, self.arg.name.encode('utf-8'),
                                                   self.arg.remark.encode('utf-8'),
                                                   'http://www.immbear.com')
        self.write(response)


@tornado_route(r'/userweb/sendinvite2', urls)
class SendInviteHandler2(HttpBaseHandler):
    # 对方手机号码, remark=对
    @tornado_argument_json('_phone', 'name', 'remark')
    def post(self):
        password = str(int(random.random() * 1000)) + '000'
        response = dbpassport.register(self.arg.phone, hashlib.md5(password).hexdigest())
        if response > 0:
            self.write(
                {'des': '推荐一款好玩的app, %s, 用你的手机号登陆就好啦, 密码是 %s' % ('http://www.immbear.com/#/index/download', password)})
        else:
            self.write({'error': 'phone account has already exist!'})


@tornado_route(r'/userweb/account/(\d+)', urls)
class AccountHandler(HttpBaseHandler):
    def get(self, id):
        self.write(get_account_info(id))


@tornado_route(r'/user/(\d+)/info', urls)
class UserInfoScanHandler(HttpBaseHandler):
    def get(self, user_id):
        uids = self.get_arguments('uid')
        self.write(get_user_info_and_relationship(user_id, uids))
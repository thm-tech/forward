# -*- coding: utf-8 -*-

import requests

from forward.common.tools import tornado_route, tornado_argument
from forward.config import CONFIG
from forward.httpbase import HttpBaseHandler

urls = []


@tornado_route(r'/thirdlogin/wechat', urls)
class WeChatHandler(HttpBaseHandler):
    @tornado_argument('_code')
    def get(self):
        response = requests.get(
            "https://api.weixin.qq.com/sns/oauth2/access_token?appid=" + CONFIG.THIRDLOGIN.WECHAT_APP_KEY + "&secret=" + CONFIG.THIRDLOGIN.WECHAT_APP_SECRET + "&code=" + self.arg.code + "&grant_type=authorization_code")
        self.write(response.text)

@tornado_route(r'/thirdlogin/wechat/info', urls)
class WeChatInfoHandler(HttpBaseHandler):
    @tornado_argument('_access_token', '_openid')
    def get(self):
        response = requests.get(
            'https://api.weixin.qq.com/sns/userinfo', params=dict(access_token=self.arg.access_token, openid=self.arg.openid)
        )
        self.write(response.content)
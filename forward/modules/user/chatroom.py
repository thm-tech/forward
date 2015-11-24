# -*- coding:utf8 -*-

from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.gen import coroutine
from forward.api.chat_api import *
import json
from forward.config import CONFIG

class ChatRoom(object):
    def __init__(self):
        pass

    @coroutine
    def visitRoom(self, shop_id, user_id, out_dict):
        url = CONFIG.FD_CHAT_SERVER + "/chat/user/" + str(user_id) + "/shop/" + str(shop_id)

        request = HTTPRequest(url, "POST")
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        out_dict["is_success"] = is_success
        return 

    @coroutine
    def exitRoom(self, shop_id, user_id, out_dict):
        url = CONFIG.FD_CHAT_SERVER + "/chat/user/" + str(user_id) + "/shop/" + str(shop_id)

        request = HTTPRequest(url, "DELETE")
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        out_dict["is_success"] = is_success
        return 

    @coroutine
    def getRoomUserCount(self, shop_id, out_dict):
        url = CONFIG.FD_CHAT_SERVER + "/chat/shop/" + str(shop_id) + "/userstotalnum"

        request = HTTPRequest(url, "GET")
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        if is_success:
            out_dict["num"] = rep_json["total_num"]
        else:
            out_dict["num"] = -1
        return

    @coroutine
    def getRoomUserList(self, shop_id, out_dict):
        url = CONFIG.FD_CHAT_SERVER + "/chat/shop/" + str(shop_id) + "/userslist"

        request = HTTPRequest(url, "GET")
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        if is_success:
            out_dict["users"] = rep_json["users"]
        else:
            out_dict["users"] = None
        return

    @coroutine
    def getRoomInfo(self, shop_id, out_dict):
        url = CONFIG.FD_CHAT_SERVER + "/chat/shop/" + str(shop_id) + "/users"

        request = HTTPRequest(url, "GET")
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        if is_success:            
            out_dict["num"] = rep_json["total_num"]
            out_dict["users"] = rep_json["users"]            
        else:
            out_dict = None
        return


#-*- coding:utf8 -*-

import json
from tornado.web import authenticated
from forward.httpbase import HttpBaseHandler
from define import * 
from forward.common.tools import *
from forward.api.chat_api import *
from forward.log import user_log

class ChatQueryRoomUserCountHandler(HttpBaseHandler):
    def get(self):
        user_log.info("ChatQueryRoomUserCount GET.")

        shop_id_list = self.get_arguments("shop_id")

        shop_dict = {}
        for shop_id in shop_id_list:
            shop_dict[shop_id] = 10
            
        rep_json = {}
        rep_json["is_success"] = True 
        rep_json["shop_dict"] = shop_dict
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class ChatInviteBeFriendHandler(HttpBaseHandler):
    def post(self):
        user_log.info("ChatInviteBeFriendHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)

        from_user_id = req_json["from_user_id"]
        from_user_name = req_json["from_user_name"]
        from_user_portrait = req_json["from_user_portrait"]
        remark = req_json["remark"]
        to_user_id = req_json["to_user_id"]
        

        rep_json = {}
        rep_json["is_success"] = True 
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

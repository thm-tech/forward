# -*- coding:utf8 -*-

import json
from datetime import *
import time
from tornado.web import authenticated
from forward.httpbase import HttpBaseHandler
from forward.common.tools import *
from error import *
from define import * 
from db_setting import *
from forward.log import user_log
dao = DBSetting()

class QuerySupportCityHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QuerySupportCityHandler GET.")

        city_list = dao.querySupportCityList()
        if city_list is None:
            user_log.error("Query support city list failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_SUPPORT_CITY_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["cityList"] = city_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class PrivateSettingHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("PrivateSettingHandler GET.")
        
        user_id = self.get_current_user()

        setting = dao.queryPrivateSetting(user_id)
        if setting is None:
            user_log.error("Query private setting failed! User id: %s", user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_PRIVATE_SETTING_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["setting"] = setting
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

    @authenticated
    def post(self):
        user_log.info("PrivateSettingHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["favoriteEnable", "fansEnable", "visitEnable"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            req_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(req_json, cls=ExtendedJsonEncoder))
            return

        favorite_enable = req_json["favoriteEnable"]
        fans_enable = req_json["fansEnable"]
        visit_enable = req_json["visitEnable"]

        user_id = self.get_current_user()

        if True != dao.modifyPrivateSetting(user_id, favorite_enable, fans_enable, visit_enable):
            user_log.error("Modify private setting failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_MODIFY_PRIVATE_SETTING_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class MessageSettingHandler(HttpBaseHandler):
    @authenticated
    def post(self):
        user_log.info("MessageSettingHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["shopID", "msgEnable"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            req_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(req_json, cls=ExtendedJsonEncoder))
            return

        shop_id = req_json["shopID"]
        msg_enable = req_json["msgEnable"]

        user_id = self.get_current_user()

        if True != dao.modifyMessageSetting(user_id, shop_id, msg_enable):
            user_log.error("Modify message setting failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_MODIFY_MESSAGE_SETTING_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class FeedbackHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("FeedbackHandler GET.")
        
        offset = self.get_argument("offset", None)
        count = self.get_argument("count", None)
        if offset is None or count is None:
            user_log.error("Query feedback info protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        feed_list = dao.queryFeedbackListByPage(user_id, offset, count)
        if feed_list is None:
            user_log.error("Query feedback info failed! User id: %s", user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FEEDBACK_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["feedList"] = feed_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

    def post(self):
        user_log.info("FeedbackHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["feedback"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            req_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(req_json, cls=ExtendedJsonEncoder))
            return

        feedback = req_json["feedback"]

        user_id = self.get_current_user()

        if True != dao.feedback(user_id, feedback):
            user_log.error("Feedback failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_FEEDBACK_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class QueryLatestVersionHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QueryLatestVersionHandler GET.")

        system = self.get_argument("sys", None)
        if system is None:
            user_log.error("Query latest version protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        version = dao.queryLatestVersion(system)
        if version is None:
            user_log.error("Query latest version failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_LATEST_VERSION_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["version"] = version
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

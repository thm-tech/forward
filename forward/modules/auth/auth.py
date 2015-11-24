# -*-coding:utf-8-*-

from forward.httpbase import HttpBaseHandler
from forward.common.tools import *
from db import *
from error import *
from forward.log import auth_log
dao = DBManage()


class AuthenticateHandler(HttpBaseHandler):
    def get(self):
        pass

    def post(self):
        auth_log.info("AuthenticateHandler.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["mode", "type"]
        optional_args = ["account", "email", "phone", "password", "openID"]
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            auth_log.error("Authenticate protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_AUTH_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        auth_mode = int(req_json["mode"])
        acc_type = int(req_json["type"])
        account = req_json["account"]
        email = req_json["email"]
        phone = req_json["phone"]
        password = req_json["password"]
        open_id = req_json["openID"]

        acc_id = dao.authenticate(auth_mode, acc_type, account, email, phone, password, open_id)
        if acc_id is None:
            auth_log.error("Authenticate failed! Paras: %s", json_msg_str)
            rep_json = {}
            rep_json["err"] = FD_ERR_AUTH_AUTHENTICATE_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        if acc_id < 0:
            auth_log.error("Account is not existed! Paras: %s", json_msg_str)
            rep_json = {}
            rep_json["err"] = FD_ERR_AUTH_ACCOUNT_UNEXISTED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_AUTH_NOERR
        rep_json["accID"] = acc_id
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class Authenticate2Handler(HttpBaseHandler):
    def get(self):
        pass

    def post(self):
        auth_log.info("Authenticate2Handler.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["accID", "password"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            auth_log.error("Authenticate protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_AUTH_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        acc_id = req_json["accID"]
        password = req_json["password"]

        if True != dao.authenticate2(acc_id, password):
            auth_log.error("Authenticate failed! Paras: %s", json_msg_str)
            rep_json = {}
            rep_json["err"] = FD_ERR_AUTH_AUTHENTICATE_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_AUTH_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

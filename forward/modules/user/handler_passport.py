#-*- coding:utf8 -*-

import json
import time
from datetime import *
import random
from tornado.web import authenticated
from forward.httpbase import *
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from forward.common.tools import *
from forward.common.define import *
from db_passport import *
from error import *
from define import *
from tornado.gen import coroutine
from forward.modules.auth.error import *
from forward.config import CONFIG
from forward.log import user_log

from forward.common.validate.phone_validate import send_phone_captcha, validate_phone_captcha

dao = DBPassport()

class LoginHandler(LoginBaseHandler):
    
    @coroutine
    def post(self):
        user_log.info("LoginHandler POST.")

        request = HTTPRequest(CONFIG.AUTH_URL, "POST", body=self.request.body)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        err = rep_json["err"]
        if FD_AUTH_NOERR != err:
            body = {}
            body["err"] = FD_ERR_USER_LOGIN_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(body))
            return

        acc_id = rep_json["accID"]
        self.set_secure_cookie("id", str(acc_id))
        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        cur_login_dev = req_json["dev"]

        last_login_dev = dao.recordLoginDevice(acc_id, cur_login_dev)

        body = {}
        body["err"] = FD_USER_NOERR
        body["accID"] = acc_id
        body["dev"] = last_login_dev
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(body))
        return
        
class LoginExHandler(LoginBaseHandler):
    def get(self):
        pass
    
    @coroutine
    def post(self):
        user_log.info("LoginExHandler POST.")
        
        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        cur_login_dev = req_json["dev"]

        request = HTTPRequest(CONFIG.AUTH_URL, "POST", body=self.request.body)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        err = rep_json["err"]
        if FD_AUTH_NOERR == err:
            acc_id = rep_json["accID"]
            self.set_secure_cookie("id", str(acc_id))

            last_login_dev = dao.recordLoginDevice(acc_id, cur_login_dev)

            body = {}
            body["err"] = FD_USER_NOERR
            body["accID"] = acc_id
            body["isReg"] = 0
            body["dev"] = last_login_dev
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(body))
            return
        elif FD_ERR_AUTH_ACCOUNT_UNEXISTED:
            #Create account
            req_json = json.loads(self.request.body)
            log_mode = req_json["mode"]
            open_id = req_json["openID"]            
            acc_id = dao.registerEx(log_mode, open_id)
            if acc_id is None:
                body = {}
                body["err"] = FD_ERR_USER_LOGIN_FAILED
                self.set_header("Content-type", "application/json")
                self.write(json.dumps(body))
                return

            self.set_secure_cookie("id", str(acc_id))

            last_login_dev = dao.recordLoginDevice(acc_id, cur_login_dev)

            body = {}
            body["err"] = FD_USER_NOERR
            body["accID"] = acc_id
            body["isReg"] = 1
            body["dev"] = last_login_dev
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(body))
            return
        else:
            body = {}
            body["err"] = FD_ERR_USER_LOGIN_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(body))
            return

class LogoutHandler(HttpBaseHandler):
    def get(self):
        pass
   
    @authenticated
    def post(self):
        user_log.info("LogoutHandler POST.")

        acc_id = self.get_current_user()
        if acc_id is not None:
            self.clear_cookie("id")
        
        body = {}
        body["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(body))
        return


class RegisterHandler(HttpBaseHandler):
    def get(self):
        pass
    
    def post(self):
        user_log.info("RegisterHandler POST.")
       
        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["phone", "password"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Register protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        phone = req_json["phone"]
        password = req_json["password"]

        acc_id = dao.register(phone, password)
        err = FD_USER_NOERR
        if -1 == acc_id:
            err = FD_ERR_USER_ACCOUNT_EXISTED
        elif -2 == acc_id:
            err = FD_ERR_USER_REGISTER_FAILED

        if FD_USER_NOERR != err:
            user_log.error("Register failed! paras: %s", json_msg_str)
            rep_json = {}
            rep_json["err"] = err
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["accID"] = acc_id
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class GenerateCodeHandler(HttpBaseHandler):
    def get(self):
        pass
    
    def post(self):
        user_log.info("GenerateCodeHandler POST.")
        
        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["phone"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Generate code protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        phone = req_json["phone"]

        #Generate phone verify code
        code = random.randint(100000, 999999)
        deadline = datetime.now() + timedelta(hours=FD_PHONE_CODE_EXPIRE_TIME)
        if True != dao.savePhoneCode(phone, code, deadline):
            user_log.error("Save phone code failed! Phone: %s, code: %s", phone, code)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_GENERATE_PHONE_CODE_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        #Send verify code to phone 
        send_phone_captcha(phone)

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return
    
class VerifyCodeHandler(HttpBaseHandler):
    def get(self):
        pass
    
    def post(self):
        user_log.info("VerifyCodeHandler POST.")
        
        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["phone", "code"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Verify code protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        phone = req_json["phone"]
        code = req_json["code"]

        # now = datetime.now()
        # if True != dao.verifyPhoneCode(phone, code, now):
        #     user_log.error("Verify phone code failed! Phone: %s, code: %s", phone, code)
        #     rep_json = {}
        #     rep_json["err"] = FD_ERR_USER_VERIFY_PHONE_CODE_FAILED
        #     self.set_header("Content-type", "application/json")
        #     self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        #     return
        if not validate_phone_captcha(code, phone)['is_success']:
            user_log.error("Verify phone code failed! Phone: %s, code: %s", phone, code)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_VERIFY_PHONE_CODE_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class ResetPasswordHandler(HttpBaseHandler):
    def get(self):
        pass
    
    def post(self):
        user_log.info("ResetPasswordHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["phone", "password"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Reset password protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        phone = req_json["phone"]
        password = req_json["password"]

        if True != dao.resetPassword(phone, password):
            user_log.error("Reset password failed! Phone: %s", phone)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_RESET_PASSWORD_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class QueryLastLoginDeviceHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryLastLoginDeviceHandler GET.")
        
        acc_id = self.get_current_user()

        last_login_dev = dao.queryLastLoginDevice(acc_id)

        body = {}
        body["err"] = FD_USER_NOERR
        body["dev"] = last_login_dev
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(body))
        return

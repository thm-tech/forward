#-*-coding:utf-8-*-
import json
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.gen import coroutine
from define import *

"""
Authenticate server define
"""
FD_AUTH_SERVER = "http://115.28.143.67:9188"

"""
Auth url define
"""
FD_AUTH_URL_REGISTER = FD_AUTH_SERVER + "/auth/register"
FD_AUTH_URL_LOGIN = FD_AUTH_SERVER + "/auth/login"
FD_AUTH_URL_AUTHENTICATE = FD_AUTH_SERVER + "/auth/auth"
FD_AUTH_URL_LOGOUT = FD_AUTH_SERVER + "/auth/logout"
FD_AUTH_URL_GENERATECODE = FD_AUTH_SERVER + "/auth/gencode"
FD_AUTH_URL_VERIFYCODE = FD_AUTH_SERVER + "/auth/vercode"
FD_AUTH_URL_RESETPASSWORD = FD_AUTH_SERVER + "/auth/resetpw"

class Auth(object):
    def __init__(self):
        pass

    @coroutine
    def register(self, register_callback, caller, acc_type, reg_mode, account=None, email=None, phone=None, code=None, password=None):
        url = FD_AUTH_SERVER + "/auth/register"
        body = {}
        body["accType"] =acc_type
        body["regMode"] = reg_mode
        body["account"] = account
        body["email"] = email
        body["phone"] = phone
        body["code"] = code
        body["password"] = password
        body_json = json.dumps(body)
        request = HTTPRequest(url, "POST", body=body_json)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        err = rep_json["err"]
        if 0 == err:
            if rep_json["accID"] is not None:
                register_callback(rep_json["accID"], caller)
                return
        register_callback(None, caller)

    @coroutine
    def login(self, login_callback, caller, log_mode, account=None, email=None, phone=None, password=None, open_id=None):
        url = FD_AUTH_SERVER + "/auth/login"
        body = {}
        body["logMode"] = log_mode
        body["account"] = account
        body["email"] = email
        body["phone"] = phone
        body["password"] = password
        body["openID"] = open_id
        body_json = json.dumps(body)
        request = HTTPRequest(url, "POST", body=body_json)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.load(response.body)
        err = rep_json["err"]
        if 0 == err:
            if rep_json["accID"] is not None:
                login_callback(rep_json["accID"], caller)
                return
        login_callback(None, caller)

    @coroutine
    def auth(self, auth_callback, caller, auth_mode, account=None, email=None, phone=None, password=None, open_id=None):
        url = FD_AUTH_SERVER + "/auth/auth"
        body = {}
        body["authMode"] = auth_mode
        body["account"] = account
        body["email"] = email
        body["phone"] = phone
        body["password"] = password
        body["openID"] = open_id
        body_json = json.dumps(body)
        request = HTTPRequest(url, "POST", body=body_json)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.load(response.body)
        err = rep_json["err"]
        if 0 == err:
            if rep_json["accID"] is not None:
                auth_callback(rep_json["accID"], caller)
                return
        auth_callback(None, caller)

    @coroutine
    def logout(self, logout_callback, caller, acc_id):
        url = FD_AUTH_SERVER + "/auth/logout"
        body = {}
        body["accID"] = acc_id
        body_json = json.dumps(body)
        request = HTTPRequest(url, "POST", body=body_json)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.load(response.body)
        err = rep_json["err"]
        if 0 == err:
            logout_callback(True, caller)
            return
        logout_callback(False, caller)

    @coroutine
    def gencode(self, gencode_callback, caller, phone):
        url = FD_AUTH_SERVER + "/auth/gencode"
        body = {}
        body["phone"] = phone
        body_json = json.dumps(body)
        request = HTTPRequest(url, "POST", body=body_json)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.load(response.body)
        err = rep_json["err"]
        if 0 == err:
            gencode_callback(True, caller)
            return
        gencode_callback(False, caller)

    @coroutine
    def vercode(self, vercode_callback, caller, phone, code):
        url = FD_AUTH_SERVER + "/auth/vercode"
        body = {}
        body["phone"] = phone
        body["code"] = code
        body_json = json.dumps(body)
        request = HTTPRequest(url, "POST", body=body_json)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.load(response.body)
        err = rep_json["err"]
        if 0 == err:
            vercode_callback(True, caller)
            return
        vercode_callback(False, caller)

    @coroutine
    def resetpw(self, resetpw_callback, caller, phone, password):
        url = FD_AUTH_SERVER + "/auth/resetpw"
        body = {}
        body["phone"] = phone
        body["password"] = password
        body_json = json.dumps(body)
        request = HTTPRequest(url, "POST", body=body_json)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.load(response.body)
        err = rep_json["err"]
        if 0 == err:
            resetpw_callback(True, caller)
            return
        resetpw_callback(False, caller)

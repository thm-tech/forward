#-*- coding:utf8 -*-

import json
import time
from tornado.web import authenticated
from forward.httpbase import HttpBaseHandler
from forward.common.tools import *
from forward.common.auth import *
from db_personal import *
from error import *
from define import *
from forward.log import user_log

dao = DBPersonal()

class PersonalInfoHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("PersonalInfoHandler GET.")
        
        acc_id = self.get_current_user()

        info = dao.queryPersonalInfo(acc_id)
        if info is None:
            user_log.error("Query personal info failed! Account id: %s", acc_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_PERSONAL_INFO_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["info"] = info
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return
    
    @authenticated
    def post(self):
        user_log.info("InfoHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["attr"]
        optional_args = ["name", "portrait", "gender", "city"]
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Modify personal info protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        attr = req_json["attr"]
        name = req_json["name"]
        portrait = req_json["portrait"]
        if portrait and portrait.startswith(OSS_URL_PRIFIX):
            portrait = portrait[len(OSS_URL_PRIFIX):]
        gender = req_json["gender"]
        city = req_json["city"]
        
        acc_id = self.get_current_user()

        if True != dao.modifyPersonalInfo(acc_id, attr, name, portrait, gender, city):
            user_log.error("Modify personal info failed! Account id: %s, attr: %s", acc_id, attr)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_MODIFY_PERSONAL_INFO_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class AddressHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("AddressHandler GET.")
        
        acc_id = self.get_current_user()

        addr_list = dao.queryAddress(acc_id)
        if addr_list is None:
            user_log.error("Query address info failed! Account id: %s", acc_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_ADDRESS_INFO_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["addressList"] = addr_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return
    
    @authenticated
    def post(self):
        user_log.info("AddressHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["addrID"]
        optional_args = ["name", "phone", "address", "postcode", "province_id", "city_id"]
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Modify address info protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        addr_id = req_json["addrID"]
        name = req_json["name"]
        phone = req_json["phone"]
        address = req_json["address"]
        # print(address, type(address))
        postcode = req_json["postcode"]
        province_id = req_json["province_id"]
        city_id = req_json["city_id"]
        
        acc_id = self.get_current_user()

        if True != dao.modifyAddress(acc_id, addr_id, name, phone, address, postcode, province_id, city_id):
            user_log.error("Modify address info failed! Account id: %s", acc_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_MODIFY_ADDRESS_INFO_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

    @authenticated
    def put(self):
        user_log.info("AddressHandler PUT.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["name", "phone", "address", "province_id", "city_id"]
        optional_args = ["postcode"]
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Modify address info protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        name = req_json["name"]
        phone = req_json["phone"]
        address = req_json["address"]
        postcode = req_json["postcode"]
        province_id = req_json["province_id"]
        city_id = req_json["city_id"]
        
        acc_id = self.get_current_user()

        addr_id = dao.addAddress(acc_id, name, phone, address, postcode, province_id, city_id)
        if addr_id is None:
            user_log.error("Add address info failed! Account id: %s", acc_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_ADD_ADDRESS_INFO_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["addrID"] = addr_id
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

    @authenticated
    def delete(self):
        user_log.info("AddressHandler DELETE.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["addrID"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Modify address info protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        addr_id = req_json["addrID"]
        
        acc_id = self.get_current_user()

        if True != dao.deleteAddress(acc_id, addr_id):
            user_log.error("Delete address info failed! Account id: %s", acc_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_DELETE_ADDRESS_INFO_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class BindPhoneHandler(HttpBaseHandler):
    def get(self):
        pass
   
    @authenticated
    def post(self):
        user_log.info("BindPhoneHandler.")
        
        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["phone"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Bind phone protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        phone = req_json["phone"]
        acc_id = self.get_current_user()

        if True != dao.bindPhone(acc_id, phone):
            user_log.error("Bind phone failed! Account id: %s, Phone: %s", acc_id, phone)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_BIND_PHONE_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class AddressDefaultSettingHandler(HttpBaseHandler):
    def get(self):
        pass
   
    @authenticated
    def post(self):
        user_log.info("AddressDefaultSettingHandler.")
        
        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["addrID"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Bind phone protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        addr_id = req_json["addrID"]
        user_id = self.get_current_user()

        if True != dao.setDefaultAddress(user_id, addr_id):
            user_log.error("Bind phone failed! Account id: %s, Phone: %s", acc_id, phone)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_SET_DEFAULT_ADDRESS_FAILED 
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
            
        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return



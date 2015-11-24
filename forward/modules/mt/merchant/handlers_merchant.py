# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import tornado.web

from forward.common.tools import tornado_argument_json, tornado_argument, tornado_route
from forward.modules.mt.merchant.db_merchant import *
from forward.httpbase import HttpBaseHandler
from forward.modules.mt.error_code import MTERROR
from forward.common.validate.phone_validate import send_phone_captcha, validate_phone_captcha
from forward.modules.mt.settings import ImageHost
from forward.log import mt_log

urls = []


@tornado_route(r'/merchants', urls)
class MerchantsHandler(HttpBaseHandler):
    @tornado_argument_json('_account', '_password')
    def post(self):
        if len(self.arg.password) != 16 and len(self.arg.password) != 32:
            self.write(dict(error_code=MTERROR.PasswordCheckError.code, des=MTERROR.PasswordCheckError.des))
            return
        response = sign_newaccount(self.arg.account, self.arg.password)
        self.write(response)


@tornado_route(r'/merchant/(.*)/info', urls)
class MerchantInfoHandler(HttpBaseHandler):
    def get(self, shop_id):
        response = get_merchant_basicinfo(shop_id)
        self.write(response)

    @tornado.web.authenticated
    @tornado_argument_json('contact_name', 'contact_phone_no', 'contact_email', 'contact_qq', 'portrait_url')
    def post(self, shop_id):
        response = modify_merchant_basicinfo(shop_id, self.arg.contact_name, self.arg.contact_phone_no,
                                             self.arg.contact_email, self.arg.contact_qq,
                                             self.arg.portrait_url[len(ImageHost):])
        self.write(response)


@tornado_route(r'/merchant/(\d*)/serviceinfo', urls)
class MerchantServiceInfoHandler(HttpBaseHandler):
    def get(self, shop_id):
        response = get_merchant_serviceinfo(shop_id)
        self.write(response)


@tornado_route(r'/merchant/isexist', urls)
class MerchantIsExistHandler(HttpBaseHandler):
    @tornado_argument('_account')
    def get(self):
        response = is_merchant_exist(self.arg.account)
        self.write(response)


@tornado_route(r'/merchant', urls)
class MerchantHandler(HttpBaseHandler):
    @tornado_argument_json('_account', '_password', 'contact_name', 'contact_phone_no', 'contact_email', 'contact_qq',
                           '_shop_name', 'brand_name', 'business_hours', 'telephone_no', '_city_id',
                           'district_id', 'business_area', 'address', 'longitude', 'latitude',
                           '_category_list')
    def post(self):
        mt_log.info(str(self.__class__) + str(self.arg))
        if len(self.arg.password) != 16 and len(self.arg.password) != 32:
            self.write(dict(error_code=MTERROR.PasswordCheckError.code, des=MTERROR.PasswordCheckError.des))
            return
        # exchange contact_phone_no and telephone_no
        response = sign_merchant(account=self.arg.account, password=self.arg.password,
                                 contact_name=self.arg.contact_name,
                                 contact_phone_no=self.arg.telephone_no, contact_email=self.arg.contact_email,
                                 contact_qq=self.arg.contact_qq,
                                 shop_name=self.arg.shop_name, brand_name=self.arg.brand_name,
                                 business_hours=self.arg.business_hours,
                                 telephone_no=self.arg.contact_phone_no, city_id=self.arg.city_id,
                                 district_id=self.arg.district_id,
                                 business_area=self.arg.business_area, address=self.arg.address,
                                 longitude=self.arg.longitude,
                                 latitude=self.arg.latitude, category_list=self.arg.category_list
                                 )
        self.write(response)


@tornado_route(r'/merchant/(\d*)/password', urls)
class MerchantPasswordHandler(HttpBaseHandler):
    @tornado.web.authenticated
    @tornado_argument_json('_old_password', '_new_password')
    def put(self, shop_id):
        response = modify_merchant_password(shop_id=shop_id, old_password=self.arg.old_password,
                                            new_password=self.arg.new_password)
        self.write(response)


@tornado_route(r'/merchant/login', urls)
class LoginHandler(HttpBaseHandler):
    @tornado_argument_json('_account', '_password', 'type')
    def post(self):
        response = login(self.arg.account, self.arg.password)
        if response.get('is_success'):
            shop_id = str(int(response.get('shop_id')))
            self.set_secure_cookie('id', shop_id)
        else:
            pass
        self.write(response)


@tornado_route(r'/merchant/logout', urls)
class LogoutHandler(HttpBaseHandler):
    def get(self):
        self.clear_all_cookies()


@tornado_route(r'/merchant/(\d*)/msgconfig', urls)
class MsgConfigHandler(HttpBaseHandler):
    def get(self, shop_id):
        response = get_fansmessageconfig(shop_id=shop_id)
        self.write(response)

    @tornado.web.authenticated
    @tornado_argument_json('_type', '_cate')
    def put(self, shop_id):
        if self.arg.type == 'desc_remain':
            if self.arg.cate == 'p2p':
                response = desc_fansmessageconfig_p2p(shop_id)
                self.write(response)
            if self.arg.cate == 'mass':
                response = desc_fansmessageconfig_mass(shop_id)
                self.write(response)
        else:
            pass


@tornado_route(r'/merchant/forgetpassword', urls)
class ForgetPasswordHandler(HttpBaseHandler):
    @tornado_argument('_step', 'acc_or_pho', 'phone')
    def get(self):
        if self.arg.step == 'is_account_exist':
            if self.arg.acc_or_pho[0].isalpha():
                response = is_account_or_phone_exist(str=self.arg.acc_or_pho, type='account')
            else:
                response = is_account_or_phone_exist(str=self.arg.acc_or_pho, type='phone')
            # set_cookie
            if response['is_exist']:
                self.set_secure_cookie('step', '1')

            self.write(response)
        elif self.arg.step == 'get_phone_captcha':
            # get step cookie
            if self.get_secure_cookie('step') == '1':
                self.set_secure_cookie('step', '2')
                v = send_phone_captcha(self.arg.phone)
                self.write({'is_success': True})
                return
            else:
                self.write({'is_success': False, 'des': 'no step1'})
                return
        else:
            self.write({'is_success': False, 'res': 'error step!'})

    @tornado_argument_json('_step', 'phone', 'phone_captcha', 'new_password', 'shop_id')
    def post(self):
        if self.arg.step == 'validate_phone_captcha':
            if self.get_secure_cookie('step') == '2':
                mt_log.info('validate_phone_captcha: get_secure_cookie_2')
                if validate_phone_captcha(self.arg.phone_captcha, self.arg.phone)['is_success']:
                    mt_log.info('validate_phone_captcha: captcha is right!')
                    self.set_secure_cookie('step', '3')
                    self.write({'is_success': True})
                    return
                else:
                    self.write({'is_success': False})
                    return
            else:
                self.write({'is_success': False, 'des': 'no step2'})
                return
            return
        elif self.arg.step == 'reset_password':
            if self.get_secure_cookie('step') == '3':
                response = modify_merchant_password(self.arg.shop_id, old_password=None,
                                                    new_password=self.arg.new_password,
                                                    need_old_password=False)
                self.clear_cookie('step')
                self.write(response)
                return
            else:
                self.write({'is_success': False, 'des': 'no step3'})
                return
        else:
            self.write({'is_success': False, 'res': 'error step!'})
            return
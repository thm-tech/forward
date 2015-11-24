# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import tornado.web

from forward.httpbase import HttpBaseHandler
from forward.common.tools import tornado_argument_json, tornado_argument, tornado_route
from forward.modules.mt.basic.db_basic import *
from forward.common.validate.validate_code import create_validate_code
from forward.common.tools import pathjoin
from forward.common.send_message import *

from forward.modules.cache.base import cache

basic_urls = []


@tornado_route(r'/basic/companyinfo', basic_urls)
class CompanyInfoHandler(HttpBaseHandler):
    @cache(86400)
    def get(self):
        response = get_companyinfo()
        self.write(response)


@tornado_route(r'/basic/countries', basic_urls)
class CountriesHandler(HttpBaseHandler):
    @cache(86400)
    def get(self):
        response = get_countries()
        self.write(response)


@tornado_route(r'/basic/provinces', basic_urls)
class ProvincesHandler(HttpBaseHandler):
    @cache(86400)
    @tornado_argument('country_id', 'all')
    def get(self):
        all = 0
        if self.arg.all is not None:
            all = int(self.arg.all)
        response = get_provinces(self.arg.country_id, all=all)
        self.write(response)


@tornado_route(r'/basic/cities', basic_urls)
class CitiesHandler(HttpBaseHandler):
    @cache(86400)
    @tornado_argument('country_id', 'province_id', 'all')
    def get(self):
        all = 0
        if self.arg.all is not None:
            all = int(self.arg.all)
        response = get_cities(self.arg.country_id, self.arg.province_id, all=all)
        self.write(response)


@tornado_route(r'/basic/city/(.*)', basic_urls)
class CityHandler(HttpBaseHandler):
    @cache(86400)
    def get(self, city_id):
        response = get_cityinfo(city_id)
        self.write(response)


@tornado_route(r'/basic/districts', basic_urls)
class DistrictsHandler(HttpBaseHandler):
    @cache(86400)
    @tornado_argument('country_id', 'province_id', 'city_id')
    def get(self):
        response = get_districts(self.arg.country_id, self.arg.province_id, self.arg.city_id)
        self.write(response)


@tornado_route(r'/basic/district/(.*)', basic_urls)
class DistrictHandler(HttpBaseHandler):
    @cache(86400)
    def get(self, districe_id):
        response = get_district_info(districe_id)
        self.write(response)


@tornado_route(r'/basic/goodscategories', basic_urls)
class GoodsCategoriesHandler(HttpBaseHandler):
    @cache(86400)
    @tornado_argument('parent_id', 'type')
    def get(self):
        if self.arg.type == 'all_tree':
            response = get_goodscategories_all_tree()
            self.write(response)
        elif self.arg.type == 'all':
            response = get_goodscategories_all()
            self.write(response)
        else:
            response = get_goodscategory(self.arg.parent_id)
            self.write(response)


@tornado_route(r'/basic/test', basic_urls)
class TemplatesTestHandler(HttpBaseHandler):
    def get(self):
        import tornado.template

        loader = tornado.template.Loader("./modules/mt/test")
        html = loader.load('test.html').generate()
        self.write(html)


@tornado_route(r'/basic/captcha', basic_urls)
class CaptchaHandler(HttpBaseHandler):
    @tornado_argument('rnd')
    def get(self):
        self.add_header('content-type', 'image/gif')
        img, img_str = create_validate_code()
        img.save(pathjoin('common', 'validate', 'captcha.gif'))

        self.set_secure_cookie('imgcaptcha', img_str)

        with open(pathjoin('common', 'validate', 'captcha.gif'), 'rb') as f:
            self.write(f.read())

    @tornado_argument_json('rnd', '_captcha_str')
    def post(self):
        if self.arg.captcha_str == self.get_secure_cookie('imgcaptcha'):
            self.write({'is_success': True})
        else:
            self.write({'is_success': False})


@tornado_route(r'/basic/phonevalidate/(\d*)', basic_urls)
class PhoneValidateHandler(HttpBaseHandler):
    def get(self, mobile):
        r = send_phone_captcha(mobile)
        self.write(r)

    @tornado_argument_json('_code')
    def post(self, mobile):
        r = validate_phone_captcha(code=self.arg.code, mobile=mobile)
        self.write(r)

@tornado_route(r'/basic/joinshops', basic_urls)
class JoinShopsHandler(HttpBaseHandler):
    @cache(86400)
    @tornado_argument('_offset', '_limit')
    def get(self):
        response = get_friend_shop(int(self.arg.offset), int(self.arg.limit))
        self.write(response)
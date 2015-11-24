# -*- encoding: utf-8 -*-
import re
import tempfile
import os
import hashlib

import tornado.web
from PIL import Image

from forward.httpbase import HttpBaseHandler
from forward.common.tools import tornado_argument_json, tornado_argument
from forward.modules.mt.shop.db_shop import *
from forward.modules.mt.settings import *
from forward.modules.mt.category.dao import *
from forward.common.tools import tornado_route
from forward.modules.mt.merchant.db_merchant import *


shop_urls = []


@tornado_route(r'/shop', shop_urls)
class ShopsHandler(HttpBaseHandler):
    @tornado_argument('_offset', '_limit')
    def get(self):
        response = get_shops_limit(int(self.arg.offset), int(self.arg.limit))
        self.write(response)

    @tornado_argument_json('_shop_id', '_shop_name', 'brand_name', 'business_hours', 'telephone_no', 'city_id',
                           'district_id',
                           'business_area', 'address', 'longitude', 'latitude', 'category_list')
    def post(self):
        response = sign_shop(shop_id=self.arg.shop_id, shop_name=self.arg.shop_name, brand_name=self.arg.brand_name,
                             business_hours=self.arg.business_hours,
                             telephone_no=self.arg.telephone_no, city_id=self.arg.city_id,
                             district_id=self.arg.district_id, business_area=self.arg.business_area,
                             address=self.arg.address, longitude=self.arg.longitude, latitude=self.arg.latitude,
                             category_list=self.arg.category_list)
        self.write(response)


@tornado_route(r'/shop/(\d*)/categories', shop_urls)
class ShopCategoryHandler(HttpBaseHandler):
    def get(self, shop_id):
        response = get_shop_all_category(shop_id)
        self.write(dict(shop_id=shop_id,
                        categories=response))


@tornado_route(r'/shops', shop_urls)
class ShopsHandler(HttpBaseHandler):
    @tornado_argument_json('shop_id', 'contact_name', 'contact_phone_no', 'contact_email', 'contact_qq',
                           'shop_name', 'brand_name', 'business_hours', 'telephone_no', 'city_id',
                           'district_id', 'business_area', 'address', 'longitude', 'latitude',
                           'category_list')
    def post(self):
        response = sign_shop(shop_id=self.arg.shop_id, contact_name=self.arg.contact_name,
                             contact_phone_no=self.arg.contact_phone_no,
                             contact_email=self.arg.contact_email, contact_qq=self.arg.contact_qq,
                             shop_name=self.arg.shop_name,
                             brand_name=self.arg.brand_name, business_hours=self.arg.business_hours,
                             telephone_no=self.arg.telephone_no,
                             city_id=self.arg.city_id, district_id=self.arg.district_id,
                             business_area=self.arg.business_area,
                             address=self.arg.address, longitude=self.arg.longitude, latitude=self.arg.latitude,
                             category_list=self.arg.category_list)
        self.write(response)


@tornado_route(r'/shop/(\d*)', shop_urls)
class ShopHandler(HttpBaseHandler):
    def get(self, shop_id):
        response = get_shop_info(shop_id)
        category_list = response['category_list']
        category_name_list = []
        for category_id in category_list:
            category_name = get_category_info(category_id).get('name')
            category_name_list.append(category_name)
        response['category_name_list'] = category_name_list
        self.write(response)

    @tornado.web.authenticated
    @tornado_argument_json('shop_name', 'brand_name', 'business_hours', 'telephone_no', 'city_id', 'district_id',
                           'business_area', 'address', 'longitude', 'latitude', 'category_list')
    def put(self, shop_id):
        response = modify_shop_info(shop_id=shop_id, brand_name=self.arg.brand_name, shop_name=self.arg.shop_name,
                                    business_hours=self.arg.business_hours,
                                    telephone_no=self.arg.telephone_no, city_id=self.arg.city_id,
                                    district_id=self.arg.district_id,
                                    business_area=self.arg.business_area,
                                    address=self.arg.address, longitude=self.arg.longitude, latitude=self.arg.latitude,
                                    pic_url_list=None, category_list=self.arg.category_list)
        self.write(response)


@tornado_route(r'/shop/(\d*)/introduction', shop_urls)
class ShopIntroductionHandler(HttpBaseHandler):
    def get(self, shop_id):
        response = get_shop_introduction(shop_id)
        self.write(response)

    @tornado.web.authenticated
    @tornado_argument_json('introduction')
    def post(self, shop_id):
        response = modify_shop_introduction(shop_id, self.arg.introduction)
        self.write(response)

    def put(self, shop_id):
        return self.post(shop_id)


@tornado_route(r'/shop/(\d*)/image', shop_urls)
class ShopImgHandler(HttpBaseHandler):
    def get(self, shop_id):
        if '0' == shop_id:
            self.write('''
                    <html>
                      <head><title>Upload File</title></head>
                      <body>
                        <form action='/shop/1/image' enctype="multipart/form-data" method='post'>
                            <input type='file' name='file'/><br/>
                            <input type='submit' value='submit'/>
                        </form>
                      </body>
                    </html>
                    ''')
        else:
            response = get_shop_img(shop_id)
            self.write(response)

    @tornado.web.authenticated
    def post(self, shop_id):
        upload_path = ImgStaticFile['shopimage']
        rule = re.compile('.*\.(?P<type>.+)')
        file_metas = self.request.files.get('file')

        file_handle_list = []

        for meta in file_metas:
            filename = meta['filename']
            matcher = rule.match(filename)
            if matcher:
                type = matcher.group('type')
                if type.lower() in LEGAL_IMG_TYPE:
                    if len(meta['body']) < IMG_SIZE:

                        new_filepath = os.path.join(upload_path,
                                                    str(hashlib.md5(meta['body']).hexdigest()) + '.' + 'jpg')
                        try:
                            fp = tempfile.TemporaryFile()
                            fp.write(meta['body'])
                            im = Image.open(fp)
                            im.save(new_filepath)
                            file_handle_list.append(dict(filename=filename, is_success=True,
                                                         img_url=ImageHost + '/fdimage/shopimage/' +
                                                                 os.path.basename(new_filepath)))
                        except Exception as e:
                            file_handle_list.append(dict(filename=filename, is_success=False, des=str(e)))
                        finally:
                            fp.close()

                    else:
                        file_handle_list.append(dict(filename=filename, error_code=MTERROR.FileSizeError.code,
                                                     des=MTERROR.FileSizeError.des))
                else:
                    file_handle_list.append(
                        dict(filename=filename, error_code=MTERROR.FileTypeError.code, des=MTERROR.FileTypeError.des))
            else:
                file_handle_list.append(
                    dict(filename=filename, error_code=MTERROR.FileTypeError.code, des=MTERROR.FileTypeError.des))
        self.write(dict(total_num=len(file_handle_list),
                        result=file_handle_list))

    @tornado.web.authenticated
    @tornado_argument_json('_pic_url_list')
    def put(self, shop_id):
        pic_url_list = [i[len(ImageHost):] for i in trans.to_list(self.arg.pic_url_list)]
        response = set_shop_img(shop_id=shop_id, img_urls=','.join(pic_url_list))
        self.write(response)


@tornado_route(r'/shop/(\d*)/activities', shop_urls)
class ShopActivitiesHandler(HttpBaseHandler):
    @tornado.web.authenticated
    @tornado_argument_json('_act_title', '_act_content', '_begin_time', '_end_time')
    def post(self, shop_id):
        begin_time = datetime.datetime.strptime(self.arg.begin_time, '%Y-%m-%d')
        end_time = datetime.datetime.strptime(self.arg.end_time, '%Y-%m-%d')
        end_time = end_time.replace(hour=23, minute=59, second=59)
        response = add_shop_activity(shop_id=shop_id, act_title=self.arg.act_title, act_content=self.arg.act_content,
                                     begin_time=begin_time, end_time=end_time)
        self.write(response)

    @tornado_argument('_offset', '_limit', 'history')
    def get(self, shop_id):
        offset = int(self.arg.offset)
        limit = int(self.arg.limit)
        if not self.arg.history:
            response = get_acitvites_by_createtime(shop_id, offset, limit)
        else:
            response = get_acitvites_by_createtime(shop_id, offset, limit, False)
        self.write(response)


@tornado_route(r'/shop/(\d*)/activity/(\d*)', shop_urls)
class ShopActivityHandler(HttpBaseHandler):
    def delete(self, shop_id, act_id):
        act_id = int(act_id)
        response = delete_activity(act_id)
        self.write(response)


@tornado_route(r'/shop/(\d*)/fans', shop_urls)
class ShopFansHandler(HttpBaseHandler):
    @tornado_argument('_offset', '_limit')
    def get(self, shop_id):
        response = get_shop_fans(shop_id, int(self.arg.offset), int(self.arg.limit))
        self.write(response)


@tornado_route(r'/shop/(\d*)/fans/(\d*)', shop_urls)
class ShopFanHandler(HttpBaseHandler):
    def get(self, shop_id, user_id):
        response = is_user_fans_a_shop(user_id=user_id, shop_id=shop_id)
        self.write(response)


@tornado_route(r'/shop/(\d*)/fansmessage', shop_urls)
class ShopFansMessages(HttpBaseHandler):
    @tornado_argument_json('_userids', '_message', 'sendall')
    def post(self, shop_id):
        userid_list = trans.to_list(self.arg.userids)
        push_time = datetime.datetime.now()

        if self.arg.sendall:
            desc_fansmessageconfig_mass(shop_id)
        else:
            desc_fansmessageconfig_p2p(shop_id)
        dbsession = DBSession()
        for user_id in userid_list:
            FD_T_Fansmessage.post(dbsession=dbsession, shop_id=shop_id, user_id=user_id,
                                  message=self.arg.message, push_time=push_time)
        dbsession.commit()
        dbsession.close()

        self.write({
            'is_success': True,
            'total_num': len(userid_list),
            'users': userid_list,
            'message': self.arg.message,
        })
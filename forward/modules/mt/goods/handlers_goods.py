# -*- encoding: utf-8 -*-
from forward.modules.mt.shop.db_shop import get_shop_fans

__author__ = 'Mohanson'

import os
import hashlib
import tempfile

import tornado.web
from PIL import Image

from forward.httpbase import HttpBaseHandler
from forward.modules.mt.goods.db_goods import *
from forward.modules.mt.settings import *
from forward.common.tools import tornado_argument, tornado_argument_json
from forward.modules.mt.merchant.handlers_merchant import desc_fansmessageconfig_mass
from forward.db.tables_define import FD_T_Fansmessage
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from forward.common.tools import pathjoin
from tornado.template import Loader
from forward.common.trans import *
from forward.common import trans
from forward.config import CONFIG

loader = Loader(pathjoin("modules", "mt", "goods"))


class GoodsCategoryHandler(HttpBaseHandler):
    def get(self, category_id):
        response = get_goodscategory(category_id)
        self.write(response)


class GoodsHandler(HttpBaseHandler):
    @tornado_argument('_shop_id', '_offset', '_limit', '_status')
    def get(self):
        """
        get goods, status could be -2~2, or multipuls with dot like 1,2
        """
        status = trans.to_list(self.arg.status)
        response = get_goods_list_by_shop(int(self.arg.shop_id), int(self.arg.offset), int(self.arg.limit),
                                          status=self.arg.status)
        self.write(response)

    @tornado.web.authenticated
    @tornado_argument_json('_shop_id', 'category_id', 'description', 'detail', 'bar_code', 'price', 'promotion_price',
                           'brand_name', 'basic_info', 'pic_url_list', '_is_sendall', 'remark')
    def post(self):
        if self.arg.pic_url_list:
            pic_url_list = ','.join([i[len(ImageHost):] for i in trans.to_list(self.arg.pic_url_list)])
        else:
            pic_url_list = ''

        response = publish_goods(shop_id=self.arg.shop_id, category_id=self.arg.category_id,
                                 description=self.arg.description, detail=self.arg.detail, bar_code=self.arg.bar_code,
                                 price=self.arg.price,
                                 promotion_price=self.arg.promotion_price, remark=self.arg.remark,
                                 brand_name=self.arg.brand_name, basic_info=self.arg.basic_info,
                                 pic_url_list=pic_url_list)
        response['is_sendall'] = False
        if self.arg.is_sendall == 1 or self.arg.is_sendall == '1' or self.arg.is_sendall is True:
            desc_fansmessageconfig_mass(self.arg.shop_id)
            fans = get_shop_fans(self.arg.shop_id)['fans']
            fans_ids = [i['user_id'] for i in fans]

            push_time = datetime.datetime.now()

            msg = loader.load("good.html").generate(description=self.arg.description, price=self.arg.price,
                                                    promotion_price=self.arg.promotion_price,
                                                    imgs=[i for i in trans.to_list(self.arg.pic_url_list)])
            dbsession = DBSession()
            FD_T_Fansmessage.post(dbsession=dbsession, shop_id=self.arg.shop_id, user_id=-1, message=msg,
                                  push_time=push_time)
            dbsession.commit()
            dbsession.close()

            http_client = AsyncHTTPClient()
            params = ""
            for i in fans_ids:
                params += "uid=%s&" % i
            url = "%s/chat/%s/fans/message/?" % (CONFIG.FD_CHAT_SERVER, self.arg.shop_id) + params
            http_client.fetch(HTTPRequest(url=url, method='POST', body=msg))

            response['is_sendall'] = True

        self.write(response)


class GoodsByteHandler(HttpBaseHandler):
    def get(self, goods_id):
        response = get_goods_info(goods_id)
        self.write(response)

    @tornado.web.authenticated
    @tornado_argument_json('category', 'description', 'bar_code', 'price', 'promotion_price',
                           'pic_url_list',
                           'brand_name', 'basic_info', 'status', 'detail', 'remark')
    def put(self, goods_id):
        response = set_goods_info(goods_id, category=self.arg.category,
                                  description=self.arg.description,
                                  bar_code=self.arg.bar_code,
                                  price=self.arg.price, promotion_price=self.arg.promotion_price,
                                  pic_url_list=self.arg.pic_url_list,
                                  brand_name=self.arg.brand_name, basic_info=self.arg.basic_info,
                                  status=self.arg.status, detail=self.arg.detail, remark=self.arg.remark)
        self.write(response)

    @tornado.web.authenticated
    def delete(self, goods_id):
        response = delete_goods(goods_id)
        self.write(response)


class GoodsStatusHandler(HttpBaseHandler):
    @tornado_argument_json('_ids', '_status')
    def put(self):
        ids = to_list(self.arg.ids)
        try:
            for id in ids:
                set_goods_info(id, status=self.arg.status)
        except Exception, e:
            self.write({'is_success': False, 'des': str(e)})
            return
        self.write({'is_success': True})


class GoodsImageHandler(HttpBaseHandler):
    def get(self, goods_id):
        if '0' == goods_id:
            self.write('''
                    <html>
                      <head><title>Upload File</title></head>
                      <body>
                        <form action='/goods/0/image' enctype="multipart/form-data" method='post'>
                            <input type='file' name='file'/><br/>
                            <input type='submit' value='submit'/>
                        </form>
                      </body>
                    </html>
                    ''')
        else:
            response = get_goods_img(goods_id)
            self.write(response)

    # @tornado.web.authenticated
    def post(self, goods_id):
        upload_path = ImgStaticFile['goodsimage']
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
                                                         img_url='/fdimage/shopimage/' +
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
    def put(self, goods_id):
        pic_url_list = [i[len(ImageHost):] for i in trans.to_list(self.arg.pic_url_list)]
        response = set_goods_img(goods_id, ','.join(pic_url_list))
        self.write(response)


class GoodsFavoriteHandler(HttpBaseHandler):
    def get(self, goods_id):
        response = get_goods_favorite(goods_id)
        self.write(response)


class GoodsFansHandler(HttpBaseHandler):
    @tornado_argument('_details', 'offset', 'limit')
    def get(self, goods_id):
        if to_boolean(self.arg.details):
            response = get_goods_fans2(goods_id, int(self.arg.offset), int(self.arg.limit))
        else:
            response = get_goods_fans(goods_id)
        self.write(response)


class GoodsFansHandler2(HttpBaseHandler):
    def get(self, goods_id):
        response = get_goods_fans2(goods_id)
        self.write(response)


class GoodsStandardHandler(HttpBaseHandler):
    def get(self, goods_id):
        response = get_goods_standard(goods_id=goods_id)
        self.write(response)

    @tornado.web.authenticated
    @tornado_argument_json('stand_key', 'stand_value', 'price', 'promotion_price')
    def post(self, goods_id):
        response = add_goods_standard(goods_id=goods_id, stand_key=self.arg.stand_key, stand_value=self.arg.stand_value,
                                      price=self.arg.price, promotion_price=self.arg.promotion_price)
        self.write(response)


class GoodsStandardByteHandler(HttpBaseHandler):
    def get(self, goods_id, standard_id):
        pass

    @tornado.web.authenticated
    @tornado_argument_json('stand_key', 'stand_value', 'price', 'promotion_price')
    def put(self, goods_id, standard_id):
        response = modify_goods_standard(goods_id=goods_id, standard_id=standard_id, stand_key=self.arg.stand_key,
                                         stand_value=self.arg.stand_value,
                                         price=self.arg.price, promotion_price=self.arg.promotion_price)
        self.write(response)

    @tornado.web.authenticated
    def delete(self, goods_id, standard_id):
        response = delete_goods_standard(goods_id=goods_id, standard_id=standard_id)
        self.write(response)


class GoodsSearch(HttpBaseHandler):
    @tornado_argument('_shop_id', '_offset', '_limit', '_status', '_input')
    def get(self):
        response = get_goods_list_by_shop(int(self.arg.shop_id), 0, 10000000, status=self.arg.status)
        goods = response['goods']
        return_goods = []
        for i in goods:
            if i['description']:
                if self.arg.input in i['description']:
                    return_goods.append(i)
            if i['bar_code']:
                if self.arg.input in i['bar_code']:
                    return_goods.append(i)
        return_goods = return_goods[int(self.arg.offset): int(self.arg.offset) + int(self.arg.limit)]
        self.write({
            'total_num': len(return_goods),
            'goods': return_goods
        })
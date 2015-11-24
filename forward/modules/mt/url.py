from tornado.web import StaticFileHandler

from .settings import ImgStaticFile
from .merchant.handlers_merchant import urls as merchant_urls
from .shop.handlers_shop import shop_urls
from .goods.url_goods import goods_urls
from .base.handlers_base import base_urls
from .basic.handlers_basic import basic_urls
from .customer.handlers_customer import urls as customer_urls


mt_urls = [(r"/fdimage/shopimage/(.*)", StaticFileHandler, {"path": ImgStaticFile['shopimage']}),
           (r"/fdimage/goodsimage/(.*)", StaticFileHandler, {"path": ImgStaticFile['goodsimage']})]

mt_urls += basic_urls
mt_urls += base_urls
mt_urls += merchant_urls
mt_urls += shop_urls
mt_urls += goods_urls
mt_urls += customer_urls
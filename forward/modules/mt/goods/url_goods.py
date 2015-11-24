# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

from .handlers_goods import *

goods_urls = [
    (r'/goods/category/(\d*)', GoodsCategoryHandler),
    (r'/goods', GoodsHandler),
    (r'/goods/(\d*)', GoodsByteHandler),
    (r'/goods/(\d*)/image', GoodsImageHandler),
    (r'/goods/(\d*)/favorite', GoodsFavoriteHandler),
    (r'/goods/(\d*)/fans', GoodsFansHandler),
    # (r'/goods/(\d*)/fans', GoodsFansHandler2),
    (r'/goods/(\d*)/standard', GoodsStandardHandler),
    (r'/goods/(\d*)/standard/(\d*)', GoodsStandardByteHandler),
    (r'/goods/status', GoodsStatusHandler),
    (r'/goods/search', GoodsSearch),
]
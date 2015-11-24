# -*- encoding: utf-8 -*-

import platform
if platform.platform().startswith('Windows'):
    ImgStaticFile = {
        'shopimage': 'C:/',
        'goodsimage': 'C:/',
    }
else:
    ImgStaticFile = {
        'shopimage': '/opt/fdimage/shopimage/',
        'goodsimage': '/opt/fdimage/goodsimage/',
    }

IMG_SIZE = 4 * 1024 * 1024
LEGAL_IMG_TYPE = ['jpg', 'bmp', 'jpeg', 'png', 'gif']

from forward.common.define import OSS_URL_PRIFIX
ImageHost = OSS_URL_PRIFIX

# @100w_100h.jpg
#-*- coding:utf-8 -*-

############
#add data define start
############
ADD_MERCHANT_JSONS = [
        {"account":"fang", "password":"12342134"},
        {"account":"yjl", "password":"asdsdf"},
        {"account":"wj", "password":"asdadf"},
        {"account":"ly", "password":"asdadf"},
        {"account":"gyt", "password":"asdsdf"},
        {"account":"wp", "password":"asdsdf"},
        {"account":"gy", "password":"asdsdf"},
        {"account":"zgl", "password":"asdsdf"},
        {"account":"lb", "password":"asdsdf"},
        {"account":"zf", "password":"asdsdf"},
    ]

ADD_CATEGORY_JSONS = [
        {"id":0x1001, "name":"sock", "topId":0x1000, "topName":"dress"},    
        {"id":0x1002, "name":u"袜子", "topId":0x1000, "topName":u"服装"},    
        {"id":0x1003, "name":u"鞋子", "topId":0x1000, "topName":u"服装"},    
    ]

ADD_BRAND_JSONS = [
        {
            "name":u"贵人鸟", "categoryId":0x1003, "description":u"中国总部", 
            "contactName":u"金正恩", "contactPhoneno":"110", "contactEmail":"",
            "contactQQ":"1234123123"
        },    
        {
            "name":u"特步", "categoryId":0x1003, "description":u"飞一般的感觉", 
            "contactName":u"刁进凹", "contactPhoneno":"110", "contactEmail":"",
            "contactQQ":"1234123123"
        },    
    ]

ADD_CITY_JSONS = [
        {
            "cityId":0x1001, "initial":'hf', "acronym":'hf', "name":u"合肥", "districtId":0x1001002,
            "districtName":u"蜀山区", "businessDistrictId":0x1001011, 
            "businessDistrictName":u"淮河路步行街", "provinceId":0x1000, "contryId":86,
        },
    ]

ADD_SHOP_JSONS = [
        {
            "brandCode":1, "name":u"彩蝶轩", "phoneno":"110", "telephoneno":"1313131131",
            "businessHours":0, "categoryId":0x1003, "description":u"灰常甜", "areaId":1,
            "address":u"淮河路步行街123号", "longititude":72.12312331, "latitude":123.7663112,
        },
        {
            "brandCode":1, "name":u"彩蝶轩1", "phoneno":"110", "telephoneno":"1313131131",
            "businessHours":0, "categoryId":0x1003, "description":u"灰常甜", "areaId":1,
            "address":u"淮河路步行街123号", "longititude":72.12312331, "latitude":123.7663112,
        },
        {
            "brandCode":1, "name":u"彩蝶轩2", "phoneno":"110", "telephoneno":"1313131131",
            "businessHours":0, "categoryId":0x1003, "description":u"灰常甜", "areaId":1,
            "address":u"淮河路步行街123号", "longititude":72.12312331, "latitude":123.7663112,
        },
        {
            "brandCode":1, "name":u"彩蝶轩3", "phoneno":"110", "telephoneno":"1313131131",
            "businessHours":0, "categoryId":0x1003, "description":u"灰常甜", "areaId":1,
            "address":u"淮河路步行街123号", "longititude":72.12312331, "latitude":123.7663112,
        },
        {
            "brandCode":1, "name":u"彩蝶轩4", "phoneno":"110", "telephoneno":"1313131131",
            "businessHours":0, "categoryId":0x1003, "description":u"灰常甜", "areaId":1,
            "address":u"淮河路步行街123号", "longititude":72.12312331, "latitude":123.7663112,
        },
    ]

ADD_MERCHANT_ARCH_NODE_JSONS = [
        #id = 1
        {
            "brandCode":1, "merchantId":1, "merchantName":u"贵人鸟总部", "merchantType":1, 
            "fatherId":None, "shopCode":None,
        },
        #id = 2
        {
            "brandCode":1, "merchantId":2, "merchantName":u"华东区", "merchantType":2, 
            "fatherId":1, "shopCode":None,
        },
        #id = 3
        {
            "brandCode":1, "merchantId":3, "merchantName":u"西北区", "merchantType":2, 
            "fatherId":1, "shopCode":None,
        },
        #id = 4
        {
            "brandCode":1, "merchantId":4, "merchantName":u"合肥", "merchantType":2, 
            "fatherId":2, "shopCode":None,
        },
        #id = 5
        {
            "brandCode":1, "merchantId":5, "merchantName":u"上海", "merchantType":2, 
            "fatherId":2, "shopCode":None,
        },
        #id = 6
        {
            "brandCode":1, "merchantId":6, "merchantName":u"商店5", "merchantType":3, 
            "fatherId":3, "shopCode":5,
        },
        #id = 7
        {
            "brandCode":1, "merchantId":7, "merchantName":u"shop1", "merchantType":3, 
            "fatherId":4, "shopCode":1,
        },
        #id = 8
        {
            "brandCode":1, "merchantId":8, "merchantName":u"shop2", "merchantType":3, 
            "fatherId":4, "shopCode":2,
        },
        #id = 9
        {
            "brandCode":1, "merchantId":9, "merchantName":u"shop3", "merchantType":3, 
            "fatherId":5, "shopCode":3,
        },
        #id = 10
        {
            "brandCode":1, "merchantId":10, "merchantName":u"shop4", "merchantType":3, 
            "fatherId":5, "shopCode":4,
        },
    ]

MERCHANT_LOGIN_JSON = {
        "account":"fang", "password":"12342134",
    }

MERCHANT_LOGIN_DEFINE = {
        'url':r'/mt/p/merchant/login',
        'datas': MERCHANT_LOGIN_JSON,
    }

INSERT_DATA = [
        {
            'url':r'/mt/p/merchant',
            'datas':ADD_MERCHANT_JSONS,
        },
        {
            'url':r'/mt/p/category',
            'datas':ADD_CATEGORY_JSONS,
        },
        {
            'url':r'/mt/p/brand',
            'datas':ADD_BRAND_JSONS,
        },
        {
            'url':r'/mt/p/city',
            'datas':ADD_CITY_JSONS,
        },
        {
            'url':r'/mt/p/shop',
            'datas':ADD_SHOP_JSONS,
        },
        {
            'url':r'/mt/p/merchant/arch',
            'datas':ADD_MERCHANT_ARCH_NODE_JSONS,
        },
    ]

############
#add data define end
############

############
#delete data define start
############
DELETE_DATA = [
        {'url':r"/mt/d/merchant/arch?key=merchantId&val=4"},    
    ]
############
#delete data define end 
############

############
#updata data define start
############
UPDATE_SHOP_JSONS = [
        {
            "shopCode":1, "brandCode":1, "name":u"巴黎甜甜", "phoneno":"110", 
            "telephoneno":"1313131131","businessHours":0, "categoryId":0x1003, 
            "description":u"灰常甜", "areaId":1,"address":u"淮河路步行街123号", 
            "longititude":72.12312331, "latitude":123.7663112,
        },
    ]

UPDATE_DATA = [
        {
            'url':r'/mt/u/shop',
            'datas':UPDATE_SHOP_JSONS,
        },
    ]
############
#updata data define end 
############

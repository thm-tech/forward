# -*- coding:utf8 - *-
import math

import pymongo
from pymongo import GEOSPHERE

from forward.config import CONFIG


MONGO_HOST = CONFIG.MONGO.HOST
PORT = CONFIG.MONGO.PORT


class GEO(object):
    client = pymongo.MongoClient(MONGO_HOST, PORT)
    db = client.shop_address
    places = db.places
    places.create_index([('local', GEOSPHERE)])

    def __init__(self):
        pass

    def getShopList(self, city_id, category_id, longitude, latitude, offset, count):
        """
        MongoDB store shop lbs into, query shop id list by API
        API IN paras: category_id, city_id, longitude, latitude, offset, count
        API OUT paras: shop_id list
        """

        datas = dict(
            city_id=city_id,
            category_list=[int(category_id)] if category_id else [],
        )
        if longitude is not None and latitude is not None:
            datas['local'] = {'$nearSphere': [longitude, latitude]}
        if not category_id:
            del datas['category_list']
        shop_id_list = [i['shop_id'] for i in self.places.find(datas).sort('weights', -1).skip(offset).limit(count)]
        return shop_id_list

    def getShopNum(self, city_id, category_id=None, longitude=None, latitude=None):
        """
        MongoDB store shop lbs into, query shop id list by API
        API IN paras: category_id, city_id, longitude, latitude, offset, count
        API OUT paras: shop_id list
        """

        datas = dict(
            city_id=city_id,
            category_list=[int(category_id)] if category_id else [],
        )
        if longitude is not None and latitude is not None:
            datas['local'] = {'$nearSphere': [longitude, latitude]}
        if not category_id:
            del datas['category_list']
        num = self.places.count(datas)
        return num

    def getDistance(self, x_long, x_lat, y_long, y_lat):
        rad_x_lat = math.radians(x_lat)
        rad_y_lat = math.radians(y_lat)
        a = rad_x_lat - rad_y_lat
        b = math.radians(x_long) - math.radians(y_long)
        s = 2 * math.asin(math.sqrt(
            math.pow(math.sin(a / 2), 2) + math.cos(rad_x_lat) * math.cos(rad_y_lat) * math.pow(math.sin(b / 2), 2)))
        earth_radius = 6378.137
        s *= earth_radius
        if s < 0:
            return -s
        else:
            return s

    def insert(self, shop_id, category_list, city_id, longitude, latitude, weights=50.1):
        return self.places.insert({'shop_id': shop_id,
                                   'category_list': category_list,
                                   'city_id': city_id,
                                   'local': [longitude, latitude],
                                   'weights': weights
                                   })

    def remove(self, shop_ids):
        if isinstance(shop_ids, int):
            shop_ids = [shop_ids]
        else:
            shop_ids = shop_ids
        self.places.remove({'shop_id': {'$in': [shop_ids]}})

    def update(self, shop_id, category_list, city_id, longitude, latitude, weights=None):
        data = {'category_list': category_list,
                'city_id': city_id,
                'local': [longitude, latitude],
                }
        if weights:
            data['weights'] = weights
        self.places.update({'shop_id': shop_id}, {'$set': data})

    def clear_all(self):
        self.places.remove({'shop_id': {'$exists': True}})


if __name__ == '__main__':
    geo = GEO()
    r = geo.getShopList(1048577, None, None, None, 0, 1)
    print(r)
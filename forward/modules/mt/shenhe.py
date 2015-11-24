# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import os

os.chdir('../../')
from forward.db.tables_define import *
from forward.common.geo import GEO
import datetime
from forward.common import trans
from forward.common.validate.phone_validate import pass_message


def shenhe(shop_id):
    dbsession = DBSession()
    geo = GEO()
    shopaccount = dbsession.query(FD_T_Shopaccount).filter(FD_T_Shopaccount.shop_id == shop_id).one()

    shopaccount.service_deadline = datetime.datetime.now() + datetime.timedelta(days=365)
    shopaccount.service_status = 2
    shop = dbsession.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()

    fansmsgconfig = dbsession.query(FD_T_Fansmessageconfig).filter(FD_T_Fansmessageconfig.shop_id == shop_id).one()
    fansmsgconfig.current_p2p_count = 30
    fansmsgconfig.p2p_remain_count = 30
    fansmsgconfig.next_p2p_count = 30
    fansmsgconfig.current_mass_count = 10
    fansmsgconfig.mass_remain_count = 10
    fansmsgconfig.next_mass_count = 10

    dbsession.add(fansmsgconfig)

    # start send pass message
    shop = dbsession.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()
    shopname = shop.shop_name
    pass_message(shopname, shopaccount.contact_phone_no)
    # end send pass message

    dbsession.commit()

    geo.insert(shop_id, [int(i) for i in trans.to_list(shop.category_list) if i],
               int(shop.city_id), float(shop.longitude), float(shop.latitude))

    dbsession.close()


def shenhe_all():
    dbsession = DBSession()
    shop_ids = [i[0] for i in
                dbsession.query(FD_T_Shopaccount.shop_id).filter(FD_T_Shopaccount.service_status == 1).all()]
    for shop_id in shop_ids:
        shenhe(shop_id)
    return shop_ids


if __name__ == '__main__':
    shenhe_all()
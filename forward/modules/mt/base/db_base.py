# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

from forward.db.tables_define import *
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


def get_newaccountid():
    session = DBSession()
    try:
        shop_id_sequence = session.query(FD_T_Sequence).filter(FD_T_Sequence.sequence_name == 'FD_ACCOUNT_ID').one()
    except NoResultFound, e:
        shop_id_sequence = FD_T_Sequence('FD_ACCOUNT_ID', 1, 1)
        session.add(shop_id_sequence)
        session.commit()
    id = shop_id_sequence.current_value
    shop_id_sequence.current_value += shop_id_sequence.increment_value
    session.commit()
    return id


def get_newimageid():
    session = DBSession()
    try:
        shopimg_id_sequence = session.query(FD_T_Sequence).filter(
            FD_T_Sequence.sequence_name == 'FD_SHOP_IMAGE_ID').one()
    except NoResultFound, e:
        shopimg_id_sequence = FD_T_Sequence('FD_SHOP_IMAGE_ID', 1, 1)
        session.add(shopimg_id_sequence)
        session.commit()
    id = shopimg_id_sequence.current_value
    shopimg_id_sequence.current_value += shopimg_id_sequence.increment_value
    session.commit()
    return id


def get_newgoodsid():
    session = DBSession()
    try:
        goods_id_sequence = session.query(FD_T_Sequence).filter(FD_T_Sequence.sequence_name == 'FD_GOODS_ID').one()
    except NoResultFound, e:
        goods_id_sequence = FD_T_Sequence('FD_GOODS_ID', 1, 1)
        session.add(goods_id_sequence)
        session.commit()
    id = goods_id_sequence.current_value
    goods_id_sequence.current_value += goods_id_sequence.increment_value
    session.commit()
    return id
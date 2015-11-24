# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from forward.db.tables_define import *
from forward.modules.mt.error_code import MTERROR
from ..settings import ImageHost
from forward.common import trans


def get_customer_favorite_goods_in_shop(shop_id, user_id):
    dbsession = DBSession()
    goods = dbsession.query(FD_T_Favorite.user_id, FD_T_Goods.goods_id, FD_T_Goods.description, FD_T_Goods.pic_url_list,
                            FD_T_Goods.price, FD_T_Goods.promotion_price) \
        .outerjoin(FD_T_Goods, FD_T_Favorite.goods_id == FD_T_Goods.goods_id) \
        .filter(FD_T_Goods.shop_id == shop_id) \
        .filter(FD_T_Favorite.user_id == user_id).all()
    return dict(total_num=len(goods),
                goods=[dict(goods_id=i.goods_id,
                            description=i.description,
                            pic_url_list=i.pic_url_list,
                            price=float(i.price),
                            promotion_price=float(i.promotion_price) if i.promotion_price else None)
                       for i in goods])


def get_fans_all_msg(shop_id, user_id):
    dbsession = DBSession()
    try:
        v = dbsession.query(FD_T_Visitedshop).filter(FD_T_Visitedshop.shop_id == shop_id,
                                                     FD_T_Visitedshop.user_id == user_id).one()
        u = dbsession.query(FD_T_User).filter(FD_T_User.user_id == user_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    res = get_customer_favorite_goods_in_shop(shop_id, user_id)
    user_name = u.name
    user_visit_num = v.visit_count
    user_favorite_num = res.get('total_num')
    last_visit_time = v.dict().get('last_visit_time')
    goods = res.get('goods')
    for good in goods:
        good['pic_url_list'] = [ImageHost + i for i in trans.to_list(good['pic_url_list'])]

    return dict(user_name=user_name,
                user_visit_num=user_visit_num,
                user_favorite_num=user_favorite_num,
                last_visit_time=last_visit_time,
                goods=goods)
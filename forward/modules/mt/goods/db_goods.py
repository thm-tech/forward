# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy import or_

from forward.db.tables_define import *
from forward.modules.mt.error_code import MTERROR
from forward.modules.mt.base.db_base import get_newgoodsid
from forward.modules.mt.settings import ImageHost
from forward.modules.mt.shop.db_shop import fresh_shop_category
from forward.common import trans














# 商品状态，-2：等待审核，-1：审核未通过，0：下架，1：上架，2：删除

def get_categorylistbycategory(category_id, category_list=[]):
    session = DBSession()
    """
    :param category_id: category_id
    :param category_list: m should not input this param, it's used for recursive
    :return: {"categories": [2, 1, 4], "total_num": 3}
    """
    try:
        category = session.query(FD_T_Goodscategory).filter(FD_T_Goodscategory.id == category_id).one()
        if not category_list:
            category_list = [int(category_id)]
    except MultipleResultsFound, e:
        return dict(total_num=len(category_list),
                    categories=category_list, is_success=False)
    except NoResultFound, e:
        return dict(total_num=len(category_list),
                    categories=category_list, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    if category.parent_id and session.query(FD_T_Goodscategory).filter(
                    FD_T_Goodscategory.id == category.parent_id).count() > 0:
        category_list.append(category.parent_id)
        return get_categorylistbycategory(category.parent_id, category_list)
    else:
        return dict(total_num=len(category_list),
                    categories=category_list)


def get_goodscategory(category_id):
    session = DBSession()
    try:
        category = session.query(FD_T_Goodscategory).filter(FD_T_Goodscategory.id == category_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    return category.dict()


def get_goods_list_by_shop(shop_id, offset, limit, status):
    session = DBSession()
    try:
        shop = session.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    goods = shop.goods
    goods_list = [dict(goods_id=i.goods_id,
                       category_list=trans.to_list(i.category_list),
                       description=i.description,
                       detail=i.detail,
                       bar_code=i.bar_code,
                       price=str(i.price) if i.price else None,
                       promotion_price=str(i.promotion_price) if i.promotion_price else None,
                       pic_url_list=trans.to_list(i.pic_url_list),
                       brand_name=i.brand_name,
                       basic_info=i.basic_info,
                       shop_ip=i.shop_id,
                       publish_time=i.publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                       favorite_num=get_goods_favorite(i.goods_id)['total_num'],
                       status=i.status) for j, i in enumerate(goods) if str(i.status) in status]
    goods_list = sorted(goods_list, key=lambda x: x['publish_time'], reverse=True)
    total_num = len(goods_list)
    goods_list = goods_list[int(offset): int(offset) + int(limit)]
    for j, goods in enumerate(goods_list):
        goods['index'] = j + offset + 1
    return dict(total_num=total_num,
                goods=goods_list,
                shop_name=shop.shop_name)


def publish_goods(shop_id, category_id=None, description=None, detail=None, bar_code=None, price=None,
                  promotion_price=None, remark=None,
                  brand_name=None, basic_info=None, pic_url_list=None):
    session = DBSession()
    goods_id = get_newgoodsid()
    if category_id:
        category_list = ','.join([str(i) for i in get_categorylistbycategory(category_id)['categories']])
    else:
        category_list = ''
    publish_time = datetime.datetime.now()
    goods = FD_T_Goods(goods_id=goods_id, shop_id=shop_id, category_list=category_list, bar_code=bar_code,
                       description=description, detail=detail, price=price, promotion_price=promotion_price,
                       brand_name=brand_name, remark=remark,
                       basic_info=basic_info, publish_time=publish_time, status=1, pic_url_list=pic_url_list)
    goodsinfo = FD_T_Goodsinfo(goods_id=goods_id, sales_volume=0, browse_count=0, attention_count=0, stock_count=0,
                               res1=0, res2=0, res3="")
    session.add(goodsinfo)

    session.add(goods)
    session.commit()
    return dict(is_success=True,
                goods_id=goods.goods_id)


def delete_goods(goods_id):
    session = DBSession()
    try:
        goods = session.query(FD_T_Goods).filter(FD_T_Goods.goods_id == goods_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    goods.status = 2
    session.commit()
    return dict(is_success=True,
                goods_id=int(goods_id))


def get_goods_img(goods_id):
    session = DBSession()
    try:
        goods = session.query(FD_T_Goods).filter(FD_T_Goods.goods_id == goods_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    pic_url_list = trans.to_list(goods.pic_url_list)
    return dict(total_num=len(pic_url_list),
                imgs=[ImageHost + i for i in pic_url_list])


def set_goods_img(goods_id, pic_url_list):
    session = DBSession()
    try:
        goods = session.query(FD_T_Goods).filter(FD_T_Goods.goods_id == goods_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    goods.pic_url_list = pic_url_list
    session.commit()
    return dict(is_success=True,
                goods_id=goods.goods_id)


def get_goods_info(goods_id):
    session = DBSession()
    try:
        goods = session.query(FD_T_Goods).filter(FD_T_Goods.goods_id == goods_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    return dict(goods_id=goods.goods_id,
                category_list=trans.to_list(goods.category_list),
                description=goods.description,
                bar_code=goods.bar_code,
                price=str(goods.price) if goods.price else None,
                promotion_price=str(goods.promotion_price) if goods.promotion_price else None,
                pic_url_list=trans.to_list(goods.pic_url_list),
                brand_name=goods.brand_name,
                basic_info=goods.basic_info,
                shop_id=goods.shop_id,
                publish_time=goods.publish_time.strftime('%Y-%m-%d %H-%M-%S'),
                favorite=get_goods_favorite(goods_id),
                detail=goods.detail,
                remark=goods.remark,
                )


def set_goods_info(goods_id, category=None, description=None, bar_code=None, price=None,
                   promotion_price=None,
                   pic_url_list=None, brand_name=None, basic_info=None, status=None, detail=None, remark=None):
    session = DBSession()
    try:
        goods = session.query(FD_T_Goods).filter(FD_T_Goods.goods_id == goods_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    if category is not None:
        goods.category_list = get_categorylistbycategory(category)
    if description is not None:
        goods.description = description
    if bar_code is not None:
        goods.bar_code = bar_code
    if price is not None:
        goods.price = price
    if promotion_price is not None:
        goods.promotion_price = promotion_price
    if pic_url_list is not None:
        goods.pic_url_list = pic_url_list
    if brand_name is not None:
        goods.brand_name = brand_name
    if basic_info is not None:
        goods.basic_info = basic_info
    if status is not None:
        goods.status = status
        goods.publish_time = datetime.datetime.now()
        fresh_shop_category(goods.shop_id)
    if detail is not None:
        goods.detail = detail
    if remark is not None:
        goods.remark = remark
    session.commit()
    return dict(is_success=True,
                goods_id=goods.goods_id)


def get_goods_favorite(goods_id):
    session = DBSession()
    users = session.query(FD_T_Favorite).filter(FD_T_Favorite.goods_id == goods_id).all()
    return dict(total_num=len(users),
                users=[user.user_id for user in users])


def get_goods_fans(goods_id):
    session = DBSession()
    try:
        goods = session.query(FD_T_Goods).filter(FD_T_Goods.goods_id == goods_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    shop_id = goods.shop_id
    fans = session.query(FD_T_Fans.user_id, FD_T_User.name).outerjoin(FD_T_User,
                                                                      FD_T_User.user_id == FD_T_Fans.user_id).filter(
        FD_T_Fans.shop_id == shop_id).all()
    fans_id = [fan[0] for fan in fans]
    favorites_id = get_goods_favorite(goods_id)['users']
    favorite_fan = [id for id in fans_id if id in favorites_id]
    favorite_names = [fan[1] for fan in fans if fan[0] in favorites_id]
    return dict(total_num=len(favorite_fan),
                fans=favorite_fan,
                names=favorite_names)


def get_goods_fans2(goods_id, offset, limit):
    """
    SELECT
        fu.user_id,
        fu.`name`,
        fu.portrait_url,
        fv.last_visit_time,
        fv.visit_count
    FROM
        fd_t_goods fd
    LEFT JOIN fd_t_favorite ff ON fd.goods_id = ff.goods_id
    LEFT JOIN fd_t_fans ffans ON ff.user_id = ffans.user_id
    LEFT JOIN fd_t_user fu ON ff.user_id = fu.user_id
    LEFT JOIN fd_t_visitedshop fv ON fu.user_id = fv.user_id
    WHERE
        fd.goods_id = 75
    AND ffans.shop_id = fd.shop_id
    AND (
        fv.shop_id = fd.shop_id
        OR fv.shop_id IS NULL
    )
    """
    session = DBSession()
    rs = session.query(FD_T_Goods.goods_id, FD_T_User.user_id, FD_T_User.name, FD_T_User.portrait_url,
                       FD_T_Visitedshop.last_visit_time, FD_T_Visitedshop.visit_count) \
        .outerjoin(FD_T_Favorite, FD_T_Favorite.goods_id == FD_T_Goods.goods_id) \
        .outerjoin(FD_T_Fans, FD_T_Fans.user_id == FD_T_Favorite.user_id) \
        .outerjoin(FD_T_User, FD_T_Favorite.user_id == FD_T_User.user_id) \
        .outerjoin(FD_T_Visitedshop, FD_T_User.user_id == FD_T_Visitedshop.user_id) \
        .filter(FD_T_Goods.goods_id == goods_id) \
        .filter(FD_T_Fans.shop_id == FD_T_Goods.shop_id) \
        .filter(or_(FD_T_Visitedshop.shop_id == FD_T_Goods.shop_id, FD_T_Visitedshop.shop_id == None)).all()
    return dict(
        total_num=len(rs),
        fans=[dict(user_id=int(i[1]),
                   name=i[2],
                   portrait_url=ImageHost + i[3] if i[3] else None,
                   last_visit_time=trans.datetime_to_string(i[4]) if i[4] else None,
                   visit_count=int(i[5]) if i[5] else 0,
                   collects=0,
                   index=offset + index + 1) for index, i in enumerate(rs[offset: offset + limit])],
    )


def add_goods_standard(goods_id, stand_key=None, stand_value=None, price=None, promotion_price=None):
    session = DBSession()
    goods_standard = FD_T_Goodsstandard(goods_id=goods_id, stand_key=stand_key, stand_value=stand_value, price=price,
                                        promotion_price=promotion_price)
    session.add(goods_standard)
    session.commit()
    return dict(is_success=True,
                standard_id=goods_standard.id)


def get_goods_standard(goods_id):
    session = DBSession()
    goods_standards = session.query(FD_T_Goodsstandard).filter(FD_T_Goodsstandard.goods_id == goods_id).all()
    glist = [dict(id=i.id, goods_id=i.goods_id, stand_key=i.stand_key, stand_value=i.stand_value,
                  price=str(i.price), promotion_price=str(i.promotion_price)) for i in goods_standards]
    return dict(total_num=len(glist),
                goods_standards=glist)


def modify_goods_standard(goods_id, standard_id, stand_key=None, stand_value=None, price=None, promotion_price=None):
    session = DBSession()
    try:
        standard = session.query(FD_T_Goodsstandard).filter(FD_T_Goodsstandard.id == standard_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    if stand_key:
        standard.stand_key = stand_key
    if stand_value:
        standard.stand_value = stand_value
    if price:
        standard.price = price
    if promotion_price:
        standard.promotion_price = promotion_price
    session.commit()
    return dict(is_success=True,
                goods_id=standard.goods_id,
                standard_id=standard.id)


def delete_goods_standard(goods_id, standard_id):
    session = DBSession()
    try:
        standard = session.query(FD_T_Goodsstandard).filter(FD_T_Goodsstandard.id == standard_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    session.delete(standard)
    session.commit()
    return dict(is_success=True,
                goods_id=standard.goods_id,
                standard_id=standard.id)


def get_good_info_by_barcode(shop_id, barcode):
    session = DBSession()
    infos = session.query(FD_T_Goods).filter(FD_T_Goods.bar_code == barcode, FD_T_Goods.shop_id == shop_id)
    infos = [i.dict() for i in infos]
    session.close()
    return infos


def search_goods_by_name(shop_id, name):
    session = DBSession()
    infos = session.query(FD_T_Goods).filter(FD_T_Goods.description.like('%' + name + '%'),
                                             FD_T_Goods.shop_id == shop_id)
    infos = [i.dict() for i in infos]
    session.close()
    return infos
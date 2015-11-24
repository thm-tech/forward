# -*- encoding: utf-8 -*-
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from forward.common.trans import to_list
import sqlalchemy
from sqlalchemy import or_

from forward.common.geo import GEO
from forward.common import trans
from forward.log import mt_log
from forward.config import CONFIG
from forward.db.tables_define import *
from forward.modules.mt.error_code import MTERROR


def get_shop_all_category(shop_id):
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
    categorys = set()
    for good in goods:
        if int(good.status) == 1:
            for i in trans.to_list(good.category_list):
                categorys.add(i)
                categorys.add(str(category_get_father_category(i)))
    return list(categorys)


def category_get_father_category(category_id):
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
    return category.parent_id if category.parent_id else category_id


def fresh_shop_category(shop_id):
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
    shop.category_list = str(to_list(shop.category_list)[0]) + ',' + ','.join(get_shop_all_category(shop_id))
    session.commit()
    return True


def get_shops_limit(offset, limit):
    session = DBSession()
    total_num = session.query(FD_T_Shop).count()
    shops = session.query(FD_T_Shop).all()[offset: offset + limit]
    return dict(total_num=total_num,
                shops=[dict(shop_id=shop.shop_id,
                            shop_name=shop.shop_name,
                            qrcode=shop.qrcode,
                            business_hours=shop.business_hours,
                            telephone_no=shop.telephone_no,
                            city_id=shop.city_id,
                            district_id=shop.district_id,
                            business_area=shop.business_area,
                            address=shop.address,
                            longitude=float(shop.longitude),
                            latitude=float(shop.latitude),
                            pic_url_list=[ImageHost + i for i in trans.to_list(shop.pic_url_list)],
                            category_list=shop.pic_url_list) for shop in shops])


def sign_shop(shop_id, contact_name, contact_phone_no, contact_email,
              contact_qq,
              shop_name, brand_name, business_hours, telephone_no, city_id,
              district_id, business_area, address, longitude, latitude,
              category_list):
    session = DBSession()
    if is_shop_exist(shop_id)['is_exist']:
        return {'success': False, 'des': 'shop is already exist'}
    try:
        new_merchant = FD_T_Shopaccount(shop_id=shop_id,
                                        contact_name=contact_name,
                                        contact_phone_no=contact_phone_no,
                                        contact_email=contact_email,
                                        contact_qq=contact_qq,
                                        service_balance=0.0,
                                        service_status=1,
                                        portrait_url=CONFIG.DEFAULT_PORTRAIT_URL)
        session.add(new_merchant)
        new_shop = FD_T_Shop(shop_id=shop_id, shop_name=shop_name, brand_name=brand_name,
                             business_hours=business_hours, telephone_no=telephone_no, city_id=city_id,
                             district_id=district_id, business_area=business_area, address=address.encode('utf-8'),
                             longitude=longitude, latitude=latitude, category_list=category_list,
                             qrcode='http://www.immbear.com/shop/' + str(shop_id),
                             status=1)
        session.add(new_shop)
        session.commit()
        return {'success': True, 'shop_id': shop_id, 'is_success': False}
    except Exception, e:
        session.rollback()
        mt_log.exception(e)
        return {'success': False, 'res': str(e), 'is_success': False}


def is_shop_exist(shop_id):
    session = DBSession()
    num = session.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).count()
    if num:
        return dict(is_exist=True, shop_id=shop_id)
    else:
        return dict(is_exist=False, shop_id=shop_id)


def get_shop_info(shop_id):
    session = DBSession()
    try:
        shop = session.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
    return dict(shop_id=shop.shop_id,
                brand_name=shop.brand_name,
                shop_name=shop.shop_name,
                qrcode=shop.qrcode,
                business_hours=shop.business_hours,
                telephone_no=shop.telephone_no,
                city_id=shop.city_id,
                district_id=shop.district_id,
                business_area=shop.business_area,
                address=shop.address,
                longitude=float(shop.longitude),
                latitude=float(shop.latitude),
                pic_url_list=[ImageHost + i for i in trans.to_list(shop.pic_url_list)],
                category_list=to_list(shop.category_list))


def modify_shop_info(shop_id, brand_name=None, shop_name=None, business_hours=None, telephone_no=None,
                     city_id=None, district_id=None, business_area=None, address=None,
                     longitude=None, latitude=None, pic_url_list=None, category_list=None):
    session = DBSession()
    try:
        shop = session.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()
        if brand_name:
            shop.brand_name = brand_name
        if shop_name:
            shop.shop_name = shop_name
        if business_hours:
            shop.business_hours = business_hours
        if telephone_no:
            shop.telephone_no = telephone_no
        if city_id:
            shop.city_id = city_id
        if district_id:
            shop.district_id = district_id
        if business_area:
            shop.business_area = business_area
        if address:
            shop.address = address
        if longitude:
            shop.longitude = longitude
        if latitude:
            shop.latitude = latitude
        if pic_url_list:
            shop.pic_url_list = pic_url_list
        if category_list:
            shop.category_list = str(to_list(str(category_list))[0]) + ',' + ','.join(
                get_shop_all_category(int(shop_id)))

        GEO().update(shop.shop_id, trans.to_list(shop.category_list), shop.city_id, float(shop.longitude),
                     float(shop.latitude))

        session.commit()
        return dict(is_success=True,
                    shop_id=shop.shop_id)
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)
    except Exception, e:
        session.rollback()
        return dict(error_code=MTERROR.RegisterFailed.code, des=MTERROR.RegisterFailed.des)


def get_shop_introduction(shop_id):
    session = DBSession()
    try:
        shop_introduction = session.query(FD_T_Shop).filter(
            FD_T_Shop.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
    return {'introduction': shop_introduction.introduction}


def modify_shop_introduction(shop_id, introduction=None):
    session = DBSession()
    try:
        shop = session.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
    shop.introduction = introduction
    session.commit()
    return dict(is_success=True,
                shop_id=shop.shop_id)


def get_shop_img(shop_id):
    session = DBSession()
    try:
        shop_info = session.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
    return dict(shop_id=shop_info.shop_id,
                shop_img_urls=[ImageHost + i for i in trans.to_list(shop_info.pic_url_list)])


def set_shop_img(shop_id, img_urls):
    session = DBSession()
    try:
        shop_info = session.query(FD_T_Shop).filter(FD_T_Shop.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
    shop_info.pic_url_list = img_urls
    session.commit()
    return dict(is_success=True, shop_id=shop_info.shop_id)


def add_shop_activity(shop_id, act_title, act_content, begin_time, end_time):
    session = DBSession()
    try:
        lasta = session.query(FD_T_Activity.publish_time).filter(FD_T_Activity.shop_id == shop_id).order_by(
            FD_T_Activity.publish_time.desc()).limit(1).one()
        if datetime.datetime.now().strftime('%Y%m%d') == lasta[0].strftime('%Y%m%d'):
            return dict(is_success=False, des='you have already post a activity')
    except NoResultFound:
        pass

    activity = FD_T_Activity(act_title=act_title,
                             act_content=act_content,
                             begin_time=begin_time,
                             end_time=end_time,
                             shop_id=shop_id,
                             publish_time=datetime.datetime.now())
    session.add(activity)
    session.commit()
    return dict(is_success=True, activity_id=activity.act_id)


def delete_activity(act_id):
    session = DBSession()
    try:
        activity = session.query(FD_T_Activity).filter(FD_T_Activity.act_id == act_id).one()
        now = datetime.datetime.now()
        if activity.end_time > now:
            return dict(is_success=False,
                        shop_id=activity.shop_id,
                        des=MTERROR.DeleteActivityBeforeEndTime.des,
                        error_code=MTERROR.DeleteActivityBeforeEndTime.code)
        else:
            session.delete(activity)
            session.commit()
        return dict(is_success=True,
                    shop_id=activity.shop_id,
                    act_id=activity.act_id)
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))


def get_acitvites_by_createtime(shop_id, offset, limit, show_history=True):
    dbsession = DBSession()
    total_num = dbsession.query(FD_T_Activity).filter(FD_T_Activity.shop_id == shop_id).count()
    activites = dbsession.query(FD_T_Activity).filter(FD_T_Activity.shop_id == shop_id)
    if not show_history:
        activites = activites.filter(FD_T_Activity.end_time > datetime.datetime.now())
    activites = activites.order_by(
        FD_T_Activity.publish_time.desc())[offset: offset + limit]
    return dict(is_success=True,
                total_num=total_num,
                activities=[dict(i.dict(), **{'index': int(offset + index + 1)}) for index, i in enumerate(activites)])


def is_user_fans_a_shop(user_id, shop_id):
    dbsession = DBSession()
    num = dbsession.query(FD_T_Fans).filter(FD_T_Fans.shop_id == shop_id, FD_T_Fans.user_id == user_id).count()
    if num > 0:
        return {'success': True, 'res': 1}
    else:
        return {'success': True, 'res': 0}


def get_favorite_goods_num(user_id, shop_id):
    dbsession = DBSession()
    r = dbsession.query(sqlalchemy.func.count(FD_T_Favorite.goods_id)) \
        .outerjoin(FD_T_Goods, FD_T_Favorite.goods_id == FD_T_Goods.goods_id) \
        .filter(FD_T_Favorite.user_id == user_id).filter(FD_T_Goods.shop_id == shop_id)
    return r[0]


def get_shop_fans(shop_id, offset=0, limit=None):
    """
    select ff.user_id, fu.`name`, fv.visit_count, count(fg.goods_id) as num
    from fd_t_fans ff
    left join fd_t_user fu on ff.user_id = fu.user_id
    left join fd_t_visitedshop fv on ff.user_id = fv.user_id

    left join fd_t_favorite ffa on ff.user_id = ffa.user_id
    left join fd_t_goods fg on ffa.goods_id = fg.goods_id

    where ff.shop_id = 10061
    and (fv.shop_id = 10061 or isnull(fv.shop_id))
    and (fg.shop_id = 10061 or isnull(fg.shop_id))
    GROUP BY ff.user_id"""
    dbsession = DBSession()
    total_num = dbsession.query(FD_T_Fans).filter(FD_T_Fans.shop_id == shop_id).count()
    fans = dbsession.query(FD_T_Fans.user_id, FD_T_User.name, FD_T_Visitedshop.visit_count,
                           FD_T_Visitedshop.last_visit_time,
                           FD_T_User.portrait_url) \
        .outerjoin(FD_T_User, FD_T_User.user_id == FD_T_Fans.user_id) \
        .outerjoin(FD_T_Visitedshop, FD_T_Visitedshop.user_id == FD_T_User.user_id) \
        .filter(FD_T_Fans.shop_id == shop_id) \
        .filter(or_(FD_T_Visitedshop.shop_id == shop_id, FD_T_Visitedshop.shop_id.is_(None))) \
        .group_by(FD_T_Fans.user_id)
    if limit is not None:
        fans = fans[offset: offset + limit]
    return dict(total_num=total_num,
                is_success=True,
                fans=[dict(user_id=i[0],
                           user_name=i[1],
                           user_visit_num=i[2],
                           user_favorite_num=get_favorite_goods_num(i[0], shop_id),
                           user_last_visitime=trans.datetime_to_string(i[3]),
                           portrait_url=ImageHost + i[4] if i[4] else None,
                           index=j + offset + 1) for j, i in enumerate(fans)])

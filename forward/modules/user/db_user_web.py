# -*- encoding: utf-8 -*-
from forward.modules.user.handler_shopping import dao

__author__ = 'Mohanson'

from xpinyin import Pinyin

from forward.common.tools import piclist_to_fulllist
from forward.modules.mt.shop.db_shop import *
from forward.common.define import OSS_URL_PRIFIX
from forward.modules.user.error import FD_USER_NOERR
from forward.config import CONFIG
import sys


def get_account_info(id):
    dbsession = DBSession()
    try:
        account = dbsession.query(FD_T_Account).filter(FD_T_Account.acc_id == id).one()
    except:
        return {'err': FD_USER_NOERR}
    return account.dict()


def get_user_friends_by_initial_words(user_id):
    dbsession = DBSession()
    friends = dbsession.query(FD_T_Friend).filter(FD_T_Friend.user_id == user_id).all()
    friends = [i.dict() for i in friends]

    friends = dbsession.query(FD_T_Friend.friend_id, FD_T_Friend.friend_name, FD_T_User.gender, FD_T_User.mcode,
                              FD_T_User.qrcode,
                              FD_T_User.phone_no, FD_T_User.email, FD_T_User.portrait_url, FD_T_User.city_id,
                              FD_T_Citycode.city_name,
                              FD_T_User.name, FD_T_User.birthday) \
        .outerjoin(FD_T_User, FD_T_User.user_id == FD_T_Friend.friend_id) \
        .outerjoin(FD_T_Citycode, FD_T_User.city_id == FD_T_Citycode.city_id) \
        .filter(FD_T_Friend.user_id == user_id).distinct()
    friends = [{'friend_id': i[0],
                'friend_name': i[1],
                'gender': i[2],
                'mcode': i[3],
                'qrcode': i[4],
                'phone_no': i[5],
                'email': i[6],
                'portrait_url': OSS_URL_PRIFIX + i[7] if i[7] else OSS_URL_PRIFIX + CONFIG.PORTRAIT_URL,
                'city_id': i[8],
                'city_name': i[9],
                'name': i[10],
                'birthday': i[11].strftime('%Y-%m-%d %H:%M:%S:%f') if i[11] else None} for i in friends]

    friends_cate = {}
    p = Pinyin()
    for i in friends:
        if i['friend_name']:
            initial_word = p.get_initial(i['friend_name'][0]).upper()
            if initial_word not in friends_cate:
                friends_cate[initial_word] = []
            friends_cate[initial_word].append(i)
        else:
            initial_word = p.get_initial(i['name'][0]).upper()
            if initial_word not in friends_cate:
                friends_cate[initial_word] = []
            friends_cate[initial_word].append(i)

    return {
        'total_num': len(friends),
        'friends': friends_cate,
    }


def get_user_favorite_goods(user_id, offset, limit):
    dbsession = DBSession()
    goods = dbsession.query(FD_T_Favorite.goods_id, FD_T_Goods.description,
                            FD_T_Goods.price, FD_T_Goods.promotion_price,
                            FD_T_Goods.pic_url_list, FD_T_Goods.basic_info,
                            FD_T_Goods.status) \
        .join(FD_T_Goods, FD_T_Goods.goods_id == FD_T_Favorite.goods_id) \
        .filter(FD_T_Favorite.user_id == user_id).all()
    total_num = len(goods)
    return {
        'total_num': total_num,
        'goods': [{'id': i[0],
                   "desp": i[1],
                   "price": float(i[2]) if i[2] else None,
                   "promot": float(i[3]) if i[3] else None,
                   "picList": piclist_to_fulllist(i[4]),
                   "basic": i[5],
                   "status": i[6]
                   } for i in goods[offset: offset + limit]]}


def get_goods_by_shops(shop_ids, offset, count):
    shop_ids = trans.to_list(shop_ids)
    ret = {'total_num': len(shop_ids), 'shops': []}
    for shop_id in shop_ids:
        goods_list = dao.queryGoodsByPage(int(shop_id), int(offset), int(count))
        shop_name = get_shop_info(shop_id)['shop_name']
        ret['shops'].append({'shop_id': shop_id, 'shop_name': shop_name, 'goods': goods_list})
    return ret


def get_user_info_by_miumiu_or_phone(num):
    session = DBSession()
    if num.startswith('m'):
        aim_users = session.query(FD_T_User, FD_T_Citycode.city_name).outerjoin(FD_T_Citycode,
                                                                                FD_T_Citycode.city_id == FD_T_User.city_id).filter(
            FD_T_User.mcode == num).all()
        return {
            'is_success': True,
            'total_num': len(aim_users),
            'users': [dict(i[0].dict(), **{'city_name': i[1]}) for i in aim_users]
        }
    elif num.isdigit() and len(num) == 11:
        aim_users = session.query(FD_T_User, FD_T_Citycode.city_name).outerjoin(FD_T_Citycode,
                                                                                FD_T_Citycode.city_id == FD_T_User.city_id).filter(
            FD_T_User.phone_no == num).all()
        return {
            'is_success': True,
            'total_num': len(aim_users),
            'users': [dict(i[0].dict(), **{'city_name': i[1]}) for i in aim_users]
        }
    else:
        return {
            'is_success': False,
            'des': 'there is no your friend, happy?'
        }


def modify_friend_remark(user_id, friend_id, remark):
    session = DBSession()
    try:
        friend = session.query(FD_T_Friend).filter(FD_T_Friend.user_id == user_id,
                                                   FD_T_Friend.friend_id == friend_id).one()
    except MultipleResultsFound, e:
        return dict(is_success=False, des='there is not this friend')
    except NoResultFound, e:
        return dict(is_success=False, des='there is not this friend')
    friend.friend_name = remark
    session.commit()
    session.close()
    return dict(is_success=True)


def query_favorite_goods_news(idlist):
    dbsession = DBSession()

    goods = dbsession.query(FD_T_Goods.goods_id,
                            FD_T_Goods.description,
                            FD_T_Goods.price, FD_T_Goods.promotion_price,
                            FD_T_Goods.pic_url_list, FD_T_Goods.basic_info,
                            FD_T_Goods.status) \
        .filter(FD_T_Goods.goods_id.in_(idlist)).all()

    return {
        'goods': [{'id': i[0],
                   "desp": i[1],
                   "price": float(i[2]) if i[2] else None,
                   "promot": float(i[3]) if i[3] else None,
                   "picList": piclist_to_fulllist(i[4]),
                   "basic": i[5],
                   "status": i[6]
                   } for i in goods]}


def get_userful_shop_num(city_id, category):
    dbsession = DBSession()

    count = dbsession.query(FD_T_Shop).filter(FD_T_Shop.city_id == city_id).filter(FD_T_Shop.status == 2)
    if category:
        count = count.filter(category in FD_T_Shop.category_list)

    return count.count()


def get_activity_info(activity_id):
    dbsession = DBSession()
    try:
        actinfo = dbsession.query(FD_T_Activity.begin_time,
                                  FD_T_Activity.end_time,
                                  FD_T_Activity.act_content,
                                  FD_T_Activity.shop_id,
                                  FD_T_Shop.shop_name,
                                  FD_T_Shop.pic_url_list,
                                  FD_T_Activity.act_title).outerjoin(FD_T_Shop,
                                                                     FD_T_Shop.shop_id == FD_T_Activity.shop_id) \
            .filter(FD_T_Activity.act_id == activity_id).one()
        a = {
            'actID': activity_id,
            'err': 0,
            'bt': actinfo[0].strftime('%Y-%m-%d %H:%M:%S:%f'),
            'et': actinfo[1].strftime('%Y-%m-%d %H:%M:%S:%f'),
            'content': actinfo[2],
            'shopID': int(actinfo[3]),
            'shopName': actinfo[4],
            'shopPic': piclist_to_fulllist(actinfo[5]),
            'title': actinfo[6]
        }
    except:
        a = {'err': 1, 'des': sys.exc_info()[1]}
    return a


def select_phone_type_list(phone, phone_list):
    phone_list = [str(i) for i in phone_list if i.strip()]
    dbsession = DBSession()
    return_info = {'platform_friend': [], 'platform_notfriend': [], 'notplatform': []}

    try:
        platform_phone_list = dbsession.query(FD_T_Account.phone_no).filter(FD_T_Account.phone_no.in_(phone_list))
        platform_phone_list = [str(i[0]) for i in platform_phone_list]
        return_info['notplatform'] = [i for i in phone_list if i not in platform_phone_list]

        user_id = dbsession.query(FD_T_User.user_id).filter(FD_T_User.phone_no == phone)[0]

        friend_list = dbsession.query(FD_T_Friend.friend_id).filter(FD_T_Friend.user_id == user_id).all()
        friend_list = [str(i[0]) for i in friend_list]

        platform_friend_list = [i for i in friend_list if i in platform_phone_list]
        
        # platform_friend_list = dbsession.query(FD_T_User.phone_no).outerjoin(FD_T_Friend,
        # FD_T_User.user_id == FD_T_Friend.friend_id).filter(
        #     FD_T_User.phone_no.in_(platform_phone_list)).filter(FD_T_Friend.user_id == user_id).all()
        # platform_friend_list = [str(i[0]) for i in platform_friend_list]
        return_info['platform_friend'] = platform_friend_list

        return_info['platform_notfriend'] = [str(i) for i in platform_phone_list if i not in platform_friend_list]

        return_info['is_success'] = True
        return return_info
    except Exception as e:
        mt_log.exception(e)
        return_info['is_success'] = False
        return return_info


if __name__ == '__main__':
    pass

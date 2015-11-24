# -*- encoding: utf-8 -*-
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from forward.common.tools import piclist_to_fulllist
from forward.log import mt_log
from forward.modules.mt.error_code import MTERROR

__author__ = 'Mohanson'

from forward.common.define import *
from forward.db.tables_define import *
from forward.modules.mt.base.db_base import get_newaccountid
from forward.modules.mt.settings import ImageHost


def sign_newaccount(account, password):
    dbsession = DBSession()
    # table fd_t_account
    if is_merchant_exist(account)['is_exist']:
        return {'is_success': False, 'des': 'account is already exist!'}
    shop_id = get_newaccountid()
    newaccount = FD_T_Account(acc_id=shop_id, acc_type=FD_ACCOUNT_TYPE_MERCHANT, account=account, password=password,
                              phone_no=None, auth_mode=FD_AUTH_MODE_ACCOUNT, open_id=None,
                              register_time=datetime.datetime.now())
    dbsession.add(newaccount)
    # table fd_t_fansmessageconfig
    fansmsgconfig = FD_T_Fansmessageconfig(shop_id=shop_id, current_p2p_count=0, p2p_remain_count=0, next_p2p_count=0,
                                           current_mass_count=0, mass_remain_count=0, next_mass_count=0)
    dbsession.add(fansmsgconfig)

    dbsession.commit()
    return {'is_success': True, 'shop_id': shop_id}


def get_merchant_basicinfo(shop_id):
    session = DBSession()
    try:
        merchantinfo = session.query(FD_T_Shopaccount).filter(FD_T_Shopaccount.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    return dict(shop_id=merchantinfo.shop_id,
                contact_name=merchantinfo.contact_name,
                contact_phone_no=merchantinfo.contact_phone_no,
                contact_email=merchantinfo.contact_email,
                contact_qq=merchantinfo.contact_qq,
                portrait_url=ImageHost + merchantinfo.portrait_url if merchantinfo.portrait_url else None)


def modify_merchant_basicinfo(shop_id, contact_name=None, contact_phone_no=None, contact_email=None,
                              contact_qq=None, portrait_url=None):
    session = DBSession()
    try:
        merchantinfo = session.query(FD_T_Shopaccount).filter(FD_T_Shopaccount.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    if contact_name:
        merchantinfo.contact_name = contact_name
    if contact_phone_no:
        merchantinfo.contact_phone_no = contact_phone_no
    if contact_email:
        merchantinfo.contact_email = contact_email
    if contact_qq:
        merchantinfo.contact_qq = contact_qq
    if portrait_url:
        # 同步修改讨论组头像
        merchantinfo.portrait_url = portrait_url
        forums = session.query(FD_T_Forum).filter(FD_T_Forum.forum_id == 'shop_' + str(shop_id)).all()
        for forum in forums:
            forum.forum_pic = piclist_to_fulllist(portrait_url)
    session.commit()
    return dict(is_success=True, shop_id=merchantinfo.shop_id)


def get_merchant_serviceinfo(shop_id):
    session = DBSession()
    try:
        merchantinfo = session.query(FD_T_Shopaccount).filter(FD_T_Shopaccount.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    return dict(shop_id=shop_id,
                service_balance=float(merchantinfo.service_balance),
                # last_pay_time=merchantinfo.last_pay_time,
                # last_pay_money=merchantinfo.last_pay_money,
                service_deadline=merchantinfo.service_deadline.strftime(
                    '%Y-%m-%d %H:%M:%S:%f') if merchantinfo.service_deadline else None,
                service_status=merchantinfo.service_status)


def is_merchant_exist(account):
    session = DBSession()
    num = session.query(FD_T_Account).filter(FD_T_Account.account == account).count()
    if num:
        return dict(is_exist=True)
    else:
        return dict(is_exist=False)


def sign_merchant(account, password, contact_name, contact_phone_no, contact_email,
                  contact_qq,
                  shop_name, brand_name, business_hours, telephone_no, city_id,
                  district_id, business_area, address, longitude, latitude,
                  category_list):
    if not is_merchant_exist(account)['is_exist']:
        session = DBSession()
        # geo = GEO()
        try:
            shop_id = get_newaccountid()
            new_account = FD_T_Account(acc_id=shop_id,
                                       acc_type=FD_ACCOUNT_TYPE_MERCHANT,
                                       account=account,
                                       password=password,
                                       auth_mode=FD_AUTH_MODE_ACCOUNT,
                                       phone_no=contact_phone_no,
                                       register_time=datetime.datetime.now(),
                                       )
            session.add(new_account)
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
                                 district_id=district_id, business_area=business_area, address=address,
                                 longitude=longitude, latitude=latitude, category_list=category_list,
                                 qrcode='http://www.immbear.com/shop/' + str(shop_id),
                                 status=1)
            fansmsgconfig = FD_T_Fansmessageconfig(shop_id=shop_id, current_p2p_count=0, p2p_remain_count=0,
                                                   next_p2p_count=0,
                                                   current_mass_count=0, mass_remain_count=0, next_mass_count=0)
            session.add(fansmsgconfig)
            session.add(new_shop)
            session.commit()
            return dict(is_success=True, shop_id=new_merchant.shop_id)
        except Exception, e:
            mt_log.exception(e)
            session.rollback()
            return dict(error_code=MTERROR.RegisterFailed.code, des=MTERROR.RegisterFailed.des, is_success=False)
        finally:
            session.close()
    else:
        return dict(is_success=False, error_code=MTERROR.RegisterFailed.code, des=MTERROR.RegisterFailed.des)


def modify_merchant_password(shop_id, old_password, new_password, need_old_password=True):
    session = DBSession()
    try:
        account = session.query(FD_T_Account).filter(FD_T_Account.acc_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    if need_old_password:
        if old_password == account.password:
            if len(new_password) != 16 and len(new_password) != 32:
                return dict(error_code=MTERROR.PasswordCheckError.code, des=MTERROR.PasswordCheckError.des)
            else:
                account.password = new_password
                session.commit()
                return dict(is_success=True, shop_id=shop_id)
        else:
            session.close()
            return dict(error_code=MTERROR.ModifyPasswordError.code, des=MTERROR.ModifyPasswordError.des)
    else:
        account.password = new_password
        session.commit()
        return dict(is_success=True, shop_id=shop_id)


def login(account, password):
    dbsession = DBSession()
    try:
        merchant = dbsession.query(FD_T_Account.acc_id, FD_T_Shopaccount.portrait_url).filter(
            FD_T_Account.account == account,
            FD_T_Shopaccount.shop_id == FD_T_Account.acc_id,
            FD_T_Account.password == password,
            FD_T_Account.auth_mode == 1,
            FD_T_Account.acc_type == FD_ACCOUNT_TYPE_MERCHANT).one()
        merchant_info = get_merchant_serviceinfo(merchant[0])
        merchant_service_status = merchant_info.get('service_status', '1')
    except MultipleResultsFound, e:
        return dict(is_success=False, error_code=MTERROR.AuthError.code, des=MTERROR.AuthError.des)
    except NoResultFound, e:
        return dict(is_success=False, error_code=MTERROR.AuthError.code, des=MTERROR.AuthError.des)
    except Exception, e:
        return dict(is_success=False, error_code=MTERROR.AuthError.code, des=MTERROR.AuthError.des)
    else:
        return dict(is_success=True,
                    shop_id=merchant[0],
                    portrait_url=ImageHost + merchant[1] + '@100w_100h.jpg' if merchant[1] else None,
                    merchant_service_status=merchant_service_status)


def get_fansmessageconfig(shop_id):
    dbsession = DBSession()
    try:
        fansmsgc = dbsession.query(FD_T_Fansmessageconfig).filter(FD_T_Fansmessageconfig.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(is_success=False, error_code=MTERROR.AuthError.code, des=MTERROR.AuthError.des)
    except NoResultFound, e:
        return dict(is_success=False, error_code=MTERROR.AuthError.code, des=MTERROR.AuthError.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
    return fansmsgc.dict()


def desc_fansmessageconfig(shop_id, tp):
    dbsession = DBSession()
    try:
        fansmsgc = dbsession.query(FD_T_Fansmessageconfig).filter(FD_T_Fansmessageconfig.shop_id == shop_id).one()
    except MultipleResultsFound, e:
        return dict(is_success=False, error_code=MTERROR.AuthError.code, des=MTERROR.AuthError.des)
    except NoResultFound, e:
        return dict(is_success=False, error_code=MTERROR.AuthError.code, des=MTERROR.AuthError.des)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
    if tp == 'p2p':
        fansmsgc.p2p_remain_count -= 1
        dbsession.commit()
        return dict(is_success=True, shop_id=shop_id, remain=fansmsgc.p2p_remain_count)
    if tp == 'mass':
        fansmsgc.mass_remain_count -= 1
        dbsession.commit()
        return dict(is_success=True, shop_id=shop_id, remain=fansmsgc.mass_remain_count)


def desc_fansmessageconfig_p2p(shop_id):
    return desc_fansmessageconfig(shop_id, 'p2p')


def desc_fansmessageconfig_mass(shop_id):
    return desc_fansmessageconfig(shop_id, 'mass')


# 忘记密码部分
def is_account_or_phone_exist(str, type):
    dbsession = DBSession()
    query = dbsession.query(FD_T_Account)
    if type == 'phone':
        try:
            account = query.filter(FD_T_Account.phone_no == str).one()
        except MultipleResultsFound:
            return dict(is_exist=False, is_success=False, error_code=MTERROR.MultipleResultsFound.code,
                        des=MTERROR.MultipleResultsFound.des)
        except NoResultFound, e:
            return dict(is_exist=False, is_success=False, error_code=MTERROR.NoResultFound.code,
                        des=MTERROR.NoResultFound.des)
        except Exception, e:
            return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
        return dict(is_exist=True, phone=account.phone_no, shop_id=account.acc_id)
    if type == 'account':
        try:
            account = query.filter(FD_T_Account.account == str).one()
        except MultipleResultsFound, e:
            return dict(is_exist=False, is_success=False, error_code=MTERROR.MultipleResultsFound.code,
                        des=MTERROR.MultipleResultsFound.des)
        except NoResultFound, e:
            return dict(is_exist=False, is_success=False, error_code=MTERROR.NoResultFound.code,
                        des=MTERROR.NoResultFound.des)
        except Exception, e:
            return dict(error_code=MTERROR.UnKnowError.code, des=str(e))
        return dict(is_exist=True, phone=account.phone_no, shop_id=account.acc_id)
    else:
        return dict(is_exist=False)
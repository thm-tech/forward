# coding:utf-8
import datetime
import functools

from sqlalchemy import create_engine, Column
from sqlalchemy import (
    Integer as INT32,
    String,
    BigInteger as INT64,
    SmallInteger as INT8,
    Text,
    DATETIME,
    DECIMAL,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from forward.config import CONFIG
from forward.modules.mt.settings import ImageHost
from forward.common.define import OSS_URL_PRIFIX
from forward.common import trans


IMG_URL_LEN = 512
ADDRESS_LEN = 512

GRO_PRECISION = 10
GRO_SCALE = 6

engine = create_engine(CONFIG.SQLALCHEMY.URL, **CONFIG.SQLALCHEMY.SETTINGS)

Base = declarative_base()


def transaction(func):
    """
    If decorator and func has no error, session will commit(); else rollback()

        @transaction
        def my_function(session): ...

        if __name__ == '__main__':
            my_function(session=None, persist=None)

    :param: persist: True: commit(); False: rollback(); None: do nothing, keep the session, you
        should close it selfish.
    :param: session, default is DBsession() else use your session
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        persist = kwargs.pop('persist', True)
        session = kwargs.pop('session', DBSession())
        if session is None:
            session = DBSession()
        try:
            result = func(session=session, *args, **kwargs)
        except Exception as e:
            session.rollback()
            session.close()
            raise
        else:
            if persist is False:
                session.rollback()
            elif persist is True:
                session.commit()
            session.close()
            return result

    return wrapper


# 1
class FD_T_Sequence(Base):
    __tablename__ = 'fd_t_sequence'

    sequence_name = Column(String(64), nullable=False, primary_key=True)
    current_value = Column(INT64, nullable=False)
    increment_value = Column(INT32, nullable=False, default=1)

    def __init__(self, name, current_value, increment_value):
        self.name = name
        self.current_value = current_value
        self.increment_value = increment_value

    def dict(self):
        return {
            'sequence_name': self.sequence_name,
            'current_value': self.current_value,
            'increment_value': self.increment_value,
        }

    def __repr__(self):
        return str(self.dict())


# 2
class FD_T_Companybankaccount(Base):
    __tablename__ = 'fd_t_companybankaccount'

    account_type = Column(INT32, nullable=False, primary_key=True)
    bank_account = Column(String(64))
    bank_name = Column(String(64))
    account_holder = Column(String(64))


# 3
class FD_T_Goodscategory(Base):
    __tablename__ = 'fd_t_category'

    id = Column(INT32, nullable=False, primary_key=True)
    name = Column(String(64))
    parent_id = Column(INT32)
    cate_line = Column(Text)

    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'cate_line': self.cate_line,
        }

    def __repr__(self):
        return str(self.dict())


# 4
class FD_T_Shop(Base):
    __tablename__ = 'fd_t_shop'

    shop_id = Column(INT64, nullable=False, primary_key=True)
    brand_name = Column(String(64))
    shop_name = Column(String(256))
    qrcode = Column(String(256))
    business_hours = Column(String(64))
    telephone_no = Column(String(64))
    city_id = Column(INT8)
    district_id = Column(INT8)
    business_area = Column(String(64))
    address = Column(String(256))
    longitude = Column(DECIMAL(10, 6))
    latitude = Column(DECIMAL(10, 6))
    pic_url_list = Column(Text)
    category_list = Column(String(64))
    status = Column(INT8)
    introduction = Column(Text)

    def dict(self):
        return {
            'shop_id': self.shop_id,
            'brand_name': self.brand_name,
            'shop_name': self.shop_name,
            'qrcode': self.qrcode,
            'business_hours': self.business_hours,
            'telephone_no': self.telephone_no,
            'city_id': self.city_id,
            'district_id': self.district_id,
            'business_area': self.business_area,
            'address': self.address,
            'longitude': float(self.longitude),
            'latitude': float(self.latitude),
            'pic_url_list': self.pic_url_list,
            'category_list': self.category_list,
            'status': self.status,
            'introduction': self.introduction,
        }

    def __repr__(self):
        return str(self.dict())


# 5
class FD_T_Shopaccount(Base):
    __tablename__ = 'fd_t_shopaccount'

    shop_id = Column(INT64, nullable=False, primary_key=True)
    contact_name = Column(String(64))
    contact_phone_no = Column(String(32))
    contact_email = Column(String(128))
    contact_qq = Column(String(64))
    service_balance = Column(DECIMAL(12, 2))
    # last_pay_time = Column(DATETIME)
    # last_pay_money = Column(DECIMAL(12, 2))
    service_deadline = Column(DATETIME)
    service_status = Column(INT8)
    portrait_url = Column(String)

    def dict(self):
        return {
            'shop_id': self.shop_id,
            'contact_name': self.contact_name,
            'contact_phone_no': self.contact_phone_no,
            'contact_email': self.contact_email,
            'contact_qq': self.contact_qq,
            'service_balance': float(self.service_balance),
            'service_deadline': self.service_deadline.strftime(
                '%Y-%m-%d %H:%M:%S:%f') if self.service_deadline else None,
            'service_status': self.service_status,
            'portrait_url': self.portrait_url,
        }

    def __repr__(self):
        return str(self.dict())


# 6
class FD_T_Shoppayrecord(Base):
    __tablename__ = 'fd_t_shoppayrecord'

    id = Column(INT64, nullable=False, primary_key=True)
    shop_id = Column(INT64)
    pay_time = Column(DATETIME)
    pay_money = Column(DECIMAL(12, 2))

    def dict(self):
        return {
            'id': self.id,
            'shop_id': self.shop_id,
            'pay_time': self.pay_time.strftime('%Y-%m-%d %H:%M:%S:%f'),
            'pay_money': float(self.pay_money)
        }

    def __repr__(self):
        return str(self.dict())


# 7
class FD_T_User(Base):
    __tablename__ = 'fd_t_user'

    user_id = Column(INT64, nullable=False, primary_key=True)
    name = Column(String(32))
    gender = Column(INT8)
    birthday = Column(DATETIME)
    mcode = Column(String(32))
    qrcode = Column(String(64))
    phone_no = Column(String(32))
    email = Column(String(64))
    portrait_url = Column(String(512))
    city_id = Column(INT32)

    def dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'gender': self.gender,
            'birthday': self.birthday.strftime('%Y-%m-%d %H:%M:%S:%f') if self.birthday else None,
            'mcode': self.mcode,
            'qrcode': self.qrcode,
            'phone_no': self.phone_no,
            'email': self.email,
            'portrait_url': [OSS_URL_PRIFIX + i for i in trans.to_list(self.portrait_url) if i],
            'city_id': self.city_id
        }


# 8
class FD_T_Account(Base):
    __tablename__ = 'fd_t_account'

    acc_id = Column(INT64, nullable=False, primary_key=True)
    acc_type = Column(INT8)
    account = Column(String(64))
    password = Column(String(64))
    phone_no = Column(String(32))
    auth_mode = Column(INT8)
    open_id = Column(Text)
    register_time = Column(DATETIME)

    def dict(self):
        return dict(acc_id=self.acc_id,
                    acc_type=self.acc_type,
                    account=self.account,
                    phone_no=self.phone_no,
                    auth_mode=self.auth_mode,
                    open_id=self.open_id,
                    register_time=self.register_time.strftime('%Y-%m-%d %H:%M:%S:%f'))

    def __repr__(self):
        return str(self.dict())


# 11
class FD_T_Goods(Base):
    __tablename__ = 'fd_t_goods'

    goods_id = Column(INT64, nullable=False, primary_key=True)
    category_list = Column(Text)
    description = Column(String(256))
    detail = Column(String(256))
    bar_code = Column(String(256))
    price = Column(DECIMAL(12, 2))
    promotion_price = Column(DECIMAL(12, 2))
    pic_url_list = Column(Text)
    brand_name = Column(String(64))
    basic_info = Column(Text)
    shop_id = Column(INT64, ForeignKey('fd_t_shop.shop_id'))
    publish_time = Column(DATETIME)
    status = Column(INT8)
    remark = Column(Text)

    shop = relationship("FD_T_Shop", backref=backref('goods', order_by=goods_id))

    def dict(self):
        return {
            'goods_id': self.goods_id,
            'category_list': self.category_list,
            'description': self.description,
            'detail': self.detail,
            'bar_code': self.bar_code,
            'price': float(self.price) if self.price else self.price,
            'promotion_price': float(self.promotion_price) if self.promotion_price else self.promotion_price,
            'pic_url_list': self.pic_url_list,
            'brand_name': self.brand_name,
            'basic_info': self.basic_info,
            'shop_id': self.shop_id,
            'publish_time': self.publish_time.strftime('%Y-%m-%d %H:%M:%S:%f') if self.publish_time else self.publish_time,
            'status': self.status,
        }

    def __repr__(self):
        return str(self.dict())


# 12
class FD_T_Goodsstandard(Base):
    __tablename__ = 'fd_t_goodsstandard'

    id = Column(INT64, nullable=False, primary_key=True)
    goods_id = Column(INT64, ForeignKey('fd_t_goods.goods_id'))
    stand_key = Column(Text)
    stand_value = Column(Text)
    price = Column(DECIMAL(12, 2))
    promotion_price = Column(DECIMAL(12, 2))

    goods = relationship("FD_T_Goods", backref=backref('standards', order_by=id))

    def dict(self):
        return {
            'id': self.id,
            'goods_id': self.goods_id,
            'stand_key': self.stand_key,
            'stand_value': self.stand_value,
            'price': float(self.price),
            'promotion_price': float(self.promotion_price),
        }

    def __repr__(self):
        return str(self.dict())


# 14
class FD_T_Activity(Base):
    __tablename__ = 'fd_t_activity'

    act_id = Column(INT32, nullable=False, primary_key=True)
    act_title = Column(String)
    act_content = Column(Text)
    begin_time = Column(DATETIME)
    end_time = Column(DATETIME)
    shop_id = Column(INT32)
    publish_time = Column(DATETIME)

    def dict(self):
        return dict(act_id=int(self.act_id),
                    act_title=self.act_title,
                    act_content=self.act_content,
                    begin_time=self.begin_time.strftime('%Y-%m-%d %H:%M:%S:%f'),
                    end_time=self.end_time.strftime('%Y-%m-%d %H:%M:%S:%f'),
                    shop_id=int(self.shop_id),
                    publish_time=self.publish_time.strftime('%Y-%m-%d %H:%M:%S:%f'))

    def __repr__(self):
        return str(self.dict())


# 17
class FD_T_Favorite(Base):
    __tablename__ = 'fd_t_favorite'

    user_id = Column(INT64, nullable=False, primary_key=True)
    goods_id = Column(INT64, ForeignKey('fd_t_goods.goods_id'))

    goods = relationship("FD_T_Goods", backref=backref('favorites', order_by=user_id))


# 18
class FD_T_Fans(Base):
    __tablename__ = 'fd_t_fans'

    user_id = Column(INT64, nullable=False, primary_key=True)
    shop_id = Column(INT64, ForeignKey('fd_t_shop.shop_id'))
    join_time = Column(DATETIME)
    push_message_enable = Column(INT8)

    shop = relationship("FD_T_Shop", backref=backref('fans', order_by=join_time))

    def dict(self):
        return dict(user_id=self.user_id,
                    shop_id=self.shop_id,
                    join_time=self.join_time.strftime('%Y-%m-%d %H:%M:%S:%f'),
                    push_message_enable=self.push_message_enable)

    def __repr__(self):
        return str(self.dict())


class FD_T_Visitedshop(Base):
    __tablename__ = 'fd_t_visitedshop'

    user_id = Column(INT32, primary_key=True, nullable=False)
    shop_id = Column(INT32)
    visit_count = Column(INT32)
    last_visit_time = Column(DATETIME)

    def dict(self):
        return dict(user_id=self.user_id,
                    shop_id=self.shop_id,
                    visit_count=self.visit_count,
                    last_visit_time=self.last_visit_time.strftime('%Y-%m-%d %H:%M:%S:%f'))

    def __repr__(self):
        return str(self.dict())


# 26
class FD_T_Citycode(Base):
    __tablename__ = 'fd_t_citycode'

    id = Column(INT64, nullable=False, primary_key=True)
    city_id = Column(INT32, nullable=False)
    city_name = Column(String(64))
    district_id = Column(INT32)
    district_name = Column(String(64))
    province_id = Column(INT32)
    province_name = Column(String(64))
    country_id = Column(INT32)
    country_name = Column(String(64))
    is_support = Column(INT8)

    def dict(self):
        return {
            'id': self.id,
            'city_id': self.city_id,
            'city_name': self.city_name,
            'district_id': self.district_id,
            'district_name': self.district_name,
            'province_id': self.province_id,
            'province_name': self.province_name,
            'country_id': self.country_id,
            'country_name': self.country_name,
            'is_support': self.is_support,
        }

    def __repr__(self):
        return str(self.dict())


# 30
class FD_T_Companyinfo(Base):
    __tablename__ = 'fd_t_companyinfo'

    name = Column(String(64), primary_key=True)
    phone_no_list = Column(String(64))
    email = Column(String(64))
    introduction = Column(Text)
    disclaimer = Column(Text)

    def dict(self):
        return {
            'name': self.name,
            'phone_no_list': self.phone_no_list,
            'email': self.email,
            'introduction': self.introduction,
            'disclaimer': self.disclaimer,
        }

    def __repr__(self):
        return str(self.dict())


class FD_T_Fansmessageconfig(Base):
    __tablename__ = 'fd_t_fansmessageconfig'

    shop_id = Column(INT32, primary_key=True, nullable=False)
    current_p2p_count = Column(INT32)
    p2p_remain_count = Column(INT32)
    next_p2p_count = Column(INT32)
    current_mass_count = Column(INT32)
    mass_remain_count = Column(INT32)
    next_mass_count = Column(INT32)

    def dict(self):
        return {
            'shop_id': self.shop_id,
            'current_p2p_count': self.current_p2p_count,
            'p2p_remain_count': self.p2p_remain_count,
            'next_p2p_count': self.next_p2p_count,
            'current_mass_count': self.current_mass_count,
            'mass_remain_count': self.mass_remain_count,
            'next_mass_count': self.next_mass_count,
        }

    def __repr__(self):
        return str(self.dict())


class FD_T_Fansmessage(Base):
    __tablename__ = 'fd_t_fansmessage'
    id = Column(INT32, primary_key=True)
    shop_id = Column(INT32)
    user_id = Column(INT32)
    message = Column(Text)
    push_time = Column(DATETIME)

    def dict(self):
        return {
            'id': self.id,
            'shop_id': self.shop_id,
            'user_id': self.user_id,
            'message': self.message,
            'push_time': self.push_time.strftime('%Y-%m-%d %H:%M:%S:%f'),
        }

    def __repr__(self):
        return str(self.dict())

    @staticmethod
    def post(dbsession, shop_id, user_id, message, push_time):
        msg = FD_T_Fansmessage(id=None, shop_id=shop_id, user_id=user_id, message=message, push_time=push_time)
        dbsession.add(msg)


class FD_T_Phoneauth(Base):
    __tablename__ = 'fd_t_phoneauth'
    phone_no = Column(String, primary_key=True)
    auth_code = Column(String)
    auth_deadline = Column(DATETIME)

    def dict(self):
        return {
            'phone_no': self.phone_no,
            'auth_code': self.auth_code,
            'auth_deadline': self.auth_deadline.strftime('%Y-%m-%d %H:%M:%S:%f'),
        }

    def __repr__(self):
        return str(self.dict())

    @staticmethod
    def post_or_put(dbsession, phone_no, auth_code):
        auth_deadline = datetime.datetime.now() + datetime.timedelta(hours=1)
        nums = dbsession.query(FD_T_Phoneauth).filter(FD_T_Phoneauth.phone_no == phone_no).count()
        if nums == 0:
            row = FD_T_Phoneauth(phone_no=phone_no, auth_code=auth_code, auth_deadline=auth_deadline)
            dbsession.add(row)
        elif nums == 1:
            row = dbsession.query(FD_T_Phoneauth).filter(FD_T_Phoneauth.phone_no == phone_no).one()
            row.auth_code = auth_code
            row.auth_deadline = auth_deadline
        else:
            pass


class FD_T_Joinshop(Base):
    __tablename__ = 'fd_t_joinshop'
    shop_id = Column(INT32, primary_key=True, nullable=False)
    shop_name = Column(String(256))
    pic_url = Column(Text)

    def dict(self):
        return {
            'shop_id': int(self.shop_id),
            'shop_name': self.shop_name,
            'pic_url': ImageHost + self.pic_url,
        }


class FD_T_Forum(Base):
    __tablename__ = 'fd_t_forum'
    forum_id = Column(String(256), primary_key=True, nullable=False)
    forum_name = Column(String(32))
    forum_pic = Column(String(512))
    user_id = Column(INT64)
    is_initiator = Column(INT8)
    join_time = Column(DATETIME)

    def dict(self):
        return {
            'forum_id': self.forum_id,
            'forum_name': self.forum_name,
            'forum_pic': self.forum_pic,
            'user_id': self.user_id,
            'is_initiator': self.is_initiator,
            'join_time': self.join_time.strftime('%Y-%m-%d %H:%M:%S:%f')
        }


class FD_T_Friend(Base):
    __tablename__ = 'fd_t_friend'
    user_id = Column(INT32, primary_key=True)
    friend_id = Column(INT32, primary_key=True)
    friend_name = Column(String(256), primary_key=True)

    def dict(self):
        return {
            'user_id': int(self.user_id),
            'friend_id': int(self.friend_id),
            'friend_name': self.friend_name,
        }

class FD_T_Match(Base):
    __tablename__ = 'fd_t_match'
    id = Column(INT64, primary_key=True)
    city_id = Column(INT32)
    gender = Column(INT8)
    age_min = Column(INT32)
    age_max = Column(INT32)
    spare0 = Column(String(256))
    spare1 = Column(String(256))
    spare2 = Column(String(256))
    spare3 = Column(String(256))
    spare4 = Column(String(256))
    spare5 = Column(String(256))
    spare6 = Column(String(256))
    spare7 = Column(String(256))
    user_id = Column(INT64)
    status = Column(INT32)
    time_limit = Column(INT32)
    des = Column(Text)

    def dict(self):
        return {
            'id': self.id,
            'city_id': self.city_id,
            'gender': self.gender,
            'age_min': self.age_min,
            'age_max': self.age_max,
            'spare0': self.spare0,
            'spare1': self.spare1,
            'spare2': self.spare2,
            'spare3': self.spare3,
            'spare4': self.spare4,
            'spare5': self.spare5,
            'spare6': self.spare6,
            'spare7': self.spare7,
            'user_id': self.user_id,
            'status': self.status,
            'time_limit': self.time_limit,
            'des': self.des,
        }

class FD_T_Goodsinfo(Base):
    __tablename__ = 'fd_t_goodsinfo'
    goods_id = Column(INT64, primary_key=True)
    sales_volume = Column(INT32)
    browse_count = Column(INT32)
    attention_count = Column(INT32)
    stock_count = Column(INT32)
    res1 = Column(INT32)
    res2 = Column(INT32)
    res3 = Column(Text)

    def dict(self):
        return {
            'goods_id': self.goods_id,
            'sales_volume': self.sales_volume,
            'browse_count': self.browse_count,
            'attention_count': self.attention_count,
            'stock_count': self.stock_count,
            'res1': self.res1,
            'res2': self.res2,
            'res3': self.res3
        }

DBSession = sessionmaker(bind=engine)
# Base.metadata.create_all(engine)

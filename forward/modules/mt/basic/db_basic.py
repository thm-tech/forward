# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from forward.db.tables_define import *
from forward.modules.mt.error_code import MTERROR


def get_companyinfo():
    session = DBSession()
    try:
        companyinfo = session.query(FD_T_Companyinfo).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des,
                    is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    return dict(name=companyinfo.name,
                phone_no_list=companyinfo.phone_no_list.split(','),
                email=companyinfo.email,
                introduction=companyinfo.introduction,
                disclaimer=companyinfo.disclaimer,
                )


def get_countries():
    session = DBSession()
    countries = session.query(FD_T_Citycode.country_id, FD_T_Citycode.country_name).filter(
        FD_T_Citycode.country_id.isnot(None)).distinct()
    country_list = []
    for country in countries:
        country_list.append(dict(country_id=country.country_id, country_name=country.country_name))
    return dict(total_num=len(country_list),
                countries=country_list, )


def get_provinces(country_id=None, all=False):
    session = DBSession()
    if country_id:
        provinces = session.query(FD_T_Citycode.province_id, FD_T_Citycode.province_name).filter(
            FD_T_Citycode.country_id == country_id, FD_T_Citycode.province_id.isnot(None))
        if not all:
            provinces = provinces.filter(FD_T_Citycode.is_support == 1)
        provinces = provinces.distinct()
    else:
        provinces = session.query(FD_T_Citycode.province_id, FD_T_Citycode.province_name).filter(
            FD_T_Citycode.province_id.isnot(None))
        if not all:
            provinces = provinces.filter(FD_T_Citycode.is_support == 1)
        provinces = provinces.distinct()
    province_list = []
    for province in provinces:
        province_list.append(dict(province_id=province.province_id, province_name=province.province_name))
    return dict(total_num=len(province_list),
                provinces=province_list)


def get_cities(country_id=None, province_id=None, all=False):
    session = DBSession()
    cities = session.query(FD_T_Citycode.city_id, FD_T_Citycode.city_name).filter(
        FD_T_Citycode.city_id.isnot(None))
    if not all:
        cities = cities.filter(FD_T_Citycode.is_support == 1)
    if country_id:
        cities = cities.filter(FD_T_Citycode.country_id == country_id)
    if province_id:
        cities = cities.filter(FD_T_Citycode.province_id == province_id)
    cities = cities.distinct()
    city_list = []
    for city in cities:
        city_list.append(dict(city_id=city.city_id, city_name=city.city_name))
    return dict(total_num=len(city_list),
                cities=city_list)


def get_cityinfo(city_id):
    session = DBSession()
    city = session.query(FD_T_Citycode.city_id, FD_T_Citycode.city_name, FD_T_Citycode.province_id,
                         FD_T_Citycode.province_name).filter(FD_T_Citycode.city_id == city_id).first()
    if city:
        return dict(city_id=city[0],
                    city_name=city[1],
                    province_id=city[2],
                    province_name=city[3])
    else:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des)


def get_districts(country_id=None, province_id=None, city_id=None):
    session = DBSession()
    districts = session.query(FD_T_Citycode.district_id, FD_T_Citycode.district_name).filter(
        FD_T_Citycode.district_id.isnot(None))
    if country_id:
        districts = districts.filter(FD_T_Citycode.country_id == country_id)
    if province_id:
        districts = districts.filter(FD_T_Citycode.province_id == province_id)
    if city_id:
        districts = districts.filter(FD_T_Citycode.city_id == city_id)
    districts = districts.distinct()
    district_list = []
    for district in districts:
        district_list.append(dict(district_id=district.district_id, district_name=district.district_name))
    return dict(total_num=len(district_list),
                districts=district_list)


def get_district_info(district_id):
    session = DBSession()
    district = session.query(FD_T_Citycode.district_id, FD_T_Citycode.district_name).filter(
        FD_T_Citycode.district_id == district_id).first()
    return dict(district_id=district.district_id,
                district_name=district.district_name)


def get_goodscategory(parent_id=None):
    session = DBSession()
    if parent_id:
        goodscategories = session.query(FD_T_Goodscategory).filter(FD_T_Goodscategory.parent_id == parent_id).distinct()
    else:
        goodscategories = session.query(FD_T_Goodscategory).filter(FD_T_Goodscategory.parent_id.is_(None)).distinct()
    goodscategory_list = []
    for goodscategory in goodscategories:
        goodscategory_list.append(dict(goodscategory_id=goodscategory.id, goodscategory_name=goodscategory.name))
    return dict(total_num=len(goodscategory_list), goodscategories=goodscategory_list)


def get_goodscategories_all_tree():
    # 树形结构的商品类别列表
    dbsession = DBSession()
    all_categories = dbsession.query(FD_T_Goodscategory).all()
    cl = []
    il = []
    for category in all_categories:
        if not category.parent_id:
            d = category.dict()
            d['son'] = []
            cl.append(d)
            il.append(category.id)
        else:
            pos = il.index(category.parent_id)
            cl[pos]['son'].append(category.dict())
    dbsession.close()
    return dict(total_num=len(all_categories), goodscategories=cl)


def get_goodscategories_all():
    dbsession = DBSession()
    all_categories = dbsession.query(FD_T_Goodscategory).all()
    goodscategories = []
    for category in all_categories:
        goodscategories.append(dict(goodscategory_id=category.id, goodscategory_name=category.name))
    return dict(total_num=len(all_categories), goodscategories=goodscategories)


def get_friend_shop(offset, limit):
    dbsession = DBSession()
    shops = dbsession.query(FD_T_Joinshop)[offset: offset + limit]
    return dict(shops=[i.dict() for i in shops])
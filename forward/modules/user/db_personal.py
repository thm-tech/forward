# -*- coding:utf8 -*-

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from forward.common.define import *
from forward.config import CONFIG
from forward.log import user_log
from forward.common.tools import native_str2



class DBPersonal(object):
    _pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=CONFIG.MYSQL.HOST, port=CONFIG.MYSQL.PORT,
                     user=CONFIG.MYSQL.USER, passwd=CONFIG.MYSQL.PASSWD, db=CONFIG.MYSQL.DATABASE,
                     use_unicode=False, charset="utf8", cursorclass=DictCursor)

    def __init__(self):
        pass

    def queryPersonalInfo(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        sql = "select * from fd_t_user where user_id = %s"
        paras = [user_id]
        try:
            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("No personal info. User id: %s", user_id)
                return None

            row = cursor.fetchone()
            info = dict()
            info["name"] = row["name"]
            if row["portrait_url"]:
                info["portrait"] = OSS_URL_PRIFIX + row["portrait_url"]
            else:
                info["portrait"] = OSS_URL_PRIFIX + CONFIG.PORTRAIT_URL
            info["gender"] = row["gender"]
            info["city"] = row["city_id"]
            # info["province"] = row["province_id"]
            info["phone"] = row["phone_no"]
            info["mcode"] = row["mcode"]
            info["qrcode"] = row["qrcode"]

            return info

        except MySQLdb.Error, e:
            user_log.error("Query personal info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query personal info failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def modifyPersonalInfo(self, user_id, attr, name, portrait_url, gender, city):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            if FD_PERSONAL_INFO_NAME == attr:
                sql = "update fd_t_user set name = %s where user_id = %s"
                paras = (name, user_id)
            elif FD_PERSONAL_INFO_PORTRAIT == attr:
                sql = "update fd_t_user set portrait_url = %s where user_id = %s"
                paras = (portrait_url, user_id)
            elif FD_PERSONAL_INFO_GENDER == attr:
                sql = "update fd_t_user set gender = %s where user_id = %s"
                paras = (gender, user_id)
            elif FD_PERSONAL_INFO_CITY == attr:
                sql = "update fd_t_user set city_id = %s where user_id = %s"
                paras = (city, user_id)

            row_count = cursor.execute(sql, paras)

            conn.commit()
            return True

        except MySQLdb.Error, e:
            user_log.error("Modify personal info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Modify personal info failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryAddress(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        addr_list = []

        try:
            sql = "select * from fd_t_useraddress where user_id = %s"
            paras = (user_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.info("No address info. User id: %s", user_id)
                return addr_list

            rows = cursor.fetchall()
            for row in rows:
                addr = dict()
                addr["addrID"] = row["id"]
                addr["name"] = row["name"]
                addr["phone"] = row["phone_no"]
                addr["address"] = row["address"]
                addr["postcode"] = row["postcode"]
                addr["default"] = row["default"]
                addr["province_id"] = row["province_id"]
                addr["city_id"] = row["city_id"]

                addr_list.append(addr)

            return addr_list

        except MySQLdb.Error, e:
            user_log.error("Query address info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query address info failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def modifyAddress(self, user_id, addr_id, name, phone_no, address, postcode, province_id, city_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            set_list = []

            if name is not None:
                set = "name = '" + native_str2(name) + "'"
                set_list.append(set)
            if phone_no is not None:
                set = "phone_no = '" + native_str2(phone_no) + "'"
                set_list.append(set)
            if address is not None:
                set = "address = '" + native_str2(address) + "'"
                set_list.append(set)
            if postcode is not None:
                set = "postcode = '" + native_str2(postcode) + "'"
                set_list.append(set)
            if province_id is not None:
                set = "province_id = '" + native_str2(province_id) + "'"
                set_list.append(set)
            if city_id is not None:
                set = "city_id = '" + native_str2(city_id) + "'"
                set_list.append(set)

            set_list_str = ','.join(set_list)
            sql = "update fd_t_useraddress set " + set_list_str + " where user_id = %s and id = %s"
            paras = (user_id, addr_id)
            row_count = cursor.execute(sql, paras)
            conn.commit()
            return True

        except MySQLdb.Error, e:
            user_log.error("Modify address info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Modify address info failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def getAddressID(self):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select fd_func_nextvalue('FD_ADDRESS_ID') as addr_id from dual"

            row_count = cursor.execute(sql)
            if row_count <= 0:
                user_log.error("Get address id failed")
                conn.rollback()
                return None

            row = cursor.fetchone()
            addr_id = row["addr_id"]
            conn.commit()
            return addr_id
        except MySQLdb.Error, e:
            user_log.exception(e)
            conn.rollback()
            return None
        except Exception, e:
            user_log.exception(e)
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def addAddress(self, user_id, name, phone, address, postcode, province_id, city_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            addr_id = self.getAddressID()
            if addr_id is None:
                user_log.error("Get address id failed!")
                return None

            sql = "select * from fd_t_useraddress where user_id = %s"
            paras = (user_id,)

            default = 1

            row_count = cursor.execute(sql, paras)
            if row_count > 0:
                default = 0

            sql = "insert into fd_t_useraddress values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            paras = (addr_id, user_id, name, phone, city_id, province_id, address, postcode, default)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("No address data be insert!")
                conn.rollback()
                return None

            conn.commit()
            return addr_id
        except MySQLdb.Error, e:
            user_log.error("Add address failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return None
        except Exception, e:
            user_log.error("Add address failed! Exception: %s", e)
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def deleteAddress(self, user_id, addr_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "delete from fd_t_useraddress where user_id = %s and id = %s"
            paras = (user_id, addr_id)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("No address data be delete!")
                conn.rollback()
                return False

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Delete address failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Delete address failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def bindPhone(self, acc_id, phone):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "update fd_t_account set phone_no = %s where acc_id = %s"
            paras = (phone, acc_id)

            row_count = cursor.execute(sql, paras)
            # if row_count <= 0:
            #     LOGGER.error("Bind phone no failed! Update account data failed! Phone no: %s", phone)
            #     conn.rollback()
            #     return False

            sql = "update fd_t_user set phone_no = %s where user_id = %s"
            paras = (phone, acc_id)

            row_count = cursor.execute(sql, paras)
            # if row_count <= 0:
            #     LOGGER.error("Bind phone failed! No data be updated! Phone no: %s", phone)
            #     conn.rollback()
            #     return False

            conn.commit()
            return True

        except MySQLdb.Error, e:
            user_log.error("Bind phone failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Bind phone failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()


    def setDefaultAddress(self, user_id, addr_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "update fd_t_useraddress set `default` = 0 where user_id = %s"
            paras = (user_id,)
            cursor.execute(sql, paras)

            sql = "update fd_t_useraddress set `default` = 1 where user_id = %s and id = %s "
            paras = (user_id, addr_id)
            cursor.execute(sql, paras)
            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Set user default addresss failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Set user default address failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
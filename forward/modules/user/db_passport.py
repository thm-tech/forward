# -*- coding:utf8 -*-

from datetime import datetime
import hashlib

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from forward.config import CONFIG
from forward.common.define import *
from define import *
from forward.config import CONFIG
from forward.log import user_log

class DBPassport(object):
    _pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=CONFIG.MYSQL.HOST, port=CONFIG.MYSQL.PORT,
                     user=CONFIG.MYSQL.USER, passwd=CONFIG.MYSQL.PASSWD, db=CONFIG.MYSQL.DATABASE,
                     use_unicode=False, charset="utf8", cursorclass=DictCursor)

    def __init__(self):
        pass

    def getAccountID(self):
        conn = self._pool.connection()
        cursor = conn.cursor()

        sql = "select fd_func_nextvalue(%s) as acc_id from dual"
        paras = ("FD_ACCOUNT_ID",)
        try:
            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Get account id failed")
                conn.rollback()
                return None

            row = cursor.fetchone()
            acc_id = row["acc_id"]
            conn.commit()
            return acc_id
        except MySQLdb.Error, e:
            user_log.error("Get account id failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return None
        except Exception, e:
            user_log.error("Get account id failed! Exception: %s", e)
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def recordLoginDevice(self, acc_id, cur_login_dev):
        conn = self._pool.connection()
        cursor = conn.cursor()

        sql = "select device from fd_t_userlogindevice where user_id = %s"
        paras = (acc_id,)
        try:
            last_login_dev = ""
            row_count = cursor.execute(sql, paras)
            if row_count > 0:
                row = cursor.fetchone()
                last_login_dev = row["device"]

                sql = "update fd_t_userlogindevice set device = %s, login_time = %s where user_id = %s"
                paras = (cur_login_dev, datetime.now(), acc_id)
            else:
                sql = "insert into fd_t_userlogindevice values(%s, %s, %s)"
                paras = (acc_id, cur_login_dev, datetime.now())

            cursor.execute(sql, paras)
            conn.commit()

            return last_login_dev
        except MySQLdb.Error, e:
            user_log.error("Record user login device failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return None
        except Exception, e:
            user_log.error("Record user login device failed! Exception: %s", e)
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def queryLastLoginDevice(self, acc_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        sql = "select device from fd_t_userlogindevice where user_id = %s"
        paras = (acc_id,)
        try:
            last_login_dev = ""
            row_count = cursor.execute(sql, paras)
            if row_count > 0:
                row = cursor.fetchone()
                last_login_dev = row["device"]

            return last_login_dev
        except MySQLdb.Error, e:
            user_log.error("Query user last login device failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query user last login device failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def register(self, phone, password):
        conn = self._pool.connection()
        cursor = conn.cursor()

        # Is account existed
        sql = "select acc_id from fd_t_account where phone_no = %s and acc_type = %s"
        paras = (phone, FD_ACCOUNT_TYPE_USER)
        try:
            row_count = cursor.execute(sql, paras)
            if row_count > 0:
                user_log.error("Account is existed, phone no: %s", phone)
                return -1

            # Get account id
            acc_id = self.getAccountID()
            if acc_id is None:
                user_log.error("Get account id failed!")
                return -2

            # Register account
            reg_time = datetime.now()

            sql = "insert into fd_t_account values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            paras = (acc_id, FD_ACCOUNT_TYPE_USER, FD_AUTH_MODE_PHONE, None, phone, None, password, None, reg_time)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Insert account data failed!")
                conn.rollback()
                return -2

            # Save user basic info
            mcode = "m" + str(acc_id)
            qrcode = FD_DOMAIN_NAME + "/user/" + str(acc_id)
            sql = "insert into fd_t_user values(%s, %s, null, null, %s, %s, %s, null, %s, null)"
            paras = (acc_id, mcode, mcode, qrcode, phone, CONFIG.DEFAULT_PORTRAIT_URL)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Insert user basic info failed!")
                conn.rollback()
                return -2

            # private_setting
            sql = "insert into fd_t_privatesetting values (%s, 1, 1, 1)"
            paras = (acc_id,)
            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Insert user private setting info failed!")
                conn.rollback()
                return -2

            conn.commit()
            return acc_id

        except MySQLdb.Error, e:
            user_log.error("Register failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return -2
        except Exception, e:
            user_log.error("Register failed! Exception: %s", e)
            conn.rollback()
            return -2
        finally:
            cursor.close()
            conn.close()

    def registerEx(self, log_mode, open_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            # Get account id
            acc_id = self.getAccountID()
            if acc_id is None:
                return None

            # Register account
            reg_time = datetime.now()
            sql = "insert into fd_t_account values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            paras = (
                acc_id, FD_ACCOUNT_TYPE_USER, log_mode, None, None, None, hashlib.md5(open_id).hexdigest(), open_id,
                reg_time)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Register 3rd failed, insert account data failed!")
                conn.rollback()
                return None

            # Save user basic info
            mcode = "m" + str(acc_id)
            qrcode = FD_DOMAIN_NAME + "/user/" + str(acc_id)
            sql = "insert into fd_t_user values(%s, null, null, null, %s, %s, null, null, null, null)"
            paras = (acc_id, mcode, qrcode)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Insert user basic info failed!")
                conn.rollback()
                return None

            conn.commit()
            return acc_id
        except MySQLdb.Error, e:
            user_log.error("Register 3rd account failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return None
        except Exception, e:
            user_log.error("Regisete 3rd account failed! Exception: %s", e)
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def savePhoneCode(self, phone, code, deadline):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_phoneauth where phone_no = %s"
            paras = (phone,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                sql = "insert into fd_t_phoneauth values(%s, %s, %s)"
                paras = (phone, code, deadline)
            else:
                sql = "update fd_t_phoneauth set auth_code = %s, auth_deadline = %s where phone_no = %s"
                paras = (code, deadline, phone)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Save phone verify code failed!")
                conn.rollback()
                return False

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Save phone code failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Save phone code failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def verifyPhoneCode(self, phone, code, now):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_phoneauth where phone_no = %s and auth_code = %s and auth_deadline >= %s"
            paras = (phone, code, now)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Invalid phone verify code!")
                return False

            return True
        except MySQLdb.Error, e:
            user_log.error("Verify phone code failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return False
        except Exception, e:
            user_log.error("Verify phone code failed! Exception: %s", e)
            return False
        finally:
            cursor.close()
            conn.close()

    def resetPassword(self, phone, password):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "update fd_t_account set password = %s where phone_no = %s"
            paras = (password, phone)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Reset password failed! No data be updated! Phone no: %s", phone)
                conn.rollback()
                return False

            conn.commit()
            return True

        except MySQLdb.Error, e:
            user_log.error("Reset password failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Reset password failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()


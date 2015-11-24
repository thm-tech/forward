#-*-coding:utf-8-*-

import MySQLdb
from datetime import datetime
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
from forward.config import CONFIG
from forward.common.define import *
from forward.log import auth_log


class DBManage(object):
    _pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=CONFIG.MYSQL.HOST, port=CONFIG.MYSQL.PORT,
                        user=CONFIG.MYSQL.USER, passwd=CONFIG.MYSQL.PASSWD, db=CONFIG.MYSQL.DATABASE,
                        use_unicode=False, charset="utf8", cursorclass=DictCursor)

    def __init__(self):
        pass

    def authenticate(self, auth_mode, acc_type, account, email, phone, password, open_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            if FD_AUTH_MODE_QQ == auth_mode or FD_AUTH_MODE_WECHAT == auth_mode or FD_AUTH_MODE_WEIBO == auth_mode or FD_AUTH_MODE_ALIPAY == auth_mode:
                sql = "select acc_id from fd_t_account where auth_mode = %s and acc_type = %s and open_id = %s"
                paras = (auth_mode, acc_type, open_id)
            elif FD_AUTH_MODE_ACCOUNT == auth_mode:
                sql = "select acc_id from fd_t_account where acc_type = %s and account = %s and password = %s"
                paras = (acc_type, account, password)
            elif FD_AUTH_MODE_PHONE == auth_mode:
                sql = "select acc_id from fd_t_account where acc_type = %s and phone_no = %s and password = %s"
                paras = (acc_type, phone, password)
            elif FD_AUTH_MODE_EMAIL == auth_mode:
                sql = "select acc_id from fd_t_account where acc_type = %s and email = %s and password = %s"
                paras = (acc_type, email, password)
            else:
                auth_log.error("Authenticate failed, invalid authenticate mode!")
                return None

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                auth_log.error("Authenticate failed, invalid account!")
                return -1

            row = cursor.fetchone()
            acc_id = row["acc_id"]
            return acc_id

        except MySQLdb.Error, e:
            auth_log.error("Authenticate failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            auth_log.error("Authenticate failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def authenticate2(self, acc_id, password):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_account where acc_id = %s and password = %s"
            paras = (acc_id, password)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                auth_log.error("Authenticate failed, invalid account!")
                return False
            return True
        except MySQLdb.Error, e:
            auth_log.error("Authenticate failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return False
        except Exception, e:
            auth_log.error("Authenticate failed! Exception: %s", e)
            return False
        finally:
            cursor.close()
            conn.close()

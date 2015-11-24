# -*- coding:utf8 -*-

from datetime import datetime

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from forward.config import CONFIG
from define import *
from forward.log import user_log


class DBSetting(object):
    _pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=CONFIG.MYSQL.HOST, port=CONFIG.MYSQL.PORT,
                     user=CONFIG.MYSQL.USER, passwd=CONFIG.MYSQL.PASSWD, db=CONFIG.MYSQL.DATABASE,
                     use_unicode=False, charset="utf8", cursorclass=DictCursor)

    def __init__(self):
        pass

    def querySupportCityList(self):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            city_list = []

            sql = "select DISTINCT city_id, city_name from fd_t_citycode where is_support = 1"

            row_count = cursor.execute(sql, None)
            if row_count <= 0:
                return city_list

            rows = cursor.fetchall()
            for row in rows:
                city = dict()
                city["id"] = row["city_id"]
                city["name"] = row["city_name"]
                city_list.append(city)
            return city_list
        except MySQLdb.Error, e:
            user_log.error("Query support city lsit failed! sql: %s, paras: %s, exception: %s", sql, e)
            return None
        except Exception, e:
            user_log.error("Query support city list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def insertPrivateSetting(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()
        try:
            sql = "insert into fd_t_privatesetting set (user_id, save_enable, fans_enable, visit_enable) values (%s, 1, 1, 1)"
            paras = (user_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return False
            return True
        except MySQLdb.Error, e:
            user_log.error("Query private setting failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            user_log.exception(e)
            return None
        except Exception, e:
            user_log.error("Query private setting failed! Exception: %s", e)
            user_log.exception('e')
            return None
        finally:
            cursor.close()
            conn.close()

    def queryPrivateSetting(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_privatesetting where user_id = %s"
            paras = (user_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("No private setting data! User id: %s", user_id)
                return None

            row = cursor.fetchone()
            setting = {}
            setting["favoriteEnable"] = row["save_enable"]
            setting["fansEnable"] = row["fans_enable"]
            setting["visitEnable"] = row["visit_enable"]
            return setting
        except MySQLdb.Error, e:
            user_log.error("Query private setting failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            user_log.exception(e)
            return None
        except Exception, e:
            user_log.error("Query private setting failed! Exception: %s", e)
            user_log.exception('e')
            return None
        finally:
            cursor.close()
            conn.close()

    def modifyPrivateSetting(self, user_id, favorite_enable, fans_enable, visit_enable):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "update fd_t_privatesetting set save_enable = %s, fans_enable = %s, visit_enable = %s where user_id = %s"
            paras = (favorite_enable, fans_enable, visit_enable, user_id)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Modify private setting failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Modify private setting failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def modifyMessageSetting(self, user_id, shop_id, msg_enable):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            if shop_id < 0:
                sql = "update fd_t_fans set push_message_enable = %s where user_id = %s"
                paras = (msg_enable, user_id)
            else:
                sql = "update fd_t_fans set push_message_enable = %s where user_id = %s and shop_id = %s"
                paras = (msg_enable, user_id, shop_id)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Modify message setting failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Modify message setting failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryFeedbackListByPage(self, user_id, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            feed_list = []

            sql = "select * from fd_t_feedback where user_id = %s and time <= \
                    (select time from fd_t_feedback where user_id = %s order by time desc limit %s, 1) order by time desc limit %s "
            paras = (user_id, user_id, int(offset), int(count))

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return feed_list

            rows = cursor.fetchall()
            for row in rows:
                feedback = dict()
                feedback["content"] = row["content"]
                feedback["time"] = row["time"]
                feedback["direction"] = row["direction"]

                feed_list.append(feedback)

            return feed_list
        except MySQLdb.Error, e:
            user_log.error("Query feedback info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return False
        except Exception, e:
            user_log.error("Query feedback info failed! Exception: %s", e)
            return False
        finally:
            cursor.close()
            conn.close()

    def feedback(self, user_id, feedback):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "insert into fd_t_feedback values(null, %s, %s, %s, %s)"
            paras = (FD_FEEDBACK_FROM_USER, user_id, feedback, datetime.now())

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Feedback failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Feedback failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryLatestVersion(self, system):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_appversion where system = %s and time = (select max(time) from fd_t_appversion where system = %s)"
            paras = (system, system)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return None

            row = cursor.fetchone()
            version = dict()
            version["version"] = row["version"]
            version["time"] = row["time"]
            version["remark"] = row["remark"]
            version["packet"] = row["packet"]
            return version
        except MySQLdb.Error, e:
            user_log.error("Query latest version failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query latest version failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

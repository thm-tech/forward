# -*- coding:utf8 -*-

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from forward.config import CONFIG
from forward.common.define import *
from define import *
from forward.log import user_log


class DBFriend(object):
    _pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=CONFIG.MYSQL.HOST, port=CONFIG.MYSQL.PORT,
                     user=CONFIG.MYSQL.USER, passwd=CONFIG.MYSQL.PASSWD, db=CONFIG.MYSQL.DATABASE,
                     use_unicode=False, charset="utf8", cursorclass=DictCursor)

    def __init__(self):
        pass

    def queryFriendIDList(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            frd_id_list = []

            sql = "select friend_id from fd_t_friend where user_id = %s"
            paras = (user_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return frd_id_list

            rows = cursor.fetchall()
            for row in rows:
                friend_id = row["friend_id"]
                frd_id_list.append(friend_id)
            return frd_id_list
        except MySQLdb.Error, e:
            user_log.error("Query friend id lsit failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query friend id list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryUserInfo(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_user where user_id = %s"
            paras = (user_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("No personal info. User id: %s", user_id)
                return None

            row = cursor.fetchone()
            info = {}
            info["name"] = row["name"]
            info["portrait"] = OSS_URL_PRIFIX + row["portrait_url"] if row["portrait_url"] else None
            info["gender"] = row["gender"]
            info["city"] = row["city_id"]
            info["phone"] = row["phone_no"]
            info["mcode"] = row["mcode"]
            info["qrcode"] = row["qrcode"]

            return info

        except MySQLdb.Error, e:
            user_log.error("Query user info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query user info failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def hasFriend(self, user_id, friend_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_friend where user_id = %s and friend_id = %s"
            paras = (user_id, friend_id)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return False
            return True

        except MySQLdb.Error, e:
            user_log.error("Query user info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query user info failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryUserInfoList(self, user_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            user_info_list = []
            sql = """
            SELECT
                t1.user_id,
                t1.`name`,
                t1.portrait_url,
                t2.city_name
            FROM
                fd_t_user t1
            LEFT JOIN fd_t_citycode as t2 on t1.city_id = t2.city_id
            WHERE
                t1.user_id IN %s
            """
            paras = [user_id_list]
            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("No user data. User id list: %s", user_id_list)
                return None

            rows = cursor.fetchall()
            for row in rows:
                info = {}
                info["userID"] = row["user_id"]
                info["nickName"] = row["name"]
                info["city"] = row["city_name"]
                info["portrait"] = OSS_URL_PRIFIX + row["portrait_url"]
                user_info_list.append(info)

            return user_info_list
        except MySQLdb.Error, e:
            user_log.error("Query user info list failed! sql: %s, paras: %s, exception: %s", sql, '', e)
            return None
        except Exception, e:
            user_log.error("Query user info list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryFriendInfoList(self, user_id, frd_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            frd_list = []
            sql = "select t1.friend_id, t1.friend_name, t2.name, t2.mcode, t2.portrait_url from fd_t_friend t1, fd_t_user t2 \
                    where t1.user_id = %s and t1.friend_id in %s and t1.friend_id = t2.user_id"
            paras = (user_id, frd_id_list)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return frd_list

            rows = cursor.fetchall()
            for row in rows:
                friend = {}
                friend["frdID"] = row["friend_id"]
                friend["rmkName"] = row["friend_name"]
                friend["nickName"] = row["name"]
                friend["mcode"] = row["mcode"]
                friend["portrait"] = OSS_URL_PRIFIX + row["portrait_url"]

                frd_list.append(friend)
            return frd_list
        except MySQLdb.Error, e:
            user_log.error("Query friend info lsit failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query friend info list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def modifyFriendName(self, user_id, frd_id, rmk_name):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "update fd_t_friend set friend_name = %s where user_id = %s and friend_id = %s"
            paras = (rmk_name, user_id, frd_id)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Modify friend name failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Modify friend name failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryFriendPrivateSetting(self, user_id, frd_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select t1.save_enable, t1.fans_enable, t1.visit_enable from fd_t_privatesetting t1, fd_t_friend t2 \
                    where t1.user_id = %s and t2.user_id = %s and t2.friend_id = %s"
            paras = (frd_id, user_id, frd_id)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                setting = {}
                setting["favoriteEnable"] = 1
                setting["fansEnable"] = 1
                setting["visitEnable"] = 1
                return setting

            setting = {}
            row = cursor.fetchone()
            setting["favoriteEnable"] = row["save_enable"]
            setting["fansEnable"] = row["fans_enable"]
            setting["visitEnable"] = row["visit_enable"]
            return setting
        except MySQLdb.Error, e:
            user_log.error("Query friend private setting failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query friend private setting failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def acceptFriendAdding(self, user_id, friend_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "insert into fd_t_friend values(%s, %s, ''),(%s, %s, '')"
            paras = (user_id, friend_id, friend_id, user_id)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Insert friend relationship failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Insert friend relationship failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryUserIDByPhoneNo(self, phone_no):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select user_id from fd_t_user where phone_no = %s"
            paras = (phone_no,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("No user info by phone no. Phone no: %s", phone_no)
                return None

            row = cursor.fetchone()
            user_id = row["user_id"]

            return user_id
        except MySQLdb.Error, e:
            user_log.error("Query user id by phone no failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query user id by phone no failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryUserFFVCount(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            ffv_count = {}

            # query user fans shop count
            sql = "select count(0) as count from fd_t_fans where user_id = %s"
            paras = (user_id,)
            cursor.execute(sql, paras)
            row = cursor.fetchone()
            ffv_count["fans"] = row["count"]

            # query user favorite goods count
            sql = "select count(0) as count from fd_t_favorite where user_id = %s"
            paras = (user_id,)
            cursor.execute(sql, paras)
            row = cursor.fetchone()
            ffv_count["favorite"] = row["count"]

            # query user fans shop count
            sql = "select count(0) as count from fd_t_visitedshop where user_id = %s"
            paras = (user_id,)
            cursor.execute(sql, paras)
            row = cursor.fetchone()
            ffv_count["visited"] = row["count"]

            return ffv_count
        except MySQLdb.Error, e:
            user_log.error("Query user ffv count failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query user ffv count failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def deleteFriendship(self, uid, fid):
        conn = self._pool.connection()
        cursor = conn.cursor()
        sql = "DELETE FROM fd_t_friend WHERE user_id = %s AND friend_id = %s OR user_id = %s AND friend_id = %s"
        params = (uid, fid, fid, uid)
        try:
            row_count = cursor.execute(sql, params)
            cursor.close()
            conn.commit()
            conn.close()
            return True
        except:
            cursor.close()
            conn.close()
            return False


if __name__ == '__main__':
    a = DBFriend().deleteFriendship(10001, 10003)
    print(a)

# -*- coding:utf8 -*-

from datetime import datetime, timedelta

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from forward.config import CONFIG
from forward.common.define import *
from define import *
from forward.common import trans
from forward.common.tools import piclist_to_fulllist
from forward.log import user_log


class DBShop(object):
    _pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=CONFIG.MYSQL.HOST, port=CONFIG.MYSQL.PORT,
                     user=CONFIG.MYSQL.USER, passwd=CONFIG.MYSQL.PASSWD, db=CONFIG.MYSQL.DATABASE,
                     use_unicode=False, charset="utf8", cursorclass=DictCursor)

    def __init__(self):
        pass

    def queryCategoryList(self):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            category_list = []
            # Query all father category
            sql = "select * from fd_t_category where parent_id is null"
            row_count = cursor.execute(sql, None)
            if row_count <= 0:
                return category_list

            rows = cursor.fetchall()
            for row in rows:
                category = dict()
                category["id"] = row["id"]
                category["name"] = row["name"]
                category["pic"] = OSS_URL_PRIFIX + row["cate_pic"]
                category["child"] = []

                # Query child category
                sql = "select * from fd_t_category where parent_id = %s"
                paras = (category["id"])

                cursor.execute(sql, paras)

                rows_c = cursor.fetchall()
                for row_c in rows_c:
                    category_c = dict()
                    category_c["id"] = row_c["id"]
                    category_c["name"] = row_c["name"]
                    category_c["pic"] = OSS_URL_PRIFIX + row_c["cate_pic"]

                    category["child"].append(category_c)

                category_list.append(category)

            return category_list
        except MySQLdb.Error, e:
            user_log.error("Query category list failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query category failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryRecommendShops(self, city_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            shop_list = []

            sql = "select t1.shop_id, t2.shop_name, t2.pic_url_list, t1.declaration from fd_t_recommend t1, fd_t_shop t2 where t1.city_id = %s and t1.status = 2 and t1.shop_id = t2.shop_id"
            paras = (city_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return shop_list

            rows = cursor.fetchall()
            for row in rows:
                shop = dict()
                shop["id"] = row["shop_id"]
                shop["name"] = row["shop_name"]
                shop["dec"] = row["declaration"]
                shop["pic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        shop["pic"] = OSS_URL_PRIFIX + pic_url_list[0]

                shop_list.append(shop)

            return shop_list
        except MySQLdb.Error, e:
            user_log.error("Query recommend shops failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query recommend shops failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryShopBriefInfo(self, shop_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            shop_list = []
            if not shop_id_list:
                return shop_list

            sql = "select shop_id, shop_name, pic_url_list, longitude, latitude from fd_t_shop where shop_id in (" + ','.join(
                map(str, shop_id_list)) + ")"

            row_count = cursor.execute(sql, None)
            if row_count <= 0:
                return shop_list

            rows = cursor.fetchall()
            for row in rows:
                shop = dict()
                shop["shop_id"] = row["shop_id"]
                shop["shop_name"] = row["shop_name"]
                shop["pic_url_list"] = piclist_to_fulllist(row["pic_url_list"])
                shop["longitude"] = row["longitude"]
                shop["latitude"] = row["latitude"]
                shop_list.append(shop)

            shop_list.sort(key=lambda _: shop_id_list.index(_['shop_id']))
            return shop_list
        except MySQLdb.Error, e:
            user_log.error("Query shop brief info failed! sql: %s, paras: %s, exception: %s", sql, None, e)
            return None
        except Exception, e:
            user_log.error("Query shop brief info failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryShopFansCount(self, shop_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select count(user_id) as count from fd_t_fans where shop_id = %s"
            paras = (shop_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return -1

            row = cursor.fetchone()
            fans_count = row["count"]

            return fans_count
        except MySQLdb.Error, e:
            user_log.error("Query shop fans count failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return -1
        except Exception, e:
            user_log.error("Query shop fans count failed! Exception: %s", e)
            return -1
        finally:
            cursor.close()
            conn.close()

    def queryShopListFansCount(self, shop_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        shop_fans_dict = {}
        if not shop_id_list:
            return shop_fans_dict

        try:
            sql = "select shop_id, count(user_id) as count from fd_t_fans where shop_id in %s group by shop_id"
            paras = [shop_id_list]

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return shop_fans_dict

            rows = cursor.fetchall()
            for row in rows:
                shop_id = row["shop_id"]
                fans_count = row["count"]

                shop_fans_dict[shop_id] = fans_count

            return shop_fans_dict
        except MySQLdb.Error, e:
            user_log.error("Query shop fans count failed! sql: %s, paras: %s, exception: %s", sql, None, e)
            return shop_fans_dict
        except Exception, e:
            user_log.error("Query shop fans count failed! Exception: %s", e)
            return shop_fans_dict
        finally:
            cursor.close()
            conn.close()

    def queryShopName(self, shop_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select shop_name from fd_t_shop where shop_id = %s"
            paras = (shop_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return ""

            row = cursor.fetchone()
            shop_name = row["shop_name"]

            return shop_name

        except MySQLdb.Error, e:
            user_log.error("Query shop name failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query shop name failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def visitShop(self, shop_id, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_visitedshop where user_id = %s and shop_id = %s"
            paras = (user_id, shop_id)

            visit_time = datetime.now()

            row_count = cursor.execute(sql, paras)
            if row_count > 0:
                sql = "update fd_t_visitedshop set visit_count = visit_count + 1, last_visit_time = %s where user_id = %s and shop_id = %s"
                paras = (visit_time, user_id, shop_id)
            else:
                sql = "insert into fd_t_visitedshop values(%s, %s, 1, %s)"
                paras = (user_id, shop_id, visit_time)

            cursor.execute(sql, paras)

            sql = "insert into fd_t_visitshoprecord values (null, %s, %s, %s, %s)"
            paras = (shop_id, user_id, FD_SHOP_ACTION_ENTER, visit_time)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Record visit shop failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Record visit shop failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def exitShop(self, shop_id, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            visit_time = datetime.now()

            sql = "insert into fd_t_visitshoprecord values (null, %s, %s, %s, %s)"
            paras = (shop_id, user_id, FD_SHOP_ACTION_EXIT, visit_time)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Record exit shop failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Record exit shop failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryGoodsByPage(self, shop_id, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            goods_list = []

            sql = "select goods_id, description, price, promotion_price, pic_url_list, publish_time from fd_t_goods where shop_id = %s and status = 1 and publish_time <= \
                    (select publish_time from fd_t_goods where shop_id = %s and status = 1 order by publish_time desc limit %s, 1) \
                    order by publish_time desc limit %s"
            paras = (shop_id, shop_id, offset, count)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return goods_list

            rows = cursor.fetchall()
            for row in rows:
                goods = {}
                goods["id"] = row["goods_id"]
                goods["name"] = row["description"]
                goods["price"] = float(row["price"]) if row["price"] else None
                goods["promot"] = float(row["promotion_price"]) if row["promotion_price"] else None
                goods["pic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        goods["pic"] = OSS_URL_PRIFIX + pic_url_list[0]
                goods["time"] = trans.datetime_to_string(row["publish_time"])

                goods_list.append(goods)

            return goods_list

        except MySQLdb.Error, e:
            user_log.error("Query goods by page failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query goods by page failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryActivityByShop(self, shop_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            act_list = []
            now = datetime.now() - timedelta(days=1)
            sql = "select * from fd_t_activity where shop_id = %s and end_time >= %s order by publish_time desc"
            paras = (shop_id, now)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return act_list

            rows = cursor.fetchall()
            for row in rows:
                act = {}
                act["id"] = row["act_id"]
                act["title"] = row["act_title"]
                act["content"] = row["act_content"]
                act["bt"] = row["begin_time"]
                act["et"] = row["end_time"]

                act_list.append(act)

            return act_list

        except MySQLdb.Error, e:
            user_log.error("Query shop activity failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query shop activity failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryActivities(self, city_id, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            act_list = []
            now = datetime.now() - timedelta(days=1)
            sql = "select t1.act_id, t1.act_title, t1.act_content, t1.begin_time, t1.end_time, t1.shop_id, t2.shop_name, t2.pic_url_list \
                    from fd_t_activity t1, fd_t_shop t2 where t2.city_id = %s and t2.shop_id = t1.shop_id and t1.end_time >= %s and t1.act_id >= \
                    (select t3.act_id from fd_t_activity t3, fd_t_shop t4 where t4.city_id = %s and t4.shop_id = t3.shop_id and t3.end_time >= %s \
                    order by t3.act_id limit %s,1) order by t1.act_id desc limit %s"
            paras = (city_id, now, city_id, now, offset, count)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return act_list

            rows = cursor.fetchall()
            for row in rows:
                act = {}
                act["actID"] = row["act_id"]
                act["title"] = row["act_title"]
                act["content"] = row["act_content"]
                act["bt"] = row["begin_time"]
                act["et"] = row["end_time"]
                act["shopID"] = row["shop_id"]
                act["shopName"] = row["shop_name"]
                act["shopPic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        act["shopPic"] = OSS_URL_PRIFIX + pic_url_list[0]

                act_list.append(act)

            return act_list
        except MySQLdb.Error, e:
            user_log.error("Query activities failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query activities failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryActivityNum(self, city_id):
        conn = self._pool.connection()
        cursor = conn.cursor()
        now = datetime.now()
        sql = "select t1.act_id, t1.act_title, t1.act_content, t1.begin_time, t1.end_time, t1.shop_id, t2.shop_name, t2.pic_url_list \
                from fd_t_activity t1, fd_t_shop t2 where t2.city_id = %s and t2.shop_id = t1.shop_id and t1.end_time >= %s and t1.act_id >= \
                (select t3.act_id from fd_t_activity t3, fd_t_shop t4 where t4.city_id = %s and t4.shop_id = t3.shop_id and t3.end_time >= %s \
                order by t3.act_id limit 0, 1) order by t1.act_id"
        paras = (city_id, now, city_id, now)

        row_count = cursor.execute(sql, paras)
        cursor.close()
        conn.close()
        return row_count

    def queryShopInfo(self, shop_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_shop t1 where shop_id = %s"
            paras = (shop_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Query shop info failed! No shop data. Shop id: %s", shop_id)
                return None

            row = cursor.fetchone()
            info = {}
            info["id"] = shop_id
            info["name"] = row["shop_name"]
            info["picList"] = piclist_to_fulllist(row["pic_url_list"])
            info["address"] = row["address"]
            info["long"] = row["longitude"]
            info["lat"] = row["latitude"]
            info["hours"] = row["business_hours"]
            info["phone"] = row["telephone_no"]
            info["intro"] = row["introduction"]
            return info

        except MySQLdb.Error, e:
            user_log.error("Query shop info failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query shop info failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryGoodsDetail(self, goods_id, bar_code):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            if goods_id is not None:
                sql = "select * from fd_t_goods left join fd_t_goodsinfo on fd_t_goods.goods_id = fd_t_goodsinfo.goods_id where fd_t_goods.goods_id = %s"
                paras = (goods_id,)
            elif bar_code is not None:
                sql = "select * from fd_t_goods where bar_code = %s"
                paras = (bar_code,)
            else:
                user_log.error("Query goods detail failed! Goods is and barcode are none.")
                return None
            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Query goods detail failed! No goods data. Goods id: %s", goods_id)
                return None

            row = cursor.fetchone()
            info = {}
            info["id"] = goods_id
            info["shop_id"] = row["shop_id"]
            info["desp"] = row["description"]
            info["price"] = row["price"]
            info["promot"] = row["promotion_price"]
            info["attention_count"] = row["attention_count"] if row["attention_count"] else 0
            pic_url_list_str = row["pic_url_list"]
            pic_url_list_prifix = piclist_to_fulllist(pic_url_list_str)
            # if pic_url_list_str:
            # pic_url_list = pic_url_list_str.split(",")
            # pic_url_list_prifix = map(lambda x:OSS_URL_PRIFIX+x, pic_url_list)
            info["picList"] = pic_url_list_prifix
            info["basic"] = row["basic_info"]
            info["detail"] = row["detail"]
            info["barcode"] = row["bar_code"]
            info["brandName"] = row["brand_name"]
            info["remark"] = row["remark"]
            return info
        except MySQLdb.Error, e:
            user_log.error("Query goods detail failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query goods detail failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryGoodsFitting(self, goods_id, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            pic_list = []

            sql = "select pic_url from fd_t_fitting where goods_id = %s and fit_time <= \
                    (select fit_time from fd_t_fitting where goods_id = %s order by fit_time desc limit %s,1) \
                    order by fit_time desc limit %s"
            paras = (goods_id, goods_id, offset, count)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return pic_list

            rows = cursor.fetchall()
            for row in rows:
                pic = OSS_URL_PRIFIX + row["pic_url"]
                pic_list.append(pic)

            return pic_list
        except MySQLdb.Error, e:
            user_log.error("Query goods fitting failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query goods fitting failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryVisitedShops(self, user_id, visit_time, direct, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            shop_list = []

            if direct == FD_QUERY_VISITED_SHOP_DIRECT_TOP:
                sql = "select t1.shop_id, t1.last_visit_time, t2.shop_name from fd_t_visitedshop t1, fd_t_shop t2 \
                        where t1.user_id = %s and t1.last_visit_time > %s and t1.shop_id = t2.shop_id order by t1.last_visit_time limit %s"
                paras = (user_id, visit_time, count)
            else:
                sql = "select t1.shop_id, t1.last_visit_time, t2.shop_name from fd_t_visitedshop t1, fd_t_shop t2 \
                        where t1.user_id = %s and t1.last_visit_time < %s and t1.shop_id = t2.shop_id order by t1.last_visit_time desc limit %s"
                paras = (user_id, visit_time, count)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return shop_list

            rows = cursor.fetchall()
            for row in rows:
                shop = {}
                shop["id"] = row["shop_id"]
                shop["name"] = row["shop_name"]
                shop["time"] = row["last_visit_time"]

                shop_list.append(shop)

            return shop_list
        except MySQLdb.Error, e:
            user_log.error("Query visited shop list failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query visited shop list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryFriendFavoriteGoods(self, user_id, frd_id, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            sql = "select * from fd_t_friend where user_id = %s and friend_id = %s"
            paras = (user_id, frd_id)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Not friend!")
                return None

            sql = "select t1.goods_id, t2.shop_id, t2.description, t2.price, t2.promotion_price, t2.pic_url_list \
                    from fd_t_favorite t1, fd_t_goods t2 where user_id = %s and t1.goods_id = t2.goods_id and t1.save_time <= \
                    (select t3.save_time from fd_t_favorite t3 where t3.user_id = %s order by t3.save_time desc limit %s,1) \
                    order by t1.save_time desc limit %s"
            paras = (frd_id, frd_id, offset, count)

            goods_list = []
            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return goods_list

            rows = cursor.fetchall()
            for row in rows:
                goods = {}
                goods["id"] = row["goods_id"]
                goods["shop_id"] = row["shop_id"]
                goods["desc"] = row["description"]
                goods["price"] = row["price"]
                goods["promot"] = row["promotion_price"]
                goods["pic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        goods["pic"] = OSS_URL_PRIFIX + pic_url_list[0]

                goods_list.append(goods)

            return goods_list
        except MySQLdb.Error, e:
            user_log.error("Query friend favorite goods failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query friend favorite goods failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryFriendFansShop(self, user_id, frd_id, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            shop_list = []

            sql = "select * from fd_t_friend where user_id = %s and friend_id = %s"
            paras = (user_id, frd_id)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Not friend!")
                return None

            sql = "select t1.shop_id, t2.shop_name, t2.pic_url_list \
                    from fd_t_fans t1, fd_t_shop t2 where t1.user_id = %s and t1.shop_id = t2.shop_id and t1.join_time <= \
                    (select t3.join_time from fd_t_fans t3 where t3.user_id = %s order by t3.join_time desc limit %s,1) \
                    order by t1.join_time desc limit %s"
            paras = (frd_id, frd_id, offset, count)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return shop_list

            rows = cursor.fetchall()
            for row in rows:
                shop = {}
                shop["id"] = row["shop_id"]
                shop["name"] = row["shop_name"]
                shop["pic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        shop["pic"] = OSS_URL_PRIFIX + pic_url_list[0]

                shop["hasAct"] = self.hasActivity(shop["id"])
                shop["hasNew"] = self.hasNewGoods(shop["id"])
                shop_list.append(shop)

            return shop_list
        except MySQLdb.Error, e:
            user_log.error("Query friend fans shop failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query friend fans shop failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def hasActivity(self, shop_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            now = datetime.now()
            sql = "select * from fd_t_activity where shop_id = %s and end_time >= %s"
            paras = (shop_id, now)

            row_count = cursor.execute(sql, paras)
            if row_count > 0:
                return 1
            else:
                return 0
        except MySQLdb.Error, e:
            user_log.error("Query shop has activity failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return 0
        except Exception, e:
            user_log.error("Query shop has activity failed! Exception: %s", e)
            return 0
        finally:
            cursor.close()
            conn.close()

    def hasNewGoods(self, shop_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            time = datetime.now() - timedelta(days=7)
            sql = "select * from fd_t_goods where shop_id = %s and publish_time >= %s"
            paras = (shop_id, time)

            row_count = cursor.execute(sql, paras)
            if row_count > 0:
                return 1
            else:
                return 0
        except MySQLdb.Error, e:
            user_log.error("Query shop has new goods failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return 0
        except Exception, e:
            user_log.error("Query shop has new goods failed! Exception: %s", e)
            return 0
        finally:
            cursor.close()
            conn.close()

    def queryFriendVisitedShop(self, user_id, frd_id, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            shop_list = []

            sql = "select * from fd_t_friend where user_id = %s and friend_id = %s"
            paras = (user_id, frd_id)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                user_log.error("Not friend!")
                return None

            sql = "select t1.shop_id, t1.last_visit_time, t2.shop_name, t2.pic_url_list \
                    from fd_t_visitedshop t1, fd_t_shop t2 where user_id = %s and t1.shop_id = t2.shop_id and t1.last_visit_time <= \
                    (select t3.last_visit_time from fd_t_visitedshop t3 where t3.user_id = %s order by t3.last_visit_time desc limit %s,1) \
                    order by t1.last_visit_time desc limit %s"
            paras = (frd_id, frd_id, offset, count)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return shop_list

            rows = cursor.fetchall()
            for row in rows:
                shop = {}
                shop["id"] = row["shop_id"]
                shop["name"] = row["shop_name"]
                shop["time"] = row["last_visit_time"]
                shop["pic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        shop["pic"] = OSS_URL_PRIFIX + pic_url_list[0]

                shop_list.append(shop)

            return shop_list
        except MySQLdb.Error, e:
            user_log.error("Query friend visited shop failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query friend visited shop failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryFansShopIDList(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            fans_id_list = []

            sql = "select shop_id from fd_t_fans where user_id = %s"
            paras = (user_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return fans_id_list

            rows = cursor.fetchall()
            for row in rows:
                fans_id = row["shop_id"]
                fans_id_list.append(fans_id)
            return fans_id_list
        except MySQLdb.Error, e:
            user_log.error("Query fans shop id lsit failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query fans shop id list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryFansShopInfoList(self, user_id, fans_shop_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            fans_shop_list = []

            sql = "select t1.shop_id, t1.join_time, t1.push_message_enable, t2.shop_name, t2.pic_url_list from fd_t_fans t1, fd_t_shop t2 \
                    where t1.user_id = %s and t1.shop_id in %s and t1.shop_id = t2.shop_id"
            paras = (user_id, fans_shop_id_list)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return fans_shop_list

            rows = cursor.fetchall()
            for row in rows:
                shop = {}
                shop["id"] = row["shop_id"]
                shop["name"] = row["shop_name"]
                shop["time"] = row["join_time"]
                shop["msgEnable"] = row["push_message_enable"]
                shop["pic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        shop["pic"] = OSS_URL_PRIFIX + pic_url_list[0]

                fans_shop_list.append(shop)

            fans_shop_id_list = [int(i) for i in fans_shop_id_list]
            fans_shop_list_sorted = sorted(fans_shop_list, key=lambda _: fans_shop_id_list.index(int(_['id'])))
            return fans_shop_list_sorted
        except MySQLdb.Error, e:
            user_log.error("Query fans shop info lsit failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryFansShopNewsList(self, fans_shop_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            fans_shop_list = []

            for shop_id in fans_shop_id_list:
                shop = {}
                shop["id"] = shop_id
                shop["hasAct"] = self.hasActivity(shop_id)
                shop["hasNew"] = self.hasNewGoods(shop_id)

                fans_shop_list.append(shop)

            return fans_shop_list
        except MySQLdb.Error, e:
            user_log.error("Query fans shop news list failed! Exception: %s", e)
            return None
        except Exception, e:
            user_log.error("Query fans shop news list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def concernShop(self, user_id, shop_id, oper):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            if FD_CONCERN == oper:
                join_time = datetime.now()
                sql = "insert into fd_t_fans values (%s, %s, %s, 1)"
                paras = (user_id, shop_id, join_time)
            else:
                sql = "delete from fd_t_fans where user_id = %s and shop_id = %s"
                paras = (user_id, shop_id)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Concern shop failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return True
        except Exception, e:
            user_log.error("Concern shop failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryFavoriteGoodsIDList(self, user_id):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            goods_id_list = []

            sql = "select goods_id from fd_t_favorite where user_id = %s"
            paras = (user_id,)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return goods_id_list

            rows = cursor.fetchall()
            for row in rows:
                goods_id = row["goods_id"]
                goods_id_list.append(goods_id)
            return goods_id_list
        except MySQLdb.Error, e:
            user_log.error("Query favorite goods id lsit failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query favorite goods id list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def queryFavoriteGoodsInfoList(self, user_id, goods_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            goods_list = []

            sql = "select t1.goods_id, t2.shop_id, t2.description, t2.price, t2.promotion_price, t2.pic_url_list \
                    from fd_t_favorite t1, fd_t_goods t2 \
                    where t1.user_id = %s and t1.goods_id in %s and t1.goods_id = t2.goods_id"
            paras = (user_id, goods_id_list)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return goods_list

            rows = cursor.fetchall()
            for row in rows:
                goods = {}
                goods["gid"] = row["goods_id"]
                goods["sid"] = row["shop_id"]
                goods["desp"] = row["description"]
                goods["price"] = row["price"]
                goods["promot"] = row["promotion_price"]
                goods["pic"] = ""
                pic_url_list_str = row["pic_url_list"]
                if pic_url_list_str is not None:
                    pic_url_list = pic_url_list_str.split(',')
                    if pic_url_list:
                        goods["pic"] = OSS_URL_PRIFIX + pic_url_list[0]

                goods_list.append(goods)
            return goods_list
        except MySQLdb.Error, e:
            user_log.error("Query favorite goods info lsit failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query favorite goods info list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def concernGoods(self, user_id, goods_id, oper):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            if FD_CONCERN == oper:
                save_time = datetime.now()
                sql = "insert into fd_t_favorite values (%s, %s, %s)"
                paras = (user_id, goods_id, save_time)
                cursor.execute('update fd_t_goodsinfo set attention_count = attention_count + 1 where goods_id = %s',
                               (goods_id, ))
            else:
                sql = "delete from fd_t_favorite where user_id = %s and goods_id = %s"
                paras = (user_id, goods_id)
                cursor.execute('update fd_t_goodsinfo set attention_count = attention_count - 1 where goods_id = %s',
                               (goods_id, ))

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Concern goods failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Concern goods failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def queryGoodsPromotionList(self, goods_id_list):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            goods_list = []

            sql = "select goods_id, promotion_price from fd_t_goods where goods_id in %s"
            paras = [goods_id_list]

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return goods_list

            rows = cursor.fetchall()
            for row in rows:
                goods = {}
                goods["gid"] = row["goods_id"]
                goods["promot"] = row["promotion_price"]

                goods_list.append(goods)
            return goods_list
        except MySQLdb.Error, e:
            user_log.error("Query goods promotion lsit failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        except Exception, e:
            user_log.error("Query goods promotion list failed! Exception: %s", e)
            return None
        finally:
            cursor.close()
            conn.close()

    def searchShopList(self, city_id, shop_name, offset, count):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            shop_id_list = []
            sql = "select s1.shop_id from fd_t_shop s1, fd_t_shopaccount s2 where s1.shop_id = s2.shop_id and s2.service_status = 2 and s1.city_id = %s and s1.shop_name like '%%" + shop_name + "%%' and s1.shop_id >= \
                    (select shop_id from fd_t_shop where city_id = %s and shop_name like '%%" + shop_name + "%%' limit %s,1) \
                    limit %s"
            paras = (city_id, city_id, offset, count)

            row_count = cursor.execute(sql, paras)
            if row_count <= 0:
                return shop_id_list

            rows = cursor.fetchall()
            shop_id_list = [row['shop_id'] for row in rows]
            return shop_id_list
        except MySQLdb.Error, e:
            user_log.error("Search shop id list by name failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            return None
        finally:
            cursor.close()
            conn.close()

    def searchShopTotalNum(self, city_id, shop_name):
        conn = self._pool.connection()
        cursor = conn.cursor()

        paras = (city_id, str(shop_name.encode('utf-8')))
        sql = 'select count(*) as count \
          from fd_t_shop left join fd_t_shopaccount on fd_t_shop.shop_id = fd_t_shopaccount.shop_id \
          where city_id = %s \
          and fd_t_shop.shop_name like "%%%s%%"' % paras

        count = cursor.execute(sql)
        if count:
            count = cursor.fetchall()[0]['count']

        return count

    def addCustomerFitting(self, acc_id, goods_id, pic_url, description):
        conn = self._pool.connection()
        cursor = conn.cursor()

        try:
            fit_time = datetime.now()
            sql = "insert into fd_t_fitting values(%s, %s, %s, %s, %s)"
            paras = (goods_id, acc_id, pic_url, fit_time, description)

            cursor.execute(sql, paras)

            conn.commit()
            return True
        except MySQLdb.Error, e:
            user_log.error("Add cutomer fiiting failed! sql: %s, paras: %s, exception: %s", sql, paras, e)
            conn.rollback()
            return False
        except Exception, e:
            user_log.error("Add customer fitting failed! Exception: %s", e)
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def isFans(self, uid, sid):
        conn = self._pool.connection()
        cursor = conn.cursor()

        sql = "select * from fd_t_fans where user_id = %s and shop_id = %s"
        paras = (uid, sid)
        count = cursor.execute(sql, paras)
        cursor.close()
        conn.close()
        if count:
            return True
        else:
            return False

    def getShopNums(self, city_id, category_id=None):
        conn = self._pool.connection()
        cursor = conn.cursor()

        sql = "select count(*) as count from fd_t_shop left join fd_t_shopaccount on fd_t_shop.shop_id = fd_t_shopaccount.shop_id \
              where city_id = %s \
              and fd_t_shopaccount.service_status = 2"
        paras = [city_id]
        if category_id:
            sql += "and category_list like '%%%s%'"
            paras.append(category_id)
        count = cursor.execute(sql, paras)
        if count:
            count = cursor.fetchall()[0]['count']

        return count


if __name__ == '__main__':
    print(DBShop().queryGoodsByPage(10010, 0, 10))

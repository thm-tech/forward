# -*- coding:utf8 -*-

from tornado.web import authenticated

from forward.httpbase import HttpBaseHandler
from forward.common.tools import *
from forward.common.auth import *
from error import *
from db_shop import *
from forward.log import user_log
from forward.common.tools import tornado_argument, tornado_argument, is_sql_secure_input

dao = DBShop()


class QueryFansShopDifferenceHandler(HttpBaseHandler):
    @authenticated
    @tornado_argument_json('_shopIDs')
    def post(self):
        user_log.info("QueryFansShopDifferenceHandler POST.")

        front_fans_id_list = self.arg.shopIDs
        user_id = self.get_current_user()

        end_fans_id_list = dao.queryFansShopIDList(user_id)
        if end_fans_id_list is None:
            user_log.error("Query fans shop id list failed! User id: %s", user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FANS_SHOP_ID_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        front_fans_id_set = set(front_fans_id_list)
        end_fans_id_set = set(end_fans_id_list)

        add_fans_id_set = end_fans_id_set - front_fans_id_set
        delete_fans_id_set = front_fans_id_set - end_fans_id_set

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["addShopIDs"] = list(add_fans_id_set)
        rep_json["delShopIDs"] = list(delete_fans_id_set)
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryFansShopInfoHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFansShopInfoHandler POST.")

        fans_shop_id_list = self.get_arguments("sid")
        if not fans_shop_id_list:
            rep_json = {}
            user_log.error("Query fans shop info list protocol data error!")
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        fans_shop_list = dao.queryFansShopInfoList(user_id, fans_shop_id_list)
        if fans_shop_list is None:
            user_log.error("Query fans shop info list failed! User id: %s, shop id list: %s", user_id, fans_shop_id_list)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FANS_SHOP_INFO_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = fans_shop_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryFansShopNewsHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFansShopNewsHandler POST.")

        fans_shop_id_list = self.get_arguments("sid")
        if not fans_shop_id_list:
            rep_json = {}
            user_log.error("Query fans shop news protocol data error!")
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        fans_shop_list = dao.queryFansShopNewsList(fans_shop_id_list)
        if fans_shop_list is None:
            user_log.error("Query fans shop news list failed! Shop id list: %s", fans_shop_id_list)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FANS_SHOP_NEWS_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = fans_shop_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class ConcerShopHandler(HttpBaseHandler):
    @authenticated
    def post(self):
        user_log.info("ConcerShopHandler POST.")

        shop_id = self.get_argument("sid", None)
        if shop_id is None:
            rep_json = dict()
            user_log.error("Concern shop protocol data error!")
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        if True != dao.concernShop(user_id, shop_id, FD_CONCERN):
            user_log.error("Concer shop failed! User id: %s, shop id: %s", user_id, shop_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_CONCERN_SHOP_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

    @authenticated
    def delete(self):
        user_log.info("ConcerShopHandler DELETE.")

        shop_id = self.get_argument("sid")
        if shop_id is None:
            rep_json = {}
            user_log.error("Unconcern shop protocol data error!")
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        if True != dao.concernShop(user_id, shop_id, FD_UNCONCERN):
            user_log.error("Unconcer shop failed! User id: %s, shop id: %s", user_id, shop_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_UNCONCERN_SHOP_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return 















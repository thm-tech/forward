# -*- coding:utf8 -*-

import json
from datetime import *
import time
from tornado.web import authenticated
from forward.httpbase import HttpBaseHandler
from forward.common.tools import *
from forward.common.auth import *
from error import *
from define import *
from db_shop import *
from forward.log import user_log

dao = DBShop()

class QueryFavoriteDifferenceHandler(HttpBaseHandler):
    @authenticated
    def post(self):
        user_log.info("QueryFavoriteDifferenceHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["goodsIDs"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            req_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(req_json, cls=ExtendedJsonEncoder))
            return

        front_goods_id_list = req_json["goodsIDs"]
        user_id = self.get_current_user()

        end_goods_id_list = dao.queryFavoriteGoodsIDList(user_id)
        if end_goods_id_list is None:
            user_log.error("Query favorite goods id list failed! User id: %s", user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FAVORITE_GOODS_ID_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        front_goods_id_set = set(front_goods_id_list)
        end_goods_id_set = set(end_goods_id_list)

        add_goods_id_set = end_goods_id_set - front_goods_id_set
        delete_goods_id_set = front_goods_id_set - end_goods_id_set

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["addGoodsIDs"] = list(add_goods_id_set)
        rep_json["delGoodsIDs"] = list(delete_goods_id_set)
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class QueryFavoriteInfoHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFavoriteInfoHandler GET.")

        goods_id_list = self.get_arguments("gid")
        user_id = self.get_current_user()

        goods_list = dao.queryFavoriteGoodsInfoList(user_id, goods_id_list)
        if goods_list is None:
            user_log.error("Query favorite goods info list failed! User id: %s, goods id list: %s", user_id, goods_id_list)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FAVORITE_GOODS_INFO_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["goodsList"] = goods_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class ConcerGoodsHandler(HttpBaseHandler):
    @authenticated
    def post(self):
        user_log.info("ConcerGoodsHandler POST.")

        goods_id = self.get_argument("gid")
        user_id = self.get_current_user()

        if True != dao.concernGoods(user_id, goods_id, FD_CONCERN):
            user_log.error("Concer goods failed! User id: %s, goods id: %s", user_id, goods_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_CONCERN_GOODS_FAILED
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
        user_log.info("ConcerGoodsHandler DELETE.")

        goods_id = self.get_argument("gid")
        user_id = self.get_current_user()

        if True != dao.concernGoods(user_id, goods_id, FD_UNCONCERN):
            user_log.error("Unconcer goods failed! User id: %s, goods id: %s", user_id, goods_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_UNCONCERN_GOODS_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

class QueryGoodsPromotHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QueryGoodsPromotHandler GET.")

        goods_id_list = self.get_arguments("gid")

        if not goods_id_list:
            user_log.error("Query goods promotion list failed! goods id list: %s", goods_id_list)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_GOODS_PROMOTION_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        goods_list = dao.queryGoodsPromotionList(goods_id_list)
        if goods_list is None:
            user_log.error("Query goods promotion list failed! goods id list: %s", goods_id_list)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_GOODS_PROMOTION_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["goodsList"] = goods_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return 


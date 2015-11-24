# -*- coding:utf8 -*-

from tornado.web import authenticated

from forward.httpbase import HttpBaseHandler
from forward.common.tools import *
from forward.common.auth import *
from db_shop import *
from error import *
from define import *
from forward.common.geo import *
from forward.api.chat_api import *
from forward.modules.cache.base import cache
from forward.log import user_log
from forward.config import CONFIG

dao = DBShop()
geo = GEO()

from forward.db.tables_define import *


def get_userful_shop(shop_id_list):
    session = DBSession()
    shop_ids = session.query(FD_T_Shopaccount.shop_id).filter(FD_T_Shopaccount.service_status == 2).filter(
        FD_T_Shopaccount.shop_id.in_(shop_id_list)).all()
    shop_ids = [i[0] for i in shop_ids]
    return_list = [i for i in shop_id_list if i in shop_ids]
    return return_list


class QueryCategoryHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QueryCategoryHandler GET.")

        category_list = dao.queryCategoryList()
        if category_list is None:
            user_log.error("Query category list failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_CATEGORY_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["categoryList"] = category_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryRecommendHandler(HttpBaseHandler):
    @cache(86400)
    def get(self):
        user_log.info("QueryRecommendHandler GET.")

        city_id = self.get_argument("city", None)
        if city_id is None or city_id < 0:
            user_log.error("Query recommend shop protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        shop_list = dao.queryRecommendShops(city_id)
        if shop_list is None:
            user_log.error("Query recommend shop failed! City ID: %s", city_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_RECOMMEND_SHOP_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = shop_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryShopsByCategoryHandler(HttpBaseHandler):
    # @cache(3600)
    @coroutine
    def get(self):
        user_log.info("QueryShopsByCategoryHandler GET.")

        category_id = self.get_argument("category", None)
        category_id = int(category_id) if category_id else None
        city_id = self.get_argument("city", None)
        city_id = int(city_id) if city_id else None
        longitude = self.get_argument("long", None)
        longitude = float(longitude) if longitude else None
        latitude = self.get_argument("lat", None)
        latitude = float(latitude) if latitude else None
        offset = self.get_argument("offset", None)
        offset = int(offset) if offset else None
        count = self.get_argument("count", None)
        count = int(count) if count else None
        if category_id is None or city_id is None or offset is None or count is None:
            user_log.error("Query shops by category protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        shop_id_list = geo.getShopList(city_id, category_id, longitude, latitude, offset, count)

        if shop_id_list is None:
            user_log.error("Query shop id list by geo info failed! City ID: %s, category ID: %s", city_id, category_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_SHOP_ID_LIST_BY_GEO_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        # Select shops which are used nornally, shop service status is 2
        shop_id_list = get_userful_shop(shop_id_list)

        # Query shop brief info
        shop_list_tmp = dao.queryShopBriefInfo(shop_id_list)
        if shop_list_tmp is None:
            user_log.error("Query shop brief info failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_SHOP_BRIEF_INFO_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        # Query shop fans count
        shop_fans_dict = dao.queryShopListFansCount(shop_id_list)

        #Query shop current customer count
        try:
            shop_customer_dict = {}
            shop_id_list_str = ""
            for shop_id in shop_id_list:
                shop_id_list_str = shop_id_list_str + "shop_id=" + str(shop_id) + "&"
            if shop_id_list_str:
                shop_id_list_str = shop_id_list_str[0:len(shop_id_list_str) - 1]
            url = CONFIG.FD_CHAT_SERVER + "/chat/shops/usernum?" + shop_id_list_str
            request = HTTPRequest(url, "GET")
            http = AsyncHTTPClient()
            response = yield http.fetch(request)
            rep_json = json.loads(response.body)
            is_success = rep_json["is_success"]
            if is_success:
                shop_customer_dict = rep_json["shop_dict"]
        except Exception, e:
            user_log.warn("Query shop current customer count error!")

        #Combind info
        shop_list = []

        for element in shop_list_tmp:
            shop = {}
            shop_id = element["shop_id"]
            shop["id"] = shop_id
            shop["name"] = element["shop_name"]
            shop["picList"] = element["pic_url_list"]
            shop_longitude = element["longitude"]
            shop_latitude = element["latitude"]
            if latitude and latitude:
                shop["distance"] = geo.getDistance(longitude, latitude, float(shop_longitude), float(shop_latitude))
            shop["fans"] = 0
            shop["customers"] = 0

            if shop_id in shop_fans_dict.keys():
                fans_count = shop_fans_dict[shop["id"]]
                shop["fans"] = fans_count

            if str(shop_id) in shop_customer_dict.keys():
                customer_count = shop_customer_dict[str(shop["id"])]
                shop["customers"] = customer_count

            shop_list.append(shop)


        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = shop_list
        rep_json["total_num"] = dao.getShopNums(city_id, category_id)
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class SearchShopsByNameHandler(HttpBaseHandler):
    @coroutine
    def get(self):
        user_log.info("SearchShopsByNameHandler GET.")

        shop_name = self.get_argument("name", None)
        city_id = self.get_argument("city", None)
        city_id = int(city_id) if city_id else None
        longitude = self.get_argument("long", None)
        longitude = float(longitude) if longitude else None
        latitude = self.get_argument("lat", None)
        latitude = float(latitude) if latitude else None
        offset = self.get_argument("offset", None)
        offset = int(offset) if offset else None
        count = self.get_argument("count", None)
        count = int(count) if count else None
        if shop_name is None or city_id is None or offset is None or count is None:
            user_log.error("Search shops by name protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        shop_id_list = dao.searchShopList(city_id, shop_name, offset, count)
        if shop_id_list is None:
            user_log.error("Search shop id list by shop name failed! City ID: %s, shop name: %s", city_id, shop_name)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_SEARCH_SHOP_ID_LIST_BY_NAME_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        # Query shop brief info
        shop_list_tmp = dao.queryShopBriefInfo(shop_id_list)
        if shop_list_tmp is None:
            user_log.error("Query shop brief info failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_SHOP_BRIEF_INFO_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        # Query shop fans count
        shop_fans_dict = dao.queryShopListFansCount(shop_id_list)

        # Query shop current customer count
        shop_customer_dict = {}
        shop_id_list_str = ""
        for shop_id in shop_id_list:
            shop_id_list_str = shop_id_list_str + "shop_id=" + str(shop_id) + "&"
        if shop_id_list_str:
            shop_id_list_str = shop_id_list_str[0:len(shop_id_list_str) - 1]
        url = CONFIG.FD_CHAT_SERVER + "/chat/shops/usernum?" + shop_id_list_str
        request = HTTPRequest(url, "GET")
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        if is_success:
            shop_customer_dict = rep_json["shop_dict"]

        #Combind info
        shop_list = []

        for element in shop_list_tmp:
            shop = {}
            shop_id = element["shop_id"]
            shop["id"] = shop_id
            shop["name"] = element["shop_name"]
            shop["picList"] = element["pic_url_list"]
            shop_longitude = element["longitude"]
            shop_latitude = element["latitude"]
            if longitude and latitude:
                shop["distance"] = geo.getDistance(longitude, latitude, shop_longitude, shop_latitude)
            shop["fans"] = 0
            shop["customers"] = 0

            if shop_id in shop_fans_dict.keys():
                fans_count = shop_fans_dict[shop["id"]]
                shop["fans"] = fans_count

            if str(shop_id) in shop_customer_dict.keys():
                customer_count = shop_customer_dict[str(shop["id"])]
                shop["customers"] = customer_count

            shop_list.append(shop)

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = shop_list
        rep_json["total_num"] = dao.searchShopTotalNum(city_id, shop_name)
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryShopNameHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QueryShopNameHandler GET.")

        shop_id = self.get_argument("sid", None)
        if shop_id is None:
            user_log.error("Query shop name protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        shop_name = dao.queryShopName(shop_id)
        if shop_name is None:
            user_log.error("Query shop name failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_SHOP_NAME_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopName"] = shop_name
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class VisitShopHandler(HttpBaseHandler):
    def post(self):
        user_log.info("VisitShopHandler GET.")

        shop_id = self.get_argument("sid", None)
        if shop_id is None:
            user_log.error("Visit shop protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        if user_id:
            dao.visitShop(shop_id, user_id)

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class ExitShopHandler(HttpBaseHandler):
    def post(self):
        user_log.info("ExitShopHandler GET.")

        shop_id = self.get_argument("sid", None)
        if shop_id is None:
            user_log.error("Exit shop protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        if user_id:
            dao.exitShop(shop_id, user_id)

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryShopCurrentCustomerHandler(HttpBaseHandler):
    @coroutine
    def get(self):
        user_log.info("QueryShopCurrentCustomerHandler GET.")

        shop_id = self.get_argument("sid", None)
        if shop_id is None:
            user_log.error("Query shop current customer count protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        url = CONFIG.FD_CHAT_SERVER + "/chat/shop/" + str(shop_id) + "/userstotalnum"
        request = HTTPRequest(url, "GET")
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        if is_success:
            customer_count = rep_json["total_num"]
            rep_json = {}
            rep_json["err"] = FD_USER_NOERR
            rep_json["count"] = customer_count
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
        else:
            user_log.error("Query shop current customer count failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_SHOP_CUSTOMER_COUNT_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return


class QueryGoodsByShopHandler(HttpBaseHandler):
    # @cache(3600)
    def get(self):
        user_log.info("QueryGoodsByShopHandler GET.")

        shop_id = self.get_argument("sid", None)
        offset = self.get_argument("offset", None)
        count = self.get_argument("count", None)
        if shop_id is None or offset is None or count is None:
            user_log.error("Query goods by shop protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        goods_list = dao.queryGoodsByPage(int(shop_id), int(offset), int(count))
        if goods_list is None:
            user_log.error("Query goods by page failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_GOODS_BY_PAGE_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["goodsList"] = goods_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryActivityByShopHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QueryActivityByShopHandler GET.")

        shop_id = self.get_argument("sid", None)
        if shop_id is None:
            user_log.error("Query shop activity protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        act_list = dao.queryActivityByShop(shop_id)
        if act_list is None:
            user_log.error("Query shop activity list failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_ACTIVITY_BY_SHOP_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["actList"] = act_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryActivitiesHandler(HttpBaseHandler):
    @cache(3600)
    def get(self):
        user_log.info("QueryActivitiesHandler GET.")

        city_id = int(self.get_argument("city"))
        offset = int(self.get_argument("offset"))
        count = int(self.get_argument("count"))
        if city_id is None or offset is None or count is None:
            user_log.error("Query activities protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        act_list = dao.queryActivities(city_id, offset, count)
        if act_list is None:
            user_log.error("Query activities failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_ACTIVITIES_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["actList"] = act_list
        rep_json["count"] = dao.queryActivityNum(city_id)
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryActivityNumHandlers(HttpBaseHandler):
    @tornado_argument('_city_id')
    def get(self):
        count = dao.queryActivityNum(self.arg.city_id)
        self.write({
            'count': count,
            'err': 0,
        })


class QueryShopInfoHandler(HttpBaseHandler):
    @coroutine
    def get(self):
        user_log.info("QueryShopInfoHandler GET.")

        shop_id = self.get_argument("sid", None)
        uid = self.get_current_user()
        if shop_id is None:
            user_log.error("Query recommend shop info protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        info = dao.queryShopInfo(shop_id)
        info['isFans'] = dao.isFans(uid, shop_id)
        if info is None:
            user_log.error("Query recommend shop info failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_RECOMMEND_SHOP_INFO_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        # Query shop fans count
        shop_fans_count = dao.queryShopFansCount(shop_id)
        info["fans"] = shop_fans_count

        # Query shop current customer count
        try:
            shop_customer_dict = {}
            url = CONFIG.FD_CHAT_SERVER + "/chat/shops/usernum?shop_id=" + shop_id
            request = HTTPRequest(url, "GET")
            http = AsyncHTTPClient()
            response = yield http.fetch(request)
            rep_json = json.loads(response.body)
            is_success = rep_json["is_success"]
            if is_success:
                shop_customer_dict = rep_json["shop_dict"]
                info["customers"] = shop_customer_dict[str(shop_id)]
        except Exception, e:
            user_log.warn("Query shop current customer count error!")

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["info"] = info
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryGoodsDetailHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QueryGoodsDetailHandler GET.")

        goods_id = self.get_argument("gid", None)
        bar_code = self.get_argument("barcode", None)
        if goods_id is None:
            user_log.error("Query goods detail protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        goods = dao.queryGoodsDetail(goods_id, bar_code)
        if goods is None:
            user_log.error("Query goods detail failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_GOODS_DETAIL_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["info"] = goods
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class CustomerFittingHandler(HttpBaseHandler):
    def get(self):
        user_log.info("QueryCustomerFittingHandler GET.")

        goods_id = self.get_argument("gid", None)
        offset = self.get_argument("offset", None)
        count = self.get_argument("count", None)
        if goods_id is None or offset is None or count is None:
            user_log.error("Query goods customer fitting protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        pic_list = dao.queryGoodsFitting(int(goods_id), int(offset), int(count))
        if pic_list is None:
            user_log.error("Query goods fitting picture list failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_GOODS_FITTING_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["picList"] = pic_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

    @authenticated
    def put(self):
        user_log.info("CustomerFittingHandler PUT.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["goodsID", "picURL"]
        optional_args = ["description"]
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Add customer fitting picture protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        goods_id = req_json["goodsID"]
        pic_url = req_json["picURL"]
        description = req_json["description"]

        acc_id = self.get_current_user()

        if True != dao.addCustomerFitting(acc_id, goods_id, pic_url, description):
            user_log.error("Add customer fitting picture failed! Account id: %s", acc_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_ADD_CUSTOMER_FITTING_PICTURE_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryVisitedShopsHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryVisitedShopsHandler GET.")

        time = self.get_argument("time", None)
        direct = self.get_argument("direct", None)
        count = self.get_argument("count", None)
        if time is None or count is None:
            user_log.error("Query goods customer fitting protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        visit_time = datetime.datetime.fromtimestamp(int(time))
        user_id = self.get_current_user()

        shop_list = dao.queryVisitedShops(user_id, visit_time, int(direct), int(count))
        if shop_list is None:
            user_log.error("Query visited shop list failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_VISITED_SHOPS_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = shop_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return
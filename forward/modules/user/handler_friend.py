# -*- coding:utf8 -*-

from tornado.web import authenticated

from forward.httpbase import HttpBaseHandler
from forward.common.tools import *
from forward.common.auth import *
from forward.api.chat_api import *
from db_shop import *
from forward.modules.user.error import *
from forward.common.send_message import send_invite_friend_download_app
from forward.modules.user.db_friend import *
from forward.log import user_log
from forward.config import CONFIG
dao_friend = DBFriend()
dao_shop = DBShop()


class QueryFriendsDifferenceHandler(HttpBaseHandler):
    @authenticated
    def post(self):
        user_log.info("QueryFriendsDifferenceHandler POST.")
        print(self.request.body)

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["frdIDs"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Query friend difference protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        front_frd_id_list = req_json["frdIDs"]
        user_id = self.get_current_user()

        end_frd_id_list = dao_friend.queryFriendIDList(user_id)
        if end_frd_id_list is None:
            user_log.error("Query friend id list failed! User id: %s", user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FRIEND_ID_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        front_frd_id_set = set(front_frd_id_list)
        end_frd_id_set = set(end_frd_id_list)

        add_frd_id_set = [i for i in end_frd_id_list if i not in front_frd_id_list]

        delete_frd_id_set = front_frd_id_set - end_frd_id_set

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["addFrdIDs"] = list(add_frd_id_set)
        rep_json["delFrdIDs"] = list(delete_frd_id_set)
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryFriendInfoHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFriendInfoHandler GET.")

        frd_id_list = self.get_arguments("uid")
        if not frd_id_list:
            user_log.error("Query friend info list protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        frd_list = dao_friend.queryFriendInfoList(user_id, frd_id_list)
        if frd_list is None:
            user_log.error("Query friend info list failed! Friend id list: %s", frd_id_list)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FRIEND_ID_LIST_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["frdList"] = frd_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class ModifyFriendRemarkNameHandler(HttpBaseHandler):
    @authenticated
    def post(self):
        user_log.info("ModifyFriendRemarkNameHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["frdID", "rmkName"]
        optional_args = []
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Modify friend remark name protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        frd_id = req_json["frdID"]
        rmk_name = req_json["rmkName"]
        user_id = self.get_current_user()

        if True != dao_friend.modifyFriendName(user_id, frd_id, rmk_name):
            user_log.error("Modify friend remark name failed! User id: %s, friend id: %s", user_id, frd_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_MODIFY_FRIEND_NAME_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryFriendPrivateSettingHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFriendPrivateSettingHandler GET.")

        frd_id = self.get_argument("uid", None)
        if frd_id is None:
            user_log.error("Query friend private setting protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        setting = dao_friend.queryFriendPrivateSetting(user_id, frd_id)
        if setting is None:
            user_log.error("Query friend private setting failed! User id: %s, friend id: %s", user_id, frd_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FRIEND_PRIVATE_SETTING_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["setting"] = setting
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryFriendFavoriteGoodsHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFriendFavoriteGoodsHandler GET.")

        frd_id = self.get_argument("uid", None)
        offset = self.get_argument("offset", None)
        count = self.get_argument("count", None)
        if frd_id is None or offset is None or count is None:
            user_log.error("Query friend favorite goods protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        goods_list = dao_shop.queryFriendFavoriteGoods(int(user_id), int(frd_id), int(offset), int(count))
        if goods_list is None:
            user_log.error("Query friend favorite goods failed! User id: %s, friend id: %s", user_id, frd_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FRIEND_FAVORITE_GOODS_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["goodsList"] = goods_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryFriendFansShopHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFriendFansShopHandler GET.")

        frd_id = self.get_argument("uid", None)
        offset = self.get_argument("offset", None)
        count = self.get_argument("count", None)
        if frd_id is None or offset is None or count is None:
            user_log.error("Query friend fans shop protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        shop_list = dao_shop.queryFriendFansShop(int(user_id), int(frd_id), int(offset), int(count))
        if shop_list is None:
            user_log.error("Query friend fans shop failed! User id: %s, friend id: %s", user_id, frd_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FRIEND_FANS_SHOP_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = shop_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryFriendVisitedShopHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryFriendVisitedShopHandler GET.")

        frd_id = self.get_argument("uid", None)
        offset = self.get_argument("offset", None)
        count = self.get_argument("count", None)
        if frd_id is None or offset is None or count is None:
            user_log.error("Query friend fans shop protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        shop_list = dao_shop.queryFriendVisitedShop(int(user_id), int(frd_id), int(offset), int(count))
        if shop_list is None:
            user_log.error("Query friend visited shop failed! User id: %s, friend id: %s", user_id, frd_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_FRIEND_VISITED_SHOP_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["shopList"] = shop_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class InviteFriendAddingHandler(HttpBaseHandler):
    @authenticated
    @coroutine
    def post(self):
        user_log.info("InviteFriendAddingHandler POST.")

        json_msg_str = self.request.body
        req_json = json.loads(json_msg_str)
        required_args = ["mode"]
        optional_args = ["phone", "mcode", "userID", "remark"]
        if True != httpJSONArgsCheck(req_json, required_args, optional_args):
            user_log.error("Invite firend adding protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        mode = req_json["mode"]
        phone_no = req_json["phone"]
        mcode = req_json["mcode"]
        user_id = req_json["userID"]
        remark = req_json["remark"]


        cur_user_id = self.get_current_user()
        user_info = dao_friend.queryUserInfo(cur_user_id)
        if user_info is None:
            user_log.error("Query user info failed! User id: %s", cur_user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_USER_INFO_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        if FD_FRIEND_ADD_MODE_PHONE_NO == mode:
            user_id = dao_friend.queryUserIDByPhoneNo(phone_no)
            # if phone not exist in db, try send a short message to phonenumber owner
            if user_id is None:
                if len(str(phone_no)) != 11:
                    rep_json = {}
                    rep_json["err"] = FD_ERR_USER_QUERY_USER_INFO_FAILED
                    self.set_header("Content-type", "application/json")
                    self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
                    self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
                    return
                else:
                    r = send_invite_friend_download_app(phone_no, user_info['name'], remark.encode('utf-8'), 'www.immbear.com')
                    r = json.loads(r)
                    if r['code'] != 0:
                        user_log.error("Send Message Failed! User id: %s, phone: %s" % (cur_user_id, phone_no))
                    self.write({'is_success': False,
                                'des': 'This phone master is not our user, but we has send a phone message to him/her'})
                    return
        elif FD_FRIEND_ADD_MODE_MCODE == mode:
            # mcode format: m1234
            user_id = int(mcode[1:])

        if int(cur_user_id) != int(user_id) and not dao_friend.hasFriend(cur_user_id, user_id):
            # Send invite be friend info
            url = CONFIG.FD_CHAT_SERVER + "/chat/friend/invite/" + str(cur_user_id) + "/to/" + str(user_id)
            body = {}
            body["invitor_id"] = cur_user_id
            body["invitor_name"] = user_info["name"]
            body["invitor_portrait"] = user_info["portrait"]
            body["remark"] = remark
            body["receivor_id"] = user_id

            body_str = json.dumps(body)

            request = HTTPRequest(url, "POST", body=body_str)
            http = AsyncHTTPClient()
            response = yield http.fetch(request)
            rep_json = json.loads(response.body)
            is_success = rep_json["is_success"]
            if is_success:
                rep_json = {}
                rep_json["err"] = FD_USER_NOERR
                self.set_header("Content-type", "application/json")
                self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
                return
            else:
                user_log.error("Send inviting be friend message failed! Invitor id: %s, receivor id: %s", cur_user_id,
                             user_id)
                rep_json = {}
                rep_json["err"] = FD_ERR_USER_SEND_INVITING_BE_FRIEND_MESSAGE_FAILED
                self.set_header("Content-type", "application/json")
                self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
                return
        else:
            self.write({'is_success': False, 'des': 'This User is already your friend!'})


class AcceptFriendAddingHandler(HttpBaseHandler):
    @authenticated
    @coroutine
    def post(self):
        user_log.info("AcceptFriendAddingHandler POST.")

        frd_id = self.get_argument("uid", None)
        accept = self.get_argument("accept", '1')
        if frd_id is None:
            user_log.error("Accept friend adding protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_id = self.get_current_user()

        if accept == '1':
            if True != dao_friend.acceptFriendAdding(int(user_id), int(frd_id)):
                user_log.error("Accept friend adding failed! User id: %s, friend id: %s", user_id, frd_id)
                rep_json = {}
                rep_json["err"] = FD_ERR_USER_ACCEPT_FRIEND_ADDING_FAILED
                self.set_header("Content-type", "application/json")
                self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
                return

        # Push confirm message to invitor
        user_info = dao_friend.queryUserInfo(user_id)
        if user_info is None:
            user_log.error("Query user info failed! User id: %s", user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_USER_INFO_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        url = CONFIG.FD_CHAT_SERVER + "/chat/friend/confirm/" + str(user_id) + "/to/" + str(frd_id) + "/" + str(accept)
        body = {}
        body["invitor_id"] = frd_id
        body["receivor_id"] = user_id
        body["receivor_name"] = user_info["name"]
        body["receivor_portrait"] = user_info["portrait"]

        body_str = json.dumps(body)

        request = HTTPRequest(url, "POST", body=body_str)
        http = AsyncHTTPClient()
        response = yield http.fetch(request)
        rep_json = json.loads(response.body)
        is_success = rep_json["is_success"]
        if is_success:
            rep_json = {}
            rep_json["err"] = FD_USER_NOERR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return
        else:
            user_log.error("Send confirming be friend message failed! Invitor id: %s, receivor id: %s", frd_id, user_id)
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_SEND_CONFIRMING_BE_FRIEND_MESSAGE_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryUserInfoHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryUserInfoHandler GET.")

        user_id_list = self.get_arguments("uid")
        if not user_id_list:
            user_log.error("Query user info list protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        user_info_list = dao_friend.queryUserInfoList(user_id_list)
        if user_info_list is None:
            user_log.error("Query user info list failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_USER_INFO_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["userList"] = user_info_list
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return


class QueryUserFFVCountHandler(HttpBaseHandler):
    @authenticated
    def get(self):
        user_log.info("QueryUserFFVCountHandler GET.")

        user_id = self.get_argument("uid", None)
        if user_id is None:
            user_log.error("Query user ffv count protocol data error!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_PROTOCOL_DATA_ERROR
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        ffv_count = dao_friend.queryUserFFVCount(user_id)
        if ffv_count is None:
            user_log.error("Query user ffv count failed!")
            rep_json = {}
            rep_json["err"] = FD_ERR_USER_QUERY_USER_FFV_COUNT_FAILED
            self.set_header("Content-type", "application/json")
            self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
            return

        rep_json = {}
        rep_json["err"] = FD_USER_NOERR
        rep_json["ffvCount"] = ffv_count
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(rep_json, cls=ExtendedJsonEncoder))
        return

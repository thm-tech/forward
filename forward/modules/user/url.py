# -*- coding:utf-8 -*-

from forward.modules.user.handler_passport import *
from forward.modules.user.handler_personal import *
from forward.modules.user.handler_shopping import *
from forward.modules.user.handler_friend import *
from forward.modules.user.handler_fans import *
from forward.modules.user.handler_favorite import *
from forward.modules.user.handler_setting import *
from forward.modules.user.handler_testchat import *
from forward.modules.user.handler_user_web import urls as urls_ywb
from forward.modules.user.handlers_thirdlogin import urls as urls_thirdlogin

user_urls = [
    (r"/user/login", LoginHandler),
    (r"/user/loginex", LoginExHandler),
    (r"/user/logout", LogoutHandler),
    (r"/user/register", RegisterHandler),
    (r"/user/gencode", GenerateCodeHandler),
    (r"/user/vercode", VerifyCodeHandler),
    (r"/user/resetpw", ResetPasswordHandler),
    (r"/user/device", QueryLastLoginDeviceHandler),

    (r"/user/personal", PersonalInfoHandler),
    (r"/user/address", AddressHandler),
    (r"/user/bindphone", BindPhoneHandler),
    (r"/user/address/default", AddressDefaultSettingHandler),

    (r"/user/category", QueryCategoryHandler),
    (r"/user/shop/recommend", QueryRecommendHandler),
    (r"/user/shop", QueryShopsByCategoryHandler),
    (r"/user/shop/name", QueryShopNameHandler),
    (r"/user/shop/enter", VisitShopHandler),
    (r"/user/shop/exit", ExitShopHandler),
    (r"/user/shop/customer", QueryShopCurrentCustomerHandler),
    (r"/user/goods", QueryGoodsByShopHandler),
    (r"/user/shop/activity", QueryActivityByShopHandler),
    (r"/user/shop/info", QueryShopInfoHandler),
    (r"/user/goods/info", QueryGoodsDetailHandler),
    (r"/user/goods/fit", CustomerFittingHandler),
    (r"/user/shop/visit", QueryVisitedShopsHandler),
    (r"/user/activity", QueryActivitiesHandler),
    (r"/user/activity/num", QueryActivityNumHandlers),
    (r"/user/shop/search", SearchShopsByNameHandler),

    (r"/user/friend/diff", QueryFriendsDifferenceHandler),
    (r"/user/friend", QueryFriendInfoHandler),
    (r"/user/friend/name", ModifyFriendRemarkNameHandler),
    (r"/user/friend/private", QueryFriendPrivateSettingHandler),
    (r"/user/friend/favorite", QueryFriendFavoriteGoodsHandler),
    (r"/user/friend/fans", QueryFriendFansShopHandler),
    (r"/user/friend/visit", QueryFriendVisitedShopHandler),
    (r"/user/friend/invite", InviteFriendAddingHandler),
    (r"/user/friend/accept", AcceptFriendAddingHandler),
    (r"/user/info", QueryUserInfoHandler),
    (r"/user/ffv/count", QueryUserFFVCountHandler),

    (r"/user/fans/diff", QueryFansShopDifferenceHandler),
    (r"/user/fans/info", QueryFansShopInfoHandler),
    (r"/user/fans/news", QueryFansShopNewsHandler),
    (r"/user/shop/concern", ConcerShopHandler),

    (r"/user/favorite/diff", QueryFavoriteDifferenceHandler),
    (r"/user/favorite/info", QueryFavoriteInfoHandler),
    (r"/user/goods/concern", ConcerGoodsHandler),
    (r"/user/goods/promot", QueryGoodsPromotHandler),

    (r"/user/city", QuerySupportCityHandler),
    (r"/user/setting/private", PrivateSettingHandler),
    (r"/user/setting/message", MessageSettingHandler),
    (r"/user/feedback", FeedbackHandler),
    (r"/user/version", QueryLatestVersionHandler),

    #test begin
    (r"/chat/shops/usernum", ChatQueryRoomUserCountHandler),
    (r"/chat/user/friend/invite", ChatInviteBeFriendHandler),
    #test end

]

user_urls += urls_ywb
user_urls += urls_thirdlogin

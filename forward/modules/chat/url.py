# -*- encoding: utf-8 -*-
from chat import *
from REST_api import *

chat_urls = [
    (r"/chat/", ChatSocketHandler),
    (r"/chat/user/(.*)/shop/(.*)", ChatUserShopHandler),
    (r"/chat/shop/(.*)/users", ChatShopUsersHandler),
    (r"/chat/room/(.*)/users", ChatRoomUsersHandler),
    (r"/chat/shop/(.*)/userslist", ChatShopUsersListHandler),
    (r"/chat/shops/usernum", ChatShopsUsernumHandler),
    (r"/chat/shop/(.*)/userstotalnum", ChatGroupUserNumHandler),
    (r"/chat/friend/invite/(.*)/to/(.*)", ChatInviteFriendHandler),
    (r"/chat/friend/confirm/(.*)/to/(.*)/(.*)", ChatConfirmFriendHandler),

    (r"/chat/user/(.*)/info", ChatUserInfoHandler),
    #(r"/chat/file", ChatFileUploadHandler),
    (r"/chat/file", ChatStreamUploader),
    #(r"/file/uploader", StreamUploader),
    (r"/file/uploader", OssStreamUploader),
    (r"/ck/file/uploader", CkStreamUploader),
    #(r"/oss/file/uploader", OssStreamUploader),

    (r"/chat/(.*)/fans/message/*", ChatFansMessageHandler),

    (r"/chat/room/(.*)/info", ChatRoomInfoHandler),
    (r"/chat/match", ChatMatchHandler),
]

# -*- coding:utf-8 -*-
from httpbase import *
from forward.config import CONFIG

MODULES_SWITCH = {
    "auth": CONFIG.MODULES.AUTH,
    "user": CONFIG.MODULES.USER,
    "chat": CONFIG.MODULES.CHAT,
    "mt": CONFIG.MODULES.MT,
    "test": 0,
}

URL_SETTINGS = [
    (r"/login", LoginBaseHandler),
]

if MODULES_SWITCH["auth"]:
    from forward.modules.auth.url import auth_urls

    URL_SETTINGS = URL_SETTINGS + auth_urls

if MODULES_SWITCH["user"]:
    from forward.modules.user.url import user_urls

    URL_SETTINGS = URL_SETTINGS + user_urls

if MODULES_SWITCH["chat"]:
    from forward.modules.chat.url import chat_urls

    URL_SETTINGS = URL_SETTINGS + chat_urls

if MODULES_SWITCH["mt"]:
    from forward.modules.mt.url import mt_urls

    URL_SETTINGS = URL_SETTINGS + mt_urls

if MODULES_SWITCH["test"]:
    from forward.modules.test.url import test_urls

    URL_SETTINGS = URL_SETTINGS + test_urls

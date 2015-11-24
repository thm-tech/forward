#-*- coding:utf-8 -*-

from forward.modules.auth.auth import *

auth_urls = [
        (r"/auth", AuthenticateHandler),
        (r"/auth2", Authenticate2Handler),
        ]

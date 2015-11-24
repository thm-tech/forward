# -*- encoding: utf-8 -*-

from user_ws_session import UserSession
from redis_py import RedisClient
from settings import *
import json

class CallBackProccessor(object):
    def __init__(self, routing_key, body):
        self.routing_key = routing_key
        self.body = body

    def callback(self):
        print 'father callback processor'
        pass

    def sendToUserDevices(self, user_name, msg):
        UserSession.sendToUserDevices(user_name, msg)


class E2eCallBackProcessor(CallBackProccessor):
    def __init__(self, routing_key, body):
        super(E2eCallBackProcessor, self).__init__(routing_key, body)

    def callback(self):
        user = self.routing_key[4:]

        if user in UserSession.users:
            self.sendToUserDevices(user, self.body)
            CHAT_LOG.info("e2e user in user session:%s", user)
        else:
            redis_cli = RedisClient()
            redis_cli.addUserOfflineMessage(user, self.body)
            CHAT_LOG.info("e2e user not in user session:%s", user)

        print "e2e call back processor"


class GroupCallBackProcessor(CallBackProccessor):
    def __init__(self, routing_key, body):
        super(GroupCallBackProcessor, self).__init__(routing_key, body)
        
    def callback(self):
        json_body = json.loads(self.body)
        if KEY_GROUP_NAME in json_body:
            group_name = json_body[KEY_GROUP_NAME]
        else:
            CHAT_LOG.error('group name not in message body')
            return

        redis_cli = RedisClient()
        users = redis_cli.queryUsersByGroupInServer(group_name, SERVER_SCORE)
        CHAT_LOG.debug("users in current serve:%s",users)

        for user in users:
            if user in UserSession.users:
                self.sendToUserDevices(user, self.body)
                CHAT_LOG.info("group user in user session:%s", user)
            else:
                CHAT_LOG.info("group user not in user session:%s", user)
                redis_cli.addUserOfflineMessage(user, self.body)

def getProcessor(routing_key, body):
    p = {
            KEY_E2E:E2eCallBackProcessor, 
            KEY_USERS:GroupCallBackProcessor,
            KEY_SHOP:GroupCallBackProcessor,
        }
    key = routing_key.split('_')[0]
    if key in p:
        return p[key](routing_key, body)
    else:
        CHAT_LOG.error("unknow routing key:%s",routing_key)
        return None



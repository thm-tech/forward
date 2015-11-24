# -*- encoding: utf-8 -*-
import json
from redis_py import RedisClient
from mq import rabbit_mq 
from user_ws_session import UserSession
from settings import *
from forward.common.tools import *
import time
import emoji


class ChatProcessor(object):
    def __init__(self, user, message = None):
        self.user = user
        if message:
            self.message = message
            try:
                self.message_obj =  json.loads(message)
            except:
                CHAT_LOG.error('json load message failed')
                return None 

            self.message_type = self.message_obj[KEY_COMMAND]
            CHAT_LOG.debug("m type:%s",self.message_type)

        self.redis_cli = RedisClient()
        self.mq = rabbit_mq 

    #@property
    def client(self):
        return UserSession.getSession(self.user)


    def process(self):
        if self.message_type in self.processes:
            self.processes[self.message_type](self)
        else:
            CHAT_LOG.error("unknow message type:%s", self.message_type)

    def _send(self, response):
        self.client().write_message(response)

    def _sendJson(self, response):
        try:
            self.client().write_message(json.dumps(response, cls=ExtendedJsonEncoder))
        except Exception,e:
            CHAT_LOG.error('send json error[%s]:%s',e,response)

    def _getUserChannel(self, user):
        return KEY_E2E + '_' + unicode(user)

    def _getE2eGroupName(self, u1, u2):
        if u1 > u2:
            return KEY_E2E + '_' + u1 + u2
        else:
            return KEY_E2E + '_' + u2 + u1

    def userOnline(self):
        #UserSession.addSession(self.client.user, self.client)
        gnames = self.redis_cli.queryGroupsByUser(self.client().user)
        CHAT_LOG.info("user online query group names:%s",gnames)

        for gname in gnames:
            self.redis_cli.addGroupUsers(gname, self.client().user, SERVER_SCORE)
            self.mq.subscribe(gname)

        user_channel = self._getUserChannel(self.client().user)

        self.mq.subscribe(user_channel)

        messages = self.redis_cli.queryUserOfflineMessage(self.client().user)
        CHAT_LOG.info("user offline messages:%s", messages)

        if messages:
            for m in messages:
                self._sendJson(m)


    def queryShopGname(self):
        gname = KEY_SHOP + u'_' + unicode(self.message_obj['sid'])
        res = {
            KEY_COMMAND:self.message_type,
            KEY_GROUP_NAME:gname
        }
        self._sendJson(res)
        CHAT_LOG.debug("send message %s",res)


    def userEnterShop(self):
        gname = self.message_obj[KEY_GROUP_NAME]
        self.mq.publish(gname, self.message)
        self.redis_cli.addGroupUsers(gname, self.client().user, SERVER_SCORE)
        self.redis_cli.addUserGroups(self.client().user, gname)

        self.mq.subscribe(gname)

    def userEnterGroup(self):
        gname = self.message_obj[KEY_GROUP_NAME]
        self.mq.publish(gname, self.message)
        self.redis_cli.addGroupUsers(gname, self.client().user, SERVER_SCORE)
        self.redis_cli.addUserGroups(self.client().user, gname)

        self.mq.subscribe(gname)

    def userChat(self):
        gname = self.message_obj[KEY_GROUP_NAME]

        cur_time = time.time()
        self.message_obj['body']['time'] = cur_time

        self.message = json.dumps(self.message_obj)

        CHAT_LOG.debug("gname prefix:%s",gname[0:4])

        if gname[0:3] == KEY_E2E:
            gname = self.message_obj["gname"]

            user_list = gname.split('_')
            
            CHAT_LOG.info("send message e2e gname:%s", gname)
            user_channel = self._getUserChannel(user_list[1])
            self.mq.publish(user_channel, self.message)
            
            user_channel = self._getUserChannel(user_list[2])
            self.mq.publish(user_channel, self.message)

        elif gname[0:4] == KEY_SHOP or gname[0:5] == KEY_USERS:
            CHAT_LOG.info("send message to group:%s",gname)
            self.mq.publish(gname, self.message)

        #self.redis_cli.addRecord(gname, self.message_obj['body']['time'], self.message_obj['body'])
        self.redis_cli.addRecord(gname, cur_time, json.dumps(self.message_obj['body']))

    def userExitGroup(self):
        gname = self.message_obj[KEY_GROUP_NAME]
        CHAT_LOG.debug("user:%s,exit group:%s",self.client().user, gname)

        self.redis_cli.exitGroup(self.client().user, gname)

        self.mq.publish(gname, self.message)
        self._send(self.message)

    def pullUsersChat(self):
        master = self.message_obj['master']
        gname = KEY_USERS + u'_' + unicode(master) + unicode(int(time.time()))

        clients = self.message_obj["clients"]

        CHAT_LOG.debug('pull users chat group name:%s, clients:%s, master:%s', 
                gname, clients, master)

        self.redis_cli.addGroupUsers(gname, master, SERVER_SCORE)
        self.redis_cli.addUserGroups(self.client().user, gname)

        invite_message = {
            KEY_COMMAND:'INVITE',
            KEY_GROUP_NAME:gname,
            KEY_USERS:[master] + clients 
        }
        msg = json.dumps(invite_message)
        self.mq.publish(self._getUserChannel(master), msg)

        for client in clients:
            self.redis_cli.addGroupUsers(gname, client, 0)
            self.redis_cli.addUserGroups(client, gname)
            self.mq.publish(self._getUserChannel(client), msg)

        self.mq.subscribe(gname)

    def acceptInvite(self):
        gname = self.message_obj[KEY_GROUP_NAME]

        #get current group users
        #self.getGroupUsers()
        #tell other members i am in
        user = self.client().user
        user_enter_group_msg = {
            KEY_COMMAND:'ENTR_GROUP',
            KEY_USER:user,
            KEY_GROUP_NAME:gname
        }
        self.mq.publish(gname, json.dumps(user_enter_group_msg))

        self.redis_cli.addGroupUsers(gname, user, SERVER_SCORE)
        self.redis_cli.addUserGroups(user, gname)

        self.mq.subscribe(gname)

    def pullUsersInGroup(self):
        gname = self.message_obj[KEY_GROUP_NAME]
        clients = self.message_obj['clients']

        invite_message = {
            KEY_COMMAND:'INVITE',
            KEY_GROUP_NAME:gname
        }
        
        for client in clients:
            self.mq.publish(self._getUserChannel(client), json.dumps(invite_message))
            self.redis_cli.addGroupUsers(gname, client, SERVER_SCORE)
            self.redis_cli.addUserGroups(client, gname)


    def getRecords(self):
        gname = self.message_obj["gname"]
        stime = self.message_obj["stime"]
        limit = self.message_obj["limit"]

        if stime == '0' or stime == 0:
            stime = time.time()

        ms = self.redis_cli.getPosRecord(gname, stime, limit)

        res = {
            KEY_COMMAND:'GET_RECORD',
            KEY_GROUP_NAME:gname,
            KEY_MESSAGES:[json.loads(m) for m in ms]
        }
        """
        res = r"{%s:'GET_RECORD', %s:%s,'ms':%s}"%(KEY_COMMAND,KEY_GROUP_NAME,gname,ms)
        """

        self._sendJson(res)

    def getGroupUsers(self):
        gname = self.message_obj["gname"]
        users = self.redis_cli.queryUsersByGroupName(gname)

        res = {
            KEY_COMMAND:'GROUP_USERS',
            KEY_GROUP_NAME:gname,
            KEY_USERS:users
        }

        self._sendJson(res)

    def getUserGroups(self):
        groups = self.redis_cli.queryGroupsByUser(self.user)

        res = {
            KEY_COMMAND:'USER_GROUPS',
            KEY_USER:self.user,
            KEY_GROUPS:[g for g in groups]
        }

        self._sendJson(res)

    def matchOther(self):
        user = self.message_obj['user']
        other,t = self.redis_cli.matchOther(user)
        current_time = time.time()
        if not other or not t:
            self.redis_cli.addMatchSet(user, current_time)
            CHAT_LOG.debug('match other return NULL')
            return
        if other and current_time - t < MATCH_SECENDS:
            CHAT_LOG.debug(' time - t:%s', current_time - t)
            CHAT_LOG.info('match suceesss:%s<------------>%s', user, other)
            self._sendJson({
                KEY_COMMAND:'SHAKE',
                KEY_USER:other
            })
            self.mq.publish(self._getUserChannel(other), json.dumps({
                KEY_COMMAND:'SHAKE',
                KEY_USER:user
            }))

            self.redis_cli.clearMatchSet(other)
        elif current_time - t >= MATCH_SECENDS:
            CHAT_LOG.debug('out time  time - t:%s', current_time - t)
            self.redis_cli.clearMatchSet(other)
            self.matchOther()
        else:
            CHAT_LOG.debug('no one in current set')
            self.redis_cli.addMatchSet(user, current_time)


    processes = {
        "SHOP_GNAME": queryShopGname,
        "ENTR_SHOP": userEnterShop,    #use enter group instead
        "ENTR_GROUP": userEnterGroup,
        "CHAT_M": userChat,
        "EXIT_G": userExitGroup,
        "PULL_US": pullUsersChat,
        "ACCEPT": acceptInvite,
        "PULL_IN_G": pullUsersInGroup,
        "GET_RECORD": getRecords,
        "GROUP_USERS": getGroupUsers,
        "USER_GROUPS": getUserGroups,
        "SHAKE":matchOther,
    }


# -*- encoding: utf-8 -*-
import time
import redis
import json
from redis.connection import Token
from settings import *

class RedisClient(object):
    pool = redis.ConnectionPool(host=REDIS_HOST, port=6379, db=0)

    def __init__(self):
        self.session = redis.StrictRedis(connection_pool=RedisClient.pool)

    def addRecord(self, name, *args, **kwargs):
        """
                       zset_name   score   value   score  value
        self.addRecord('my_zset',   1,     'fang',   2,   'hai')
        """
        return self.session.zadd(name, *args, **kwargs)

    def getNewRecord(self, zset_name, num):
        """
        get ``num`` newest items from ``zset_name``
        """
        max = time.time()

        return self.session.zrevrangebyscore(zset_name, max, 0, 0, num)

    def getPosRecord(self, zset_name, time_stamp, num):
        """
        get ``num`` items from ``zset_name`` start from ``time_stamp``
        """
        time_stamp = time_stamp - 0.000001
        return self.session.zrevrangebyscore(zset_name, time_stamp, 0, 0, num)

    def getRangeRecord(self, zset_name, time_stamp_start, time_stamp_end):
        """
        get ``num`` items from ``zset_name`` between ``time_stamp_start`` and ``time_stamp_end``
        """
        return self.session.zrevrange(zset_name, time_stamp_start, time_stamp_end)

    def _deleteUserGroup(self, user, group_name):
        set_name = self._getUserGroupsSetName(user)
        self.session.srem(set_name, group_name)

    def _deleteGroupUser(self, group_name, user):
        zset_name = self._getGroupUsersZsetName(group_name)
        self.session.zrem(zset_name,user)

    def exitGroup(self, user, group_name):
        self._deleteUserGroup(user, group_name)
        self._deleteGroupUser(group_name, user)

    def _getUserGroupsSetName(self, user):
        return u'ugroups_' + unicode(user)

    def queryGroupsByUser(self, user):
        set_name = self._getUserGroupsSetName(user)
        return self.session.smembers(set_name)

    def _getGroupUsersZsetName(self, group_name):
        return u'gusers_' + unicode(group_name)

    def queryUsersByGroupInServer(self, group_name, server_score):
        zset_name = self._getGroupUsersZsetName(group_name)
        return self.session.zrangebyscore(zset_name, server_score, server_score)

    def queryUsersByGroupName(self, group_name):
        """
        query users by group name
        """
        zset_name = self._getGroupUsersZsetName(group_name)
        return self.session.zrange(zset_name,0,-1)

    def queryUserNumInGroup(self, group_name):
        """
        return number in a group
        """
        zset_name = self._getGroupUsersZsetName(group_name)
        return self.session.zcard(zset_name)

    def addGroupUsers(self, group_name, user, server_score):
        """
        group:(user1 server_score1, user2 server_score1, user3 server_score2)
        if user already exit update user server score
        """
        zset_name = self._getGroupUsersZsetName(group_name)
        #if user already exist ,remove it 
        self.session.zrem(zset_name, user)
        self.session.zadd(zset_name, server_score, user)

    def addUserGroups(self, user, group_name):
        """
        user:(group1, group2, group3)
        """
        set_name = self._getUserGroupsSetName(user)
        #if group name already exist ,remove it 
        self.session.srem(set_name, group_name)
        self.session.sadd(set_name, group_name)

    def _getUserOfflineMessageListName(self, user):
        return u'offlinem_' + unicode(user)

    def addUserOfflineMessage(self, user, message):
        list_name = self._getUserOfflineMessageListName(user)
        self.session.rpush(list_name, message)

    def deleteUserOfflineMessage(self, user, message):
        list_name = self._getUserOfflineMessageListName(user)
        self.session.lrem(list_name, 0, message)
        
    def queryUserOfflineMessage(self, user):
        list_name = self._getUserOfflineMessageListName(user)
        offline_message = []
        while 1:
            m = self.session.lpop(list_name)
            if m == None:
                break
            offline_message.append(json.loads(m))

        return offline_message

    def matchOther(self, user):
        others = self.session.zrange(REDIS_MATCH_ZSET_NAME, 0, -1)
        time = None
        other = None
        for other in others:
            if other and other != user:
                time = self.session.zscore(REDIS_MATCH_ZSET_NAME, other)
                break
        CHAT_LOG.debug("match:%s,time:%s", other, time)

        return other, time

    def clearMatchSet(self, user):
        self.session.zrem(REDIS_MATCH_ZSET_NAME, user)

    def addMatchSet(self, user, time):
        self.session.zadd(REDIS_MATCH_ZSET_NAME, time, user)

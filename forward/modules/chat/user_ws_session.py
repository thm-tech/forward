# -*- encoding: utf-8 -*-
from settings import *
class UserSession(object):
    """
    user_name:{
        "cur_session":ws_obj,
        "sessions":set([ws_obj1,ws_obj2,ws_obj3])
    }
    """
    users = {}

    @staticmethod
    def addSession(user_name, session):
        if user_name in UserSession.users:
            UserSession.users[user_name]["sessions"].add(UserSession.users[user_name]["cur_session"])
            UserSession.users[user_name]["cur_session"] = session
        else:
            sessions_set = set()
            #sessions_set.add(session)

            ws_dict = {
                "cur_session":session,
                "sessions":sessions_set
            }

            UserSession.users[user_name] = ws_dict

        #CHAT_LOG.debug("user session users:%s",UserSession.users)
        CHAT_LOG.debug("user session users:%s,%d",user_name,len(UserSession.users[user_name]["sessions"]))

    @staticmethod
    def getSession(user_name):
        if user_name not in UserSession.users:
            CHAT_LOG.info("user [%s] not in users session",user_name)
            return None

        if "cur_session" in UserSession.users[user_name]:
            return UserSession.users[user_name]["cur_session"]
        else:
            CHAT_LOG.info("user [%s] currnet session not in users session",user_name)
            return None

    @staticmethod
    def clearUserSession(self):
        if self.user in UserSession.users:
            if id(self) == id(UserSession.users[self.user]['cur_session']):
                CHAT_LOG.debug('remove currnet user [%s]',self.user)
            else:
                CHAT_LOG.debug('remove session in set [%s]',self.user)

                if self in UserSession.users[self.user]['sessions']:
                    CHAT_LOG.debug('before remove self [%s] from set:%d',self.user,len(UserSession.users[self.user]['sessions']))
                    UserSession.users[self.user]['sessions'].remove(self)
                    CHAT_LOG.debug('remove self [%s] from set:%d',self.user,len(UserSession.users[self.user]['sessions']))
                else:
                    CHAT_LOG.error('self not in session set[%s]:',self.user)

                return

            if(len(UserSession.users[self.user]['sessions']) == 0):
                del UserSession.users[self.user]
                CHAT_LOG.debug('no more sessions del user:%s',self.user)
            else:
                UserSession.users[self.user]['cur_session'] = UserSession.users[self.user]['sessions'].pop()
                CHAT_LOG.info('change old session as current session [%s]',self.user)

        else:

            CHAT_LOG.error('clear user [%s] not in users session:%s',self.user,UserSession.users)

    @staticmethod
    def sendToUserDevices(user_name, msg):
        CHAT_LOG.info('write message to user[%s] divices:%d',user_name,len(UserSession.users[user_name]['sessions'])+1)
        if user_name in UserSession.users:
            UserSession.users[user_name]['cur_session'].write_message(msg)
            for session in UserSession.users[user_name]["sessions"]:
                session.write_message(msg)
 

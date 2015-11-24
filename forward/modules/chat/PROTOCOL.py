# -*- encoding: utf-8 -*-
import time

CHAT_URL = '/chat/'

# 消息体
"""
mtype:   mmx/*   mmx私有消息类型，如发送商品链接，或店的链接时需要用到。
发送商品：
    'mtype':'mmx/goods'
    'm':{
        id:goodsId,
        name:眼镜,
        img:http://.....png
    }
发送店面信息:
    'mtype':'mmx/shop'
    'm':{
        id:shopId,
        name:万达店,
        img:http://....png
    }
"""
MESSAGE_BODY = {
    'user': 'username',
    'time': time.time(),  #服务器端更新
    'mtype': 'text',  # 消息类型
    'm': 'hello everyone',
}

# ##################用户操作#############
# 用户上线
USER_ONLINE_DEFINE = {
    'url': 'ws://ip:port/chat/?u=username&p=passwd',
}

# 获取商店聊天室名称
QUERY_SHOP_CHAT_ROOM_NAME_DEFINE = {
    'req_message': {
        'c': 'SHOP_GNAME',
        'sid': 123
    },
    'res_message': {
        'c': 'SHOP_GNAME',
        'gname': 'shop_012304010',
    }
}

# 用户进店 尽量使用USER_ENTER_ROOM_DEFINE
USER_ENTER_SHOP_DEFINE = {
    'c': 'ENTR_SHOP',  # 命令码
    'user': 'user_name',
    'gname': 'shop_012304010',
}

#用户进入聊天室
USER_ENTER_GROUP_DEFINE = {
    'c':'ENTR_GROUP',
    'user':'user_name',
    'gname':'users_12313'
}

#获取组成员信息
GET_GROUP_USERS_DEFINE = {
    'req_message':{
        'c':'GROUP_USERS',
        'gname':'users_12313'
    },
    'res_message':{
        'c':'GROUP_USERS',
        'gname':'users_12313',
        'users':['user1','user2']
    }
}

#获取用户组信息
GET_USER_GROUPS_DEFINE = {
    'req_message':{
        'c':'USER_GROUPS',
        'user':10237,
    }
    'res_message':{
        'c':'USER_GROUPS',
        'user':10237,
        'groups':['shop_012304010','users_12345777']
    }
}

# 用户发送/接收消息
USER_CHAT_DEFINE = {
    'c': 'CHAT_M',  # chat message
    """
    #较大的ID排前面,用户发送出去的消息都会回射给自己，以确定发送是否成功
    def getE2eGroupName(u1, u2):
        if u1 > u2:
            return 'e2e' + '_' + u1 + '_'+ u2
        else:
            return 'e2e' + '_' + u2 + '_' + u1
    """
    'gname': 'shop_*',  # 接收方，组名或者 给单个用户发信息这个字段填 e2e_u1_u2 即可 如小华(012311)发送给小明(022221)，e2e_022221_012311
    'body': MESSAGE_BODY
}

# 退出组
USER_EXIT_GROUP_DEFINE = {
    'c': 'EXIT_G',
    'user': 'user_name',
    'gname': 'shop_012304010',
}

# 拉多个用户(创建用户组),拉单个用户直接发消息
USER_PULL_USERS_CHAT_DEFINE = {
    'c': 'PULL_US',
    'master': 'username',
    'clients': ['username', 'username', 'username'],
}

# 邀请消息  被拉的时候会收到
INVITE_MESSAGE_DEFINE = {
    'c': 'INVITE',
    'gname': 'users_12345777',
    'users':['u1', 'u2', 'u3'], #users[0]为创建者id,创建者也会收到些消息。
}

# !接受邀请信息 
ACCEPT_MESSAGE_DEFINE = {
    'c': 'ACCEPT',
    'gname': 'users_12345777',
}

# 拉用户进组 本来两个人拉第三个人 直接使用创建用户组接口
USER_PULL_USER_IN_GROUP_DEFINE = {
    'c': 'PULL_IN_G',
    'gname': 'users_12345777',
    'clients': ['username', 'username']
}

# 获取聊天记录
GET_CHAT_RECORD_DEFINE = {
    'req_message': {
        'c': 'GET_RECORD',
        'gname': 'users_12313',  # e2e shop...
        'stime': '1429241678.281107',  # 从什么时间开始获取,获取最新的填0
        'limit': 30,  # 获取多少条
    },
    'res_message': {
        'c': 'GET_RECORD',
        'gname': 'users_12313',  # e2e shop...
        'ms': [MESSAGE_BODY, MESSAGE_BODY],
    }
}

SHAKE_DEFINE = {
    'c':'SHAKE',
    'user':'user',
}

#收到推送的回应
#请求使用http接口   url:/chat/match
SHAKE_WITH_KEYS_DEFINE = {
    'c':'SHAKE_KEYS',
    'user':'user',   #摇到的用户
    'info':{
        'cityId':123,
        'gender':1,
        'name':'二狗子',
        'img':'...' #头像照片等。
    },
}

ADD_FRIEND_DEFINE = {
    'c':'ADD_FRIEND',
    'invitor':'1',
    'time':1429241678,
    'receiver':'2',
    'remark':'I am kit',
    'arguments':{
        'invitor_id':1,
        'invitor_name': 'kit',
        'invitor_portrait': '/mmx/image/user/1.jpg',
        'remark': 'i am kit',
        'receivor_id': 2,
    }
}

CONFIRM_FRIEND_DEFINE = {
    'c':'CON_FRIEND',
    'invitor':'1',
    'time':1429241678,
    'receiver':'2',
    'accept':0,   #1接受，0拒绝
    'arguments':{
        'invitor_id':1,
        'receivor_id': 2,
        'receivor_name':'hel',
        'receivor_portrait':'/mmx/image/user/1.jpg',
    }
}

SEND_MESSAGE_TO_FANS_DEFINE = {
    'c':'SEND_FANS_M',
    'time':1429241678,
    'shop':12345,
    'body':'mark down'
}

#换设备登陆
CHANGE_DEVICE_DEFINE = {
    'c':'CHANGE_DEVICE',
    'time':1429241678,
    'msg':""
}

# -*- coding:utf8 -*-

FD_CHAT_USER_VISIT_SHOP = {
    'url': '/chat/user/user_id/shop/shop_id',
    'post': {
        'response': {'is_success': True}
    },
    'delete': {
        'response': {'is_success': True}
    },
}

FD_CHAT_SHOP_USERS = {
    'url': '/chat/shop/shop_id/users',
    'get': {
        'response': {'is_success': True, 'total_num': 10, 'users': [1, 2, 3, 4]}
    }
}

FD_CHAT_SHOP_USER_COUNT = {
    'url': '/chat/shop/shop_id/userstotalnum',
    'get': {
        'response': {'is_success': True, 'total_num': 10}
    }
}

FD_CHAT_SHOP_USER_LIST = {
    'url': '/chat/shop/shop_id/userslist',
    'get': {
        'response': {'is_success': True, 'users': [1, 2, 3, 4]}
    }
}

FD_CHAT_SHOPS_USER_COUNT = {
    'url': '/chat/shops/usernum?shop_id=1&shop_id=2',
    'get':
        {
            'response':
                {
                    'is_success': True,
                    'shop_dict':
                        {
                            '10011': 12  # key:shop id,value:user count
                        }
                }
        }
}

# Push invite adding friend message to receivor user
FD_CHAT_FRIEND_INVITING = {
    'url': '/chat/friend/invite/(invitor_id)/to/(receivor_id)',
    'post': {
        'request': {
            'invitor_id': 1
            , 'invitor_name': 'kit'
            , 'invitor_portrait': '/mmx/image/user/1.jpg'
            , 'remark': 'i am kit'
            , 'receivor_id': 2
        },
        'response': {
            'is_success': True
        }
    }
}

# Push confirm adding friend message to invitor user
FD_CHAT_FRIEND_CONFIRMING = {
    'url': '/chat/friend/confirm/(receivor_id_id)/to/(invitor_id)',
    'post': {
        'request': {
            'invitor_id': 1
            , 'receivor_id': 2
            , 'receivor_name': 'hel'
            , 'receivor_portrait': '/mmx/image/user/2.jpg'
        },
        'response': {
        }
    }
}

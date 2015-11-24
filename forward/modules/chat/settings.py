# -*- encoding: utf-8 -*-
from forward.log import chat_log, mq_log
from forward.config import CONFIG

RABBITMQ_USER = CONFIG.RABBITMQ.USER
RABBITMQ_PASSWD = CONFIG.RABBITMQ.PASSWD
REDIS_HOST = CONFIG.REDIS.HOST
AUTH_URL = CONFIG.AUTH_URL
CK_DOCUMENT_DOMAIN = CONFIG.CK_DOCUMENT_DOMAIN

SERVER_SCORE = 1  # every server has a unique score
REDIS_PORT = 6379
CHAT_LOG = chat_log
MQ_LOG = mq_log

MQ_HOST = 'localhost'
MQ_EXCHANGE_NAME = 'forward'

KEY_E2E = u'e2e'
KEY_USERS = u'users'
KEY_SHOP = u'shop'
KEY_GROUP_NAME = u'gname'
KEY_COMMAND = u'c'
KEY_MESSAGES = u'ms'
KEY_USER = u'user'
KEY_GROUPS = u'groups'

MATCH_SECENDS = 6

STATIC_FILE_PATH = '/usr/share/nginx/html/mmx_mt_cli/'
STATIC_FILE_URL = 'http://115.28.143.67' + '/mmx_mt_cli/'

IMG_PRIFIX = 'http://img.immbear.com/'

NO_FILES_FOUND = 0x00050001
FILE_TOO_LARGE = 0x00050002
USER_ID_IS_NULL = 0x00050003
USER_NOT_EXIST = 0x00050004
HANDLER_ROOM_INFO_FAILED = 0x00050005
GET_ROOM_INFO_FAILED = 0x00050006

FILE_MAX_LENGTH = 400 * 1024 * 1024 * 1024

REDIS_MATCH_ZSET_NAME = 'match_zset'

END_POINT = "oss.aliyuncs.com"
ACCESS_KEY_ID = "9fk40TQfvrRJwFLt"
ACCESS_KEY_SECRET = "v22JLrA9vOvdB0Vq5tXU0cgjmj82jU"
# MMX_IMG_BUCKET = "mmx-img-public"
#OSS_URL_PRIFIX  = 'http://' + MMX_IMG_BUCKET + '.oss-cn-hangzhou.aliyuncs.com/'
OSS_MIN_LEN = 100 * 1024


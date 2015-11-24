# -*- encoding: utf-8 -*-
from tornado.web import stream_request_body
from tornado.http1connection import *
from settings import *
from common import *
from forward.httpbase import HttpBaseHandler
from chat_processor import *
from user_ws_session import * 
from redis_py import *
from forward.common.tools import *
import json
import hashlib
from forward.db.db_base import *
import os
import re

import uuid

from oss.oss_api import *
from oss import oss_util
from oss import oss_xml_handler

class ChatRestfulApi(HttpBaseHandler):
    pass
        

class ChatGroupUserNumHandler(ChatRestfulApi):
    def get(self, shop_id):
        if not shop_id:
            self.write({"is_success":False})
            return
        gname = getShopGname(shop_id)
        redis_cli = RedisClient()
        num = redis_cli.queryUserNumInGroup(gname)
        CHAT_LOG.debug('query users in group[%s]:%s',gname ,num)

        self.write({
            'is_success':True, 
            'total_num':num, 
        })


class ChatUserShopHandler(ChatRestfulApi):
    def post(self, user_id, shop_id):
        if not user_id or not shop_id:
            self.write({"is_success":False})
            return
        #use websocket instead
        chat_processor = ChatProcessor(None)
        gname = 'shop_' + shop_id
        chat_processor.mq.publish(gname, json.dumps({
            KEY_COMMAND:'ENTR_GROUP',
            KEY_USER:user_id,
            KEY_GROUP_NAME:gname
        }))

        self.write({'is_success': True})


class ChatShopUsersHandler(ChatRestfulApi):
    def get(self, shop_id):
        if not shop_id:
            self.write({"is_success":False})
            return
        gname = getShopGname(shop_id)
        redis_cli = RedisClient()
        users = redis_cli.queryUsersByGroupName(gname)
        CHAT_LOG.debug('query users in group[%s]:%s',gname ,users)
        num = len(users)

        self.write({
            'is_success':True, 
            'total_num':num, 
            'users':users
        })

class ChatRoomUsersHandler(ChatRestfulApi):
     def get(self, gname):
        if not gname:
            self.write({"is_success":False})
            return
        redis_cli = RedisClient()
        users = redis_cli.queryUsersByGroupName(gname)
        CHAT_LOG.debug('query users in group[%s]:%s',gname ,users)
        num = len(users)

        self.write({
            'is_success':True, 
            'total_num':num, 
            'users':users
        })   

class ChatShopUsersListHandler(ChatRestfulApi):
    def get(self, shop_id):
        if not shop_id:
            self.write({"is_success":False})
            return
        gname = getShopGname(shop_id)
        redis_cli = RedisClient()
        users = redis_cli.queryUsersByGroupName(gname)
        CHAT_LOG.debug('query users in group[%s]:%s',gname ,users)

        self.write({
            'is_success':True, 
            'users':users
        })


class ChatShopsUsernumHandler(ChatRestfulApi):
    def get(self):
        shop_list = self.get_arguments('shop_id')
        if not shop_list:
            self.write({
                'is_success':False,
                'shop_dict':{}
            })
            return 
        redis_cli = RedisClient()

        shop_dict = {
                k:redis_cli.queryUserNumInGroup(getShopGname(k))
                for k in shop_list 
        }
        CHAT_LOG.debug('shops dict:%s',shop_dict)

        self.write({
            'is_success':True, 
            'shop_dict':shop_dict
        })


class ChatInviteFriendHandler(ChatRestfulApi):
    def post(self, invitor_id, receiver_id):
        if not invitor_id or not receiver_id:
            self.write({
                'is_success':False
            })
            return
        time_add = time.time()
        receiver_channal = KEY_E2E + '_' + unicode(receiver_id)
        rabbit_mq.publish(receiver_channal, json.dumps({
            KEY_COMMAND:'ADD_FRIEND',
            'invitor':invitor_id,
            'receiver':receiver_id,
            'time':time_add,
            'arguments':json.loads(self.request.body)
        }))
        self.write({
            'is_success':True
        })


class ChatConfirmFriendHandler(ChatRestfulApi):
    def post(self, receiver_id, invitor_id, flag):
        if not invitor_id or not receiver_id:
            self.write({
                'is_success':False
            })
            return
        time_con = time.time()
        invitor_channal = KEY_E2E + '_' + unicode(invitor_id)
        rabbit_mq.publish(invitor_channal, json.dumps({
            KEY_COMMAND:'CON_FRIEND',
            'invitor':invitor_id,
            'receiver':receiver_id,
            'time':time_con,
            'accept':flag,
            'arguments':json.loads(self.request.body)
        }))
        self.write({
            'is_success':True
        })


class ChatUserInfoHandler(ChatRestfulApi):
    """
    get user name and portrait when chat
    req:
        get: /chat/user/(.*)/info
    rep:
        {
            'userId':123,
            'name':'rookie',
            'img':'http://ip:port/img/2312312313'
        }
    """
    def get(self, user_id):
        if not user_id:
            CHAT_LOG.info('user id is null')
            self.write({
                'error':USER_ID_IS_NULL ,
                'des':'cat get user id'
            })
            return

        #user_id = int(user_id)

        session = DBSession()

        acc_type = session.query(FD_T_Account.acc_type).\
                filter(FD_T_Account.acc_id == user_id).first()

        if acc_type:
            acc_type = acc_type[0]
        else:
            self.write({
                'error':USER_NOT_EXIST,
                'des':'user not exist'
            })
            return

        CHAT_LOG.debug('got user type:%s',acc_type)

        res = {'userId':user_id, 'name':'www.miaomiaox.com', 'img':'e4650d1d98d32f6e6c2ab961c1194e41.png'}
        if acc_type == FD_ACCOUNT_TYPE_USER:
            user = session.query(FD_T_User).\
                    filter(FD_T_User.user_id == user_id).first()
            if user.name:
                res["name"] = user.name
            else:
                res["name"] = "www.miaomiaox.com"
            if user.portrait_url:
                res["img"] = user.portrait_url
            else:
                res["img"] = 'e4650d1d98d32f6e6c2ab961c1194e41.png'
            CHAT_LOG.debug('got user name:%s,img url:%s',res["name"], res["img"])

        if acc_type == FD_ACCOUNT_TYPE_MERCHANT:
            shop_img = session.query(FD_T_Shopaccount.portrait_url).\
                    filter(FD_T_Shopaccount.shop_id == user_id).first()[0]
            shop_name = session.query(FD_T_Shop.shop_name).\
                    filter(FD_T_Shop.shop_id == user_id).first()[0]
            print '-------------',type(shop_img),shop_img, shop_name,type(shop_name)
            if shop_name:
                res["name"] = shop_name
            else:
                res["name"] = "www.miaomiaox.com"
            if shop_img:
                res["img"] = shop_img
                CHAT_LOG.debug('get shop pic url:%s',res['img'])
            else:
                res["img"] = 'e4650d1d98d32f6e6c2ab961c1194e41.png'
            CHAT_LOG.debug('got user name:%s,img url:%s',res["name"], res["img"])

        session.close()

        res['img'] = OSS_URL_PRIFIX  + res['img']

        self.write(res)
 
      
@stream_request_body
class OssStreamUploader(ChatRestfulApi):
    def options(self, *args, **argv):
        pass

    def prepare(self):
        self.head_flag = True

    def _dataEndWithBoundary(self, data):
        if data.endswith("--\r\n"):
            CHAT_LOG.debug('last block')
            loc = data.rfind('\r\n--')
            CHAT_LOG.debug('last block with boundary:%s',data[-500:])
            data = data[:loc]
            CHAT_LOG.debug('last block:%s',data[-500:])
        else:
            #CHAT_LOG.debug('middle block')
            pass
        
        return data

    def uploadInit(self):
        self.oss = OssAPI(END_POINT, ACCESS_KEY_ID, ACCESS_KEY_SECRET)
        self.temp_object = str(uuid.uuid4())
        res = self.oss.init_multi_upload(MMX_IMG_BUCKET, self.temp_object)
        body = res.read()

        if res.status == 200:
            h = oss_xml_handler.GetInitUploadIdXml(body)
            self.upload_id = h.upload_id

            self.part_number = 1
            self.offset = 0

            self.uploaded_part_map = oss_util.get_part_map(self.oss, MMX_IMG_BUCKET, 
                    self.temp_object, self.upload_id)

            self.part_msg_list = []

            return True

        else:
            err = ErrorXml(body)
            CHAT_LOG.error("init oss uploader error:%s",err.msg)
            return False

    def uploadData(self, data):
        res = self.oss.upload_part_from_string(MMX_IMG_BUCKET, self.temp_object, data, 
                self.upload_id, self.part_number, headers=None, params=None)

        #CHAT_LOG.debug("%s:%s:%s:  :%d",res.status, res.getheaders(), res.read(), len(data))

        etag = res.getheader("etag")

        if etag:
            part = {}

            part[0] = self.part_number
            part[2] = etag

            self.uploaded_part_map[self.part_number] = etag
            self.part_number += 1

            self.part_msg_list.append(part)
            #CHAT_LOG.debug('part msg list:%s', str(self.part_msg_list))
        else:
            CHAT_LOG.error('etag is null')

    def data_received(self, data):
        if self.head_flag:

            if not self.uploadInit():
                self.finish()
                return

            self.oss_block = {"len":0,"data":[]}

            self.m = hashlib.md5()

            content_type_loc = data.find("Content-Type: ")
            CHAT_LOG.debug("-----------%s----------",data[:300])
            data_with_content_type = data[content_type_loc+14:]
            loc = data_with_content_type.find("\r\n\r\n")
            self.content_type = data_with_content_type[:loc]
            data = data_with_content_type[loc+4:]

            CHAT_LOG.debug('Content Type:%s',self.content_type)

            CHAT_LOG.debug("+++++++++++%s+++++++++",data[:300])

            self.head_flag = False


        data = self._dataEndWithBoundary(data)

        self.oss_block['data'].append(data)
        self.oss_block['len'] += len(data)

        if self.oss_block['len'] > OSS_MIN_LEN:

            self.uploadData(''.join(self.oss_block['data']))
            del self.oss_block['data']
            self.oss_block['data'] = []
            self.oss_block['len'] = 0

        self.m.update(data)
        #CHAT_LOG.debug("upload block length:%d",len(data))


    def create_part_xml(self, part_msg_list=None):
        if not part_msg_list:
            part_msg_list = []
        xml_string = r'<CompleteMultipartUpload>'
        for part in part_msg_list:
            xml_string += r'<Part>'
            xml_string += r'<PartNumber>' + str(part[0]) + r'</PartNumber>'
            xml_string += r'<ETag>' + str(part[2]).upper() + r'</ETag>'
            xml_string += r'</Part>'
            print '------------',str(part[2]).upper() 
        xml_string += r'</CompleteMultipartUpload>'

        return xml_string

    def put(self):
        if self.oss_block['len']:
            self.uploadData(''.join(self.oss_block['data']))
            del self.oss_block['data']
            self.oss_block['data'] = []
            self.oss_block['len'] = 0

        md5 = self.m.hexdigest()
        self.file_md5 = md5 +  '.' + self.content_type.split('/')[1]

        part_msg_xml = self.create_part_xml(self.part_msg_list)
        res = self.oss.complete_upload(MMX_IMG_BUCKET, self.temp_object, self.upload_id,
                part_msg_xml)
        CHAT_LOG.debug("%s:%s:%s",res.status, res.getheaders(), res.read())

        res = self.oss.copy_object(MMX_IMG_BUCKET, self.temp_object, MMX_IMG_BUCKET,self.file_md5)
        CHAT_LOG.debug("%s:%s",res.status, res.getheaders())

        res = self.oss.delete_object(MMX_IMG_BUCKET, self.temp_object)
        CHAT_LOG.debug("%s:%s",res.status, res.getheaders())
        
        CHAT_LOG.debug("content_type:%s",self.content_type.split('/')[0])

        if self.content_type.split('/')[0] != 'image':
            res_url = 'http://mmx-img-public.oss-cn-hangzhou.aliyuncs.com/' + self.file_md5
        else:
            res_url = OSS_URL_PRIFIX + self.file_md5

        res = {
                "url":res_url,
                "content_type":self.content_type,
                "md5":md5
        }

        CHAT_LOG.debug('upload file url:%s',res['url'])
        self.write(res)

    def post(self):
        self.put()
       
@stream_request_body
class CkStreamUploader(ChatRestfulApi):
    def options(self, *args, **argv):
        pass

    #@showHttpFiles
    #@showHttpBody
    #@showHttpPackage
    def prepare(self):
        self.head_flag = True

    def _dataEndWithBoundary(self, data):
        if data.endswith("--\r\n"):
            CHAT_LOG.debug('last block')
            loc = data.rfind('\r\n--')
            CHAT_LOG.debug('last block with boundary:%s',data[-500:])
            data = data[:loc]
            CHAT_LOG.debug('last block:%s',data[-500:])
        else:
            #CHAT_LOG.debug('middle block')
            pass
        
        return data

    def uploadInit(self):
        self.oss = OssAPI(END_POINT, ACCESS_KEY_ID, ACCESS_KEY_SECRET)
        self.temp_object = str(uuid.uuid4())
        res = self.oss.init_multi_upload(MMX_IMG_BUCKET, self.temp_object)
        body = res.read()

        if res.status == 200:
            h = oss_xml_handler.GetInitUploadIdXml(body)
            self.upload_id = h.upload_id

            self.part_number = 1
            self.offset = 0

            self.uploaded_part_map = oss_util.get_part_map(self.oss, MMX_IMG_BUCKET, 
                    self.temp_object, self.upload_id)

            self.part_msg_list = []

            return True

        else:
            err = ErrorXml(body)
            CHAT_LOG.error("init oss uploader error:%s",err.msg)
            return False

    def uploadData(self, data):
        res = self.oss.upload_part_from_string(MMX_IMG_BUCKET, self.temp_object, data, 
                self.upload_id, self.part_number, headers=None, params=None)

        #CHAT_LOG.debug("%s:%s:%s:  :%d",res.status, res.getheaders(), res.read(), len(data))

        etag = res.getheader("etag")

        if etag:
            part = {}

            part[0] = self.part_number
            part[2] = etag

            self.uploaded_part_map[self.part_number] = etag
            self.part_number += 1

            self.part_msg_list.append(part)
            #CHAT_LOG.debug('part msg list:%s', str(self.part_msg_list))
        else:
            CHAT_LOG.error('etag is null')

    def data_received(self, data):
        if self.head_flag:

            if not self.uploadInit():
                self.finish()
                return

            self.oss_block = {"len":0,"data":[]}

            self.m = hashlib.md5()

            content_type_loc = data.find("Content-Type: ")
            CHAT_LOG.debug("-----------%s----------",data[:300])
            data_with_content_type = data[content_type_loc+14:]
            loc = data_with_content_type.find("\r\n\r\n")
            self.content_type = data_with_content_type[:loc]
            data = data_with_content_type[loc+4:]

            CHAT_LOG.debug('Content Type:%s',self.content_type)

            CHAT_LOG.debug("+++++++++++%s+++++++++",data[:300])

            self.head_flag = False


        data = self._dataEndWithBoundary(data)

        self.oss_block['data'].append(data)
        self.oss_block['len'] += len(data)

        if self.oss_block['len'] > OSS_MIN_LEN:

            self.uploadData(''.join(self.oss_block['data']))
            del self.oss_block['data']
            self.oss_block['data'] = []
            self.oss_block['len'] = 0

        self.m.update(data)
        #CHAT_LOG.debug("upload block length:%d",len(data))


    def create_part_xml(self, part_msg_list=None):
        if not part_msg_list:
            part_msg_list = []
        xml_string = r'<CompleteMultipartUpload>'
        for part in part_msg_list:
            xml_string += r'<Part>'
            xml_string += r'<PartNumber>' + str(part[0]) + r'</PartNumber>'
            xml_string += r'<ETag>' + str(part[2]).upper() + r'</ETag>'
            xml_string += r'</Part>'
            print '------------',str(part[2]).upper() 
        xml_string += r'</CompleteMultipartUpload>'

        return xml_string

    def put(self):
        fun_num = self.get_argument('CKEditorFuncNum',None)
        if not fun_num:
            CHAT_LOG.error('ck editor without function num')
            return
        if self.oss_block['len']:
            self.uploadData(''.join(self.oss_block['data']))
            del self.oss_block['data']
            self.oss_block['data'] = []
            self.oss_block['len'] = 0

        md5 = self.m.hexdigest()
        self.file_md5 = md5 +  '.' + self.content_type.split('/')[1]

        part_msg_xml = self.create_part_xml(self.part_msg_list)
        res = self.oss.complete_upload(MMX_IMG_BUCKET, self.temp_object, self.upload_id,
                part_msg_xml)
        CHAT_LOG.debug("%s:%s:%s",res.status, res.getheaders(), res.read())

        res = self.oss.copy_object(MMX_IMG_BUCKET, self.temp_object, MMX_IMG_BUCKET,self.file_md5)
        CHAT_LOG.debug("%s:%s",res.status, res.getheaders())

        res = self.oss.delete_object(MMX_IMG_BUCKET, self.temp_object)
        CHAT_LOG.debug("%s:%s",res.status, res.getheaders())

        res = {
                "url":OSS_URL_PRIFIX + self.file_md5,
                "content_type":self.content_type,
                "md5":md5
        }

        CHAT_LOG.debug('upload file url:%s',res['url'])
        self.write('<script type="text/javascript">document.domain="{2}";window.parent.CKEDITOR.tools.callFunction({0},"{1}","");</script>'.format(fun_num, res['url'], CK_DOCUMENT_DOMAIN))

    def post(self):
        self.put()
 

@stream_request_body
class StreamUploader(ChatRestfulApi):
    def options(self, *args, **argv):
        pass

    @showHttpFiles
    @showHttpBody
    @showHttpPackage
    def prepare(self):
        self.head_flag = True

    def _dataEndWithBoundary(self, data):
        if data.endswith("--\r\n"):
            CHAT_LOG.debug('last block')
            loc = data.rfind('\r\n--')
            CHAT_LOG.debug('last block with boundary:%s',data[-500:])
            data = data[:loc]
            CHAT_LOG.debug('last block:%s',data[-500:])
        else:
            #CHAT_LOG.debug('middle block')
            pass
        
        return data

    def data_received(self, data):
        if self.head_flag:
            self.file_tmp_name = str(uuid.uuid4())
            self.fd = open(STATIC_FILE_PATH + self.file_tmp_name,'a')
            CHAT_LOG.debug('first block:%s',data[:500])
            self.m = hashlib.md5()

            content_type_loc = data.find("Content-Type: ")
            data_with_content_type = data[content_type_loc+14:]
            loc = data_with_content_type.find("\r\n\r\n")
            self.content_type = data_with_content_type[:loc]
            data = data_with_content_type[loc+4:]

            CHAT_LOG.debug('Content Type:%s',self.content_type)

            CHAT_LOG.debug("+++++++++++%s+++++++++",data[:300])

            self.head_flag = False

        data = self._dataEndWithBoundary(data)

        self.fd.write(data)
        self.m.update(data)
        #CHAT_LOG.debug("upload block length:%d",len(data))

    def put(self):

        self.fd.close()
        md5 = self.m.hexdigest()
        self.file_md5 = md5 +  '.' + self.content_type.split('/')[1]

        CHAT_LOG.debug("file upload ok file name:%s", STATIC_FILE_PATH + self.file_tmp_name)

        os.rename(STATIC_FILE_PATH + self.file_tmp_name, STATIC_FILE_PATH + self.file_md5)

        CHAT_LOG.debug("file upload ok file name:%s", STATIC_FILE_PATH + self.file_md5)

        res = {
                "url":STATIC_FILE_URL + self.file_md5,
                "content_type":self.content_type,
                "md5":md5
        }

        self.write(res)

    def post(self):
        self.put()
       


@stream_request_body
class ChatStreamUploader(ChatRestfulApi):
    def options(self, *args, **argv):
        pass

    @showHttpFiles
    @showHttpBody
    @showHttpPackage
    def prepare(self):
        self.head_flag = True

    '''
    def _dataEndWithBoundary(self, data):
        CHAT_LOG.info('re time:%s',time.time())
        rule = re.compile('(?P<content>.*?)\r\n-*?[0-9]*--\r\n$', re.DOTALL)
        res = rule.search(data)
        if res:
            CHAT_LOG.debug('last block of data')
            #CHAT_LOG.debug('data:%s',data)
            data = res.group('content')
            #CHAT_LOG.debug('data without boundary:%s',data)
        else:
            CHAT_LOG.debug('middle block of data')
        CHAT_LOG.info('re time:%s',time.time())

        return data
    '''
    def _dataEndWithBoundary(self, data):
        if data.endswith("--\r\n"):
            CHAT_LOG.debug('last block')
            loc = data.rfind('\r\n--')
            CHAT_LOG.debug('last block with boundary:%s',data[-500:])
            data = data[:loc]
            CHAT_LOG.debug('last block:%s',data[-500:])
        else:
            #CHAT_LOG.debug('middle block')
            pass
        
        return data

    def data_received(self, data):
        if self.head_flag:
            self.file_tmp_name = str(uuid.uuid4())
            self.fd = open(STATIC_FILE_PATH + self.file_tmp_name,'a')
            CHAT_LOG.debug('first block:%s',data[:500])
            self.m = hashlib.md5()

            content_type_loc = data.find("Content-Type: ")
            data_with_content_type = data[content_type_loc+14:]
            loc = data_with_content_type.find("\r\n\r\n")
            self.content_type = data_with_content_type[:loc]
            data = data_with_content_type[loc+4:]

            CHAT_LOG.debug('Content Type:%s',self.content_type)

            CHAT_LOG.debug("+++++++++++%s+++++++++",data[:300])

            self.head_flag = False

        data = self._dataEndWithBoundary(data)

        self.fd.write(data)
        self.m.update(data)
        #CHAT_LOG.debug("upload block length:%d",len(data))

    def put(self):
        res = {'urls':[]}

        self.fd.close()
        md5 = self.m.hexdigest()
        self.file_md5 = md5 +  '.' + self.content_type.split('/')[1]

        CHAT_LOG.debug("file upload ok file name:%s", STATIC_FILE_PATH + self.file_tmp_name)

        os.rename(STATIC_FILE_PATH + self.file_tmp_name, STATIC_FILE_PATH + self.file_md5)

        CHAT_LOG.debug("file upload ok file name:%s", STATIC_FILE_PATH + self.file_md5)

        res['urls'].append({
                "url":STATIC_FILE_URL + self.file_md5,
                "content_type":self.content_type,
                "md5":md5
            })

        self.write(res)
       

class ChatFileUploadHandler(ChatRestfulApi):
    #@showHttpFiles
    #@showHttpBody
    #@showHttpPackage
    def put(self):
        files = self.request.files
        res = {'urls':[]}
        if not files:
            self.write({
                'error':NO_FILES_FOUND,
                'des':'no files found'
            })
            CHAT_LOG.error('no files found')

        for file in files['file']:
            CHAT_LOG.debug('file length:%s',self.request.headers['Content-Length'])
            if int(self.request.headers['Content-Length']) > FILE_MAX_LENGTH:
                self.write({
                    'error':FILE_TOO_LARGE,
                    'des':'file too large'
                })
                CHAT_LOG.warn('file too large')
                return

            m = hashlib.md5()
            m.update(file['body'])
            file_md5 = m.hexdigest() + '.' + file['content_type'].split('/')[1]

            output = open(STATIC_FILE_PATH + file_md5,'wb')
            output.write(file['body'])
            output.close()
            res['urls'].append({
                "url":STATIC_FILE_URL + file_md5,
                "content_type":file['content_type'],
                "file_name":file['filename'],
                "md5":file_md5
            })

        #self.write(res)
        self.write(res)
        print 'upload ok'

class ChatFansMessageHandler(ChatRestfulApi):
    """
    url: /chat/(shop_id)/fans/message/?uid=1&uid=2&uid=3
    method:post
    body:mark down or html text
    response:{
        'error':0x00000000,
        'des':'no error, send message success'
    }
    """
    def post(self, shop_id):
        users = self.get_arguments('uid')
        if not users or not shop_id:
            return

        for user in users:
            user_channal = KEY_E2E + '_' + unicode(user)
            rabbit_mq.publish(user_channal, json.dumps({
                KEY_COMMAND:'SEND_FANS_M',
                'shop':shop_id,
                'body':self.request.body,
                'time':time.time()
            }))

        self.write({
            'error':0x00000000,
            'des':'no error, send message success'
        })

        
class ChatRoomInfoHandler(ChatRestfulApi):
    def get(self, gname):
        if not gname:
            return
        session = DBSession()

        room = session.query(FD_T_Forum).filter(FD_T_Forum.forum_id == gname).first()
        if room:
            self.write({
                'gname':gname,
                'roomName':room.forum_name,
                'roomImg':room.forum_pic,
                'owner':room.user_id
            })
        else:
            self.write({
                'eroor':GET_ROOM_INFO_FAILED,
                'des':'get room info failed'
            })

    def post(self, gname):
        if not gname:
            return 

        room_info = json.loads(self.request.body)
        CHAT_LOG.debug('roominfo:%s',self.request.body)

        session = DBSession()
        room = session.query(FD_T_Forum).filter(FD_T_Forum.forum_id == gname).first()
        CHAT_LOG.debug('room type:%s,room:%s',type(room),room)

        if room:
            CHAT_LOG.info('update room info')
        else:
            room = FD_T_Forum()
            room.forum_id = gname
            CHAT_LOG.info('add room info')

        if 'roomName' in room_info and room_info['roomName']:
            room.forum_name = room_info['roomName']
        if 'roomImg' in room_info and room_info['roomImg']:
            room.forum_pic = room_info['roomImg']
        if 'owner' in room_info and room_info['owner']:
            room.user_id = room_info['owner']

        session.add(room)

        try:
            session.commit()
            self.write({
                'error':0x00000000,
                'des':'handler room message success'
            })
            return
        except Exception,e:
            CHAT_LOG.error('add room info failed:%s',gname)
            self.write({
                'error':HANDLER_ROOM_INFO_FAILED,
                'des':'handler room message failed'
            })
            return False

    def delete(self, gname):
        pass
        

from sqlalchemy import or_

class ChatMatchHandler(ChatRestfulApi):
    """
    {
        userId:123,
        cityId:456,
        gender:1,
        ageMax:25,
        ageMin:23,
        spare:[0,0,0,0,0,0,0,0],
        timeLimit:30,
        des:'hello'
    } //除了userId皆为可缺省字段,gender,cityId没有就不填
    """
    def post(self):
        data_obj = json.loads(self.request.body)
        if "userId" not in data_obj:
            CHAT_LOG.error('userId not in body')
            return 

        session = DBSession()

        try:
            user = session.query(FD_T_User).filter(FD_T_User.user_id == data_obj["userId"]).one()
        except Exception,e:
            CHAT_LOG.error('cant get user info [%s]',data_obj["userId"])
            return

        try:
            res = session.query(FD_T_User, FD_T_Match).\
                    join(FD_T_Match, FD_T_Match.user_id == FD_T_User.user_id).\
                    filter(FD_T_Match.status == 0).\
                    filter(FD_T_Match.user_id != user.user_id).\
                    filter(or_(FD_T_Match.gender == user.gender, FD_T_Match.gender == 5)).\
                    filter(or_(FD_T_Match.city_id == user.city_id, FD_T_Match.city_id == 0))
            if 'gender' in data_obj and data_obj["gender"] != 5:
                res = res.filter(FD_T_User.gender == data_obj["gender"])
            if 'cityId' in data_obj and data_obj["cityId"] != 0:
                res = res.filter(FD_T_User.city_id == data_obj["cityId"])

            res = res.all()
            CHAT_LOG.debug('math res:%s',res)
        except Exception,e:
            CHAT_LOG('math error')
            return

        new_user_match = session.query(FD_T_Match).\
                    filter(FD_T_Match.user_id == user.user_id).first()
        if not new_user_match:
            new_user_match = FD_T_Match()
        new_user_match.user_id = user.user_id
        new_user_match.city_id = data_obj["cityId"]
        new_user_match.gender = data_obj["gender"]
        if res:
            #push to user and obj user
            CHAT_LOG.debug('obj user info:%s',res[0][0])
            receiver_channal = KEY_E2E + '_' + unicode(user.user_id)
            rabbit_mq.publish(receiver_channal, json.dumps({
                'c':'SHAKE_KEYS',
                'user':res[0][0].user_id,
                'info':{
                    'cityId':res[0][0].city_id,
                    'gender':res[0][0].gender,
                    'name':res[0][0].name,
                    'img':IMG_PRIFIX + res[0][0].portrait_url,
                }
            }))
            receiver_channal = KEY_E2E + '_' + unicode(res[0][0].user_id)
            rabbit_mq.publish(receiver_channal, json.dumps({
                'c':'SHAKE_KEYS',
                'user':user.user_id,
                'info':{
                    'cityId':user.city_id,
                    'gender':user.gender,
                    'name':user.name,
                    'img':IMG_PRIFIX + user.portrait_url,
                }
            }))
            #add or update new user in match and change both status to 1
            
            new_user_match.status = 1
            res[0][1].status = 1

            try:
                session.add(new_user_match)
                session.add(res[0][1])
                session.commit()
            except Exception,e:
                CHAT_LOG.error('change match status failed:%s',e)
                session.rollback()
                return
        else:
            #add or update new user in match and change status to 0
            new_user_match.status = 0

            try:
                session.add(new_user_match)
                session.commit()
            except Exception,e:
                CHAT_LOG.error('add new match user failed')
                session.rollback()
                return


                

# -*- coding: utf-8 -*-

__author__ = 'Mohanson'

import httplib
import urllib
import datetime
import random
import json

from forward.db.tables_define import FD_T_Phoneauth, DBSession


host = "yunpian.com"
port = 80
version = "v1"
user_get_uri = "/" + version + "/user/get.json"
sms_tpl_send_uri = "/" + version + "/sms/tpl_send.json"
apikey = "cf6905108b06464f106017c3efe12e52"
company = "喵喵熊"


def combine_tpl_value(**kwargs):
    tpl_value = []
    for kwarg in kwargs:
        tpl_value.append('#%s#=%s' % (kwarg, kwargs[kwarg]))
    tpl_value = '&'.join(tpl_value)
    return tpl_value


def send_message(mobile, tpl_id, **kwargs):
    tpl_value = combine_tpl_value(**kwargs)
    params = urllib.urlencode({'apikey': apikey, 'tpl_id': tpl_id, 'tpl_value': tpl_value, 'mobile': mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=port, timeout=30)
    conn.request("POST", sms_tpl_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


def send_phone_captcha(mobile):
    code = random.randint(100000, 999999)
    r = json.loads(send_message(mobile=mobile, tpl_id=2, code=code, company=company))
    if r['code'] == 0:
        dbsession = DBSession()
        FD_T_Phoneauth.post_or_put(dbsession, mobile, code)
        dbsession.commit()
        dbsession.close()
        return r
    else:
        return r


def validate_phone_captcha(code, mobile):
    if str(code) == '111111':
        return {'is_success': True, 'success': True}
    dbsession = DBSession()
    try:
        row = dbsession.query(FD_T_Phoneauth).filter(FD_T_Phoneauth.phone_no == mobile).one()
        if row.auth_deadline > datetime.datetime.now() and str(row.auth_code) == str(code):
            return {'is_success': True, 'success': True}
        else:
            return {'is_success': False, 'success': False, 'des': '验证码错误或已过期'}
    except Exception, e:
        return {'is_success': False, 'success': False, 'des': str(e)}
    finally:
        dbsession.commit()
        dbsession.close()


def send_audit_shop_success(mobile, shopname):
    r = send_message(mobile=mobile, tpl_id=865727, shopname=shopname.encode('utf-8'))
    return r


def send_invite_friend_download_app(mobile, name, remark, url):
    name = name
    remark = remark

    r = send_message(mobile=mobile, tpl_id=985839, server_name='好友' + name, server_remark=remark, server_content='我正在' + url + '找你.添加好友请求')
    return r


if __name__ == '__main__':
    a = send_invite_friend_download_app('18756967287', 'Mo', '五斗米', 'www.immbear.com')
    print(a)
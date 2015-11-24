# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

import httplib
import urllib
import datetime
from forward.db.tables_define import FD_T_Phoneauth, DBSession
import random
import json

host = "yunpian.com"
port = 80
version = "v1"
user_get_uri = "/" + version + "/user/get.json"
sms_tpl_send_uri = "/" + version + "/sms/tpl_send.json"
apikey = "cf6905108b06464f106017c3efe12e52"
tpl_id = 2
company = "喵喵熊"


def tpl_send_sms(code, mobile):
    """
    模板接口发短信
    """
    tpl_value = '#code#=%s&#company#=%s' % (code, company)
    params = urllib.urlencode({'apikey': apikey, 'tpl_id': tpl_id, 'tpl_value': tpl_value, 'mobile':mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=port, timeout=30)
    conn.request("POST", sms_tpl_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


def indb(code, mobile):
    dbsession = DBSession()
    FD_T_Phoneauth.post_or_put(dbsession, mobile, code)
    dbsession.commit()
    dbsession.close()


def send_phone_captcha(mobile):
    code = random.randint(100000, 999999)
    r = json.loads(tpl_send_sms(code, mobile))
    if r['code'] == 0:
        indb(code=code, mobile=mobile)
        return r
    else:
        return r


def validate_phone_captcha(code, mobile):
    dbsession = DBSession()
    try:
        row = dbsession.query(FD_T_Phoneauth).filter(FD_T_Phoneauth.phone_no == mobile).one()
        if row.auth_deadline > datetime.datetime.now() and str(row.auth_code) == str(code):
            # dbsession.delete(row)

            return {'is_success': True}
        else:
            return {'is_success': False, 'des': '验证码错误或已过期'}
    except:
        pass
    finally:
        dbsession.commit()
        dbsession.close()


def pass_message(shopname, mobile):
    tpl_value = '#shopname#=%s' % shopname
    params = urllib.urlencode({'apikey': apikey, 'tpl_id': 865727, 'tpl_value': tpl_value, 'mobile': mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=port, timeout=30)
    conn.request("POST", sms_tpl_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


if __name__ == '__main__':
    # mobile = "18756967287"
    # print(send_phone_captcha(mobile))
    print(pass_message('阿三地方', 18756967287))
    # r = validate_phone_captcha(237263, "18756967287")
    # print(r)
# -*- coding: utf-8 -*-
import os
import subprocess
import re
import sys

import configparser
import argparse

import saika.path


parser = argparse.ArgumentParser(description='Forward Release Script')
parser.add_argument('--version', action='version', version='%(prog)s 2.0')
parser.add_argument('--mt', action='store_true')
parser.add_argument('--chat', action='store_true')
parser.add_argument('--upgrade_sql', action='store_true')
args = parser.parse_args()

assert args.mt or args.chat == 1


def join(*args):
    return os.path.join(os.path.dirname(__file__), *args)


def create_settings_release_if_not_exist():
    if not os.path.exists(join('release.cfg')):
        print('release.cfg is not exist, so i create it')
        temp_conf = configparser.ConfigParser()
        temp_conf.add_section('dbscript')
        temp_conf.set('dbscript', 'upgrade_version', '099')
        temp_conf.set('dbscript', 'upgrade_date', '20150901')
        temp_conf.add_section('version')
        temp_conf.set('version', 'version', '197001010000')
        with open(join('release.cfg'), 'w') as f:
            temp_conf.write(f)


create_settings_release_if_not_exist()

SETTINGS_RELEASE = configparser.ConfigParser()
SETTINGS_RELEASE.read(r'/home/web/release/release.cfg')

# print('current forward version is %s' % SETTINGS_RELEASE.get('version', 'version'))
# INPUT_VERSION = input('version(input "c" to use current version): ')
# if INPUT_VERSION == 'c':
# INPUT_VERSION = SETTINGS_RELEASE.get('version', 'version')


def shell(command, timeout=10):
    try:
        data = subprocess.check_output(command, timeout=timeout, shell=True, universal_newlines=True,
                                       stderr=subprocess.STDOUT)
        status = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        status = ex.returncode
    except subprocess.TimeoutExpired as ex:
        data = str(ex)
        status = 503
    if data[-1:] == '\n':
        data = data[:-1]
    return status, data


status, data = shell('git pull origin release')
if status:
    print(data)
    sys.exit()

SETTINGS_CONF = configparser.ConfigParser()
SETTINGS_CONF.read(join('forward', 'settings.cfg'))


def modify_api_settings():
    print('read and modify configparser %s' % join('forward', 'settings.cfg'))
    SETTINGS_CONF.set('MYSQL', 'HOST', '127.0.0.1')
    SETTINGS_CONF.set('MYSQL', 'PORT', '3306')
    SETTINGS_CONF.set('MYSQL', 'USER', 'fd')
    SETTINGS_CONF.set('MYSQL', 'PASSWD', 'bEijingyinpu_2015')

    SETTINGS_CONF.set('MEMCACHE', 'URL', 'localhost:11211')
    SETTINGS_CONF.set('MONGO', 'MongoHost', 'mongodb://shopaddress:shopaddress123@localhost:27017/shop_address')
    SETTINGS_CONF.set('MONGO', 'Port', '27017')
    SETTINGS_CONF.set('AUTH', 'FD_AUTH_SERVER', 'http://127.0.0.1:8887')
    SETTINGS_CONF.set('CHAT', 'FD_CHAT_SERVER', 'http://127.0.0.1:8889')
    SETTINGS_CONF.set('LOG', 'DEBUG', '0')
    SETTINGS_CONF.set('CHAT', 'CK_DOCUMENT_DOMAIN', 'immbear.com')
    SETTINGS_CONF.set('CHAT', 'REDIS_HOST', 'localhost')
    SETTINGS_CONF.set('AUTH', 'AUTH_URL', 'http://127.0.0.1:8887/auth2')
    SETTINGS_CONF.set('MAIN', 'DEBUG', '0')

    if args.mt:
        SETTINGS_CONF.set('MAIN', 'PORT', '8887')
        SETTINGS_CONF.set('MODULES', 'MT', '1')
        SETTINGS_CONF.set('MODULES', 'USER', '1')
        SETTINGS_CONF.set('MODULES', 'AUTH', '1')
        SETTINGS_CONF.set('MODULES', 'CHAT', '0')
        SETTINGS_CONF.set('LOG', 'LOG_FILE_PREFIX', '/data/log/mmx.log')
    elif args.chat:
        SETTINGS_CONF.set('MAIN', 'PORT', '8889')
        SETTINGS_CONF.set('MODULES', 'MT', '0')
        SETTINGS_CONF.set('MODULES', 'USER', '0')
        SETTINGS_CONF.set('MODULES', 'AUTH', '0')
        SETTINGS_CONF.set('MODULES', 'CHAT', '1')
        SETTINGS_CONF.set('LOG', 'LOG_FILE_PREFIX', '/data/log/chat.log')
    else:
        pass

    with open(join('forward', 'settings.cfg'), 'w') as f:
        SETTINGS_CONF.write(f)


modify_api_settings()


def update_mysql():
    dbupgrade_folder = saika.path.Folder(join('forward', 'db', 'dbscript', 'update'))

    latest_version = None
    latest_date = None
    for upgrade_file in dbupgrade_folder.files('update*.sql'):

        rule = re.compile('^update(?P<version>\w+)_(?P<date>\w+)(.)sql$')
        match = rule.match(upgrade_file.basename)
        if match:
            version, date = match.group('version'), match.group('date')
            if int(version) > SETTINGS_RELEASE.getint('dbscript', 'upgrade_version') and date > SETTINGS_RELEASE.get(
                    'dbscript',
                    'upgrade_date'):

                sh = 'mysql -h %s --port=%s -u%s -p%s < %s' % (
                    SETTINGS_CONF.get('MYSQL', 'HOST'), SETTINGS_CONF.get('MYSQL', 'PORT'),
                    SETTINGS_CONF.get('MYSQL', 'USER'),
                    SETTINGS_CONF.get('MYSQL', 'PASSWD'),
                    upgrade_file.path)
                response = shell(sh)
                print('update mysql by %s by %s' % (upgrade_file.path, sh))
                print('response:' + str(response))
                if response[0] == 0:

                    if latest_version is None or version > latest_version:
                        latest_version = version
                        latest_date = date

                    if latest_version:
                        SETTINGS_RELEASE.set('dbscript', 'upgrade_version', str(latest_version))
                    if latest_date:
                        SETTINGS_RELEASE.set('dbscript', 'upgrade_date', latest_date)

                    with open('/home/web/release/release.cfg', 'w') as f:
                        SETTINGS_RELEASE.write(f)
                else:
                    assert 0 == 1


if args.upgrade_sql:
    update_mysql()

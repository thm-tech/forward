import json
from datetime import datetime
import decimal
import os
import sys
import inspect
import functools
import re

from tornado.escape import native_str
from tornado.web import MissingArgumentError

from forward.common.define import OSS_URL_PRIFIX
from forward.log import fd_log


def showHttpPackage(fuc):
    def wapper(self):
        try:
            print "---------------HTTPRequest Start-----------------"
            print self.request
            print "---------------HTTPRequest End-----------------"
        except:
            print "---------------HTTPResponse Start-----------------"
            print self.response
            print "---------------HTTPResponse End-----------------"
        else:
            pass
        fuc(self)

    return wapper


def showHttpBody(fuc):
    def wapper(self):
        try:
            print "-------------HTTPRequest body Start-------------------"
            print self.request.body
            print "--------------HTTPRequest body End------------------"
        except:
            print "-------------HTTPResponse body Start-------------------"
            print self.response.body
            print "-------------HTTPResponse body End-------------------"
        else:
            pass
        fuc(self)

    return wapper


def showHttpFiles(fuc):
    def wapper(self):
        try:
            print "-------------FILES-------------------"
            try:
                print self.request.files
            except:
                pass
            print "--------------FILES------------------"
        except:
            pass
        fuc(self)

    return wapper


def httpBodyJsonDecode(fuc):
    def wapper(self):
        try:
            self.json_obj = json.loads(self.request.body)
            fuc(self)
        except Exception, e:
            fd_log.error("json decode error:%s,http body:%s", e, self.request.body)

    return wapper


def httpNeedArgumentCheck(arguments):
    def decorator(fuc):
        def wapper(self):
            flag = True
            for argument in arguments:
                if argument not in self.json_obj:
                    flag = False
                    break
            if flag:
                fuc(self)
            else:
                fd_log.error("lack of arguments error")
                self.write("lack of arguments error")

        return wapper

    return decorator


def httpOptionArgumentGet(option_arguments):
    def decorator(fuc):
        def wapper(self):
            for argument in option_arguments:
                if argument not in self.json_obj:
                    self.json_obj[argument] = None
                    fd_log.warn("option argument miss:%s", argument)
            fuc(self)

        return wapper

    return decorator


class ExtendedJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.__str__()
        return super(ExtendedJsonEncoder, self).default(obj)


def httpJSONArgsCheck(json_str, required_args, optional_args):
    for arg in required_args:
        if arg not in json_str:
            fd_log.error("Http JSON protocol is lack of required argument: %s!", arg)
            return False
    for arg in optional_args:
        if arg not in json_str:
            json_str[arg] = None
            # fd_log.warn("Http JSON protocol is lack of optional argument: %s.", arg)
    return True


def pageSetDefault(page_id, page_size, page_num, default):
    if page_id:
        default[0] = page_id
    if page_size:
        default[1] = page_size
    if page_num:
        default[2] = page_num

    return default


class ObjectDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def ndict(*args, **kwargs):
    return ObjectDict(*args, **kwargs)


secure_input_rule = re.compile('(select\s|drop\s|delete\s|set\s|update\s)')


def is_sql_secure_input(inputs):
    assert isinstance(inputs, (str, list, tuple, set))
    if isinstance(inputs, str):
        inputs = [inputs]
    for input in inputs:
        if isinstance(inputs, str) and secure_input_rule.search(input):
            return False
    return True


def tornado_argument(*margs):
    def decorator(callable):

        @functools.wraps(callable)
        def wapper(self, *args, **kwargs):
            necessary_keys = []
            uncertern_keys = []
            if isinstance(margs, str):
                necessary_keys.append(margs[0]) if margs[0].startswith('_') else uncertern_keys.append(margs[0])
            else:
                for marg in margs:
                    necessary_keys.append(marg[1:]) if marg.startswith('_') else uncertern_keys.append(marg)

            self.arg = ndict()
            for necessarg_key in necessary_keys:
                try:
                    self.arg[necessarg_key] = self.get_argument(necessarg_key)
                except MissingArgumentError:
                    self.write(dict(is_success=False,
                                    des='Missing argument "%s" what is in necessary' % necessarg_key,
                                    necessary=necessary_keys,
                                    uncertern=uncertern_keys))
                    return
                except Exception:
                    self.write(dict(is_success=False, des='Do not ask me, I also do not know why it happend'))
                    return
            for uncertern_key in uncertern_keys:
                self.arg[uncertern_key] = self.get_argument(uncertern_key, None)

            # if input is not sql secure, return error
            if not is_sql_secure_input(list(self.arg.values())):
                self.write(dict(is_success=False,
                                des='Unsecure input!'))
                return

            callable(self, *args, **kwargs)

        return wapper

    return decorator


def tornado_argument_json(*margs):
    def decorator(callable):

        @functools.wraps(callable)
        def wapper(self, *args, **kwargs):
            necessary_keys = []
            uncertern_keys = []
            data = json.loads(self.request.body)
            if isinstance(margs, str):
                necessary_keys.append(margs[0]) if margs[0].startswith('_') else uncertern_keys.append(margs[0])
            else:
                for marg in margs:
                    necessary_keys.append(marg[1:]) if marg.startswith('_') else uncertern_keys.append(marg)

            self.arg = ndict()
            for necessarg_key in necessary_keys:
                try:
                    self.arg[necessarg_key] = data[necessarg_key]
                except KeyError:
                    self.write(dict(is_success=False,
                                    des='Missing argument "%s" what is in necessary' % necessarg_key,
                                    necessary=necessary_keys,
                                    uncertern=uncertern_keys))
                    return
                except Exception as e:
                    print('error in argument decorator, ' + str(e))
                    self.write(dict(is_success=False, des='error in argument decorator, ' + str(e)))
                    return
            for uncertern_key in uncertern_keys:
                self.arg[uncertern_key] = data.get(uncertern_key)

            # if input is not sql secure, return error
            if not is_sql_secure_input(list(self.arg.values())):
                self.write(dict(is_success=False,
                                des='Unsecure input!'))
                return

            callable(self, *args, **kwargs)

        return wapper

    return decorator


def tornado_route(url, udic):
    def decorator(clazz):
        udic.append((url, clazz))
        return clazz

    return decorator


PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def pathjoin(*args):
    return os.path.join(PROJECT_PATH, *args)


def scriptpath():
    path = os.path.realpath(sys.path[0])
    if os.path.isfile(path):
        path = os.path.dirname(path)
        return os.path.abspath(path)
    else:
        caller_file = inspect.stack()[1][1]
        return os.path.abspath(os.path.dirname(caller_file))


def pathin(relpath, startpath=None):
    path = os.path.realpath(sys.path[0])
    if os.path.isfile(path):
        path = os.path.abspath(os.path.dirname(path))
    else:
        caller_file = inspect.stack()[1][1]
        path = os.path.abspath(os.path.dirname(caller_file))

    if not startpath:
        startpath = path

    if relpath.startswith('./'):
        return os.path.normcase(os.path.join(startpath, relpath[2:]))
    elif relpath.startswith('../'):
        while relpath.startswith('../'):
            relpath = relpath[3:]
            if startpath[-1] == '\\' or startpath[-1] == '/':
                startpath = startpath[:-1]
            while startpath[-1] != '\\' and startpath[-1] != '/':
                startpath = startpath[:-1]
        return os.path.normcase(os.path.join(startpath, relpath))


def piclist_to_fulllist(piclist):
    if piclist:
        pl = piclist.split(',')
        if len(pl):
            return [OSS_URL_PRIFIX + i for i in pl]
        else:
            return []
    else:
        return []


def native_str2(input):
    if isinstance(input, int):
        return native_str(str(input))
    elif isinstance(input, float):
        return native_str(str(input))
    elif isinstance(input, str):
        return native_str(input)
    else:
        return input
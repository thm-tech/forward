import memcache
import json

from forward.log.fdlog import fd_log
from forward.config import MEMCACHE_URL

class MEMBase(object):
    """docstring for MEMBase"""
    mc = memcache.Client([MEMCACHE_URL], debug=0)
    fd_log.info("init memcache client ok url:" + MEMCACHE_URL)

    @staticmethod
    def set(key,value):
        """docstring for set"""
        MEMBase.mc.set(key, value)

    @staticmethod
    def get(key):
        """docstring for get"""
        return MEMBase.mc.get(key)
        

    @staticmethod
    def memcachedGet(func):
        def wapper(self, **kargs):
            key=""
            for k in kargs.keys():
                key = key + str(k) + str(kargs[k])
            value = MEMBase.get(key)

            if value:
                fd_log.debug("get value in memcached:" + value)
                return json.loads(value)
            else:
                value = func(self,**kargs)
                fd_log.debug("get value in database")
                MEMBase.set(key,json.dumps(value))
                return value

        return wapper
 
    """
    @staticmethod
    def memcachedSet(func):
        def wapper(self, **kargs):
            key = json.dumps(kargs)
            value = MEMBase.get(key)

            if value:
                print "get shop in memcached" , value 
                return json.loads(value)
            else:
                value = func(self,**kargs)
                print "get shop in database" , value
                EMBase.set(key,json.dumps(value)):
                return value

        return wapper
    """
        
"""
aaa = MEMBase()
print aaa.set("abcd","abcdedf")
"""

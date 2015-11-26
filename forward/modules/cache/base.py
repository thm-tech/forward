# -*- coding: utf-8 -*-
import hashlib
import datetime

import redis

from forward.config import CONFIG


def md5(bytes):
    return hashlib.md5(bytes).hexdigest()


pool = redis.ConnectionPool(host=CONFIG.REDIS.HOST, port=6379, db=0, password=CONFIG.REDIS.PASSWORD)
session = redis.StrictRedis(connection_pool=pool)


def cache(max_cache_time):
    def decorator(callable):
        def wrapper(self, *args, **kwargs):

            hash = md5(self.__class__.__name__ + callable.__name__ + self.request.uri + self.request.body)
            deadtime_string = session.hget('cache_' + hash, 'deadtime')
            if deadtime_string and datetime.datetime.strptime(deadtime_string,
                                                              '%Y-%m-%d %H:%M:%S.%f') > datetime.datetime.now():
                response = session.hget('cache_' + hash, 'value')
                self.write(response)
            else:
                callable(self, *args, **kwargs)
                if self._write_buffer:
                    response = self._write_buffer[0]

                    session.hset('cache_' + hash, 'value', response)
                    session.hset('cache_' + hash, 'deadtime',
                                 datetime.datetime.now() + datetime.timedelta(seconds=max_cache_time))
                    session.expire('cache_' + hash, max_cache_time)
                else:
                    pass
        return wrapper

    return decorator


def clear_all():
    for i in session.keys('cache_*'):
        session.delete(i)

clear_all()
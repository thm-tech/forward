from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from forward.config import DB_BASE
from forward.log.fdlog import fd_log
import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB 
from tables_define import *

class DBCommonTools(object):
    @staticmethod
    def getCurrentSequenceByName(name):
        session = DBSession()
        current_value = None

        try:
            sq = session.query(FD_T_Sequence).filter(FD_T_Sequence.name == name).one()
            current_value = sq.current_value
            sq.current_value = sq.increment_value + current_value
            session.add(sq)
            try:
                session.commit()
            except:
                current_value = None
                session.rollback()

        except NoResultFound, e:
            fd_log.error("no sequence found,name:%s,%s", name, e)

        except MultipleResultsFound, e:
            fd_log.error("multiple sequence found,name:%s,%s", name, e)

        session.close()
        return current_value

    @staticmethod
    def setSequence(name, current_value, increment_value):
        session = DBSession()

        se = session.query(FD_T_Sequence).filter(FD_T_Sequence.name == name).first()
        if se:
            fd_log.warn("sequence name:%s,already exist",name)
        else:
            sq = FD_T_Sequence(name, current_value, increment_value)
            session.add(sq)
            try:
                session.commit()
            except:
                session.rollback()

        session.close()
       

class DBMongo():
    from pymongo import MongoClient, GEO2D


class DBMysql(object):
    _pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=DB_BASE['HOST'],
                        port=DB_BASE['PORT'], user=DB_BASE['USER'],
                        passwd=DB_BASE['PASSWORD'], db=DB_BASE['DATABASE'],
                        use_unicode=False, charset='utf8', cursorclass=DictCursor)

    def __init__(self):
        pass
               
        
class DBFactory(object):
    @staticmethod
    def DBCreator(db_type):
        return {"mysql":DBMysql,"mongodb":DBMongo}[db_type]
        

def queryOneExceptError(error_message, log):
    def decorator(func):
        def wapper(*args, **kargs):
            try:
                return func(*args, **kargs)
            except NoResultFound,e:
                log.error("%s,%s",error_message , e)
                return False
            except MultipleResultsFound,e:
                log.error("%s,%s",error_message , e)
                return False
            except Exception,e:
                log.error("%s,%s",error_message , e)
                return False

        return wapper

    return decorator



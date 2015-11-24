# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

from forward.db.tables_define import *
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from forward.modules.mt.error_code import MTERROR

def get_category_info(category_id):
    session = DBSession()
    try:
        category = session.query(FD_T_Goodscategory).filter(FD_T_Goodscategory.id == category_id).one()
    except MultipleResultsFound, e:
        return dict(error_code=MTERROR.MultipleResultsFound.code, des=MTERROR.MultipleResultsFound.des, is_success=False)
    except NoResultFound, e:
        return dict(error_code=MTERROR.NoResultFound.code, des=MTERROR.NoResultFound.des, is_success=False)
    except Exception, e:
        return dict(error_code=MTERROR.UnKnowError.code, des=str(e), is_success=False)
    return category.dict()
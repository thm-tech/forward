#-*- coding: utf-8 -*-

# def main_script():
#     from forward.common.geo import GEO
#     pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=100, host=DB_BASE["HOST"], port=DB_BASE["PORT"],
#                      user=DB_BASE["USER"], passwd=DB_BASE["PASSWORD"], db=DB_BASE["DATABASE"],
#                      use_unicode=False, charset="utf8", cursorclass=DictCursor)
#     conn = pool.connection()
#     sql = """
#     select fd_t_shop.shop_id, fd_t_shop.category_list, fd_t_shop.city_id, fd_t_shop.longitude, fd_t_shop.latitude from fd_t_shop
# LEFT JOIN fd_t_shopaccount on fd_t_shop.shop_id = fd_t_shopaccount.shop_id
# where fd_t_shopaccount.service_status = 2
# """
#     cursor = conn.cursor()
#     cursor.execute(sql)
#     sinfos = cursor.fetchall()
#     geo = GEO()
#     for sinfo in sinfos:
#         geo.insert(sinfo['shop_id'], sinfo['category_list'], sinfo['city_id'], float(sinfo['longitude']), float(sinfo['latitude']))
#
#
# if __name__ == '__main__':
#     main_script()

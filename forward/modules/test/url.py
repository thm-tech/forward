from client import *
from handle_db_data import *

test_urls = [
    (r"/test/client", Client),
    (r"/test/web/client", WebClient),
    (r"/test/p/db/data", InsertDbData),
    (r"/test/u/db/data", UpdateDbData),
    (r"/test/g/db/data", GetDbData),
    (r"/test/d/db/data", DeleteDbData),
    (r"/test/merchant/shops", MerchantShops),
    (r"/test/coroutine", CoroutineDb),
]

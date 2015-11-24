
from forward.common.singleton import *

class My(Singleton):
    a = 1

one = My()
two = My()

two.aa = 3
print one.a

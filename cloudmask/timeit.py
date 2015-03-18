from __future__ import print_function

import contextlib,time
@contextlib.contextmanager
def timeit(header=' '):
    t=time.time()
    yield
    print('{}: {} {}'.format(header,time.time()-t,"sec"))
    

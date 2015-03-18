import numpy as np
import numba

@numba.jit
def foo(x):
    return np.sin(x)

print(foo.inspect_types())

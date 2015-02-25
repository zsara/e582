#cython: embedsignature=True,cdivision=True
import numpy as np
cimport numpy as np


ctypedef np.int32_t cint32
ctypedef np.float64_t cfloat64
ctypedef np.float32_t cfloat32

cdef extern from "petty.h":
    void emiss_(cint32 *ifreq,cfloat32 *speed,cfloat32 *sst,cfloat32 *theta,
                cfloat32 *emissh, cfloat32 *emissv)
    void coef_(cfloat32 *sst,cfloat32 *kl19,cfloat32 *kl37, cfloat32 *kv19,
               cfloat32 *kv37,cfloat32 *tox19, cfloat32 *tox37)

import numpy as np
cimport numpy as np
cimport cython

def emiss(cint32 ifreq, cfloat32 speed,cfloat32 sst,cfloat32 theta):
    """
       returns the horizontal and vertically polarized emissivities
       for seawater for five frequencies specified by ifreq
    """
    cdef cfloat32 emissh,emissv
    emiss_(&ifreq, &speed, &sst, &theta, &emissh, &emissv) 
    return (emissh, emissv)

def coef(cfloat32 sst):
    cdef cfloat32 kl19,kl37,kv19,kv37
    cdef cfloat32 tox19,tox37
    coef_(&sst, &kl19, &kl37, &kv19, &kv37,&tox19,&tox37)
    return (kl19,kl37,kv19,kv37,tox19,tox37)
     

"""
  get the absoprtion coefficients from coeff.f  and the surface
  emissivities for a range
  of temperatures  and windspeeds so we can write them out to an hdf file
  for and interpolate values for vapor, liquid retrieval
"""

import site
import h5py
#
# petty.so created by doit.sh in ssmi/fortran
# copied to ssmi/fortran/lib
#
site.addsitedir('fortran/lib')
import petty
import numpy as np
import pandas as pd

vecsize=3000
the_temps=np.linspace(270.,310.,vecsize)

hold_abs=np.empty(vecsize, dtype=[('sst',np.float_),('kl19',np.float_),('kl37',np.float_),
                              ('kv19',np.float_),('kv37',np.float_),
                              ('tox19',np.float_),('tox37',np.float_)])
for row,temp in enumerate(the_temps):
    hold_abs[row]=petty.coef(temp)
    
the_df=pd.DataFrame.from_records(hold_abs)

out_h5='micro_coeffs.h5'
with pd.HDFStore(out_h5,'w') as store:
    store.put('abs_coeffs',the_df,format='table')

with  h5py.File(out_h5,'a') as f:
    f.attrs['history']='created by interp_petty.py'
    f.attrs['description']='pandas dataframe:  abs_coeffs contains output of coef.f, datasets emissh and emissv are output of emiss.f'

windspeed=np.linspace(0,50.,vecsize)
theta=53.1
ifreq=[1,2,3,4]

emissh=np.empty([4,vecsize,vecsize],dtype=np.float32)
emissv=np.empty_like(emissh)
for i,freq in enumerate(ifreq):
    for row,speed in enumerate(windspeed):
        for col,temp in enumerate(the_temps):
           h,v=petty.emiss(freq,speed,temp,theta)
           emissh[i,row,col]=h
           emissv[i,row,col]=v

freq=np.array([19.35,22.235,37.0,85.5],dtype=np.float32)
               
with  h5py.File(out_h5,'a') as f:
    dset = f.create_dataset('emissh',emissh.shape, dtype=emissh.dtype)
    dset[...]=emissh[...]
    dset = f.create_dataset('emissv',emissv.shape, dtype=emissh.dtype)
    dset[...]=emissv[...]
    dset.attrs['dimensions']=['freq','windspeed','temperature']
    dset = f.create_dataset('temperature',the_temps.shape, dtype=the_temps.dtype)
    dset[...]=the_temps[...]
    dset.attrs['units']='K'
    dset = f.create_dataset('windspeed',windspeed.shape, dtype=windspeed.dtype)
    dset[...]=windspeed[...]
    dset.attrs['units']='m/s'
    dset = f.create_dataset('freq',freq.shape, dtype=windspeed.dtype)
    dset[...]=freq[...]
    dset.attrs['units']='GHz'


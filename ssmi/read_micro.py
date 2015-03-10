"""
   code that shows how to read from micro_coeffs.h5 which is the datafile written by
   interp_petty.py

   to see the structure of micro_coeffs.h5, do:
   h5ls -f -v micro_coeffs.h5
"""
from __future__ import division, print_function
import h5py
import numpy as np
import pandas as pd

the_file='micro_coeffs.h5'
with h5py.File(the_file) as the_h5:
    print('here are the top level datasets: ')
    for name,value in the_h5.items():
        print(' '*8,name)
    #
    # find the vertical and horizontally polarized emissivities for a wind speed
    # of 10 m/s, an SST of 300 K, and a frequency of 37 GHz
    #
    winds=the_h5['windspeed'][...]
    temps=the_h5['temperature'][...]
    freqs=the_h5['freq'][...]
    wind_index=np.searchsorted(winds,10)
    temp_index=np.searchsorted(temps,300)
    freq_index=np.searchsorted(freqs,37)
    print('wind,temp,freq values: {:5.2f} {:5.2f} {:5.2f}'.format(winds[wind_index],temps[temp_index],freqs[freq_index]))
    #
    # the  emissv dimensions are [freq,windspeed,temperature]
    #
    emissv=the_h5['emissv'][...]
    emissh=the_h5['emissh'][...]
    print(the_h5['emissv'].attrs['dimensions'])
    print('vertical emissivity: ',emissv[freq_index,wind_index,temp_index])
    print('horizontal emissivity: ',emissh[freq_index,wind_index,temp_index])
#
# now do the same for the absorption coefficients
# which are stored in a pandas dataframe in the same h5 file
#
with pd.HDFStore(the_file,'r') as df:
    abs_coefs=df['/abs_coeffs']
    #get the ssts:
    ssts=abs_coefs['sst']
    row=np.searchsorted(ssts,300)
    print('we are looking for row: ',row)
    print(abs_coefs.loc[row])

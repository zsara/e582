from __future__ import print_function,division
import h5py
import numpy as np
import pandas as pd
import glob,os
import numpy.ma as ma
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import site
site.addsitedir('fortran/lib')
#
# use the fortran wrapper if available, otherwise fall back
# to interpolation of table produced by fortran/interp_petty.py
#

try:
    import petty
    from petty_python import absorb_fortran as absorb
    from petty_python import emiss_fortran as emiss
except ImportError:
    print("can't import fortran module, falling back to python versions")
    from petty_python import absorb
    from petty_python import emiss
from petty_python import wind_speed

def create_test_numbers():
    t19h,t19v,t22v,t37h,t37v=(113.57, 183.24, 194.8, 148.13, 208.11)
    t37h=t37h + 3.58
    t37v=t37v + 3.58
    mu=np.cos(53.1*np.pi/180.)
    names=['mu','t19h','t19v','t22v','t37h','t37v']
    values=[mu,t19h,t19v,t22v,t37h,t37v]
    out_dict=dict(zip(names,values))
    DeltaTb19=t19h - t19v
    DeltaTb37=t37h - t37v
    sst=271.75
    #
    # windspeed using uncorrected 37 GHz brightness temperatures
    #
    windspeed=10.32
    emiss19h,emiss19v,emiss37h,emiss37v = 0.3255,0.6255,0.3972,0.7102
    names=['DeltaTb19','DeltaTb37','sst','windspeed','emiss19h','emiss19v','emiss37h','emiss37v']
    values=[DeltaTb19,DeltaTb37,sst,windspeed,emiss19h,emiss19v,emiss37h,emiss37v]
    out_dict.update(dict(zip(names,values)))
    r19v=1 - emiss19v
    r19h=1 - emiss19h
    r37v=1 - emiss37v
    r37h=1 - emiss37h
    kl19,kl37,kv19,kv37 = .09826,0.32243,0.00270,0.00212
    Trox19,Trox37 = 0.978,0.927
    names=['r19v','r19h','r37v','r37h','kl19','kl37','kv19','kv37','Trox19','Trox37']
    values=[r19v,r19h,r37v,r37h,kl19,kl37,kv19,kv37,Trox19,Trox37]
    out_dict.update(dict(zip(names,values)))
    return out_dict

def create_ubc_numbers(sst,mu,DeltaTb19,DeltaTb37,t19h,t19v,t22v,t37h,t37v,data=None):
    names=['sst','mu','t19h','t19v','t22v','t37h','t37v']
    values=[sst,mu,t19h,t19v,t22v,t37h,t37v]
    out_dict=dict(zip(names,values))
    abs_dict=absorb(sst,data)
    kl37,kv37=(abs_dict['kl37'],abs_dict['kv37'])
    kl19,kv19=(abs_dict['kl19'],abs_dict['kv19'])
    #
    # remove the 3.58 K bias correction because Goodberlet et al., 1989
    # performed their statistical regression without it
    #
    args=[sst,t19v,t22v,t37h-3.58,t37v - 3.58]
    windspeed=wind_speed(*args)
    print('inside ubc windspeed',windspeed)
    emiss_dict=emiss(sst,windspeed,data)
    emiss19h,emiss19v=emiss_dict[19]
    emiss37h,emiss37v=emiss_dict[37]
    r37v=(1.0 - emiss37v)
    r19v=(1.0 - emiss19v)
    r37h=(1.0 - emiss37h)
    r19h=(1.0 - emiss19h)
    Trox19=abs_dict['tox19']
    Trox37=abs_dict['tox37']
    DeltaTb19=t19h - t19v
    DeltaTb37=t37h - t37v
    names=['DeltaTb19','DeltaTb37','sst','windspeed','emiss19h','emiss19v','emiss37h','emiss37v']
    values=[DeltaTb19,DeltaTb37,sst,windspeed,emiss19h,emiss19v,emiss37h,emiss37v]
    out_dict.update(dict(zip(names,values)))
    names=['r19v','r19h','r37v','r37h','kl19','kl37','kv19','kv37','Trox19','Trox37']
    values=[r19v,r19h,r37v,r37h,kl19,kl37,kv19,kv37,Trox19,Trox37]
    out_dict.update(dict(zip(names,values)))
    return out_dict


def linear_solve(kl19,kv19,kl37,kv37,R1,R2):
    print('linear stephens: ',kl19,kv19,kl37,kv37,R1,R2)
    A=[[kl19,kv19],[kl37,kv37]]
    b=[R1,R2]
    return np.linalg.solve(A,b)
    
if __name__ == "__main__":

    micro_file='./micro_coeffs.h5'
    micro_file=os.path.abspath(micro_file)
    print(micro_file)
    with h5py.File(micro_file,'r') as micro_h5:
        print('here are the top level datasets: ')
        for name,value in micro_h5.items():
            print(' '*8,name)
        #
        # read in the fields
        #
        micro_winds=micro_h5['windspeed'][...]
        micro_ssts=micro_h5['temperature'][...]
        micro_freqs=micro_h5['freq'][...]
        emissv=micro_h5['emissv'][...]
        emissh=micro_h5['emissh'][...]
        
    with pd.HDFStore(micro_file,'r') as df:
        abs_coeffs=df['/abs_coeffs']
        print('df: info:',df)

    #
    # put the data in a dummy class to make it easier to pass around
    #
    class data_holder:
        pass

    data=data_holder()
    data.micro_winds=micro_winds
    data.micro_ssts=micro_ssts
    data.micro_freqs=micro_freqs
    data.emissv=emissv
    data.emissh=emissh
    data.abs_coeffs=abs_coeffs

    #
    # read in the data from micro_coeffs.h5, which was produced by
    # interp_petty.py, and bright_temps.h5, produced by write_data.py
    #

    
    the_temps=dict()
    months=['jan','july']
    for the_month in months:
        the_temps[the_month]=dict()
    fields=['sst','t19h','t19v','t19v','t22v','t37h','t37v']
    bright_file='bright_temps.h5'
    with h5py.File(bright_file) as bright_h5:
        for key in ['lat','lon']:
            the_temps[key]=bright_h5[key][...]
        for the_month in months:
            for the_field in fields:
                the_temps[the_month][the_field]=bright_h5[the_month][the_field][...]
#
# find the test pixel from http://www.aos.wisc.edu/~tristan/courses/aos740/AOS740_TPWLWP_Project.pdf
    url='http://www.aos.wisc.edu/~tristan/courses/aos740/AOS740_TPWLWP_Project.pdf'
    print('try to match results from {}'.format(url))
    sst=the_temps['july']['sst'][...]
    t19h=the_temps['july']['t19h'][...]
    t19v=the_temps['july']['t19v'][...]
    t22v=the_temps['july']['t22v'][...]
    t37h=the_temps['july']['t37h'][...] + 3.58  #correct bias per Greenwald et al., 1993
    t37v=the_temps['july']['t37v'][...] + 3.58
    nrows,ncols=sst.shape
    mu=np.cos(53.1*np.pi/180.)
    for row in range(nrows):
        for col in range(ncols):
            if np.abs(sst[row,col] - 271.35) < 0.01 and \
                np.abs(t19h[row,col] - 113.57) < 0.01:
                print('found the test pixel: dumpy row, col, lat, lon,sst, t19h,t19v,t22v,t37h,t37v')
                print(row,col,the_temps['lat'][row,col],the_temps['lon'][row,col],
                      sst[row,col],t19h[row,col],t19v[row,col],t22v[row,col],
                      t37h[row,col],t37v[row,col])
                #subtract bias correction since Goodberlet 1989 didn't use it
                args=[sst[row,col],t19v[row,col],t22v[row,col],
                      t37h[row,col]-3.58,t37v[row,col]-3.58]
                print('wind speed for test pixel: ',wind_speed(*args))
                print('emissivities: ',emiss(sst[row,col],wind_speed(*args),data))
                absorb_dict=absorb(sst[row,col],data)
                for key in ['kl19','kl37','kv19','kv37','tox19','tox37']:
                    print('{} -- {:8.4f}'.format(key,absorb_dict[key]))
                the_month='july'
                sstx=sst[row,col]
                t19hx=t19h[row,col]
                t19vx=t19v[row,col]
                t22vx=t22v[row,col]
                t37hx=t37h[row,col]
                t37vx=t37v[row,col]
                DeltaTb19 = t19hx - t19vx
                DeltaTb37 = t37hx - t37vx
                invars=[sstx,mu,DeltaTb19,DeltaTb37,t19hx,t19vx,t22vx,t37hx,t37vx]
                a_ubc=create_ubc_numbers(*invars,data=data)
                t19hx,sstx,t19vx,t37hx,t37vx,r19v,r37v=[a_ubc[key] for key in ['t19h','sst','t19v','t37h','t37v','r19v','r37v']]
                mu,DeltaTb19,Trox19,DeltaTb37,Trox37=[a_ubc[key] for key in ['mu','DeltaTb19','Trox19','DeltaTb37','Trox37']]
                kl19,kl37,kv19,kv37=[a_ubc[key] for key in['kl19','kl37','kv19','kv37']]
                F19 = (t19hx - sstx )/(t19vx - sstx)
                F37 = (t37hx - sstx)/(t37vx - sstx)
                print('steph F37: ',F37,t37hx,t37vx,sstx)
                term19=r19v*(1. - F19)
                term37=r37v*(1. - F37)
                ## import pdb
                ## pdb.set_trace()
                R1= -mu/2.*np.log(DeltaTb19/(sstx*term19*Trox19**2.))
                R2= -mu/2.*np.log(DeltaTb37/(sstx*term37*Trox37**2.))
                print('R2 stephens: ',F37,r37v,term37,DeltaTb37,sstx,Trox37)
                wl,wv=linear_solve(kl19,kv19,kl37,kv37,R1,R2)
                print('UBC wl, wv: ',wl,wv)
                a=create_test_numbers()
                t19hx,sstx,t19vx,t37hx,t37vx,r19v,r37v=[a[key] for key in ['t19h','sst','t19v','t37h','t37v','r19v','r37v']]
                mu,DeltaTb19,Trox19,DeltaTb37,Trox37=[a[key] for key in ['mu','DeltaTb19','Trox19','DeltaTb37','Trox37']]
                kl19,kl37,kv19,kv37=[a[key] for key in['kl19','kl37','kv19','kv37']]
                F19 = (t19hx - sstx )/(t19vx - sstx)
                F37 = (t37hx - sstx)/(t37vx - sstx)
                term19=r19v*(1. - F19)
                term37=r37v*(1. - F37)
                R1= -mu/2.*np.log(DeltaTb19/(sstx*term19*Trox19**2.))
                R2= -mu/2.*np.log(DeltaTb37/(sstx*term37*Trox37**2.))
                wl,wv=linear_solve(kl19,kv19,kl37,kv37,R1,R2)
                print('Wisconsin wl, wv: ',wl,wv)
                all_keys=list(a_ubc.keys())
                all_keys.sort()
                print('-'*15)
                for key in all_keys:
                    print(key,a_ubc[key],a[key])
                
                ## wv_val,wl_val=find_greenwald(*invars,data=data)
                ## #wv_val,wl_val=find_wv_wl(*invars,data=data)
                ## print('wv, wl ',wv_val,wl_val)
                ## invars.insert(0,wl_val)
                ## invars.insert(0,wl_val)
                ## solvepha()



    
        

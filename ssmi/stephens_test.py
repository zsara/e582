import h5py
import numpy as np
import pandas as pd
import glob,os
import numpy.ma as ma
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap


def wind_speed(sst,t19v,t22v,t37h,t37v):
    """
       input: sst (K), t19v (K), t22v (K), t37h (K)
       output: windspeed (m/s)
    """
    speed=1.0969*(t19v)-0.4555e0*(t22v)- 1.76*(t37v)+0.786*(t37h)+ 147.9
    return speed

def emiss(sst,windspeed,data):
    """
       input:  sst (K), windspeed (m/s), data instance
       return dict(19:(emissv, emissh),37:(emissv,emissh))
         which are the vertically and horizontally polarized emissivities
         at 19 GHz and 37 GHz
    """
    winds=data.micro_winds
    temps=data.micro_ssts
    wind_index=np.searchsorted(winds,windspeed)
    temp_index=np.searchsorted(temps,sst)
    freq_index=0 #19 GHz
    emissv=data.emissv[freq_index,wind_index,temp_index]
    emissh=data.emissh[freq_index,wind_index,temp_index]
    out={19:(emissh,emissv)}
    freq_index=2 #37 GHz
    emissv=data.emissv[freq_index,wind_index,temp_index]
    emissh=data.emissh[freq_index,wind_index,temp_index]
    out[37]=(emissh,emissv)
    return out

def absorb(sst,data):
    """
       input: sst, data instance
       output: dictionary with values for
       'kl19' (m^2/kg), 'kv19' (m^2/kg), 'tox37', 'kv37' (m^2/kg), 'kl37' (m^2/kg), 'tox19', 'sst' (K)
    """
    row=np.searchsorted(data.micro_ssts,sst)
    values=data.abs_coeffs.loc[row]
    out=dict(values)
    return out


def find_wv_wl(sst,mu,DeltaTb19,DeltaTb37,t19h,t19v,t22v,t37h,t37v,data=None):
    abs_dict=absorb(sst,data)
    args=[sst,t19v,t22v,t37h,t37v]
    windspeed=wind_speed(*args)
    emiss_dict=emiss(sst,windspeed,data)
    Trox=abs_dict['tox19']
    emissh19,emissv19=emiss_dict[19]
    Rv_Rh19=(1 - emissv19) - (1 - emissh19)
    R1= -mu/2.*np.log(DeltaTb19/(sst*(Rv_Rh19)*Trox**2.))
    kl19,kw19=(abs_dict['kl19'],abs_dict['kv19'])
    Trox=abs_dict['tox37']
    emissh37,emissv37=emiss_dict[37]
    Rv_Rh37=(1 - emissv37) - (1 - emissh37)
    kl37,kw37=(abs_dict['kl37'],abs_dict['kv37'])
    R2= -mu/2.*np.log(DeltaTb37/(sst*(Rv_Rh37)*Trox**2.))
    kl37,kw19=(abs_dict['kl37'],abs_dict['kv37'])
    delta=kw19*kl37 - kl19*kw37
    w=(R1*kl37 - R2*kl19)/delta
    l=(R2*kw19 - R1*kw37)/delta
    return (w,l)


def find_greenwald(sst,mu,DeltaTb19,DeltaTb37,t19h,t19v,t22v,t37h,t37v,data=None):
    abs_dict=absorb(sst,data)
    args=[sst,t19v,t22v,t37h,t37v]
    windspeed=wind_speed(*args)
    emiss_dict=emiss(sst,windspeed,data)
    Trox=abs_dict['tox19']
    emissh19,emissv19=emiss_dict[19]
    F19 = (t19h - sst )/(t19v - sst)
    F37 = (t37h + 3.58 - sst)/(t37v + 3.58 - sst)
    Rv_Rh19=(1 - emissv19) - (1 - emissh19)
    r19v=(1.0 - emissv19)
    term19=Rv_Rh19
    term19b=r19v*(1. - F19)
    print('term19: ',term19,term19b)
    R1= -mu/2.*np.log(DeltaTb19/(sst*term19b*Trox**2.))
    kl19,kw19=(abs_dict['kl19'],abs_dict['kv19'])
    Trox=abs_dict['tox37']
    emissh37,emissv37=emiss_dict[37]
    r37v=(1.0 - emissv37)
    Rv_Rh37=(1 - emissv37) - (1 - emissh37)
    term37=Rv_Rh37
    kl37,kw37=(abs_dict['kl37'],abs_dict['kv37'])
    term37b=r37v*(1. - F37)
    print('term37: ',term37,term37b)
    R2= -mu/2.*np.log(DeltaTb37/(sst*term37b*Trox**2.))
    kl37,kw19=(abs_dict['kl37'],abs_dict['kv37'])
    delta=kw19*kl37 - kl19*kw37
    w=(R1*kl37 - R2*kl19)/delta
    l=(R2*kw19 - R1*kw37)/delta
    return (w,l)

def test_left_right(w,l,sst,mu,DeltaTb19,DeltaTb37,t19h,t19v,t22v,t37h,t37v,data=None):
    abs_dict=absorb(sst,data)
    kl37,kw37=(abs_dict['kl37'],abs_dict['kv37'])
    kl19,kw19=(abs_dict['kl19'],abs_dict['kv19'])
    args=[sst,t19v,t22v,t37h,t37v]
    windspeed=wind_speed(*args)
    emiss_dict=emiss(sst,windspeed,data)
    emiss19h,emiss19v=emiss_dict[19]
    r19v=(1.0 - emiss19v)
    emiss37h,emiss37v=emiss_dict[37]
    r37v=(1.0 - emiss37v)
    Trox19=abs_dict['tox19']
    Trox37=abs_dict['tox37']
    F19 = (t19h - sst )/(t19v - sst)
    F37 = (t37h + 3.58 - sst)/(t37v + 3.58 - sst)
    term19b=r19v*(1. - F19)
    term37b=r37v*(1. - F37)
    t19h,t19v,t22v,t37h,t37v=(113.57, 183.24, 194.8, 148.13, 208.11)
    t37h=t37h + 3.58
    t37v=t37v + 3.58
    DeltaTb19=t19h - t19v
    DeltaTb37=t37h - t37v
    sst=271.75
    windspeed=10.32
    emiss19h,emiss19v,emiss37h,emiss37v = 0.3255,0.6255,0.3972,0.7102
    r19v=1 - emiss19v
    r19h=1 - emiss19h
    r37v=1 - emiss37v
    r37h=1 - emiss37h
    kl19,kl37,kv19,kv37 = .09826,0.32243,0.00270,0.00212
    Trox19,Trox37 = 0.978,0.927
    wv = 8.55276
    wl = 0.05486
    term19=r19v - r19h
    term37=r37v - r37h
    R1= -mu/2.*np.log(DeltaTb19/(sst*term19*Trox19**2.))
    R2= -mu/2.*np.log(DeltaTb37/(sst*term37*Trox37**2.))
    L1=kw19*wv + kl19*wl
    L2=kw37*wv + kl37*wl
    print('matching pairs: ',L1,R1,L2,R2)
    wl,wv=linear_solve(kl19,kw19,kl37,kw37,R1,R2)
    print('new wl, wv: ',wl,wv)
    L1=kw19*wv + kl19*wl
    L2=kw37*wv + kl37*wl
    print('new matching pairs: ',L1,R1,L2,R2)
    delta=kw19*kl37 - kl19*kw37
    w=(R1*kl37 - R2*kl19)/delta
    l=(R2*kw19 - R1*kw37)/delta
    print('analytic pairs: ',w,l)
    F19 = (t19h - sst )/(t19v - sst)
    F37 = (t37h - sst)/(t37v - sst)
    term19=r19v*(1. - F19)
    term37=r37v*(1. - F37)
    R1= -mu/2.*np.log(DeltaTb19/(sst*term19*Trox19**2.))
    R2= -mu/2.*np.log(DeltaTb37/(sst*term37*Trox37**2.))
    wl,wv=linear_solve(kl19,kw19,kl37,kw37,R1,R2)
    print('another wl, wv: ',wl,wv)
    

def linear_solve(kl19,kw19,kl37,kw37,R1,R2):
    A=[[kl19,kw19],[kl37,kw37]]
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
    t37h=the_temps['july']['t37h'][...]
    t37v=the_temps['july']['t37v'][...]
    nrows,ncols=sst.shape
    mu=np.cos(53.1*np.pi/180.)
    for row in range(nrows):
        for col in range(ncols):
            if np.abs(sst[row,col] - 271.35) < 0.01 and \
                np.abs(t19h[row,col] - 113.57) < 0.01:
                print('found the test pixel: ')
                print(row,col,the_temps['lat'][row,col],the_temps['lon'][row,col],
                      sst[row,col],t19h[row,col],t19v[row,col],t22v[row,col],
                      t37h[row,col],t37v[row,col])
                args=[sst[row,col],t19v[row,col],t22v[row,col],
                      t37h[row,col],t37v[row,col]]
                print('wind speed: ',wind_speed(*args))
                print('emissivities: ',emiss(sst[row,col],wind_speed(*args),data))
                absorb_dict=absorb(sst[row,col],data)
                for key in ['kl19','kl37','kv19','kv37','tox19','tox37']:
                    print('{} -- {:8.4f}'.format(key,absorb_dict[key]))
                the_month='july'
                sstx=the_temps[the_month]['sst'][row,col]
                t19hx=the_temps[the_month]['t19h'][row,col]
                t19vx=the_temps[the_month]['t19v'][row,col]
                t22vx=the_temps[the_month]['t22v'][row,col]
                t37hx=the_temps[the_month]['t37h'][row,col]
                t37vx=the_temps[the_month]['t37v'][row,col]
                DeltaTb19 = t19hx - t19vx
                DeltaTb37 = t37hx - t37vx
                invars=[sstx,mu,DeltaTb19,DeltaTb37,t19hx,t19vx,t22vx,t37hx,t37vx]
                wv_val,wl_val=find_greenwald(*invars,data=data)
                #wv_val,wl_val=find_wv_wl(*invars,data=data)
                print('wv, wl ',wv_val,wl_val)
                invars.insert(0,wl_val)
                invars.insert(0,wl_val)
                test_left_right(*invars,data=data)



    
        

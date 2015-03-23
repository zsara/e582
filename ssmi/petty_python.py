import numpy as np

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

def wind_speed(sst,t19v,t22v,t37h,t37v):
    """
       input: sst (K), t19v (K), t22v (K), t37h (K)
       output: windspeed (m/s)
    """
    speed=1.0969*(t19v)-0.4555e0*(t22v)- 1.76*(t37v)+0.786*(t37h)+ 147.9
    return speed


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

def emiss_fortran(sst,windspeed,data):
    """
       input:  sst (K), windspeed (m/s), data instance
       return dict(19:(emissv, emissh),37:(emissv,emissh))
         which are the vertically and horizontally polarized emissivities
         at 19 GHz and 37 GHz
    """
    #19 GHz  = 1
    freq=1
    theta=53.1
    h,v=petty.emiss(freq,windspeed,sst,theta)
    out={19:(h,v)}
    freq=3
    h,v=petty.emiss(freq,windspeed,sst,theta)
    out[37]=(h,v)
    return out


def absorb_fortran(sst,data):
    """
       input: sst, data instance
       output: dictionary with values for
       'kl19' (m^2/kg), 'kv19' (m^2/kg), 'tox37', 'kv37' (m^2/kg), 'kl37' (m^2/kg), 'tox19', 'sst' (K)
    """
    names=['sst','kl19','kl37','kv19','kv37','tox19','tox37']
    values=petty.coef(sst)
    out=dict(zip(names,values))
    return out

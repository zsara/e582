from gasabsr98 import gasabsr98
import numpy as np
from matplotlib import pyplot as plt
import hydrostat
reload(hydrostat)
from hydrostat import hydrostat 


freq=[50.3000,52.8000,53.7110,54.4000,
      54.9400,55.5000,57.2900,57.5070]

#buid the atmosphere and plot it
T_surf=280.
P_surf=102.e3
lapse= -7.e-3
delta_z=10.
num_levels=1000
temp,press,rho,height=hydrostat(T_surf,P_surf,lapse,delta_z,num_levels)

keep_down={}
keep_down_vapor={}
top_down_z=height[::-1]
top_down_tk=temp[::-1]
top_down_p=press[::-1]
top_down_rho=rho[::-1]
top_down_rhowv=10.e-3*np.exp(-top_down_z/3000.)

    
plt.close('all')

tk=260.
pa=80.e3
rhowv=10.e-3
freqs=np.linspace(1,90.,100)
airlist=[]
wvlist=[]
for f in freqs:
    air,wv=gasabsr98(f,tk,rhowv,pa)
    airlist.append(air)
    wvlist.append(wv)

fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
out = ax.plot(freqs, airlist, 'b-')
ax.set_title('air abs coeff vs. freq')

fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
out = ax.plot(freqs, wvlist, 'b-')
ax.set_title('vapor abs coeff vs. freq')

fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
out = ax.plot(rho, height, 'b+')
ax.set_title('air vs. height')

fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
out = ax.plot(top_down_rhowv, top_down_z, 'b+')
ax.set_title('vapor density vs. height')

#now plot the five weighting functions -- first from the top down


for f in freq:
    print('calculating f={}'.format(f))
    absair=list()
    abswv=list()
    deltau=list()
    for row,height in enumerate(top_down_z):
        tk=top_down_tk[row]
        pa=top_down_p[row]
        rho=top_down_rho[row]
        rhowv=top_down_rhowv[row]
        absair_val,abswv_val=gasabsr98(f,tk,rhowv,pa)
        absair.append(absair_val*rho)
        abswv.append(abswv_val*rhowv)
        deltau.append(absair_val*rho*delta_z)
    keep_down[f]=(np.array(absair),np.array(abswv),np.array(deltau))
        
freqs=keep_down.keys()
freqs.sort()
    
fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    out = ax.plot(keep_down[freq][0],top_down_z,label='{} GHz'.format(freq))
ax.set_title('volume abs coeff for air')
ax.legend()

fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    out = ax.plot(keep_down[freq][1],top_down_z,label='{} GHz'.format(freq))
ax.set_title('volume abs coeff for h2o')
ax.legend()


fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    tau=np.cumsum(keep_down[freq][2])
    trans=np.exp(-tau)
    out = ax.plot(trans,top_down_z,label='{} GHz'.format(freq))
ax.set_title('transmission for air')
ax.legend()


fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    tau=np.cumsum(keep_down[freq][2])
    trans=np.exp(-tau)
    out = ax.plot(-np.diff(trans)/delta_z,top_down_z[1:],label='{} GHz'.format(freq))
ax.set_xlim([0,2.e-4])    
ax.set_title('upward radiation weighting functions for air')
ax.legend(loc='best')




             
    
    
plt.show()

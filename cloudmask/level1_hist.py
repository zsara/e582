from __future__ import division,print_function
import glob
import h5py
from hist2d import hist2d, numba_hist2d
import numpy as np
import numpy.ma as ma
import numba
import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import cm
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt

from timeit import timeit


plotdir='{}/{}'.format(os.getcwd(),'plots')
if not os.path.exists(plotdir):
    os.makedirs(plotdir)

l1b_file,=glob.glob('../datasets/MYD021*h5')

with h5py.File(l1b_file) as l1b_file:
    #channel31 is emissive channel 10
    index31=10
    chan31=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'][index31,:,:]
    scale=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_scales'][index31]
    offset=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_offsets'][index31]
    chan31=(chan31 - offset)*scale
    index1=0  #channel 1 is first 250 meter reflective channel
    reflective=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'][0,:,:]
    scale=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_scales']
    offset=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_offsets']
    chan1=(reflective - offset[0])*scale[0]

chan1_min,chan31_min=np.amin(chan1),np.amin(chan31)
chan1_max,chan31_max=np.amax(chan1),np.amax(chan31)

chan1_edges=np.linspace(0,1,30)
chan31_edges=np.linspace(0,10,40)

for i in range(3):
    print('\npython iteration #{}'.format(i))
    with timeit('call hist2d -- plain python'):
        hist_array,chan1_centers,chan31_centers=hist2d(chan1,chan31,chan1_edges,chan31_edges)

for i in range(3):
    print('\nnumba iteration #{}'.format(i))
    with timeit('call hist2d -- numba'):
        hist_array,chan1_centers,chan31_centers=numba_hist2d(chan1,chan31,chan1_edges,chan31_edges)

hist_array=ma.array(hist_array,mask=np.isnan(hist_array))

cmap=cm.RdBu_r
cmap.set_over('y')
cmap.set_under('w')
cmap.set_bad('0.75') #75% grey
vmin= 0.
vmax= 10000.
the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

fig=plt.figure(2)
fig.clf()
ax=fig.add_subplot(111)
im=ax.pcolormesh(chan1_centers,chan31_centers,hist_array,cmap=cmap,norm=the_norm)
cb=fig.colorbar(im,extend='both')
ax.set_title('2d histogram B')
fig.canvas.draw()
geom_file,=glob.glob('../datasets/MYD03*h5')
figpath='{}/{}'.format(plotdir,'histogram1.png')
fig.savefig(figpath)

vmin= 0.
vmax= 5.
the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
log_hist_array=np.log10(hist_array)

fig=plt.figure(3)
fig.clf()
ax=fig.add_subplot(111)
im=ax.pcolormesh(chan1_centers,chan31_centers,log_hist_array,cmap=cmap,norm=the_norm)
cb=fig.colorbar(im,extend='both')
ax.set_title('2d histogram C')
fig.canvas.draw()
figpath='{}/{}'.format(plotdir,'histogram2.png')
fig.savefig(figpath)


#plt.show()

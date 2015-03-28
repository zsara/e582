#!/usr/bin/env python
"""
  read the level1b file
  and produce a 2d histogram of channel1 vs. channel31

  usage:

  ./level1_ocean.py level1bfile maskfile
"""

from __future__ import division,print_function
import glob
import h5py
from hist_numba import numba_hist2d
import numpy as np
import numpy.ma as ma
import numba
import os
import site
site.addsitedir('../utilities')
from planck import planckInvert

import matplotlib
matplotlib.use('Agg')
from matplotlib import cm
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import argparse
import textwrap


if __name__ == "__main__":

    linebreaks=argparse.RawTextHelpFormatter
    descrip=textwrap.dedent(globals()['__doc__'])
    parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
    parser.add_argument('l1bfile',type=str,help='MYD21KM radiance file')
    parser.add_argument('maskfile',type=str,help='h5 cloudmask file')
    args=parser.parse_args()

    plotdir='{}/{}'.format(os.getcwd(),'plots')
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)

    l1b_file,=glob.glob(args.l1bfile)

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


    c31_bright=planckInvert(11.03,chan31)
    
    mask_file,=glob.glob(args.maskfile)
    with h5py.File(mask_file) as mask_h5:
        land_mask=mask_h5['landmask'][...]

    water_hit=land_mask==0    

    chan1=chan1[water_hit]
    chan31=chan31[water_hit]
    c31_bright=c31_bright[water_hit]

    chan1_min,chan31_min=np.amin(chan1),np.amin(chan31)
    chan1_max,chan31_max=np.amax(chan1),np.amax(chan31)

    chan1_edges=np.linspace(0,1,30)
    chan31_edges=np.linspace(0,10,40)

    hist_array,chan1_centers,chan31_centers=numba_hist2d(chan1,chan31,chan1_edges,chan31_edges)
    hist_array=ma.array(hist_array,mask=np.isnan(hist_array))
    

    bright31_edges=np.linspace(200,305,40)
    bright31_array,chan1_centers,bright31_centers=numba_hist2d(chan1,c31_bright,
                                                           chan1_edges,bright31_edges)
    bright31_array=ma.array(bright31_array,mask=np.isnan(bright31_array))
    
    cmap=cm.YlGn  #see http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
    cmap.set_over('r')
    cmap.set_under('b')
    cmap.set_bad('0.75') #75% grey
    vmin= 0.
    vmax= 10000.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

    plt.close('all')
    fig,ax=plt.subplots(figsize=(12,12))
    im=ax.pcolormesh(chan1_centers,chan31_centers,hist_array,cmap=cmap,norm=the_norm)
    cb=fig.colorbar(im,extend='both')
    ax.set_title('raw counts for channel 1 vs. channel 31')
    fig.canvas.draw()
    figpath='{}/{}'.format(plotdir,'histogram.png')
    fig.savefig(figpath)

    vmin= 0.
    vmax= 5.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    log_hist_array=np.log10(hist_array)

    fig,ax=plt.subplots(figsize=(12,12))
    im=ax.pcolormesh(chan1_centers,chan31_centers,log_hist_array,cmap=cmap,norm=the_norm)
    cb=fig.colorbar(im,extend='both')
    ax.set_title('log10 counts for chan1 vs. chan31')
    ax.set_xlabel('channel 1 reflectvity')
    ax.set_ylabel('channel 31 radiance (W/m^2/micron/sr)')
    fig.canvas.draw()
    figpath='{}/{}'.format(plotdir,'histogram_log10.png')
    fig.savefig(figpath)

    log_bright=np.log10(bright31_array)
    log_hist_array=np.log10(hist_array)
    fig,ax=plt.subplots(figsize=(12,12))
    im=ax.pcolormesh(chan1_centers,bright31_centers,log_bright,cmap=cmap,norm=the_norm)
    cb=fig.colorbar(im,extend='both')
    ax.set_title('log10 counts for Channel 31 brightness')
    ax.set_xlabel('channel 1 reflectvity')
    ax.set_ylabel('channel 31 brightness temperature (K)')
    ax.set_ylim([200,305])
    fig.canvas.draw()
    figpath='{}/{}'.format(plotdir,'c31_bright.png')
    fig.savefig(figpath)


#plt.show()

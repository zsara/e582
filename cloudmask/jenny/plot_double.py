#!/usr/bin/env python
"""
  read the level1b file and the cloud mask file from dump_cloudmask.py and
  produce plots of the chan31 radiance, channel 1 reflectance,
  cloud mask and landmask

  usage:

  ./plot_double.py names.json

"""
from __future__ import division
import argparse
import h5py
import glob
from matplotlib import pyplot as plt
import site
site.addsitedir('../../utilities')
from reproject import reproj_numba
import planck
import io,json
from collections import OrderedDict as od
import os,errno

#
# compat module redefines importlib.reload if we're
# running python3
#
from compat import cpreload as reload
reload(planck)
from planck import planckInvert
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import Normalize
from matplotlib import cm
import numpy as np
import textwrap

def make_plot(lcc_values):
    """
      set up the basic map projection details with coastlines and meridians
      return the projection object for further plotting
    """
    proj = Basemap(**lcc_values)
    parallels = np.arange(-90, 90, 1)
    meridians = np.arange(0, 360, 2)
    proj.drawparallels(parallels, labels=[1, 0, 0, 0],
                       fontsize=10, latmax=90)
    proj.drawmeridians(meridians, labels=[0, 0, 0, 1],
                       fontsize=10, latmax=90)
    # draw coast & fill continents
    # map.fillcontinents(color=[0.25, 0.25, 0.25], lake_color=None) # coral
    proj.drawcoastlines(linewidth=2.5, linestyle='solid', color='k')
    return proj


def find_corners(lons, lats):
    """
      guess values for the upper right and lower left corners of the
      lat/lon grid and the grid center based on max/min lat lon in the
      data and return a dictionary that can be passed to Basemap to set
      the lcc projection.  Also return the theest lat and lon differences
      to get a feeling for the image resolution
    """
    min_lat, min_lon = np.min(lats), np.min(lons)
    max_lat, max_lon = np.max(lats), np.max(lons)
    llcrnrlon, llcrnrlat = min_lon, min_lat
    urcrnrlon, urcrnrlat = max_lon, max_lat
    lon_res=np.min(np.abs(np.diff(lons.flat)))
    lat_res=np.min(np.abs(np.diff(lats.flat)))
    out=dict(llcrnrlon=llcrnrlon,llcrnrlat=llcrnrlat,
             urcrnrlon=urcrnrlon,urcrnrlat=urcrnrlat,
             lat_1=llcrnrlat,lat_2=urcrnrlat,lat_0=(llcrnrlat+urcrnrlat)/2.,
             lon_0=(llcrnrlon + urcrnrlon)/2.)
    return(out,lon_res,lat_res)


if __name__ == "__main__":
    #
    # the following two lines help format the docstring at the top of the file
    # into a help text
    #
    linebreaks=argparse.RawTextHelpFormatter
    descrip=textwrap.dedent(globals()['__doc__'])
    parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
    parser.add_argument('initfile',type=str,help='name of json file with filenames')
    args=parser.parse_args()

    with io.open(args.initfile,'r',encoding='utf8') as f:
        name_dict=json.loads(f.read(),object_pairs_hook=od)

    keys=['l1b_fileA','l1b_fileB','geom_fileA','geom_fileB',
          'mask_fileA','mask_fileB']
        
    l1b_fileA,l1b_fileB,geom_fileA,geom_fileB,\
        mask_fileA,mask_fileB=[name_dict[key] for key in keys]

    plot_dir='plots'
    try:
        os.makedirs(plot_dir)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass  #not a problem if file exists

        
    with h5py.File(l1b_fileA) as l1bA_file,h5py.File(l1b_fileB) as l1bB_file:
        #channel31 is emissive channel 10
        index31=10
        chan31A=l1bA_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'][index31,:,:]
        scale=l1bA_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_scales'][index31]
        offset=l1bA_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_offsets'][index31]
        chan31A=(chan31A - offset)*scale
        index1=0  #channel 1 is first 250 meter reflective channel
        reflective=l1bA_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'][0,:,:]
        scale=l1bA_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_scales']
        offset=l1bA_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_offsets']
        chan1A=(reflective - offset[0])*scale[0]
        chan1A=chan1A.ravel()

        chan31B=l1bB_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'][index31,:,:]
        scale=l1bB_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_scales'][index31]
        offset=l1bB_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_offsets'][index31]
        chan31B=(chan31B - offset)*scale
        index1=0  #channel 1 is first 250 meter reflective channel
        reflective=l1bB_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'][0,:,:]
        scale=l1bB_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_scales']
        offset=l1bB_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_offsets']
        chan1B=(reflective - offset[0])*scale[0]
    chan1=np.concatenate([chan1A.ravel(),chan1B.ravel()])
    chan31=np.concatenate([chan31A.ravel(),chan31B.ravel()])

    with h5py.File(geom_fileA) as geomA_file,h5py.File(geom_fileB) as geomB_file:
        the_lonA=geomA_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Longitude'][...]
        the_latA=geomA_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Latitude'][...]
        the_lonB=geomB_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Longitude'][...]
        the_latB=geomB_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Latitude'][...]
    the_lons=np.concatenate([the_lonA.ravel(),the_lonB.ravel()])
    the_lats=np.concatenate([the_latA.ravel(),the_latB.ravel()])
    hit=np.logical_and(the_lats > 47.5,the_lats < 51.5)
    the_lons=the_lons[hit]
    the_lats=the_lats[hit]
    chan1=chan1[hit]
    chan31=chan31[hit]
    
    lim= None
    the_slice=slice(0,lim)
    with h5py.File(mask_fileA) as cm_h5A,h5py.File(mask_fileB) as cm_h5B:
         maskoutA=cm_h5A['cloudmask'][the_slice,:]
         landoutA=cm_h5A['landmask'][the_slice,:]
         maskoutB=cm_h5B['cloudmask'][the_slice,:]
         landoutB=cm_h5B['landmask'][the_slice,:]
    landout=np.concatenate([landoutA.ravel(),landoutB.ravel()])
    maskout=np.concatenate([maskoutA.ravel(),maskoutB.ravel()])
    landout=landout[hit]
    maskout=maskout[hit]
    
    c31_bright=planckInvert(11.03,chan31)
    

    lcc_values,lon_res,lat_res=find_corners(the_lons,the_lats)
    lcc_values['fix_aspect']=True
    lcc_values['lat_0']=49.5
    lcc_values['lat_1']=47.5
    lcc_values['lat_2']=51
    lcc_values['llcrnrlat']=48.
    lcc_values['urcrnrlat']=50.5
    lcc_values['llcrnrlon']= -126.5
    lcc_values['urcrnrlon']= -121.5
    ## lcc_values['width']=500.e3
    ## lcc_values['height']=200.e3
    lcc_values['resolution']='h'
    lcc_values['projection']='lcc'

    #
    #pixels with map projection
    #

    plt.close('all')

    missing_val=-999.
    latlim=[lcc_values['llcrnrlat'],lcc_values['urcrnrlat']]
    lonlim=[lcc_values['llcrnrlon'],lcc_values['urcrnrlon']]
    res=0.03
    chan31_grid, longrid, latgrid, bin_count = reproj_numba(chan31,missing_val, the_lons, the_lats, lonlim, latlim, res)
    chan1_grid, longrid, latgrid, bin_count = reproj_numba(chan1,missing_val, the_lons, the_lats, lonlim, latlim, res)
    mask_grid, longrid, latgrid, bin_count = reproj_numba(maskout,missing_val, the_lons, the_lats, lonlim, latlim, res)
    land_grid, longrid, latgrid, bin_count = reproj_numba(landout,missing_val, the_lons, the_lats, lonlim, latlim, res)
    land_grid, longrid, latgrid, bin_count = reproj_numba(landout,missing_val, the_lons, the_lats, lonlim, latlim, res)
    c31bright_grid, longrid, latgrid, bin_count = reproj_numba(c31_bright,missing_val, the_lons, the_lats, lonlim, latlim, res)

    cmapA=cm.YlGn  #see http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
    cmapA.set_over('r')
    cmapA.set_under('0.5')
    cmapA.set_bad('0.75') #75% grey

    cmapB=cm.YlGn_r 
    cmapB.set_over('r')
    cmapB.set_under('b')
    cmapB.set_bad('0.75') #75% grey

    vmin= 0.
    vmax= 10.

    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    fig,ax=plt.subplots(1,1,figsize=(12,12))
    #
    # tell Basemap what axis to plot into
    #
    lcc_values['ax']=ax
    proj=make_plot(lcc_values)
    x,y=proj(longrid,latgrid)
    CS=proj.ax.pcolormesh(x,y,chan31_grid,cmap=cmapB,norm=the_norm)
    CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
    CBar.set_label('Channel 31 radiance (W/m^2/micron/sr')
    proj.ax.set_title('A2014126 Channel 31 radiance')
    proj.ax.figure.canvas.draw()
    fig.savefig('{}/chan31.png'.format(plot_dir))

    fig,ax=plt.subplots(1,1,figsize=(12,12))
    #
    # tell Basemap what axis to plot into
    #
    vmin= 0.
    vmax= 1.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    lcc_values['ax']=ax
    proj=make_plot(lcc_values)
    CS=proj.ax.pcolormesh(x,y,chan1_grid,cmap=cmapA,norm=the_norm)
    CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
    CBar.set_label('Channel 1 reflectance')
    proj.ax.set_title('A2014126 Channel 1 reflectance')
    proj.ax.figure.canvas.draw()
    fig.savefig('{}/chan1.png'.format(plot_dir))

    fig,ax=plt.subplots(1,1,figsize=(12,12))
    #
    # tell Basemap what axis to plot into
    #
    vmin= 0.
    vmax= 3.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    lcc_values['ax']=ax
    proj=make_plot(lcc_values)
    CS=proj.ax.pcolormesh(x,y,mask_grid,cmap=cmapA,norm=the_norm)
    CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
    CBar.set_label('A2014126 cloud mask')
    proj.ax.set_title('cloud mask')
    proj.ax.figure.canvas.draw()
    fig.savefig('{}/cloudmask.png'.format(plot_dir))
    fig,ax=plt.subplots(1,1,figsize=(12,12))
    #
    # tell Basemap what axis to plot into
    #
    vmin= 0.
    vmax= 3.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    lcc_values['ax']=ax
    proj=make_plot(lcc_values)
    CS=proj.ax.pcolormesh(x,y,land_grid,cmap=cmapB,norm=the_norm)
    CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
    CBar.set_label('land mask')
    proj.ax.set_title('A2014126 land mask')
    proj.ax.figure.canvas.draw()
    fig.savefig('{}/landmask.png'.format(plot_dir))



    fig,ax=plt.subplots(1,1,figsize=(12,12))
    #
    # tell Basemap what axis to plot into
    #
    vmin= 275.
    vmax= 290.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
    lcc_values['ax']=ax
    proj=make_plot(lcc_values)
    CS=proj.ax.pcolormesh(x,y,c31bright_grid,cmap=cmapB,norm=the_norm)
    CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
    CBar.set_label('11 micron brightness temp (K)')
    proj.ax.set_title('A2014126 11 micron brightness temp')
    proj.ax.figure.canvas.draw()
    fig.savefig('{}/c31_bright.png'.format(plot_dir))
    plt.show()

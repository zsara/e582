import h5py
import glob
from matplotlib import pyplot as plt
import site
site.addsitedir('../../src')
from reproject import reproj_L1B
from matplotlib.colors import Normalize
from matplotlib import cm
import numpy as np
from mpl_toolkits.basemap import Basemap


def make_plot(lcc_values):
    """
      set up the basic map projection details with coastlines and meridians
      return the projection object for further plotting
    """
    proj = Basemap(**lcc_values)
    parallels = np.arange(-90, 90, 5)
    meridians = np.arange(0, 360, 5)
    proj.drawparallels(parallels, labels=[1, 0, 0, 0],
                       fontsize=10, latmax=90)
    proj.drawmeridians(meridians, labels=[0, 0, 0, 1],
                       fontsize=10, latmax=90)
    # draw coast & fill continents
    # map.fillcontinents(color=[0.25, 0.25, 0.25], lake_color=None) # coral
    proj.drawcoastlines(linewidth=1.5, linestyle='solid', color='k')
    return proj


def find_corners(lons, lats):
    """
      guess values for the upper right and lower left corners of the
      lat/lon grid and the grid center based on max/min lat lon in the
      data and return a dictionary that can be passed to Basemap to set
      the lcc projection.  Also return the smallest lat and lon differences
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


l1b_file,=glob.glob('../../dataset/MYD021*h5')
l1b_file=h5py.File(l1b_file)
geom_file,=glob.glob('../../dataset/MYD03*h5')
geom_file=h5py.File(geom_file)
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
the_lon=geom_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Longitude'][...]
the_lat=geom_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Latitude'][...]

lim= 500
the_slice=slice(0,lim)
small_lons=the_lon[the_slice]
small_lats=the_lat[the_slice]
chan31_small=chan31[the_slice]
chan1_small=chan1[the_slice]


lcc_values,lon_res,lat_res=find_corners(small_lons,small_lats)
lcc_values['resolution']='l'
lcc_values['projection']='lcc'

#
#pixels with map projection
#

plt.close('all')

missing_val=-999.
latlim=[lcc_values['llcrnrlat'],lcc_values['urcrnrlat']]
lonlim=[lcc_values['llcrnrlon'],lcc_values['urcrnrlon']]
res=0.05
chan31_grid, longrid, latgrid, bin_count = reproj_L1B(chan31_small,missing_val, small_lons, small_lats, lonlim, latlim, res)
chan1_grid, longrid, latgrid, bin_count = reproj_L1B(chan1_small,missing_val, small_lons, small_lats, lonlim, latlim, res)

cmap=cm.YlGn  #see http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
cmap.set_over('r')
cmap.set_under('0.5')
cmap.set_bad('0.75') #75% grey
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
CS=proj.ax.pcolormesh(x,y,chan31_grid,cmap=cmap,norm=the_norm)
CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
CBar.set_label('Channel 31 radiance (W/m^2/micron/sr')
proj.ax.set_title('Channel 31 radiance')
proj.ax.figure.canvas.draw()


fig,ax=plt.subplots(1,1,figsize=(12,12))
#
# tell Basemap what axis to plot into
#
vmin= 0.
vmax= 1.
the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
lcc_values['ax']=ax
proj=make_plot(lcc_values)
CS=proj.ax.pcolormesh(x,y,chan1_grid,cmap=cmap,norm=the_norm)
CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
CBar.set_label('Channel 1 reflectance')
proj.ax.set_title('Channel 1 reflectance')
proj.ax.figure.canvas.draw()


plt.show()

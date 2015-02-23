"""


"""

import numpy as np
import numpy.ma as ma
import h5py
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap

nsstlon=180
nsstlat=91
nlon=360
nlat=180


names=dict(july=('sst.jul90','btemps.jul90'),
           jan=('sst.jan90','btemps.jan90'))

bigdict={}
for season in ['jan','july']:
    sstfile,btempsfile=names[season]
    sst=np.empty([nsstlon,nsstlat],dtype='float32')
    with open(sstfile,'r') as f:
        for jlat in range(nsstlat):
            for jlon in range(nsstlon):
              line=f.readline()
              sstval=float(line)
              sst[jlon,jlat]=sstval + 273.15

    arrays={}
    varnames=['t19h','t19v','t22v','t37h','t37v','sst']
    for name in varnames:
        arrays[name]=np.empty([nlon,nlat],dtype='float32')

    import re
    spaces=re.compile(r'\s+')

    with open(btempsfile,'r') as f:
        for ilat in range(nlat):
            for ilon in range(nlon):
                line=f.readline()
                vals=spaces.split(line.strip())
                for count,channel in enumerate(varnames[:5]):
                    arrays[channel][ilon,ilat]=float(vals[count])
                jlat=int(ilat/2.)
                jlon=int(ilon/2.)
                if jlon > nlon:
                    jlon=0
                if arrays['t19h'][ilon,ilat] > 500.:
                   arrays['sst'][ilon,ilat]=999.
                else:
                   arrays['sst'][ilon,ilat]=sst[jlon,jlat]
#
# flip arrays so that dimensions become [nlat,nlon]
#
    for key,value in arrays.items():
        arrays[key]=np.rot90(value)
    bigdict[season]=arrays

lats=np.arange(90,-90.,-1.)
lons=np.arange(0,360.)
lons,lats=np.meshgrid(lons,lats)
bigdict['lon']=lons
bigdict['lat']=lats

season='jan'
#season='july'
arrays=bigdict[season]

## plt.close('all')
## fig=plt.figure(figsize=[12,12])
## ax1=fig.add_subplot(111)
sst=arrays['sst']
hit=np.logical_or(sst < 273.,sst > 350.)
sst=ma.masked_where(hit,sst)

fig=plt.figure(figsize=[12,12])
ax1=fig.add_subplot(111)
# llcrnrlat,llcrnrlon,urcrnrlat,urcrnrlon
# are the lat/lon values of the lower left and upper right corners
# of the map.
# resolution = 'c' means use crude resolution coastlines.
m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c',ax=ax1)
m.drawcoastlines()
x,y=m(bigdict['lon'],bigdict['lat'])
# draw parallels and meridians.
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
vals=m.pcolormesh(x,y,sst)
fig.colorbar(vals)
plt.title("SST (K) for {}".format(season))

t19v=bigdict[season]['t19v']
t19v=ma.masked_where(hit,t19v)
fig=plt.figure(figsize=[12,12])
ax1=fig.add_subplot(111)
m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,\
            llcrnrlon=0,urcrnrlon=360,resolution='c',ax=ax1)
m.drawcoastlines()
#reuse x,y from last plot
# draw parallels and meridians.
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
vals=m.pcolormesh(x,y,t19v)
fig.colorbar(vals)
plt.title("T19V (K) for {}".format(season))
plt.show()

output_name='bright_temps.h5'
with h5py.File(output_name, "w") as f:
    comments=dict(lat='degrees lat (between -90 and 90)',
                  lon='degrees lon (betwen 0 and 360)')
    for var in ['lat','lon']:
        dset = f.create_dataset(var,bigdict[var].shape, dtype=bigdict[var].dtype)
        dset[...]=bigdict[var][...]                         
        dset.attrs['comment']=comments[var]
    #
    # write the 6 temperature arrays in two groups, one for each season
    #
    for season in ['july','jan']:
        group=f.create_group(season)
        for var in varnames:
            dset = group.create_dataset(var,bigdict[season][var].shape, dtype=bigdict[season][var].dtype)
            dset[...]=bigdict[season][var][...]                         

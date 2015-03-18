import glob
import h5py
#from hist2d import hist2d
import numpy as np
import numpy.ma as ma
import numba

import matplotlib
matplotlib.use('Agg')
from matplotlib import cm
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt

import contextlib,time
@contextlib.contextmanager
def timeit():
    t=time.time()
    yield
    print(time.time()-t,"sec")

# nopython=True means an error will be raised
# if fast compilation is not possible.


def hist2d(x_raw,y_raw,x_edges,y_edges):
    x_centers=(x_edges[:-1] + x_edges[1:])/2.
    y_centers=(y_edges[:-1] + y_edges[1:])/2.
    num_xbins=len(x_centers)
    num_ybins=len(y_centers)
    x_indices=np.searchsorted(x_edges, x_raw.flat, 'right')
    y_indices=np.searchsorted(y_edges, y_raw.flat, 'right')
    print('python inner loop')
    with timeit():
        hist_array=np.zeros([len(y_centers), len(x_centers)], dtype=np.float)
        for n in range(len(y_indices)): #y_indices and x_indices both size of raw data
            if x_indices[n] > 0 and y_indices[n] > 0 and \
                x_indices[n] <= num_xbins and y_indices[n] <= num_ybins:
                bin_row=y_indices[n]-1 # '-1' to get the index of the bin center
                bin_col=x_indices[n]-1
                hist_array[bin_row, bin_col] += 1
        rows,cols=hist_array.shape
        for row in range(rows):
            for col in range(cols):
                if hist_array[row,col] < 1.:
                    hist_array[row,col]=np.nan
    return hist_array,x_centers,y_centers


@numba.jit(nopython=True)
def fill_counts(y_centers,x_centers,y_indices,x_indices,hist_array):
    num_xbins=x_centers.shape[0]
    num_ybins=y_centers.shape[0]
    num_y=y_indices.shape[0]
    num_x=x_indices.shape[0]
    for n in range(num_y): #y_indices and x_indices both size of raw data
        if x_indices[n] > 0 and y_indices[n] > 0 and \
            x_indices[n] <= num_xbins and y_indices[n] <= num_ybins:
            bin_row=y_indices[n]-1 # '-1' to get the index of the bin center
            bin_col=x_indices[n]-1
            hist_array[bin_row, bin_col] += 1
    rows,cols=hist_array.shape
    for row in range(rows):
        for col in range(cols):
            if hist_array[row,col] < 1.:
                hist_array[row,col]=np.nan
    return hist_array

            
def numba_hist2d(x_raw,y_raw,x_edges,y_edges):
    x_centers=(x_edges[:-1] + x_edges[1:])/2.
    y_centers=(y_edges[:-1] + y_edges[1:])/2.
    num_xbins=int(len(x_centers))
    num_ybins=int(len(y_centers))
    x_indices=np.asarray(np.searchsorted(x_edges, x_raw.flat, 'right'),dtype=np.int64)
    y_indices=np.asarray(np.searchsorted(y_edges, y_raw.flat, 'right'),dtype=np.int64)
    hist_array=np.zeros([num_ybins, num_xbins], dtype=np.float)
    print('numba inner loop')
    with timeit():
        hist_array=fill_counts(y_centers,x_centers,y_indices,x_indices,hist_array)
        #print(fill_counts.inspect_types())
    return hist_array,x_centers,y_centers


    
l1b_file,=glob.glob('../datasets/MYD021*h5')
geom_file,=glob.glob('../datasets/MYD03*h5')
with h5py.File(geom_file) as geom_file,h5py.File(l1b_file) as l1b_file:
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

print('types found: ',fill_counts.inspect_types())

print('plain python')
for i in range(3):
    with timeit():
        hist_array,chan1_centers,chan31_centers=hist2d(chan1,chan31,chan1_edges,chan31_edges)

print('now numba')
for i in range(3):
    with timeit():
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
fig.savefig('histogram2.png')

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
fig.savefig('histogram3.png')


#plt.show()

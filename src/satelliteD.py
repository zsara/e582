
# coding: utf-8

# ##Satellite exercise for Wed. Jan. 14 cont.

# In[1]:

from __future__ import print_function
import glob  #this module gets file names using wildcards
#
# the h5dump.py file is one folder up in the utilities folder
# use site.addsitedir to add this folder to the list of folders
# python searches for imports
#
import site
site.addsitedir('../utilities')
from h5dump import dumph5
import h5py
import matplotlib.pyplot as plt
import numpy as np
import tile_calc



# In[2]:

#get_ipython().magic(u'matplotlib inline')


# 1.  Look at the product definitions for level 2 and level 3 data at http://oceancolor.gsfc.nasa.gov/cms/products
# 2.  Find a month of level 3 chlorophyll concentration data for the Modis instrument from http://oceancolor.gsfc.nasa.gov/cgi/l3
# 3.  Download the bz2 zipped files for the Standard Mapped Image and binned data to a folder called dataset
# 4.  unzip the two files with bunzip2
# 5.  Convert hdf4 to hdf5 with http://www.hdfgroup.org/h4toh5/download.html or http://hdfeos.org/software/h4toh5/bin/mac/

# Take a look at the Level3 mapped dataset specification:  http://oceancolor.gsfc.nasa.gov/DOCS/Ocean_Level-3_SMI_Products.pdf
# Compare that specification with the data dump given by dumph5:  (a reference page on the data type notation for h5py: https://www.safaribooksonline.com/library/view/python-and-hdf5/9781491944981/ch07.html and for numpy:http://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html).

# ##Binned data

# 1. Take a look at http://oceancolor.gsfc.nasa.gov/cms/L3Bins.html which describes the binning scheme
# 2. Here is a description of the hdf file layout: http://oceancolor.gsfc.nasa.gov/DOCS/Ocean_Level-3_Binned_Data_Products.pdf

# In[3]:

binned_file=glob.glob('../dataset/A20101522010181.L3b_MO_CHL.h5')[0]
dumph5(binned_file)


# Note that the chlorphyll data is stored as an 8 byte opaque type (V8).  On OSX, anaconda installs an hdf5 program call 'h5ls' which we can use to see more detail about this type.  On Windows, you'll need to install the utility separately
# http://www.hdfgroup.org/HDF5/release/obtain5.html

# ``` bash
# phil@rail% h5ls -v -r A20101522010181.L3b_MO_CHL.h5
# 
# /Level-3\ Binned\ Data/chlor_a Dataset {11384896/Inf}
#     Attribute: CLASS scalar
#         Type:      5-byte space-padded ASCII string
#         Data:  "TABLE"
#     Attribute: FIELD_0_NAME scalar
#         Type:      11-byte space-padded ASCII string
#         Data:  "chlor_a_sum"
#     Attribute: FIELD_1_NAME scalar
#         Type:      14-byte space-padded ASCII string
#         Data:  "chlor_a_sum_sq"
#     Attribute: HDF4_OBJECT_NAME scalar
#         Type:      7-byte space-padded ASCII string
#         Data:  "chlor_a"
#     Attribute: HDF4_OBJECT_TYPE scalar
#         Type:      5-byte space-padded ASCII string
#         Data:  "Vdata"
#     Attribute: HDF4_REF_NUM scalar
#         Type:      16-bit big-endian unsigned integer
#         Data:  5
#     Attribute: TITLE scalar
#         Type:      7-byte space-padded ASCII string
#         Data:  "chlor_a"
#     Attribute: VERSION scalar
#         Type:      3-byte space-padded ASCII string
#         Data:  "1.0"
#     Location:  1:216324552
#     Links:     1
#     Chunks:    {11384896} 91079168 bytes
#     Storage:   91079168 logical bytes, 91079168 allocated bytes, 100.00% utilization
#     Type:      shared-1:216324384 struct {
#                    "chlor_a_sum"      +0    IEEE 32-bit big-endian float
#                    "chlor_a_sum_sq"   +4    IEEE 32-bit big-endian float
#                } 8 bytes
# /Level-3\ Binned\ Data/chlor_a_t Type
#     Location:  1:216324384
#     Links:     2
#     Type:      shared-1:216324384 struct {
#                    "chlor_a_sum"      +0    IEEE 32-bit big-endian float
#                    "chlor_a_sum_sq"   +4    IEEE 32-bit big-endian float
#                } 8 bytes
# ```

# h5py reads this 8 byte vector in as a vector of two 4 byte tuples.  The first is the total chorophyll and the second is the squared sum.  To get the mean and variance for the binned chlorophyll we need to write a function as described in
# Section 4 of http://oceancolor.gsfc.nasa.gov/DOCS/Ocean_Level-3_Binned_Data_Products.pdf

# ##Exercise

# Write a function that calculates the mean chloryphyll concentration from level3 monthly binned file by extracting the weights from the binlist array and dividing each chlor_a_sum value by its weight.   Print out the first 50 non-zero chlorophyll concentrations in your file.

#     Here are the six fields for the BinList dataset -- read bin_num, nobs and weights separate lists
# ```
# FIELD_0_NAME: bin_num
# FIELD_1_NAME: nobs
# FIELD_2_NAME: nscenes
# FIELD_3_NAME: time_rec
# FIELD_4_NAME: weights
# FIELD_5_NAME: sel_cat
# FIELD_6_NAME: flags_set
# ```
                
# ##get the mean chlorophyl and store in dictionary indexed by tile number

# In[4]:

veclength=None
with  h5py.File(binned_file,'r') as infile:

    root_key=infile.keys()[0]
    binlist=infile[root_key]['BinList']
    chlor_a=infile[root_key]['chlor_a']
    veclength=binlist.shape[0]
    print('length: ',veclength)
    out = dict()
    chlor_a_data=chlor_a['chlor_a_sum'][:veclength]
    chlor_a_sq_data=chlor_a['chlor_a_sum_sq'][:veclength]
    weights_data=binlist['weights'][:veclength]
    binnums=binlist['bin_num'][:veclength]
    for i in range(veclength):
        meanval=chlor_a_data[i]/weights_data[i]
        meansq=chlor_a_sq_data[i]/weights_data[i]
        out[binnums[i]]=chlor_a_data[i]/weights_data[i]

#small change


# In[5]:

test=out.keys()
out[test[8000000]]


# In[ ]:

len(test)


# ##Problem for Wednesday Jan 28

# Write a function that creates a list of latitude,longitude tuples that cover a 500 x 500 lat/lon array
# in a area your are interested in.  Loop over this list of tuples and find the tile that contains
# each lat/lon pair.   Save these 25,000 items in a structured array with three columns:  latitude, longitude and tile number.
# Write this out to disk for future reference.
# 

# In[ ]:

with  h5py.File(binned_file,'r') as infile:
    root_key=infile.keys()[0]
    num_rows=infile[root_key]['BinIndex'].shape[0]
print('num_rows: ',num_rows)

nlats=500
nlons=500
lats=np.linspace(40.,50.,nlats)
lons=np.linspace(-121,-131.,nlons)
tile_find=tile_calc.tile_calc(num_rows)
lat_array=np.empty([nlats,nlons])
lon_array=np.empty([nlats,nlons])
chlor_array=np.empty([nlats,nlons])
count=0
for row,the_lat in enumerate(lats):
    for col,the_lon in enumerate(lons):
        lat_array[row,col]=the_lat
        lon_array[row,col]=the_lon
        
        
np.savez('lat_lon_tile.npz',keeprows=out)
        
        
    


# In[ ]:

out


# In[ ]:

out


# ##For next Wednesday -- find the mean chlorophyll concentration for every latitude and longitude point and plot on a Lambert-Conformal-Conic projection map

# Approach: fill a dictionary with the chlorophyll values with the tile numbers as keys, then use the dictionary
# to look up the chlorophyl for each one of your lat/lon pairs.  Put these values into a 500 x 500 array 

# In[ ]:




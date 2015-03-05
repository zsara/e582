from __future__ import division
import h5py
import bitmap
import numpy as np

mask_name='../dataset/MYD35_L2.A2014125.2135.006.2014125184012.h5'

with h5py.File(mask_name,'r') as infile:
    cloud_mask=infile['mod35/Data Fields/Cloud_Mask'][...]

maskVals=cloud_mask[0,...] #get the first byte
maskout,landout=bitmap.getmask_zero(maskVals)
oceanvals=(landout==0)
cloudvals=np.logical_and(maskout==0,oceanvals)
cloudfrac=np.sum(cloudvals)/oceanvals.size
oceanfrac=np.sum(oceanvals)/landout.size




from __future__ import division
import h5py
import glob
from matplotlib import pyplot as plt
import site
site.addsitedir('../src')
from reproject import reproj_L1B
from matplotlib.colors import Normalize
from matplotlib import cm
import numpy as np
from mpl_toolkits.basemap import Basemap
import bitmap

cloud_mask,=glob.glob('../datasets/MYD35*h5')
with  h5py.File(cloud_mask) as cloud_mask_h5:
    cloud_mask_byte0=cloud_mask_h5['mod35']['Data Fields']['Cloud_Mask'][0,:,:]

maskout,landout=bitmap.getmask_zero(cloud_mask_byte0)
maskout=maskout.astype(np.float32)
landout=landout.astype(np.float32)

output_name='cloud_mask.h5'
with h5py.File(output_name, "w") as f:
    dset=f.create_dataset('cloudmask',maskout.shape, dtype=maskout.dtype)
    dset[...]=maskout[...]
    dset.attrs['input_file']=cloud_mask
    dset.attrs['description']='0 = Cloud;1 = 66% prob. Clear;2 = 95% prob. Clear;3 = 99% prob. Clear'
    dset=f.create_dataset('landmask',landout.shape, dtype=landout.dtype)
    dset.attrs['input_file']=cloud_mask
    dset.attrs['description']='0=Water;1=Coastal;2=Desert;3=Land'
    dset[...]=landout[...]


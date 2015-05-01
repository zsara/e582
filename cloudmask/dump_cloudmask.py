#!/usr/bin/env python

"""
dump the cloud and land masks into a new h5 file
usage:

   ./dump_cloudmask.py MYD35_L2.A2010261.0525.006.2014075120621.h5 mask_day261_0525.h5

"""
from __future__ import division
import h5py
import glob
from matplotlib import pyplot as plt
import site
import numpy as np
import bitmap
import argparse
import textwrap

if __name__ == "__main__":
    #
    # the following two lines help format the docstring at the top of the file
    # into a help text
    #
    linebreaks=argparse.RawTextHelpFormatter
    descrip=textwrap.dedent(globals()['__doc__'])
    parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
    parser.add_argument('infile',type=str,help='MYD35_L2 input hdf5 file path')
    parser.add_argument('outfile',type=str,help='output hdf5 file for cloud/land mask')
    args=parser.parse_args()

    cloud_mask,=glob.glob(args.infile)
    with  h5py.File(cloud_mask) as cloud_mask_h5:
        cloud_mask_byte0=cloud_mask_h5['mod35']['Data Fields']['Cloud_Mask'][0,:,:]

    maskout,landout=bitmap.getmask_zero(cloud_mask_byte0)
    maskout=maskout.astype(np.float32)
    landout=landout.astype(np.float32)

    with h5py.File(args.outfile, "w") as f:
        dset=f.create_dataset('cloudmask',maskout.shape, dtype=maskout.dtype)
        dset[...]=maskout[...]
        dset.attrs['input_file']=cloud_mask
        dset.attrs['description']='0 = Cloud;1 = 66% prob. Clear;2 = 95% prob. Clear;3 = 99% prob. Clear'
        dset=f.create_dataset('landmask',landout.shape, dtype=landout.dtype)
        dset.attrs['input_file']=cloud_mask
        dset.attrs['description']='0=Water;1=Coastal;2=Desert;3=Land'
        dset[...]=landout[...]


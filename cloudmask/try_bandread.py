#!/usr/bin/env python
"""
  read the band names for the EV_Emissive channels into a list and select 1

  usage: ./try_bandread.py names.json
"""
from __future__ import division,print_function

import h5py
import site
site.addsitedir('../utilities')
from compat import text_,is_py3
import argparse,textwrap
import io,json
from collections import OrderedDict as od
import sys,traceback

if __name__ == "__main__":

    linebreaks=argparse.RawTextHelpFormatter
    descrip=textwrap.dedent(globals()['__doc__'])
    parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
    parser.add_argument('initfile',type=str,help='name of json file with filenames')
    args=parser.parse_args()

    with io.open(args.initfile,'r',encoding='utf8') as f:
        name_dict=json.loads(f.read(),object_pairs_hook=od)

    keys=['l1b_file', 'geom_file', 'mask_file', 'm06_file']

    l1b_file,geom_file,mask_file,mod06_file=\
          [name_dict[key] for key in keys]

    if is_py3:
        print("\nI see you're running python 3 -- trouble ahead\n")

    with h5py.File(l1b_file) as l1b_h5:
        #channel31 is emissive channel 10
        band_names=l1b_h5['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['band_names']
        try:
            band_names_ascii=band_names
            band_names_list=band_names.split(',')
            index31=band_names_list.index('31')
            print('success: type of band_names: {} -- value of index31: {}'.format(type(band_names),index31))
        except TypeError as ex:
            ex_type, ex_val, tb = sys.exc_info()
            print('bummer: ',ex_val)
            print('\nhere is the traceback:\n')
            traceback.print_tb(tb)
            print("python3 reads band_names as bytes, won't split on comma")

        if is_py3:
            print('\nTry this again, decoding the byte string assuming an ascii encoding')
            band_names_ascii=band_names.decode('ascii','strict')
            print('\nbandnames was {}, now it is {}'.format(type(band_names),type(band_names_ascii)))
            band_names_list=band_names_ascii.split(',')
            index31=band_names_list.index('31')
            print('success: type of band_names: {} -- value of index31: {}\n\n'.format(type(band_names),index31))
            
        print('\nFinally -- show how the text_ helper handles both python2 and python3\n')
        band_names=text_(l1b_h5['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['band_names'])
        band_names_list=band_names_ascii.split(',')
        index31=band_names_list.index('31')
        print('success: type of band_names: {} -- value of index31: {}\n\n'.format(type(band_names),index31))
        
            
              

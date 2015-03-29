#!/usr/bin/env python
"""
  read the level1b file and the cloud mask file from dump_cloudmask.py and
  produce plots of the chan31 radiance, channel 1 reflectance,
  cloud mask and landmask

  usage:

  ./plot_cloudmask.py MYD021KM.*35*.h5 MYD021KM.*35*.h5 MYD35*.35*.h5  MYD35*.40*.h5  mask_*35*.h5  mask_*40*.h5 

"""
from __future__ import division
import argparse
import h5py
import glob
from matplotlib import pyplot as plt
import site
site.addsitedir('../utilities')
from reproject import reproj_numba
import planck
import io,json
from collections import OrderedDict as od

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

if __name__ == "__main__":
    #
    # the following two lines help format the docstring at the top of the file
    # into a help text
    #
    linebreaks=argparse.RawTextHelpFormatter
    descrip=textwrap.dedent(globals()['__doc__'])
    parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
    parser.add_argument('l1bAfile',type=str,help='MYD21KM radiance fileA')
    parser.add_argument('l1bBfile',type=str,help='MYD21KM radiance fileB')
    parser.add_argument('geomAfile',type=str,help='MYD03 geometry fileA')
    parser.add_argument('geomBfile',type=str,help='MYD03 geometry fileA')
    parser.add_argument('cloudmaskAfile',type=str,help='cloud mask fileA')
    parser.add_argument('cloudmaskBfile',type=str,help='cloud mask fileB')
    args=parser.parse_args()
        
    l1b_fileA,=glob.glob(args.l1bAfile)
    l1b_fileB,=glob.glob(args.l1bBfile)
    geom_fileA,=glob.glob(args.geomAfile)
    geom_fileB,=glob.glob(args.geomBfile)
    mask_fileA,=glob.glob(args.cloudmaskAfile)
    mask_fileB,=glob.glob(args.cloudmaskBfile)
    keys=['l1b_fileA','l1b_fileB','geom_fileA','geom_fileB',
          'mask_fileA','mask_fileB']
    values=[l1b_fileA,l1b_fileB,geom_fileA,geom_fileB,
            mask_fileA,mask_fileB]
    filedict=od()
    filedict['comment']='day 126 case for Jenny'
    for key,value in zip(keys,values):
        filedict[key]=value

    with io.open('names.json','w',encoding='utf8') as f:
        f.write(json.dumps(filedict,indent=4,ensure_ascii=False))



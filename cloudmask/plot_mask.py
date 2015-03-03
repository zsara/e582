from __future__ import division
import matplotlib
matplotlib.use('Agg')
from satellite.modismeta import parseMeta
import sys,os
import numpy as np
import pyhdf.SD
import matplotlib.pyplot as plt
from dateutil.parser import parse
from ubcplot.stdplot import simplots
from pyutils import process

import dateutil.tz as tz
import re
sys.path.insert(0,'testlib')
import bitmap

if len(sys.argv) == 1:
    plot_dir='figures'
else:
    plot_dir=sys.argv[1]

if not os.path.isdir(plot_dir):
    os.makedirs(plot_dir)


mask_name='MYD35_L2.A2008290.0740.005.2008290182115.hdf'

mask=pyhdf.SD.SD(mask_name)
theMeta=parseMeta(mask)
theDate=parse(theMeta['startdate'][:-3] + theMeta['starttime'])
theDate=theDate.replace(tzinfo=tz.tzutc())


maskVals=mask.select('Cloud_Mask')
maskVals=maskVals.get()
maskVals=maskVals[0,...] #get the first byte
maskout,landout=bitmap.getmask_zero(maskVals)
oceanvals=(landout==0)
cloudvals=np.logical_and(maskout==0,oceanvals)
cloudfrac=np.sum(cloudvals)/oceanvals.size
oceanfrac=np.sum(oceanvals)/landout.size

options={'fignum':1}
corner_plot=simplots(option_dict=options)
theMap=corner_plot.make_lambert()
x,y=theMap(theMeta['cornerlons'],theMeta['cornerlats'])
theMap.plot(x,y)
theFig=theMap.ax.figure
theFig.canvas.draw()
theTitle=theMap.ax.set_title('cloud frac: %5.3f, oceanfrac: %5.3f' % (cloudfrac,oceanfrac))
x,y=theTitle.get_position()
theSize=theTitle.get_fontsize()
y=y*1.12
theMatch=re.compile('^MYD35_L2.(.*).005.*')
topTitle=theMatch.match(theMeta['filename']).group(1)
topText=theMap.ax.text(x,y,'%s' % topTitle,transform=theMap.ax.transAxes,ha='center',fontsize=theSize)
title='map.png'
figname='%s/%s.png' % (plot_dir,title)
theFig.canvas.print_figure(figname,dpi=150)
process.command("firefox %s" % figname)


#plt.show()




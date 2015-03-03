from __future__ import division
import matplotlib
matplotlib.use('Agg')
from satellite.modismeta import parseMeta
import bitmap
import numpy as np
import pyhdf.SD
import matplotlib.pyplot as plt
from dateutil.parser import parse
import dateutil.tz as tz
import re
## test=np.arange(5,dtype=np.int32)
## bitmap.printdata(test)


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

from ubcplot.stdplot import makeFig,makeMap

figDict={}
fignum=1
figDict[fignum]=makeFig(maskout,0.,3.,fignum)

fignum=2
figDict[fignum]=makeFig(landout,0.,3.,fignum)

fignum=3
theFig,theMap=makeMap(fignum)
x,y=theMap(theMeta['cornerlons'],theMeta['cornerlats'])
theMap.plot(x,y)
theFig.canvas.draw()
theTitle=theMap.ax.set_title('cloud frac: %5.3f, oceanfrac: %5.3f' % (cloudfrac,oceanfrac))
x,y=theTitle.get_position()
theSize=theTitle.get_fontsize()
y=y*1.12
theMatch=re.compile('^MYD35_L2.(.*).005.*')
topTitle=theMatch.match(theMeta['filename']).group(1)
topText=theMap.ax.text(x,y,'%s' % topTitle,transform=theMap.ax.transAxes,ha='center',fontsize=theSize)
theFig.canvas.print_figure('map.png',dpi=150)

fignum=4
theFig=plt.figure(fignum)
theFig.clf()
theAxis=theFig.add_subplot(111)
theAxis.hist(maskout.ravel())

fignum=5
theFig=plt.figure(fignum)
theFig.clf()
theAxis=theFig.add_subplot(111)
theAxis.hist(landout.ravel())


#plt.show()




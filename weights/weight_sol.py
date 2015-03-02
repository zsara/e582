"""
  solutions to March 2 problem set
"""
from __future__ import print_function,division
from gasabsr98 import gasabsr98
import numpy as np
from matplotlib import pyplot as plt
from jinja2 import Template

import hydrostat as hydro
reload(hydro)
import os
import site
site.addsitedir('../gallery')
import build_gallery as bg
reload(bg)

freq=[50.3000,52.8000,53.7110,54.4000,
      54.9400,55.5000,57.2900,57.5070]

#buid the atmosphere and plot it
T_surf=280.
P_surf=102.e3
lapse= -7.e-3
delta_z=10.
num_levels=1000
temp,press,rhos,heights=hydro.hydrostat(T_surf,P_surf,lapse,delta_z,num_levels)
rhowv0=20.e-3
vapor_scale=3000.

#
# we need the transmission between the TOA and height z, so flip
# vectors so that they start from top
#
keep_down={}
keep_up={}
keep_down_vapor={}
top_down_z=heights[::-1]
top_down_tk=temp[::-1]
top_down_p=press[::-1]
top_down_rho=rhos[::-1]
top_down_rhowv=rhowv0*np.exp(-top_down_z/vapor_scale)
bottom_up_rhowv=rhowv0*np.exp(-heights/vapor_scale)
    
plt.close('all')
figlist=[]

tk=260.
pa=80.e3
rhowv=10.e-3
freqs=np.linspace(1,90.,100)
airlist=[]
wvlist=[]
for f in freqs:
    air,wv=gasabsr98(f,tk,rhowv,pa)
    airlist.append(air)
    wvlist.append(wv)

    
plotdir='{}/{}'.format(os.getcwd(),'plots')
if not os.path.exists(plotdir):
    os.makedirs(plotdir)

def make_fig(x=None,y=None,title=None,figpath=None):
    fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
    ax.plot(x, y, 'b-')
    ax.set_title(title)
    fig.savefig(figpath)
    return None
            
title='air abs coeff vs. freq'
plotfile='mass_abs_coeff_air.png'
figpath='{}/{}'.format(plotdir,plotfile)
figdict=dict(title=title,figpath=figpath,
             x=freqs,y=airlist)
make_fig(**figdict)
figdict['caption']='caption'
figdict['plotfile']=plotfile
figlist.append(figdict)

title='vapor abs coeff vs. freq'
plotfile='mass_abs_coeff_h2o.png'
figpath='{}/{}'.format(plotdir,plotfile)
figdict=dict(title=title,figpath=figpath,
             x=freqs,y=wvlist)
make_fig(**figdict)
figdict['caption']='caption'
figdict['plotfile']=plotfile
figlist.append(figdict)

title='air density vs. height'
plotfile='air_dens.png'
figpath='{}/{}'.format(plotdir,plotfile)
figdict=dict(title=title,figpath=figpath,
             x=rhos,y=heights)
make_fig(**figdict)
figdict['caption']='caption'
figdict['plotfile']=plotfile
figlist.append(figdict)


title='vapor density vs. height'
plotfile='h2o_dens.png'
figpath='{}/{}'.format(plotdir,plotfile)
figdict=dict(title=title,figpath=figpath,
             x=top_down_rhowv,y=top_down_z)
make_fig(**figdict)
figdict['caption']='caption'
figdict['plotfile']=plotfile
figlist.append(figdict)


#now plot the five weighting functions -- first from the top down


for f in freq:
    print('calculating f={}'.format(f))
    absair=list()
    abswv=list()
    deltau=list()
    for row,height in enumerate(top_down_z):
        tk=top_down_tk[row]
        pa=top_down_p[row]
        rho=top_down_rho[row]
        rhowv=top_down_rhowv[row]
        absair_val,abswv_val=gasabsr98(f,tk,rhowv,pa)
        absair.append(absair_val*rho)
        abswv.append(abswv_val*rhowv)
        deltau.append(absair_val*rho*delta_z)
    keep_down[f]=(np.array(absair),np.array(abswv),np.array(deltau))
    #now repeat from surface up
    absair=list()
    abswv=list()
    deltau=list()
    for row,height in enumerate(heights):
        tk=temp[row]
        pa=press[row]
        rho=rhos[row]
        rhowv=bottom_up_rhowv[row]
        absair_val,abswv_val=gasabsr98(f,tk,rhowv,pa)
        absair.append(absair_val*rho)
        abswv.append(abswv_val*rhowv)
        deltau.append(absair_val*rho*delta_z)
    keep_up[f]=(np.array(absair),np.array(abswv),np.array(deltau))
        
freqs=keep_down.keys()
freqs.sort()

#remember that the tuples are (air absorption coeff, h2o absorption coef, deltau)
#                                       0                    1              2 
title='volume abs coeff for air'
plotfile='volume_abs_air.png'
figpath='{}/{}'.format(plotdir,plotfile)   
fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    out = ax.plot(keep_down[freq][0],top_down_z,label='{} GHz'.format(freq))
ax.set_title(title)
ax.legend(loc='best')
fig.savefig(figpath)
figlist.append(dict(title=title,plotfile=plotfile,figpath=figpath,caption='caption'))

title='volume abs coeff for h2o'
plotfile='volume_abs_h2o.png'
figpath='{}/{}'.format(plotdir,plotfile)   
fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    out = ax.plot(keep_down[freq][1],top_down_z,label='{} GHz'.format(freq))
ax.set_title(title)
ax.legend(loc='best')
fig.savefig(figpath)
figlist.append(dict(title=title,plotfile=plotfile,figpath=figpath,caption='caption'))

title='transmission from TOA to z for air'
plotfile='transmission_upward_air.png'
figpath='{}/{}'.format(plotdir,plotfile)    
fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    tau=np.cumsum(keep_down[freq][2])
    trans=np.exp(-tau)
    out = ax.plot(trans,top_down_z,label='{} GHz'.format(freq))
ax.set_title(title)
ax.legend(loc='best')
fig.savefig(figpath)
figlist.append(dict(title=title,plotfile=plotfile,figpath=figpath,
                    caption='transmission between TOA and height z'))

title='weighting functions for upward radiation: air'
plotfile='upweights_air.png'
figpath='{}/{}'.format(plotdir,plotfile)
fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    tau=np.cumsum(keep_down[freq][2])
    trans=np.exp(-tau)
    out = ax.plot(-np.diff(trans)/delta_z,top_down_z[1:],label='{} GHz'.format(freq))
ax.set_xlim([0,2.e-4])    
ax.set_title(title)
ax.legend(loc='best')
fig.savefig(figpath)
figlist.append(dict(title=title,plotfile=plotfile,figpath=figpath,
                    caption='weight function for upwelling radiation'))


title='transmission from surface to z for air'
plotfile='transmission_downward_air.png'
figpath='{}/{}'.format(plotdir,plotfile)    
fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    tau=np.cumsum(keep_up[freq][2])
    trans=np.exp(-tau)
    out = ax.plot(trans,heights,label='{} GHz'.format(freq))
ax.set_title(title)
ax.legend(loc='best')
fig.savefig(figpath)
figlist.append(dict(title=title,plotfile=plotfile,figpath=figpath,
                    caption='transmission between surface and height z'))

title='weighting functions for downward radiation: air'
plotfile='down_weights_air.png'
figpath='{}/{}'.format(plotdir,plotfile)
fig, ax = plt.subplots(1, 1, figsize = (12, 12) )
for freq in freqs:
    tau=np.cumsum(keep_up[freq][2])
    trans=np.exp(-tau)
    out = ax.plot(-np.diff(trans)/delta_z,heights[1:],label='{} GHz'.format(freq))
#ax.set_xlim([0,2.e-4])    
ax.set_title(title)
ax.legend(loc='best')
fig.savefig(figpath)
figlist.append(dict(title=title,plotfile=plotfile,figpath=figpath,
                    caption='weight function for downwelling radiation'))

#
# now turn all these png files into an html gallery using the figlist.
# We also need a title for the page (which papears in the browser tab) and a description
# that appears at the top of the page
#
figdict=dict(plotdir=plotdir,title='weight_sol',description='weights solution: March 2',
             figlist=figlist)

#
# generate smaller thumbnails so that a lot of plots can be browsed
#
bg.generateThumbnails(figdict)

#
# use jinja2 to fill in the plots using a template
#
template_path=bg.path_to_template('jinja_responsive.tmpl')
index_path='{}/index.html'.format(plotdir)    


with open(template_path,'r') as f:
    template = Template(f.read())

#
# this will write and index.html file in the plotdir directory
# you should be able to see the plots by doing:
#  > firefox index.html
#
with open(index_path,'w') as f:
    f.write(template.render(captions=figdict))
    
    
plt.show()

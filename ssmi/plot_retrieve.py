import numpy.ma as ma
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
from matplotlib.colors import Normalize
import h5py
import numpy as np

if __name__=="__main__":

    input='correct.h5'
    data_dict={}
    with h5py.File(input,'r') as f:
        g=f['latlon']
        data_dict['latlon']={}
        for key in ['lat','lon']:
            data_dict['latlon'][key]=g[key][...]
        for month in ['jan','july']:
            data_dict[month]={}
            for name,var in f[month].items():
                data_dict[month][name]=var[...]
        data_dict['correct']=f.attrs['correct_flag']

    input='incorrect.h5'
    wrong_dict={}
    with h5py.File(input,'r') as f:
        g=f['latlon']
        wrong_dict['latlon']={}
        for key in ['lat','lon']:
            wrong_dict['latlon'][key]=g[key][...]
        for month in ['jan','july']:
            wrong_dict[month]={}
            for name,var in f[month].items():
                wrong_dict[month][name]=var[...]
        wrong_dict['correct']=f.attrs['correct_flag']

            
    cmap=cm.YlGn  #see http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
    cmap.set_over('r')
    cmap.set_under('b')
    cmap.set_bad('0.75') #75% grey
    lats=data_dict['latlon']['lat']
    lons=data_dict['latlon']['lon']
    correct=data_dict['correct']
    
    plotdir='plots'
    for the_month in ['jan','july']:
        print('plotting {}'.format(the_month))
        fields=data_dict[the_month]
        wrong_fields=wrong_dict[the_month]
        vmin= 0.
        vmax= 50.
        the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
        fig,ax1=plt.subplots(figsize=[12,12])
        ax1=fig.add_subplot(111)
        m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,\
                    llcrnrlon=0,urcrnrlon=360,resolution='c',ax=ax1)
        m.drawcoastlines()
        x,y=m(lons,lats)
        # draw parallels and meridians.
        m.drawparallels(np.arange(-90.,91.,30.))
        m.drawmeridians(np.arange(-180.,181.,60.))
        wv=ma.array(fields['wv'],mask=np.isnan(fields['wv']))
        vals=m.pcolormesh(x,y,wv,cmap=cmap,norm=the_norm)
        fig.colorbar(vals,extend='both')
        plt.title("wv {} (kg/m^2) for {}".format(correct,the_month))
        figpath='{}/wv_{}_{}.png'.format(plotdir,correct,the_month)
        fig.savefig(figpath)

        vmin= 0.
        vmax= 0.5
        the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
        fig,ax1=plt.subplots(figsize=[12,12])
        m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,\
                    llcrnrlon=0,urcrnrlon=360,resolution='c',ax=ax1)
        m.drawcoastlines()
        # draw parallels and meridians.
        m.drawparallels(np.arange(-90.,91.,30.))
        m.drawmeridians(np.arange(-180.,181.,60.))
        wl=ma.array(fields['wl'],mask=np.isnan(fields['wl']))
        vals=m.pcolormesh(x,y,wl,cmap=cmap,norm=the_norm)
        fig.colorbar(vals,extend='both')
        plt.title("wl {} (kg/m^2) for {}".format(correct,the_month))
        figpath='{}/wl_{}_{}.png'.format(plotdir,correct,the_month)
        fig.savefig(figpath)

        ## vmin= 0.
        ## vmax= 0.5
        ## the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
        the_norm=None
        wl_diff=fields['wl'] - wrong_fields['wl']
        wl_diff=ma.array(wl_diff,mask=np.isnan(wl_diff))
        fig,ax1=plt.subplots(figsize=[12,12])
        m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,\
                    llcrnrlon=0,urcrnrlon=360,resolution='c',ax=ax1)
        m.drawcoastlines()
        # draw parallels and meridians.
        m.drawparallels(np.arange(-90.,91.,30.))
        m.drawmeridians(np.arange(-180.,181.,60.))
        vals=m.pcolormesh(x,y,wl_diff,cmap=cmap,norm=the_norm)
        fig.colorbar(vals,extend='both')
        plt.title("wl_corr - wl_wrong (%) for {}".format(correct,the_month))
        figpath='{}/wl_{}_diff.png'.format(plotdir,the_month)
        fig.savefig(figpath)

        wv_diff=fields['wv'] - wrong_fields['wv']
        wv_diff=ma.array(wv_diff,mask=np.isnan(fields['wv']))
        ## vmin= 0.
        ## vmax= 50
        #the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
        the_norm=None
        fig,ax1=plt.subplots(figsize=[12,12])
        m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,\
                    llcrnrlon=0,urcrnrlon=360,resolution='c',ax=ax1)
        m.drawcoastlines()
        # draw parallels and meridians.
        m.drawparallels(np.arange(-90.,91.,30.))
        m.drawmeridians(np.arange(-180.,181.,60.))
        vals=m.pcolormesh(x,y,wl_diff,cmap=cmap,norm=the_norm)
        fig.colorbar(vals,extend='both')
        plt.title("wv_corr - wv_wrong (%) for {}".format(correct,the_month))
        figpath='{}/wv_{}_diff.png'.format(plotdir,the_month)
        fig.savefig(figpath)

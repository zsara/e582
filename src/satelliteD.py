# coding: utf-8
from __future__ import print_function

import glob  #this module gets file names using wildcards
import site
site.addsitedir('../utilities')
import tile_calc
import h5py
import matplotlib.pyplot as plt
import numpy as np
import tile_calc
from contexttimer import Timer
import pickle
import pandas as pd
import tables
import time
import datetime as dt

if __name__ == "__main__":
    binned_file=glob.glob('../dataset/A20101522010181.L3b_MO_CHL.h5')[0]
    final_file='navigated.h5'
    with  h5py.File(binned_file,'r') as infile:
        root_key=infile.keys()[0]
        start_day=int(infile.attrs['Start Day_GLOSDS'])
        start_year=infile.attrs['Start Year_GLOSDS']
        start=dt.datetime(start_year-1,12,31) + dt.timedelta(days=start_day)
        end_day=int(infile.attrs['End Day_GLOSDS'])
        end_year=infile.attrs['End Year_GLOSDS']
        end=dt.datetime(end_year-1,12,31) + dt.timedelta(days=end_day)
        start_date=start.strftime('%Y-%m-%d')
        end_date=end.strftime('%Y-%m-%d')
        binlist=infile[root_key]['BinList']
        chlor_a=infile[root_key]['chlor_a']
        veclength=binlist.shape[0]
        print('reading length: ',veclength)
        chlor_a_data=chlor_a['chlor_a_sum'][:veclength]
        #chlor_a_sq_data=chlor_a['chlor_a_sum_sq'][:veclength]
        weights_data=binlist['weights'][:veclength]
        binnums=binlist['bin_num'][:veclength]
        out = np.empty((veclength,),dtype=[('binnum','>i4'),('chlor_a_mean','>f4')])
        write=False
        out_h5='store.h5'
        with Timer() as t:
            if write:
                for i in range(veclength):
                    meanval=chlor_a_data[i]/weights_data[i]
                    #meansq=chlor_a_sq_data[i]/weights_data[i]
                    out[i]=(binnums[i],chlor_a_data[i]/weights_data[i])
                print("time to create structured array: ",t.elapsed)
                the_df=pd.DataFrame.from_records(out,index='binnum')
                print("time to create dataframe: ",t.elapsed)
                with pd.HDFStore('store.h5','w') as store:
                    store.put('chlor_a_mean',the_df,format='table')
                with tables.open_file(out_h5,'a') as f:
                    f.root._v_attrs.history='created by satelliteD.py'
                    f.root._v_attrs.created_on=time.strftime("%c")
                    f.root._v_attrs.start_date=start_date
                    f.root._v_attrs.end_date=end_date
                    node=f.get_node('/chlor_a_mean')
                    units='micrograms/m^3'
                    title='mean chlorophyll concentration'
                    node._v_attrs.units=units
                    node._v_attrs.title=title
                print('time to write dataframe: ',t.elapsed)
            else:
                with pd.HDFStore(out_h5,'r') as store:
                    the_df=store['chlor_a_mean']
                with tables.open_file(out_h5,'r') as f:
                    node=f.get_node('/chlor_a_mean')
                    units=node._v_attrs.units
                    title=node._v_attrs.title
                    node=f.get_node('/')
                    f.root._v_attrs.start_date=start_date

                    
        ## tc=tile_calc.tile_calc(4320)
        ## nlats=500
        ## nlons=500
        ## lats=np.linspace(40.,50.,nlats)
        ## lons=np.linspace(-121,-131.,nlons)
        ## num_rows=4320
        ## tile_find=tile_calc.tile_calc(num_rows)
        ## lat_array=np.empty([nlats,nlons],dtype=np.float32)
        ## lon_array=np.empty_like(lat_array)
        ## chlor_array=np.empty_like(lat_array)
        ## print(type(chlor_array),chlor_array.dtype)
        ## count=0
        ## with Timer() as t:
        ##     with pd.HDFStore(out_h5,'r') as store:
        ##         for row,the_lat in enumerate(lats):
        ##             for col,the_lon in enumerate(lons):
        ##                 lat_array[row,col]=the_lat
        ##                 lon_array[row,col]=the_lon
        ##                 tile=tc.latlon2tile(the_lat,the_lon)
        ##                 if tile in the_df.index:
        ##                     chlor_array[row,col]=the_df.loc[tile]
        ##                 else:
        ##                     chlor_array[row,col]=np.nan
        ##                     #print(np.isnan(chlor_array[row,col]))
        ##     print('through calc: ',t.elapsed)

        ##     with h5py.File(final_file, "w") as f:
        ##         dset_lat = f.create_dataset("lattitude", lat_array.shape, dtype=lat_array.dtype)
        ##         dset_lat[...]=lat_array[...]
        ##         dset_lon = f.create_dataset("longitude", lon_array.shape, dtype=lon_array.dtype)
        ##         dset_lon[...]=lon_array[...]
        ##         dset_var = f.create_dataset("chlor_a_mean", chlor_array.shape, dtype=chlor_array.dtype)
        ##         dset_var[...]=chlor_array[...]
        ##         dset_var.attrs['units']=units
        ##         dset_var.attrs['title']=title
        ##         f.attrs['created_on']=time.strftime("%c")
        ##         print('through final write: ',t.elapsed)


        
            
            

                    

                

                
                


                

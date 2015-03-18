"""
   bin modis data into regular latitude and longitude bins   
"""

from __future__ import division
from builtins import range
import numpy as np
import numba


def hist2d(x_raw,y_raw,x_edges,y_edges):
    x_centers=(x_edges[:-1] + x_edges[1:])/2.
    y_centers=(y_edges[:-1] + y_edges[1:])/2.
    num_xbins=len(x_centers)
    num_ybins=len(y_centers)
    x_indices=np.searchsorted(x_edges, x_raw.flat, 'right')
    y_indices=np.searchsorted(y_edges, y_raw.flat, 'right')
    hist_array=np.zeros([len(y_centers), len(x_centers)], dtype=np.float)
    for n in range(len(y_indices)): #y_indices and x_indices both size of raw data
        if x_indices[n] > 0 and y_indices[n] > 0 and \
            x_indices[n] <= num_xbins and y_indices[n] <= num_ybins:
            bin_row=y_indices[n]-1 # '-1' to get the index of the bin center
            bin_col=x_indices[n]-1
            hist_array[bin_row, bin_col] += 1
    rows,cols=hist_array.shape
    for row in range(rows):
        for col in range(cols):
            if hist_array[row,col] < 1.:
                hist_array[row,col]=np.nan
    return hist_array,x_centers,y_centers


# nopython=True means an error will be raised
# if fast compilation is not possible.

def fill_counts(y_centers,x_centers,y_indices,x_indices):
    num_xbins=len(x_centers)
    num_ybins=len(y_centers)
    hist_array=np.zeros([num_ybins, num_xbins], dtype=np.float)
    for n in range(len(y_indices)): #y_indices and x_indices both size of raw data
        if x_indices[n] > 0 and y_indices[n] > 0 and \
            x_indices[n] <= num_xbins and y_indices[n] <= num_ybins:
            bin_row=y_indices[n]-1 # '-1' to get the index of the bin center
            bin_col=x_indices[n]-1
            hist_array[bin_row, bin_col] += 1
    rows,cols=hist_array.shape
    for row in range(rows):
        for col in range(cols):
            if hist_array[row,col] < 1.:
                hist_array[row,col]=np.nan
    return hist_array

c_fill_counts=numba.jit(fill_counts)
            
def numba_hist2d(x_raw,y_raw,x_edges,y_edges):
    x_centers=(x_edges[:-1] + x_edges[1:])/2.
    y_centers=(y_edges[:-1] + y_edges[1:])/2.
    num_xbins=len(x_centers)
    num_ybins=len(y_centers)
    x_indices=np.searchsorted(x_edges, x_raw.flat, 'right')
    y_indices=np.searchsorted(y_edges, y_raw.flat, 'right')
    hist_array=c_fill_counts(y_centers,x_centers,y_indices,x_indices)
    return hist_array,x_centers,y_centers


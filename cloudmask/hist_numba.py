from __future__ import division,print_function
import numba
import numpy as np

# nopython=True means an error will be raised
# if fast compilation is not possible.
@numba.jit(nopython=True)
def fill_counts(y_centers,x_centers,y_indices,x_indices,hist_array):
    num_xbins=x_centers.shape[0]
    num_ybins=y_centers.shape[0]
    num_y=y_indices.shape[0]
    num_x=x_indices.shape[0]
    for n in range(num_y): #y_indices and x_indices both size of raw data
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

            
def numba_hist2d(x_raw,y_raw,x_edges,y_edges):
    x_centers=(x_edges[:-1] + x_edges[1:])/2.
    y_centers=(y_edges[:-1] + y_edges[1:])/2.
    num_xbins=int(len(x_centers))
    num_ybins=int(len(y_centers))
    x_indices=np.asarray(np.searchsorted(x_edges, x_raw.flat, 'right'),dtype=np.int64)
    y_indices=np.asarray(np.searchsorted(y_edges, y_raw.flat, 'right'),dtype=np.int64)
    hist_array=np.zeros([num_ybins, num_xbins], dtype=np.float)
    hist_array=fill_counts(y_centers,x_centers,y_indices,x_indices,hist_array)
    return hist_array,x_centers,y_centers


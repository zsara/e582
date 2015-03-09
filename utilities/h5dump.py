#!/usr/bin/env python
from __future__ import print_function
import h5py
import argparse
import types

def print_attrs(name, obj):
    print("item name: ",name,repr(obj))
    for key, val in obj.attrs.items():
        print("    %s: %s" % (key, val))

def dumph5(filename):
    #
    # make sure that have a filename, not an open file
    #
    if isinstance(filename,h5py._hl.files.File):
        raise Exception('need simple filename')
    with  h5py.File(filename,'r') as infile:
        infile.visititems(print_attrs)
        print('-------------------')
        print("attributes for the root file")
        print('-------------------')
        for key,value in infile.attrs.items():
            print("attribute name: ",key,"--- value: ",value)
    return None
        
if __name__ == "__main__":
    #
    # if we are tunning as main program pass filename as argument
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('h5_file',type=str,help='name of h5 file')
    args=parser.parse_args()
    filename=args.h5_file
    dumph5(filename)

    
    

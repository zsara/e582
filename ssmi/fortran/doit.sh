#!/bin/bash
#make -f Makefile_fort clean
#make -f Makefile_fort all
python setup_petty.py build_ext --inplace clean
python test_petty.py

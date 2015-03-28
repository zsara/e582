from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy
import os

os.environ["CC"] = "clang"
os.environ["CXX"] = "clang++" 

ext_modules = [Extension('bitmap', ['bitmap.pyx','bitmask.cpp'],
                       include_dirs = [numpy.get_include(),'.'],
                       extra_compile_args=['-O3', '-fPIC'],
                       library_dirs=['.'],
                       language="c++")]
                       #extra_objects=["bitmask.o"])]

setup(name        = 'bitmap',
      cmdclass    = {'build_ext': build_ext},
      ext_modules = ext_modules
      )

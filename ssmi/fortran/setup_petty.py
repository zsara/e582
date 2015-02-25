from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

setup(name        = 'petty',
      ext_modules = [Extension('petty', ['petty.pyx'],
                               include_dirs = [numpy.get_include(),'.'],
                               extra_compile_args=['-O3'],
                               library_dirs=['.'],
                               libraries=['petty','gfortran'])],
      cmdclass    = {'build_ext': build_ext},
      )


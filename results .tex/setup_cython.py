from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("util_cython.pyx")
)

#python setup_cython.py build_ext --inplace
#output in NEW SUBFOLDER mDataStore. Need to move and rename (pyd)
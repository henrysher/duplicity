#!/usr/bin/env python

import sys, os
from distutils.core import setup, Extension

assert len(sys.argv) == 1
sys.argv.append("build")

setup(name="CModule",
	  version="cvs",
	  description="duplicity's C component",
	  ext_modules=[Extension("_librsync",
							 ["_librsyncmodule.c"],
							 libraries=["rsync"])])

assert not os.system("mv `find build -name _librsync.so` .")
assert not os.system("rm -rf build")

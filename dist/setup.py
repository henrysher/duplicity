#!/usr/bin/env python

import sys, os, getopt
from distutils.core import setup, Extension

version_string = "$version"

if sys.version_info[:2] < (2,2):
	print "Sorry, duplicity requires version 2.2 or later of python"
	sys.exit(1)

setup(name="duplicity",
	  version=version_string,
	  description="Encrypted backup using rsync algorithm",
	  author="Kenneth Loafman",
	  author_email="kenneth@loafman.com",
	  url="http://duplicity.nongnu.org/index.html",
	  packages = ['duplicity'],
	  package_dir = {"duplicity": "src"},
	  ext_modules = [Extension("duplicity._librsync",
							   ["_librsyncmodule.c"],
							   libraries=["rsync"])],
	  scripts = ['rdiffdir', 'duplicity'],
	  data_files = [('share/man/man1', ['duplicity.1', 'rdiffdir.1']),
					('share/doc/duplicity-%s' % version_string,
					 ['COPYING', 'README', 'CHANGELOG'])])



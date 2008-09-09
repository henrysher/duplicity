#!/usr/bin/env python

import sys, os, getopt
from distutils.core import setup, Extension

version_string = "$version"

if sys.version_info[:2] < (2,3):
    print "Sorry, duplicity requires version 2.3 or later of python"
    sys.exit(1)

try:
    import pexpect
    pexpect_version = pexpect.__version__
except ImportError:
    pexpect_version = None

if not pexpect_version or pexpect_version < "2.1":
    print ("Warning: pexpect version 2.1 or greater is required for the ssh backend.\n"
           "         If you do not plan to use the ssh backend, this is not a problem.")

incdir_list = libdir_list = None 

if os.name == 'posix':
    LIBRSYNC_DIR = os.environ.get('LIBRSYNC_DIR', '')
    args = sys.argv[:]
    for arg in args:
        if arg.startswith('--librsync-dir='):
            LIBRSYNC_DIR = arg.split('=')[1]
            sys.argv.remove(arg)
    if LIBRSYNC_DIR:
        incdir_list = [os.path.join(LIBRSYNC_DIR, 'include')]
        libdir_list = [os.path.join(LIBRSYNC_DIR, 'lib')]

setup(name="duplicity",
      version=version_string,
      description="Encrypted backup using rsync algorithm",
      author="Ben Escoto",
      author_email="bescoto@stanford.edu",
      maintainer="Kenneth Loafman",
      maintainer_email="kenneth@loafman.com",
      url="http://duplicity.nongnu.org/index.html",
      packages = ['duplicity', 'duplicity.backends'],
      package_dir = {"duplicity" : "src",
                     "duplicity.backends" : "src/backends"},
      ext_modules = [Extension("duplicity._librsync",
                               ["_librsyncmodule.c"],
                               include_dirs=incdir_list,
                               library_dirs=libdir_list,
                               libraries=["rsync"])],
      scripts = ['rdiffdir', 'duplicity'],
      data_files = [('share/man/man1', ['duplicity.1', 'rdiffdir.1']),
                    ('share/doc/duplicity-%s' % version_string,
                     ['COPYING', 'README', 'CHANGELOG'])])



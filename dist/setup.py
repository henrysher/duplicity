#!/usr/bin/env python
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-

import sys, os, getopt
from distutils.core import setup, Extension

version_string = "$version"

if sys.version_info[:2] < (2,3):
    print "Sorry, duplicity requires version 2.3 or later of python"
    sys.exit(1)

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

data_files = [('share/man/man1',
               ['duplicity.1',
                'rdiffdir.1']),
              ('share/doc/duplicity-%s' % version_string,
               ['COPYING',
                'CVS-README',
                'LOG-README',
                'README',
                'tarfile-LICENSE',
                'CHANGELOG']),
              ]

assert os.path.exists("po"), "Missing 'po' directory."
for root, dirs, files in os.walk("po"):
    for file in files:
        path = os.path.join(root, file)
        if path.endswith("duplicity.mo"):
            lang = os.path.split(root)[-1]
            data_files.append(
                ('share/locale/%s/LC_MESSAGES' % lang,
                 ["po/%s/duplicity.mo" % lang]))

setup(name="duplicity",
      version=version_string,
      description="Encrypted backup using rsync algorithm",
      author="Ben Escoto",
      author_email="bescoto@stanford.edu",
      maintainer="Kenneth Loafman",
      maintainer_email="kenneth@loafman.com",
      url="http://duplicity.nongnu.org/index.html",
      packages = ['duplicity',
                  'duplicity.backends',],
      package_dir = {"duplicity" : "src",
                     "duplicity.backends" : "src/backends",},
      ext_modules = [Extension("duplicity._librsync",
                               ["_librsyncmodule.c"],
                               include_dirs=incdir_list,
                               library_dirs=libdir_list,
                               libraries=["rsync"])],
      scripts = ['rdiffdir', 'duplicity'],
      data_files = data_files,
      )

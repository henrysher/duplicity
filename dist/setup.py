#!/usr/bin/env python
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys, os
from distutils.core import setup, Extension

version_string = "$version"

if sys.version_info[:2] < (2,4):
    print "Sorry, duplicity requires version 2.4 or later of python"
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
               ['bin/duplicity.1',
                'bin/rdiffdir.1']),
              ('share/doc/duplicity-%s' % version_string,
               ['COPYING',
                'README',
                'README-REPO',
                'README-LOG',
                'tarfile-LICENSE',
                'tarfile-CHANGES',
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
      author="Ben Escoto <ben@emerose.org>",
      author_email="bescoto@stanford.edu",
      maintainer="Kenneth Loafman <kenneth@loafman.com>",
      maintainer_email="kenneth@loafman.com",
      url="http://duplicity.nongnu.org/index.html",
      packages = ['duplicity',
                  'duplicity.backends',],
      package_dir = {"duplicity" : "duplicity",
                     "duplicity.backends" : "duplicity/backends",},
      ext_modules = [Extension("duplicity._librsync",
                               ["duplicity/_librsyncmodule.c"],
                               include_dirs=incdir_list,
                               library_dirs=libdir_list,
                               libraries=["rsync"])],
      scripts = ['bin/rdiffdir', 'bin/duplicity'],
      data_files = data_files,
      )

# -*- coding: utf-8 -*-
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright © 2009 Larry Gilbert <larry+duplicity@L2G.to>
# Copyright © 2009 Kenneth Loafman <kenneth@loafman.com>
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

import config
import os, py
from subprocess import check_call

def extract_test_files():
    # Darwin (Mac OS X) has its own batch of test files
    if os.uname()[0] == 'Darwin':
        tar_file = 'testfiles-darwin.tar.gz'
    else:
        tar_file = 'testfiles.tar.gz'

    tar_file = os.path.join(config.test_root, tar_file)
    check_call(['tar', 'xzf', tar_file])
    # raises subprocess.CalledProcessError if it fails

def cleanup_test_files():
    for path in ('temp2.tar', 'testfiles', 'tempdir'):
        lpath = py.path.local(path)
        if lpath.check():
            lpath.remove(rec=1)
    return

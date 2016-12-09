# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2012 Canonical Ltd
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

import os
import sys
import time

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from duplicity import backend
from duplicity import globals
from duplicity import log

_testing_dir = os.path.dirname(os.path.abspath(__file__))
_top_dir = os.path.dirname(_testing_dir)
_overrides_dir = os.path.join(_testing_dir, 'overrides')
_bin_dir = os.path.join(_testing_dir, 'overrides', 'bin')

# Adjust python path for duplicity and override modules
sys.path = [_overrides_dir, _top_dir, _bin_dir] + sys.path

# Also set PYTHONPATH for any subprocesses
os.environ['PYTHONPATH'] = _overrides_dir + ":" + _top_dir + ":" + os.environ.get('PYTHONPATH', '')

# And PATH for any subprocesses
os.environ['PATH'] = _bin_dir + ":" + os.environ.get('PATH', '')

# Now set some variables that help standardize test behavior
os.environ['LANG'] = ''
os.environ['GNUPGHOME'] = os.path.join(_testing_dir, 'gnupg')

# Standardize time
os.environ['TZ'] = 'US/Central'
time.tzset()


class DuplicityTestCase(unittest.TestCase):

    sign_key = '839E6A2856538CCF'
    sign_passphrase = 'test'
    encrypt_key1 = '839E6A2856538CCF'
    encrypt_key2 = '453005CE9B736B2A'

    def setUp(self):
        super(DuplicityTestCase, self).setUp()
        self.savedEnviron = {}
        self.savedGlobals = {}

        # TODO: remove these lines
        log.setup()
        log.setverbosity(log.WARNING)
        self.set_global('print_statistics', 0)
        backend.import_backends()

        # Have all file references in tests relative to our testing dir
        os.chdir(_testing_dir)

    def tearDown(self):
        for key in self.savedEnviron:
            self._update_env(key, self.savedEnviron[key])
        for key in self.savedGlobals:
            setattr(globals, key, self.savedGlobals[key])
        assert not os.system("rm -rf testfiles")
        super(DuplicityTestCase, self).tearDown()

    def unpack_testfiles(self):
        assert not os.system("rm -rf testfiles")
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")
        assert not os.system("mkdir testfiles/output testfiles/cache")

    def _update_env(self, key, value):
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

    def set_environ(self, key, value):
        if key not in self.savedEnviron:
            self.savedEnviron[key] = os.environ.get(key)
        self._update_env(key, value)

    def set_global(self, key, value):
        assert hasattr(globals, key)
        if key not in self.savedGlobals:
            self.savedGlobals[key] = getattr(globals, key)
        setattr(globals, key, value)

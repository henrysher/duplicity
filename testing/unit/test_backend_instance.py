# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2014 Canonical Ltd
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
import StringIO
import unittest

import duplicity.backend
from duplicity import log
from duplicity import path
from duplicity.errors import BackendException
from . import UnitTestCase


class BackendInstanceBase(UnitTestCase):

    def setUp(self):
        UnitTestCase.setUp(self)
        assert not os.system("rm -rf testfiles")
        os.makedirs('testfiles')
        self.local = path.Path('testfiles/local')
        self.local.writefileobj(StringIO.StringIO("hello"))

    def tearDown(self):
        if hasattr(self.backend, '_close'):
            self.backend._close()

    def test_get(self):
        self.backend._put(self.local, 'a')
        getfile = path.Path('testfiles/getfile')
        self.backend._get('a', getfile)
        self.assertTrue(self.local.compare_data(getfile))

    def test_list(self):
        self.backend._put(self.local, 'a')
        self.backend._put(self.local, 'b')
        # It's OK for backends to create files as a side effect of put (e.g.
        # the par2 backend does), so only check that at least a and b exist.
        self.assertTrue('a' in self.backend._list())
        self.assertTrue('b' in self.backend._list())

    def test_delete(self):
        if not hasattr(self.backend, '_delete'):
            self.assertTrue(hasattr(self.backend, '_delete_list'))
            return
        self.backend._put(self.local, 'a')
        self.backend._put(self.local, 'b')
        self.backend._delete('a')
        self.assertFalse('a' in self.backend._list())
        self.assertTrue('b' in self.backend._list())

    def test_delete_clean(self):
        if not hasattr(self.backend, '_delete'):
            self.assertTrue(hasattr(self.backend, '_delete_list'))
            return
        self.backend._put(self.local, 'a')
        self.backend._delete('a')
        self.assertEqual(self.backend._list(), [])

    def test_delete_missing(self):
        if not hasattr(self.backend, '_delete'):
            self.assertTrue(hasattr(self.backend, '_delete_list'))
            return
        # Backends can either silently ignore this, or throw an error
        # that gives log.ErrorCode.backend_not_found.
        try:
            self.backend._delete('a')
        except BackendException as e:
            pass  # Something went wrong, but it was an 'expected' something
        except Exception as e:
            code = duplicity.backend._get_code_from_exception(self.backend, e)
            self.assertEqual(code, log.ErrorCode.backend_not_found)

    def test_delete_list(self):
        if not hasattr(self.backend, '_delete_list'):
            self.assertTrue(hasattr(self.backend, '_delete'))
            return
        self.backend._put(self.local, 'a')
        self.backend._put(self.local, 'b')
        self.backend._put(self.local, 'c')
        self.backend._delete_list(['a', 'd', 'c'])
        self.assertFalse('a' in self.backend._list())
        self.assertTrue('b' in self.backend._list())
        self.assertFalse('c' in self.backend._list())

    def test_move(self):
        if not hasattr(self.backend, '_move'):
            return

        copy = path.Path('testfiles/copy')
        self.local.copy(copy)

        self.backend._move(self.local, 'a')
        self.assertTrue('a' in self.backend._list())
        self.assertFalse(self.local.exists())

        getfile = path.Path('testfiles/getfile')
        self.backend._get('a', getfile)
        self.assertTrue(copy.compare_data(getfile))

    def test_query_exists(self):
        if not hasattr(self.backend, '_query'):
            return
        self.backend._put(self.local, 'a')
        info = self.backend._query('a')
        self.assertEqual(info['size'], self.local.getsize())

    def test_query_missing(self):
        if not hasattr(self.backend, '_query'):
            return
        # Backends can either return -1 themselves, or throw an error
        # that gives log.ErrorCode.backend_not_found.
        try:
            info = self.backend._query('a')
        except BackendException as e:
            pass  # Something went wrong, but it was an 'expected' something
        except Exception as e:
            code = duplicity.backend._get_code_from_exception(self.backend, e)
            self.assertEqual(code, log.ErrorCode.backend_not_found)
        else:
            self.assertEqual(info['size'], -1)

    def test_query_list(self):
        if not hasattr(self.backend, '_query_list'):
            return
        self.backend._put(self.local, 'a')
        self.backend._put(self.local, 'c')
        info = self.backend._query_list(['a', 'b'])
        self.assertEqual(info['a']['size'], self.local.getsize())
        self.assertEqual(info['b']['size'], -1)
        self.assertFalse('c' in info)


class LocalBackendTest(BackendInstanceBase):
    def setUp(self):
        super(LocalBackendTest, self).setUp()
        url = 'file://testfiles/output'
        self.backend = duplicity.backend.get_backend_object(url)


class GIOBackendTest(BackendInstanceBase):
    def setUp(self):
        super(GIOBackendTest, self).setUp()
        url = 'gio+file://%s/testfiles/output' % os.getcwd()
        self.backend = duplicity.backend.get_backend_object(url)


class Par2BackendTest(BackendInstanceBase):
    def setUp(self):
        super(Par2BackendTest, self).setUp()
        url = 'par2+file://testfiles/output'
        self.backend = duplicity.backend.get_backend_object(url)

    # TODO: Add par2-specific tests here, to confirm that we can recover from
    # a missing file


class NestedPrefixBackendTest(BackendInstanceBase):
    def setUp(self):
        super(NestedPrefixBackendTest, self).setUp()
        url = 'par2+gio+file://%s/testfiles/output' % os.getcwd()
        self.backend = duplicity.backend.get_backend_object(url)


class RsyncBackendTest(BackendInstanceBase):
    def setUp(self):
        super(RsyncBackendTest, self).setUp()
        os.makedirs('testfiles/output')  # rsync needs it to exist first
        url = 'rsync://%s/testfiles/output' % os.getcwd()
        self.backend = duplicity.backend.get_backend_object(url)


class TahoeBackendTest(BackendInstanceBase):
    def setUp(self):
        super(TahoeBackendTest, self).setUp()
        os.makedirs('testfiles/output')
        url = 'tahoe://testfiles/output'
        self.backend = duplicity.backend.get_backend_object(url)


class HSIBackendTest(BackendInstanceBase):
    def setUp(self):
        super(HSIBackendTest, self).setUp()
        os.makedirs('testfiles/output')
        # hostname is ignored...  Seemingly on purpose
        url = 'hsi://hostname%s/testfiles/output' % os.getcwd()
        self.backend = duplicity.backend.get_backend_object(url)


class FTPBackendTest(BackendInstanceBase):
    def setUp(self):
        super(FTPBackendTest, self).setUp()
        os.makedirs('testfiles/output')
        url = 'ftp://user:pass@hostname/testfiles/output'
        self.backend = duplicity.backend.get_backend_object(url)


class FTPSBackendTest(BackendInstanceBase):
    def setUp(self):
        super(FTPSBackendTest, self).setUp()
        os.makedirs('testfiles/output')
        url = 'ftps://user:pass@hostname/testfiles/output'
        self.backend = duplicity.backend.get_backend_object(url)


# So we don't run tests on the base class itself, remove it from the module
del BackendInstanceBase


if __name__ == "__main__":
    unittest.main()

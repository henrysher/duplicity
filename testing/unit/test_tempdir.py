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

import os
import tempfile
import unittest

from duplicity import tempdir
from . import UnitTestCase


class TempDirTest(UnitTestCase):
    def test_all(self):
        td = tempdir.default()

        # are generated temp files unique?
        self.assertTrue(td.mktemp() != td.mktemp())

        # create and remove a temp dir
        dir = td.mktemp()
        os.mkdir(dir)
        os.rmdir(dir)

        # test mkstemp()
        fd, fname = td.mkstemp()
        os.close(fd)
        os.unlink(fname)
        td.forget(fname)

        # test mkstemp_file()
        fo, fname = td.mkstemp_file()
        fo.close()  # don't forget, leave to cleanup()

        # cleanup
        td.cleanup()

    def test_dirname(self):
        """
        test if we generated a dirname
        """
        td = tempdir.default()
        dirname = td.dir()
        self.assertTrue( dirname is not None )

        """
        test if duplicity's temp files are created in our temp dir
        """
        f1d, f1_name = tempdir.default().mkstemp()
        f1_dirname = os.path.dirname( f1_name )

        self.assertTrue( dirname == f1_dirname )

        """
        test if tempfile creates in our temp dir now as well by default
        """
        f2 = tempfile.NamedTemporaryFile()
        f2_dirname = os.path.dirname( f2.name )

        self.assertTrue( dirname == f2_dirname )

        # cleanup
        os.close(f1d)
        os.unlink(f1_name)
        td.forget(f1_name)
        f2.close()

        td.cleanup()

if __name__ == "__main__":
    unittest.main()

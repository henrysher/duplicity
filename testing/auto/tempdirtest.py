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

import helper
import sys, os, unittest

from duplicity import tempdir

helper.setup()

class TempDirTest(unittest.TestCase):
    def test_all(self):
        td = tempdir.default()

        self.assert_(td.mktemp() != td.mktemp())

        dir = td.mktemp()
        os.mkdir(dir)
        os.rmdir(dir)

        fd, fname = td.mkstemp()
        os.close(fd)
        os.unlink(fname)
        td.forget(fname)

        fo, fname = td.mkstemp_file()
        fo.close() # don't forget, leave to cleanup()

        td.cleanup()

if __name__ == "__main__":
    unittest.main()


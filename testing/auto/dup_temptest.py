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
import sys, os, unittest, gzip

from duplicity import dup_temp
from duplicity import file_naming

helper.setup()

prefix = "testfiles/output"

class TempTest(unittest.TestCase):
    """Test various temp files methods"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def del_tmp(self):
        """Delete testfiles/output and recreate"""
        assert not os.system("rm -rf " + prefix)
        assert not os.system("mkdir " + prefix)

    def test_temppath(self):
        """Allocate new temppath, try open_with_delete"""
        tp = dup_temp.new_temppath()
        assert not tp.exists()
        fileobj = tp.open("wb")
        fileobj.write("hello, there")
        fileobj.close()
        tp.setdata()
        assert tp.isreg()

        fin = tp.open_with_delete("rb")
        buf = fin.read()
        assert buf == "hello, there", buf
        fin.close()
        assert not tp.exists()

    def test_tempduppath(self):
        """Allocate new tempduppath, then open_with_delete"""
        # pr indicates file is gzipped
        pr = file_naming.ParseResults("inc", manifest = 1,
                                      start_time = 1, end_time = 3,
                                      compressed = 1)

        tdp = dup_temp.new_tempduppath(pr)
        assert not tdp.exists()
        fout = tdp.filtered_open("wb")
        fout.write("hello, there")
        fout.close()
        tdp.setdata()
        assert tdp.isreg()

        fin1 = gzip.GzipFile(tdp.name, "rb")
        buf = fin1.read()
        assert buf == "hello, there", buf
        fin1.close()

        fin2 = tdp.filtered_open_with_delete("rb")
        buf2 = fin2.read()
        assert buf2 == "hello, there", buf
        fin2.close()
        assert not tdp.exists()


if __name__ == "__main__":
    unittest.main()

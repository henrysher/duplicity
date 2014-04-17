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
import sys, os, unittest, cStringIO

from duplicity import misc

helper.setup()

class MiscTest(unittest.TestCase):
    """Test functions/classes in misc.py"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def deltmp(self):
        assert not os.system("rm -rf testfiles/output")
        os.mkdir("testfiles/output")

    def test_file_volume_writer(self):
        """Test FileVolumeWriter class"""
        self.deltmp()
        s = "hello" * 10000
        assert len(s) == 50000
        infp = cStringIO.StringIO(s)
        fvw = misc.FileVolumeWriter(infp, "testfiles/output/volume")
        fvw.volume_size = 20000
        fvw.blocksize = 5000

        l = []
        for filename in fvw: l.append(filename)
        assert l == ['testfiles/output/volume.1',
                     'testfiles/output/volume.2',
                     'testfiles/output/volume.3'], l

        s2 = ""
        for filename in l:
            infp2 = open(filename, "rb")
            s2 += infp2.read()
            assert not infp2.close()

        assert s2 == s

    def test_file_volume_writer2(self):
        """Test again but one volume this time"""
        self.deltmp()
        fvw = misc.FileVolumeWriter(cStringIO.StringIO("hello, world!"),
                                    "testfiles/output/one_vol")
        assert fvw.next() == "testfiles/output/one_vol"
        self.assertRaises(StopIteration, fvw.next)

    def test_file_volume_writer3(self):
        """Test case when end of file falls exactly on volume boundary"""
        self.deltmp()
        s = "hello" * 10000
        assert len(s) == 50000
        infp = cStringIO.StringIO(s)
        fvw = misc.FileVolumeWriter(infp, "testfiles/output/volume")
        fvw.volume_size = 25000
        fvw.blocksize = 5000

        l = []
        for filename in fvw: l.append(filename)
        assert l == ['testfiles/output/volume.1',
                     'testfiles/output/volume.2']



if __name__ == "__main__":
    unittest.main()

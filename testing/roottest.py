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

import config
import sys, os, unittest
sys.path.insert(0, "../")

from duplicity import diffdir
from duplicity import patchdir
from duplicity import selection
from duplicity.path import *

config.setup()

class RootTest(unittest.TestCase):
    """Test doing operations that only root can"""

    def setUp(self):
        # must run with euid/egid of root
        assert(os.geteuid() == 0)
        # make sure uid/gid match euid/egid
        os.setuid(os.geteuid())
        os.setgid(os.getegid())
        assert not os.system("tar xzf testfiles.tar.gz >& /dev/null")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def copyfileobj(self, infp, outfp):
        """Copy in fileobj to out, closing afterwards"""
        blocksize = 32 * 1024
        while 1:
            buf = infp.read(blocksize)
            if not buf: break
            outfp.write(buf)
        assert not infp.close()
        assert not outfp.close()

    def deltmp(self):
        """Delete temporary directories"""
        assert not os.system("rm -rf testfiles/output")
        os.mkdir("testfiles/output")

    def total_sequence(self, filelist):
        """Test signatures, diffing, and patching on directory list"""
        assert len(filelist) >= 2
        self.deltmp()
        assert not os.system("cp -pR %s testfiles/output/sequence" %
                             (filelist[0],))
        seq_path = Path("testfiles/output/sequence")
        sig = Path("testfiles/output/sig.tar")
        diff = Path("testfiles/output/diff.tar")
        for dirname in filelist[1:]:
            new_path = Path(dirname)
            diffdir.write_block_iter(
                diffdir.DirSig(selection.Select(seq_path).set_iter()), sig)

            diffdir.write_block_iter(
                diffdir.DirDelta(selection.Select(new_path).set_iter(),
                                 sig.open("rb")),
                diff)

            patchdir.Patch(seq_path, diff.open("rb"))

            assert seq_path.compare_recursive(new_path, 1)

    def test_basic_cycle(self):
        """Test cycle on dir with devices, changing uid/gid, etc."""
        self.total_sequence(['testfiles/root1', 'testfiles/root2'])

def runtests(): unittest.main()

if __name__ == "__main__":
    unittest.main()

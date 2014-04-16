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
import sys, unittest, os

from duplicity import path

helper.setup()

class RdiffdirTest(unittest.TestCase):
    """Test rdiffdir command line program"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def run_cmd(self, command):
        assert not os.system(command)

    def del_tmp(self):
        """Make new testfiles/output dir"""
        self.run_cmd("rm -rf testfiles/output")
        os.mkdir("testfiles/output")

    def run_rdiffdir(self, argstring):
        """Run rdiffdir with given arguments"""
        self.run_cmd("rdiffdir " + argstring)

    def run_cycle(self, dirname_list):
        """Run diff/patch cycle on directories in dirname_list"""
        assert len(dirname_list) >= 2
        self.del_tmp()

        seq_path = path.Path("testfiles/output/sequence")
        new_path = path.Path(dirname_list[0])
        delta_path = path.Path("testfiles/output/delta.tar")
        sig_path = path.Path("testfiles/output/sig.tar")

        self.run_cmd("cp -pR %s %s" % (new_path.name, seq_path.name))
        seq_path.setdata()
        self.run_rdiffdir("sig %s %s" % (seq_path.name, sig_path.name))
        sig_path.setdata()
        assert sig_path.exists()

        # FIXME: How does this work?  Path comparisons don't seem to work right
        #assert new_path.compare_recursive(seq_path, verbose = 1)

        for dirname in dirname_list[1:]:
            new_path = path.Path(dirname)

            # Make delta
            if delta_path.exists(): delta_path.delete()
            assert not delta_path.exists()
            self.run_rdiffdir("delta %s %s %s" %
                              (sig_path.name, new_path.name, delta_path.name))
            delta_path.setdata()
            assert delta_path.exists()

            # patch and compare
            self.run_rdiffdir("patch %s %s" % (seq_path.name, delta_path.name))
            seq_path.setdata()
            new_path.setdata()
            assert new_path.compare_recursive(seq_path, verbose = 1)

            # Make new signature
            sig_path.delete()
            assert not sig_path.exists()
            self.run_rdiffdir("sig %s %s" % (seq_path.name, sig_path.name))
            sig_path.setdata()
            assert sig_path.isreg()

    def test_dirx(self):
        """Test cycle on testfiles/dirx"""
        self.run_cycle(['testfiles/empty_dir',
                        'testfiles/dir1',
                        'testfiles/dir2',
                        'testfiles/dir3',
                        'testfiles/empty_dir'])


if __name__ == "__main__":
    unittest.main()

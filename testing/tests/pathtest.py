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
import sys, unittest

from duplicity import log #@UnusedImport
from duplicity.path import * #@UnusedWildImport

helper.setup()

class PathTest(unittest.TestCase):
    """Test basic path functions"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def test_deltree(self):
        """Test deleting a tree"""
        assert not os.system("rm -rf testfiles/output")
        assert not os.system("cp -pR testfiles/deltree testfiles/output")
        p = Path("testfiles/output")
        assert p.isdir()
        p.deltree()
        assert not p.type, p.type

    # FIXME: How does this test make any sense?  Two separate Path objects 
    # will never be equal (they don't implement __cmp__ or __eq__)
    #def test_compare(self):
    #    """Test directory comparisons"""
    #    assert not os.system("rm -rf testfiles/output")
    #    assert not os.system("cp -pR testfiles/dir1 testfiles/output")
    #    assert Path("testfiles/dir1").compare_recursive(Path("testfiles/output"), 1)
    #    assert not Path("testfiles/dir1").compare_recursive(Path("testfiles/dir2"), 1)

    def test_quote(self):
        """Test path quoting"""
        p = Path("hello")
        assert p.quote() == '"hello"'
        assert p.quote("\\") == '"\\\\"', p.quote("\\")
        assert p.quote("$HELLO") == '"\\$HELLO"'

    def test_unquote(self):
        """Test path unquoting"""
        p = Path("foo") # just to provide unquote function
        def t(s):
            """Run test on string s"""
            quoted_version = p.quote(s)
            unquoted = p.unquote(quoted_version)
            assert unquoted == s, (unquoted, s)

        t("\\")
        t("$HELLO")
        t(" aoe aoe \\ \n`")

    def test_canonical(self):
        """Test getting canonical version of path"""
        c = Path(".").get_canonical()
        assert c == ".", c

        c = Path("//foo/bar/./").get_canonical()
        assert c == "/foo/bar", c

    def test_compare_verbose(self):
        """Run compare_verbose on a few files"""
        vft = Path("testfiles/various_file_types")
        assert vft.compare_verbose(vft)
        reg_file = vft.append("regular_file")
        assert not vft.compare_verbose(reg_file)
        assert reg_file.compare_verbose(reg_file)
        file2 = vft.append("executable")
        assert not file2.compare_verbose(reg_file)
        assert file2.compare_verbose(file2)


if __name__ == "__main__":
    unittest.main()

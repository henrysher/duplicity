# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2014 Aaron Whitehouse <aaron@whitehouse.kiwi.nz>
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

import types
import StringIO
import unittest
import duplicity.path

from duplicity.selection import *  # @UnusedWildImport
from duplicity.lazy import *  # @UnusedWildImport
from . import UnitTestCase
from mock import patch


class MatchingTest(UnitTestCase):
    """Test matching of file names against various selection functions"""
    def setUp(self):
        super(MatchingTest, self).setUp()
        self.unpack_testfiles()
        self.root = Path(u"testfiles/select")
        self.Select = Select(self.root)

    def makeext(self, path):
        return self.root.new_index(tuple(path.split(u"/")))

    def testRegexp(self):
        """Test regular expression selection func"""
        sf1 = self.Select.regexp_get_sf(u".*\.py", 1)
        assert sf1(self.makeext(u"1.py")) == 1
        assert sf1(self.makeext(u"usr/foo.py")) == 1
        assert sf1(self.root.append(u"1.doc")) is None

        sf2 = self.Select.regexp_get_sf(u"hello", 0)
        assert sf2(Path(u"hello")) == 0
        assert sf2(Path(u"foohello_there")) == 0
        assert sf2(Path(u"foo")) is None

    def test_tuple_include(self):
        """Test include selection function made from a regular filename"""
        self.assertRaises(FilePrefixError, self.Select.glob_get_normal_sf,
                          u"foo", 1)

        sf2 = self.Select.glob_get_sf(u"testfiles/select/usr/local/bin/", 1)

        with patch(u"duplicity.path.ROPath.isdir") as mock_isdir:
            mock_isdir.return_value = True
            # Can't pass the return_value as an argument to patch, i.e.:
            # with patch("duplicity.path.ROPath.isdir", return_value=True):
            # as build system's mock is too old to support it.

            self.assertEqual(sf2(self.makeext(u"usr")), 2)
            self.assertEqual(sf2(self.makeext(u"usr/local")), 2)
            self.assertEqual(sf2(self.makeext(u"usr/local/bin")), 1)
            self.assertEqual(sf2(self.makeext(u"usr/local/doc")), None)
            self.assertEqual(sf2(self.makeext(u"usr/local/bin/gzip")), 1)
            self.assertEqual(sf2(self.makeext(u"usr/local/bingzip")), None)

    def test_tuple_exclude(self):
        """Test exclude selection function made from a regular filename"""
        self.assertRaises(FilePrefixError, self.Select.glob_get_normal_sf,
                          u"foo", 0)

        sf2 = self.Select.glob_get_sf(u"testfiles/select/usr/local/bin/", 0)

        with patch(u"duplicity.path.ROPath.isdir") as mock_isdir:
            mock_isdir.return_value = True

            assert sf2(self.makeext(u"usr")) is None
            assert sf2(self.makeext(u"usr/local")) is None
            assert sf2(self.makeext(u"usr/local/bin")) == 0
            assert sf2(self.makeext(u"usr/local/doc")) is None
            assert sf2(self.makeext(u"usr/local/bin/gzip")) == 0
            assert sf2(self.makeext(u"usr/local/bingzip")) is None

    def test_glob_star_include(self):
        """Test a few globbing patterns, including **"""
        sf1 = self.Select.glob_get_sf(u"**", 1)
        assert sf1(self.makeext(u"foo")) == 1
        assert sf1(self.makeext(u"")) == 1

        sf2 = self.Select.glob_get_sf(u"**.py", 1)
        assert sf2(self.makeext(u"foo")) == 2
        assert sf2(self.makeext(u"usr/local/bin")) == 2
        assert sf2(self.makeext(u"what/ever.py")) == 1
        assert sf2(self.makeext(u"what/ever.py/foo")) == 1

    def test_glob_star_exclude(self):
        """Test a few glob excludes, including **"""
        sf1 = self.Select.glob_get_sf(u"**", 0)
        assert sf1(self.makeext(u"/usr/local/bin")) == 0

        sf2 = self.Select.glob_get_sf(u"**.py", 0)
        assert sf2(self.makeext(u"foo")) is None
        assert sf2(self.makeext(u"usr/local/bin")) is None
        assert sf2(self.makeext(u"what/ever.py")) == 0
        assert sf2(self.makeext(u"what/ever.py/foo")) == 0

    def test_simple_glob_double_asterisk(self):
        """test_simple_glob_double_asterisk - primarily to check that the defaults used by the error tests work"""
        assert self.Select.glob_get_normal_sf(u"**", 1)

    def test_glob_sf_exception(self):
        """test_glob_sf_exception - see if globbing errors returned"""
        self.assertRaises(GlobbingError, self.Select.glob_get_normal_sf,
                          u"testfiles/select/hello//there", 1)

    def test_file_prefix_sf_exception(self):
        """test_file_prefix_sf_exception - see if FilePrefix error is returned"""
        # These should raise a FilePrefixError because the root directory for the selection is "testfiles/select"
        self.assertRaises(FilePrefixError,
                          self.Select.glob_get_sf, u"testfiles/whatever", 1)
        self.assertRaises(FilePrefixError,
                          self.Select.glob_get_sf, u"testfiles/?hello", 0)

    def test_scan(self):
        """Tests what is returned for selection tests regarding directory scanning"""
        select = Select(Path(u"/"))

        assert select.glob_get_sf(u"**.py", 1)(Path(u"/")) == 2
        assert select.glob_get_sf(u"**.py", 1)(Path(u"foo")) == 2
        assert select.glob_get_sf(u"**.py", 1)(Path(u"usr/local/bin")) == 2
        assert select.glob_get_sf(u"/testfiles/select/**.py", 1)(Path(u"/testfiles/select")) == 2
        assert select.glob_get_sf(u"/testfiles/select/test.py", 1)(Path(u"/testfiles/select")) == 2
        assert select.glob_get_normal_sf(u"/testfiles/se?ect/test.py", 1)(Path(u"/testfiles/select")) == 2
        assert select.glob_get_sf(u"/testfiles/select/test.py", 0)(Path(u"/testfiles/select")) is None
        assert select.glob_get_normal_sf(u"/testfiles/select/test.py", 0)(Path(u"/testfiles/select")) is None

    def test_ignore_case(self):
        """test_ignore_case - try a few expressions with ignorecase:"""

        sf = self.Select.glob_get_sf(u"ignorecase:testfiles/SeLect/foo/bar", 1)
        assert sf(self.makeext(u"FOO/BAR")) == 1
        assert sf(self.makeext(u"foo/bar")) == 1
        assert sf(self.makeext(u"fOo/BaR")) == 1
        self.assertRaises(FilePrefixError, self.Select.glob_get_sf, u"ignorecase:tesfiles/sect/foo/bar", 1)

    def test_root(self):
        """test_root - / may be a counterexample to several of these.."""
        root = Path(u"/")
        select = Select(root)

        self.assertEqual(select.glob_get_sf(u"/", 1)(root), 1)
        self.assertEqual(select.glob_get_sf(u"/foo", 1)(root), 2)
        self.assertEqual(select.glob_get_sf(u"/foo/bar", 1)(root), 2)
        self.assertEqual(select.glob_get_sf(u"/", 0)(root), 0)
        self.assertEqual(select.glob_get_sf(u"/foo", 0)(root), None)

        assert select.glob_get_sf(u"**.py", 1)(root) == 2
        assert select.glob_get_sf(u"**", 1)(root) == 1
        assert select.glob_get_sf(u"ignorecase:/", 1)(root) == 1
        assert select.glob_get_sf(u"**.py", 0)(root) is None
        assert select.glob_get_sf(u"**", 0)(root) == 0
        assert select.glob_get_sf(u"/foo/*", 0)(root) is None

    def test_other_filesystems(self):
        """Test to see if --exclude-other-filesystems works correctly"""
        root = Path(u"/")
        select = Select(root)
        sf = select.other_filesystems_get_sf(0)
        assert sf(root) is None
        if os.path.ismount(u"/usr/bin"):
            sfval = 0
        else:
            sfval = None
        assert sf(Path(u"/usr/bin")) == sfval, \
            u"Assumption: /usr/bin is on the same filesystem as /"
        if os.path.ismount(u"/dev"):
            sfval = 0
        else:
            sfval = None
        assert sf(Path(u"/dev")) == sfval, \
            u"Assumption: /dev is on a different filesystem"
        if os.path.ismount(u"/proc"):
            sfval = 0
        else:
            sfval = None
        assert sf(Path(u"/proc")) == sfval, \
            u"Assumption: /proc is on a different filesystem"


class ParseArgsTest(UnitTestCase):
    """Test argument parsing"""
    def setUp(self):
        super(ParseArgsTest, self).setUp()
        self.unpack_testfiles()
        self.root = None
        self.expected_restored_tree = [(), (u"1",), (u"1", u"1sub1"), (u"1", u"1sub1", u"1sub1sub1"),
                                       (u"1", u"1sub1", u"1sub1sub1", u"1sub1sub1_file.txt"),
                                       (u"1", u"1sub1", u"1sub1sub3"), (u"1", u"1sub2"), (u"1", u"1sub2", u"1sub2sub1"),
                                       (u"1", u"1sub3"), (u"1", u"1sub3", u"1sub3sub3"), (u"1.py",), (u"2",),
                                       (u"2", u"2sub1"), (u"2", u"2sub1", u"2sub1sub1"),
                                       (u"2", u"2sub1", u"2sub1sub1", u"2sub1sub1_file.txt"),
                                       (u"3",), (u"3", u"3sub2"), (u"3", u"3sub2", u"3sub2sub1"),
                                       (u"3", u"3sub2", u"3sub2sub2"), (u"3", u"3sub2", u"3sub2sub3"), (u"3", u"3sub3"),
                                       (u"3", u"3sub3", u"3sub3sub1"), (u"3", u"3sub3", u"3sub3sub2"),
                                       (u"3", u"3sub3", u"3sub3sub2", u"3sub3sub2_file.txt"),
                                       (u"3", u"3sub3", u"3sub3sub3")]

    def ParseTest(self, tuplelist, indicies, filelists=[]):
        """No error if running select on tuple goes over indicies"""
        if not self.root:
            self.root = Path(u"testfiles/select")
        self.Select = Select(self.root)
        self.Select.ParseArgs(tuplelist, self.remake_filelists(filelists))
        self.Select.set_iter()
        results_as_list = list(Iter.map(lambda path: path.index, self.Select))
        # print(results_as_list)
        self.assertEqual(indicies, results_as_list)

    def remake_filelists(self, filelist):
        """Turn strings in filelist into fileobjs"""
        new_filelists = []
        for f in filelist:
            if isinstance(f, unicode):
                new_filelists.append(StringIO.StringIO(f))
            else:
                new_filelists.append(f)
        return new_filelists

    def test_parse(self):
        """Test just one include, all exclude"""
        self.ParseTest([(u"--include", u"testfiles/select/1/1"),
                        (u"--exclude", u"**")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"1"),
                        (u"1", u"1", u"2"), (u"1", u"1", u"3")])

    def test_parse2(self):
        """Test three level include/exclude"""
        self.ParseTest([(u"--exclude", u"testfiles/select/1/1/1"),
                        (u"--include", u"testfiles/select/1/1"),
                        (u"--exclude", u"testfiles/select/1"),
                        (u"--exclude", u"**")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")])

    def test_filelist(self):
        """Filelist glob test similar to above testParse2"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_1_trailing_whitespace(self):
        """Filelist glob test similar to globbing filelist, but with 1 trailing whitespace on include"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"testfiles/select/1/1 \n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_2_trailing_whitespaces(self):
        """Filelist glob test similar to globbing filelist, but with 2 trailing whitespaces on include"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"testfiles/select/1/1  \n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_1_leading_whitespace(self):
        """Filelist glob test similar to globbing filelist, but with 1 leading whitespace on include"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u" testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_2_leading_whitespaces(self):
        """Filelist glob test similar to globbing filelist, but with 2 leading whitespaces on include"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"  testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_1_trailing_whitespace_exclude(self):
        """Filelist glob test similar to globbing filelist, but with 1 trailing whitespace on exclude"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1 \n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_2_trailing_whitespace_exclude(self):
        """Filelist glob test similar to globbing filelist, but with 2 trailing whitespaces on exclude"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1  \n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_1_leading_whitespace_exclude(self):
        """Filelist glob test similar to globbing filelist, but with 1 leading whitespace on exclude"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u" - testfiles/select/1/1/1\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_2_leading_whitespaces_exclude(self):
        """Filelist glob test similar to globbing filelist, but with 2 leading whitespaces on exclude"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"  - testfiles/select/1/1/1\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_check_excluded_folder_included_for_contents(self):
        """Filelist glob test to check excluded folder is included if contents are"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3"), (u"1", u"2"), (u"1", u"2", u"1"), (u"1", u"3"), (u"1", u"3", u"1"),
                        (u"1", u"3", u"2"), (u"1", u"3", u"3")],
                       [u"+ testfiles/select/1/2/1\n"
                        u"- testfiles/select/1/2\n"
                        u"testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_with_unnecessary_quotes(self):
        """Filelist glob test similar to globbing filelist, but with quotes around one of the paths."""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- 'testfiles/select/1/1/1'\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_with_unnecessary_double_quotes(self):
        """Filelist glob test similar to globbing filelist, but with double quotes around one of the paths."""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u'- "testfiles/select/1/1/1"\n'
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_with_full_line_comment(self):
        """Filelist glob test similar to globbing filelist, but with a full-line comment."""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"# This is a test\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_with_blank_line(self):
        """Filelist glob test similar to globbing filelist, but with a blank line."""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_with_blank_line_and_whitespace(self):
        """Filelist glob test similar to globbing filelist, but with a blank line and whitespace."""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"  \n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_asterisk(self):
        """Filelist glob test with * instead of 'testfiles'"""
        # Thank you to Elifarley Cruz for this test case
        # (https://bugs.launchpad.net/duplicity/+bug/884371).
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"1"),
                        (u"1", u"1", u"2"), (u"1", u"1", u"3")],
                       [u"*/select/1/1\n"
                        u"- **"])

    def test_include_filelist_asterisk_2(self):
        """Identical to test_filelist, but with the exclude "select" replaced with '*'"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/*/1/1/1\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_asterisk_3(self):
        """Identical to test_filelist, but with the auto-include "select" replaced with '*'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"testfiles/*/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_asterisk_4(self):
        """Identical to test_filelist, but with a specific include "select" replaced with '*'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"+ testfiles/*/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_asterisk_5(self):
        """Identical to test_filelist, but with all 'select's replaced with '*'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/*/1/1/1\n"
                        u"+ testfiles/*/1/1\n"
                        u"- testfiles/*/1\n"
                        u"- **"])

    def test_include_filelist_asterisk_6(self):
        """Identical to test_filelist, but with numerous excluded folders replaced with '*'"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- */*/1/1/1\n"
                        u"+ testfiles/select/1/1\n"
                        u"- */*/1\n"
                        u"- **"])

    def test_include_filelist_asterisk_7(self):
        """Identical to test_filelist, but with numerous included/excluded folders replaced with '*'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- */*/1/1/1\n"
                        u"+ */*/1/1\n"
                        u"- */*/1\n"
                        u"- **"])

    def test_include_filelist_double_asterisk_1(self):
        """Identical to test_filelist, but with the exclude "select' replaced with '**'"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/**/1/1/1\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_double_asterisk_2(self):
        """Identical to test_filelist, but with the include 'select' replaced with '**'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"**ct/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_double_asterisk_3(self):
        """Identical to test_filelist, but with the exclude 'testfiles/select' replaced with '**'"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- **/1/1/1\n"
                        u"testfiles/select/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_double_asterisk_4(self):
        """Identical to test_filelist, but with the include 'testfiles/select' replaced with '**'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1\n"
                        u"**t/1/1\n"
                        u"- testfiles/select/1\n"
                        u"- **"])

    def test_include_filelist_double_asterisk_5(self):
        """Identical to test_filelist, but with all 'testfiles/select's replaced with '**'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- **/1/1/1\n"
                        u"**t/1/1\n"
                        u"- **t/1\n"
                        u"- **"])

    def test_include_filelist_trailing_slashes(self):
        """Filelist glob test similar to globbing filelist, but with trailing slashes"""
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- testfiles/select/1/1/1/\n"
                        u"testfiles/select/1/1/\n"
                        u"- testfiles/select/1/\n"
                        u"- **"])

    def test_include_filelist_trailing_slashes_and_single_asterisks(self):
        """Filelist glob test similar to globbing filelist, but with trailing slashes and single asterisks"""
        # Regression test for Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- */select/1/1/1/\n"
                        u"testfiles/select/1/1/\n"
                        u"- testfiles/*/1/\n"
                        u"- **"])

    def test_include_filelist_trailing_slashes_and_double_asterisks(self):
        """Filelist glob test similar to globbing filelist, but with trailing slashes and double asterisks"""
        # Regression test for Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"- **/1/1/1/\n"
                        u"testfiles/select/1/1/\n"
                        u"- **t/1/\n"
                        u"- **"])

    def test_filelist_null_separator(self):
        """test_filelist, but with null_separator set"""
        self.set_global(u"null_separator", 1)
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"\0- testfiles/select/1/1/1\0testfiles/select/1/1\0- testfiles/select/1\0- **\0"])

    def test_exclude_filelist(self):
        """Exclude version of test_filelist"""
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"testfiles/select/1/1/1\n"
                        u"+ testfiles/select/1/1\n"
                        u"testfiles/select/1\n"
                        u"- **"])

    def test_exclude_filelist_asterisk_1(self):
        """Exclude version of test_include_filelist_asterisk"""
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"1"),
                        (u"1", u"1", u"2"), (u"1", u"1", u"3")],
                       [u"+ */select/1/1\n"
                        u"- **"])

    def test_exclude_filelist_asterisk_2(self):
        """Identical to test_exclude_filelist, but with the exclude "select" replaced with '*'"""
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"1",), (u"1", "1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"testfiles/*/1/1/1\n"
                        u"+ testfiles/select/1/1\n"
                        u"testfiles/select/1\n"
                        u"- **"])

    def test_exclude_filelist_asterisk_3(self):
        """Identical to test_exclude_filelist, but with the include "select" replaced with '*'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"testfiles/select/1/1/1\n"
                        u"+ testfiles/*/1/1\n"
                        u"testfiles/select/1\n"
                        u"- **"])

    def test_exclude_filelist_asterisk_4(self):
        """Identical to test_exclude_filelist, but with numerous excluded folders replaced with '*'"""
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"*/select/1/1/1\n"
                        u"+ testfiles/select/1/1\n"
                        u"*/*/1\n"
                        u"- **"])

    def test_exclude_filelist_asterisk_5(self):
        """Identical to test_exclude_filelist, but with numerous included/excluded folders replaced with '*'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"*/select/1/1/1\n"
                        u"+ */*/1/1\n"
                        u"*/*/1\n"
                        u"- **"])

    def test_exclude_filelist_double_asterisk(self):
        """Identical to test_exclude_filelist, but with all included/excluded folders replaced with '**'"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"1", u"3")],
                       [u"**/1/1/1\n"
                        u"+ **t/1/1\n"
                        u"**t/1\n"
                        u"- **"])

    def test_exclude_filelist_single_asterisk_at_beginning(self):
        """Exclude filelist testing limited functionality of functional test"""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.root = Path(u"testfiles/select/1")
        self.ParseTest([(u"--exclude-filelist", u"file")],
                       [(), (u"2",), (u"2", u"1")],
                       [u"+ */select/1/2/1\n"
                        u"- testfiles/select/1/2\n"
                        u"- testfiles/*/1/1\n"
                        u"- testfiles/select/1/3"])

    def test_commandline_asterisks_double_both(self):
        """Unit test the functional test TestAsterisks.test_commandline_asterisks_double_both"""
        self.root = Path(u"testfiles/select/1")
        self.ParseTest([(u"--include", u"**/1/2/1"),
                        (u"--exclude", u"**t/1/2"),
                        (u"--exclude", u"**t/1/1"),
                        (u"--exclude", u"**t/1/3")],
                       [(), (u"2",), (u"2", u"1")])

    def test_includes_files(self):
        """Unit test the functional test test_includes_files"""
        # Test for Bug 1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        self.root = Path(u"testfiles/select2/1/1sub1")
        self.ParseTest([(u"--include", u"testfiles/select2/1/1sub1/1sub1sub1"),
                        (u"--exclude", u"**")],
                       [(), (u"1sub1sub1",), (u"1sub1sub1",
                                             u"1sub1sub1_file.txt")])

    def test_includes_files_trailing_slash(self):
        """Unit test the functional test test_includes_files_trailing_slash"""
        # Test for Bug 1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        self.root = Path(u"testfiles/select2/1/1sub1")
        self.ParseTest([(u"--include", u"testfiles/select2/1/1sub1/1sub1sub1/"),
                        (u"--exclude", u"**")],
                       [(), (u"1sub1sub1",), (u"1sub1sub1",
                                             u"1sub1sub1_file.txt")])

    def test_includes_files_trailing_slash_globbing_chars(self):
        """Unit test functional test_includes_files_trailing_slash_globbing_chars"""
        # Test for Bug 1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        self.root = Path(u"testfiles/select2/1/1sub1")
        self.ParseTest([(u"--include", u"testfiles/s?lect2/1/1sub1/1sub1sub1/"),
                        (u"--exclude", u"**")],
                       [(), (u"1sub1sub1",), (u"1sub1sub1",
                                             u"1sub1sub1_file.txt")])

    def test_glob(self):
        """Test globbing expression"""
        self.ParseTest([(u"--exclude", u"**[3-5]"),
                        (u"--include", u"testfiles/select/1"),
                        (u"--exclude", u"**")],
                       [(), (u"1",), (u"1", u"1"),
                        (u"1", u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"2"), (u"1", u"2", u"1"), (u"1", u"2", u"2")])
        self.ParseTest([(u"--include", u"testfiles/select**/2"),
                        (u"--exclude", u"**")],
                       [(), (u"1",), (u"1", u"1"),
                        (u"1", u"1", u"2"),
                        (u"1", u"2"),
                        (u"1", u"2", u"1"), (u"1", u"2", u"2"), (u"1", u"2", u"3"),
                        (u"1", u"3"),
                        (u"1", u"3", u"2"),
                        (u"2",), (u"2", u"1"),
                        (u"2", u"1", u"1"), (u"2", u"1", u"2"), (u"2", u"1", u"3"),
                        (u"2", u"2"),
                        (u"2", u"2", u"1"), (u"2", u"2", u"2"), (u"2", u"2", u"3"),
                        (u"2", u"3"),
                        (u"2", u"3", u"1"), (u"2", u"3", u"2"), (u"2", u"3", u"3"),
                        (u"3",), (u"3", u"1"),
                        (u"3", u"1", u"2"),
                        (u"3", u"2"),
                        (u"3", u"2", u"1"), (u"3", u"2", u"2"), (u"3", u"2", u"3"),
                        (u"3", u"3"),
                        (u"3", u"3", u"2")])

    def test_filelist2(self):
        """Filelist glob test similar to above testGlob"""
        self.ParseTest([(u"--exclude-filelist", u"asoeuth")],
                       [(), (u"1",), (u"1", u"1"),
                        (u"1", u"1", u"1"), (u"1", u"1", u"2"),
                        (u"1", u"2"), (u"1", u"2", u"1"), (u"1", u"2", u"2")],
                       [u"""
**[3-5]
+ testfiles/select/1
**
"""])
        self.ParseTest([(u"--include-filelist", u"file")],
                       [(), (u"1",), (u"1", u"1"),
                        (u"1", u"1", u"2"),
                        (u"1", u"2"),
                        (u"1", u"2", u"1"), (u"1", u"2", u"2"), (u"1", u"2", u"3"),
                        (u"1", u"3"),
                        (u"1", u"3", u"2"),
                        (u"2",), (u"2", u"1"),
                        (u"2", u"1", u"1"), (u"2", u"1", u"2"), (u"2", u"1", u"3"),
                        (u"2", u"2"),
                        (u"2", u"2", u"1"), (u"2", u"2", u"2"), (u"2", u"2", u"3"),
                        (u"2", u"3"),
                        (u"2", u"3", u"1"), (u"2", u"3", u"2"), (u"2", u"3", u"3"),
                        (u"3",), (u"3", u"1"),
                        (u"3", u"1", u"2"),
                        (u"3", u"2"),
                        (u"3", u"2", u"1"), (u"3", u"2", u"2"), (u"3", u"2", u"3"),
                        (u"3", u"3"),
                        (u"3", u"3", u"2")],
                       [u"""
testfiles/select**/2
- **
"""])

    def test_glob2(self):
        """Test more globbing functions"""
        self.ParseTest([(u"--include", u"testfiles/select/*foo*/p*"),
                        (u"--exclude", u"**")],
                       [(), (u"efools",), (u"efools", u"ping"),
                        (u"foobar",), (u"foobar", u"pong")])
        self.ParseTest([(u"--exclude", u"testfiles/select/1/1/*"),
                        (u"--exclude", u"testfiles/select/1/2/**"),
                        (u"--exclude", u"testfiles/select/1/3**"),
                        (u"--include", u"testfiles/select/1"),
                        (u"--exclude", u"**")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"2")])

    def test_glob3(self):
        """ regression test for bug 25230 """
        self.ParseTest([(u"--include", u"testfiles/select/**1"),
                        (u"--include", u"testfiles/select/**2"),
                        (u"--exclude", u"**")],
                       [(), (u"1",), (u"1", u"1"),
                        (u"1", u"1", u"1"), (u"1", u"1", u"2"), (u"1", u"1", u"3"),
                        (u"1", u"2"),
                        (u"1", u"2", u"1"), (u"1", u"2", u"2"), (u"1", u"2", u"3"),
                        (u"1", u"3"),
                        (u"1", u"3", u"1"), (u"1", u"3", u"2"), (u"1", u"3", u"3"),
                        (u"2",), (u"2", u"1"),
                        (u"2", u"1", u"1"), (u"2", u"1", u"2"), (u"2", u"1", u"3"),
                        (u"2", u"2"),
                        (u"2", u"2", u"1"), (u"2", u"2", u"2"), (u"2", u"2", u"3"),
                        (u"2", u"3"),
                        (u"2", u"3", u"1"), (u"2", u"3", u"2"), (u"2", u"3", u"3"),
                        (u"3",), (u"3", u"1"),
                        (u"3", u"1", u"1"), (u"3", u"1", u"2"), (u"3", u"1", u"3"),
                        (u"3", u"2"),
                        (u"3", u"2", u"1"), (u"3", u"2", u"2"), (u"3", u"2", u"3"),
                        (u"3", u"3"),
                        (u"3", u"3", u"1"), (u"3", u"3", u"2")])

    def test_alternate_root(self):
        """Test select with different root"""
        self.root = Path(u"testfiles/select/1")
        self.ParseTest([(u"--exclude", u"testfiles/select/1/[23]")],
                       [(), (u"1",), (u"1", u"1"), (u"1", u"2"), (u"1", u"3")])

        self.root = Path(u"/")
        self.ParseTest([(u"--exclude", u"/tmp/*"),
                        (u"--include", u"/tmp"),
                        (u"--exclude", u"/")],
                       [(), (u"tmp",)])

    def test_exclude_after_scan(self):
        """Test select with an exclude after a pattern that would return a scan for that file"""
        self.root = Path(u"testfiles/select2/3")
        self.ParseTest([(u"--include", u"testfiles/select2/3/**file.txt"),
                        (u"--exclude", u"testfiles/select2/3/3sub2"),
                        (u"--include", u"testfiles/select2/3/3sub1"),
                        (u"--exclude", u"**")],
                       [(), (u"3sub1",), (u"3sub1", u"3sub1sub1"), (u"3sub1", u"3sub1sub2"), (u"3sub1", u"3sub1sub3"),
                        (u"3sub3",), (u"3sub3", u"3sub3sub2"), (u"3sub3", u"3sub3sub2", u"3sub3sub2_file.txt")])

    def test_include_exclude_basic(self):
        """Test functional test test_include_exclude_basic as a unittest"""
        self.root = Path(u"testfiles/select2")
        self.ParseTest([(u"--include", u"testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt"),
                        (u"--exclude", u"testfiles/select2/3/3sub3/3sub3sub2"),
                        (u"--include", u"testfiles/select2/3/3sub2/3sub2sub2"),
                        (u"--include", u"testfiles/select2/3/3sub3"),
                        (u"--exclude", u"testfiles/select2/3/3sub1"),
                        (u"--exclude", u"testfiles/select2/2/2sub1/2sub1sub3"),
                        (u"--exclude", u"testfiles/select2/2/2sub1/2sub1sub2"),
                        (u"--include", u"testfiles/select2/2/2sub1"),
                        (u"--exclude", u"testfiles/select2/1/1sub3/1sub3sub2"),
                        (u"--exclude", u"testfiles/select2/1/1sub3/1sub3sub1"),
                        (u"--exclude", u"testfiles/select2/1/1sub2/1sub2sub3"),
                        (u"--include", u"testfiles/select2/1/1sub2/1sub2sub1"),
                        (u"--exclude", u"testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt"),
                        (u"--exclude", u"testfiles/select2/1/1sub1/1sub1sub2"),
                        (u"--exclude", u"testfiles/select2/1/1sub2"),
                        (u"--include", u"testfiles/select2/1.py"),
                        (u"--include", u"testfiles/select2/3"),
                        (u"--include", u"testfiles/select2/1"),
                        (u"--exclude", u"testfiles/select2/**")],
                       self.expected_restored_tree)

    def test_globbing_replacement(self):
        """Test functional test test_globbing_replacement as a unittest"""
        self.root = Path(u"testfiles/select2")
        self.ParseTest([(u"--include", u"testfiles/select2/**/3sub3sub2/3sub3su?2_file.txt"),
                        (u"--exclude", u"testfiles/select2/*/3s*1"),
                        (u"--exclude", u"testfiles/select2/**/2sub1sub3"),
                        (u"--exclude", u"ignorecase:testfiles/select2/2/2sub1/2Sub1Sub2"),
                        (u"--include", u"ignorecase:testfiles/sel[w,u,e,q]ct2/2/2S?b1"),
                        (u"--exclude", u"testfiles/select2/1/1sub3/1s[w,u,p,q]b3sub2"),
                        (u"--exclude", u"testfiles/select2/1/1sub[1-4]/1sub3sub1"),
                        (u"--include", u"testfiles/select2/1/1sub2/1sub2sub1"),
                        (u"--exclude", u"testfiles/select2/1/1sub1/1sub1sub3/1su?1sub3_file.txt"),
                        (u"--exclude", u"testfiles/select2/1/1*1/1sub1sub2"),
                        (u"--exclude", u"testfiles/select2/1/1sub2"),
                        (u"--include", u"testfiles/select[2-4]/*.py"),
                        (u"--include", u"testfiles/*2/3"),
                        (u"--include", u"**/select2/1"),
                        (u"--exclude", u"testfiles/select2/**")],
                       self.expected_restored_tree)


class TestGlobGetNormalSf(UnitTestCase):
    """Test glob parsing of the test_glob_get_normal_sf function. Indirectly test behaviour of glob_to_re."""

    def glob_tester(self, path, glob_string, include_exclude, root_path):
        """Takes a path, glob string and include_exclude value (1 = include, 0 = exclude) and returns the output
        of the selection function.
        None - means the test has nothing to say about the related file
        0 - the file is excluded by the test
        1 - the file is included
        2 - the test says the file (must be directory) should be scanned"""
        self.unpack_testfiles()
        self.root = Path(root_path)
        self.select = Select(self.root)
        selection_function = self.select.glob_get_normal_sf(glob_string, include_exclude)
        path = Path(path)
        return selection_function(path)

    def include_glob_tester(self, path, glob_string, root_path=u"/"):
        return self.glob_tester(path, glob_string, 1, root_path)

    def exclude_glob_tester(self, path, glob_string, root_path=u"/"):
        return self.glob_tester(path, glob_string, 0, root_path)

    def test_glob_get_normal_sf_exclude(self):
        """Test simple exclude."""
        self.assertEqual(self.exclude_glob_tester(u"/testfiles/select2/3", u"/testfiles/select2"), 0)
        self.assertEqual(self.exclude_glob_tester(u"/testfiles/.git", u"/testfiles"), 0)

    def test_glob_get_normal_sf_exclude_root(self):
        """Test simple exclude with / as the glob."""
        self.assertEqual(self.exclude_glob_tester(u"/.git", u"/"), 0)
        self.assertEqual(self.exclude_glob_tester(u"/testfile", u"/"), 0)

    def test_glob_get_normal_sf_2(self):
        """Test same behaviour as the functional test test_globbing_replacement."""
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt",
                                                  u"/testfiles/select2/**/3sub3sub2/3sub3su?2_file.txt"), 1)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/3/3sub1", u"/testfiles/select2/*/3s*1"), 1)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/2/2sub1/2sub1sub3",
                                                  u"/testfiles/select2/**/2sub1sub3"), 1)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/2/2sub1",
                                                  u"/testfiles/sel[w,u,e,q]ct2/2/2s?b1"), 1)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/1/1sub3/1sub3sub2",
                                                  u"/testfiles/select2/1/1sub3/1s[w,u,p,q]b3sub2"), 1)
        self.assertEqual(self.exclude_glob_tester(u"/testfiles/select2/1/1sub3/1sub3sub1",
                                                  u"/testfiles/select2/1/1sub[1-4]/1sub3sub1"), 0)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/1/1sub2/1sub2sub1",
                                                  u"/testfiles/select2/*/1sub2/1s[w,u,p,q]b2sub1"), 1)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt",
                                                  u"/testfiles/select2/1/1sub1/1sub1sub3/1su?1sub3_file.txt"), 1)
        self.assertEqual(self.exclude_glob_tester(u"/testfiles/select2/1/1sub1/1sub1sub2",
                                                  u"/testfiles/select2/1/1*1/1sub1sub2"), 0)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/1/1sub2", u"/testfiles/select2/1/1sub2"), 1)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/1.py", u"/testfiles/select[2-4]/*.py"), 1)
        self.assertEqual(self.exclude_glob_tester(u"/testfiles/select2/3", u"/testfiles/*2/3"), 0)
        self.assertEqual(self.include_glob_tester(u"/testfiles/select2/1", u"**/select2/1"), 1)

    def test_glob_get_normal_sf_negative_square_brackets_specified(self):
        """Test negative square bracket (specified) [!a,b,c] replacement in get_normal_sf."""
        # As in a normal shell, [!...] expands to any single character but those specified
        self.assertEqual(self.include_glob_tester(u"/test/hello1.txt", u"/test/hello[!2,3,4].txt"), 1)
        self.assertEqual(self.include_glob_tester(u"/test/hello.txt", u"/t[!w,f,h]st/hello.txt"), 1)
        self.assertEqual(self.exclude_glob_tester(u"/long/example/path/hello.txt",
                                                  u"/lon[!w,e,f]/e[!p]ample/path/hello.txt"), 0)
        self.assertEqual(self.include_glob_tester(u"/test/hello1.txt", u"/test/hello[!2,1,3,4].txt"), None)
        self.assertEqual(self.include_glob_tester(u"/test/hello.txt", u"/t[!e,f,h]st/hello.txt"), None)
        self.assertEqual(self.exclude_glob_tester(u"/long/example/path/hello.txt",
                                                  u"/lon[!w,e,g,f]/e[!p,x]ample/path/hello.txt"), None)

    def test_glob_get_normal_sf_negative_square_brackets_range(self):
        """Test negative square bracket (range) [!a,b,c] replacement in get_normal_sf."""
        # As in a normal shell, [!1-5] or [!a-f] expands to any single character not in the range specified
        self.assertEqual(self.include_glob_tester(u"/test/hello1.txt", u"/test/hello[!2-4].txt"), 1)
        self.assertEqual(self.include_glob_tester(u"/test/hello.txt", u"/t[!f-h]st/hello.txt"), 1)
        self.assertEqual(self.exclude_glob_tester(u"/long/example/path/hello.txt",
                                                  u"/lon[!w,e,f]/e[!p-s]ample/path/hello.txt"), 0)
        self.assertEqual(self.include_glob_tester(u"/test/hello1.txt", u"/test/hello[!1-4].txt"), None)
        self.assertEqual(self.include_glob_tester(u"/test/hello.txt", u"/t[!b-h]st/hello.txt"), None)
        self.assertEqual(self.exclude_glob_tester(u"/long/example/path/hello.txt",
                                                  u"/lon[!f-p]/e[!p]ample/path/hello.txt"), None)

    def test_glob_get_normal_sf_2_ignorecase(self):
        """Test same behaviour as the functional test test_globbing_replacement, ignorecase tests."""
        self.assertEqual(self.include_glob_tester(u"testfiles/select2/2/2sub1",
                                                  u"ignorecase:testfiles/sel[w,u,e,q]ct2/2/2S?b1",
                                                  u"testfiles/select2"), 1)
        self.assertEqual(self.include_glob_tester(u"testfiles/select2/2/2sub1/2sub1sub2",
                                                  u"ignorecase:testfiles/select2/2/2sub1/2Sub1Sub2",
                                                  u"testfiles/select2"), 1)

    def test_glob_get_normal_sf_3_double_asterisks_dirs_to_scan(self):
        """Test double asterisk (**) replacement in glob_get_normal_sf with directories that should be scanned"""
        # The new special pattern, **, expands to any string of characters whether or not it contains "/".
        self.assertEqual(self.include_glob_tester(u"/long/example/path", u"/**/hello.txt"), 2)

    def test_glob_get_normal_sf_3_ignorecase(self):
        """Test ignorecase in glob_get_normal_sf"""
        # If the pattern starts with "ignorecase:" (case insensitive), then this prefix will be removed and any
        # character in the string can be replaced with an upper- or lowercase version of itself.
        self.assertEqual(self.include_glob_tester(u"testfiles/select2/2", u"ignorecase:testfiles/select2/2",
                                                  u"testfiles/select2"), 1)
        self.assertEqual(self.include_glob_tester(u"testfiles/select2/2", u"ignorecase:testFiles/Select2/2",
                                                  u"testfiles/select2"), 1)
        self.assertEqual(self.include_glob_tester(u"tEstfiles/seLect2/2", u"ignorecase:testFiles/Select2/2",
                                                  u"testfiles/select2"), 1)
        self.assertEqual(self.include_glob_tester(u"TEstfiles/SeLect2/2", u"ignorecase:t?stFiles/S*ect2/2",
                                                  u"testfiles/select2"), 1)
        self.assertEqual(self.include_glob_tester(u"TEstfiles/SeLect2/2", u"ignorecase:t?stFil**ect2/2",
                                                  u"testfiles/select2"), 1)
        self.assertEqual(self.exclude_glob_tester(u"TEstfiles/SeLect2/2", u"ignorecase:t?stFiles/S*ect2/2",
                                                  u"testfiles/select2"), 0)
        self.assertEqual(self.exclude_glob_tester(u"TEstFiles/SeLect2/2", u"ignorecase:t?stFile**ect2/2",
                                                  u"testfiles/select2"), 0)

    def test_glob_dirs_to_scan(self):
        """Test parent directories are marked as needing to be scanned"""
        with patch(u"duplicity.path.Path.isdir") as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                self.glob_tester(u"parent", u"parent/hello.txt", 1, u"parent"), 2)

    def test_glob_dirs_to_scan_glob(self):
        """Test parent directories are marked as needing to be scanned - globs"""
        with patch(u"duplicity.path.Path.isdir") as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                self.glob_tester(u"testfiles/select/1", u"*/select/1/1", 1,
                                 u"testfiles/select"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select/1/2",
                                 u"*/select/1/2/1", 1, u"testfiles/select"), 2)
            self.assertEqual(
                self.glob_tester(u"parent", u"parent/hel?o.txt", 1, u"parent"), 2)
            self.assertEqual(
                self.glob_tester(u"test/parent/folder",
                                 u"test/par*t/folder/hello.txt", 1, u"test"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select/1/1",
                                 u"**/1/2/1", 1, u"testfiles"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select2/3/3sub2",
                                 u"testfiles/select2/3/**file.txt", 1,
                                 u"testfiles"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select/1/2",
                                 u"*/select/1/2/1", 1, u"testfiles"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select/1",
                                 u"testfiles/select**/2", 1, u"testfiles"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select/efools",
                                 u"testfiles/select/*foo*/p*", 1,
                                 u"testfiles"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select/3",
                                 u"testfiles/select/**2", 1, u"testfiles"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select2/1/1sub1/1sub1sub2",
                                 u"testfiles/select2/**/3sub3sub2/3sub3su?2_file.txt",
                                 1, u"testfiles"), 2)
            self.assertEqual(
                self.glob_tester(u"testfiles/select/1",
                                 u"*/select/1/1", 1, u"testfiles"), 2)

if __name__ == "__main__":
    unittest.main()

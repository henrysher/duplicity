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

import sys
from duplicity.globmatch import *
from duplicity.path import *
from . import UnitTestCase
from mock import patch
import unittest


class MatchingTest(UnitTestCase):
    """Test matching of file names against various selection functions"""

    def test_glob_re(self):
        """test_glob_re - test translation of shell pattern to regular exp"""
        assert glob_to_regex("hello") == "hello"
        assert glob_to_regex(".e?ll**o") == "\\.e[^/]ll.*o"
        r = glob_to_regex("[abc]el[^de][!fg]h")
        assert r == "[abc]el[^de][^fg]h", r
        r = glob_to_regex("/usr/*/bin/")
        assert r == "\\/usr\\/[^/]*\\/bin\\/", r
        assert glob_to_regex("[a.b/c]") == "[a.b/c]"
        r = glob_to_regex("[a*b-c]e[!]]")
        assert r == "[a*b-c]e[^]]", r


class TestDoubleAsteriskOnIncludesExcludes(UnitTestCase):
    """Test ** on includes and exclude patterns"""

    def test_double_asterisk_include(self):
        """Test a few globbing patterns, including **"""
        self.assertEqual(
            path_matches_glob_fn("**", 1)(Path("foo.txt")), 1)
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("**", 1)(Path("folder")), 1)

    def test_double_asterisk_extension_include(self):
        """Test **.py"""
        self.assertEqual(
            path_matches_glob_fn("**.py", 1)(Path("what/ever.py")), 1)
        self.assertEqual(
            path_matches_glob_fn("**.py", 1)(Path("what/ever.py/foo")), 1)
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("**.py", 1)(Path("foo")), 2)
            self.assertEqual(
                path_matches_glob_fn("**.py", 1)(Path("usr/local/bin")), 2)
            self.assertEqual(
                path_matches_glob_fn("**.py", 1)(Path("/usr/local/bin")), 2)


class TestTrailingSlash(UnitTestCase):
    """Test glob matching where the glob has a trailing slash"""

    def test_trailing_slash_matches_only_dirs(self):
        """Test matching where glob includes a trailing slash"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("fold*/", 1)(Path("folder")), 1)

            # Test the file named "folder" is not included if it is not a dir
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("fold*/", 1)(Path("folder")), None)

            # Test the file named "folder" is not included if it is not a dir
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("folder/", 1)(Path("folder")), None)

            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("fo*/", 1)(Path("foo.txt")), None)

    def test_included_files_are_matched_no_slash(self):
        """Test that files within an included folder are matched"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("fold*", 1)(Path("folder/file.txt")), 1)

        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("fold*", 1)(Path("folder/2/file.txt")), 1)

    def test_included_files_are_matched_no_slash_2(self):
        """Test that files within an included folder are matched"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("folder", 1)(Path("folder/file.txt")), 1)

        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("folder/2", 1)(Path("folder/2/file.txt")), 1)

    def test_included_files_are_matched_slash(self):
        """Test that files within an included folder are matched with /"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("folder/", 1)(Path("folder/file.txt")), 1)

    def test_included_files_are_matched_slash_2(self):
        """Test that files within an included folder are matched with /"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("testfiles/select2/1/1sub1/1sub1sub1/", 1)
                (Path("testfiles/select2/1/1sub1/1sub1sub1/1sub1sub1_file.txt")
                 ), 1)

    def test_included_files_are_matched_slash_2_parents(self):
        """Test that duplicity will scan parent of glob/"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("testfiles/select2/1/1sub1/1sub1sub1/", 1)
                (Path("testfiles/select2/1/1sub1/1sub1sub1")
                 ), 1)
            self.assertEqual(
                path_matches_glob_fn("testfiles/select2/1/1sub1/1sub1sub1/", 1)
                (Path("testfiles/select2/1/1sub1")
                 ), 2)

    def test_included_files_are_matched_slash_wildcard(self):
        """Test that files within an included folder are matched with /"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            self.assertEqual(
                path_matches_glob_fn("fold*/", 1)(Path("folder/file.txt")), 1)
    #
    # def test_slash_matches_everything(self):
    #     """Test / matches everything"""
    #     # ToDo: Not relevant at this stage, as "/" would not go through
    #     # globmatch because it has no special characters, but it should be
    #     # made to work
    #     with patch('duplicity.path.Path.isdir') as mock_isdir:
    #         mock_isdir.return_value = True
    #         self.assertEqual(
    #             path_matches_glob_fn("/",
    #                                  1)(Path("/tmp/testfiles/select/1/2")), 1)
    #         self.assertEqual(
    #             path_matches_glob_fn("/",
    #                                  1)(Path("/test/random/path")), 1)
    #         self.assertEqual(
    #             path_matches_glob_fn("/",
    #                                  1)(Path("/")), 1)
    #         self.assertEqual(
    #             path_matches_glob_fn("/",
    #                                  1)(Path("/var/log")), 1)
    #         self.assertEqual(
    #             path_matches_glob_fn("/",
    #                                  1)(Path("/var/log/log.txt")), 1)

    def test_slash_star_scans_folder(self):
        """Test that folder/* scans folder/"""
        # This behaviour is a bit ambiguous - either include or scan could be
        # argued as most appropriate here, but only an empty folder is at stake
        # so long as test_slash_star_includes_folder_contents passes.
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("folder/*", 1)(Path("folder")), 2)

    def test_slash_star_includes_folder_contents(self):
        """Test that folder/* includes folder contents"""
        self.assertEqual(path_matches_glob_fn("folder/*", 1)
                         (Path("folder/file.txt")), 1)
        self.assertEqual(path_matches_glob_fn("folder/*", 1)
                         (Path("folder/other_file.log")), 1)

    def test_slash_star_star_includes_folder(self):
        """Test that folder/** includes folder/"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True

    def test_simple_trailing_slash_match(self):
        """Test that a normal folder string ending in / matches that path"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            test_path = "testfiles/select/1/2/1"
            self.assertEqual(
                path_matches_glob_fn(test_path, 1)(Path(test_path)), 1)

    def test_double_asterisk_string_slash(self):
        """Test string starting with ** and ending in /"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("**/1/2/",
                                     1)(Path("testfiles/select/1/2")), 1)

    def test_string_double_asterisk_string_slash(self):
        """Test string ** string /"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("testfiles**/2/",
                                     1)(Path("testfiles/select/1/2")), 1)


class TestDoubleAsterisk(UnitTestCase):
    """Test glob matching where the glob finishes with a **"""

    def test_simple_trailing_slash_match(self):
        """Test that a folder string ending in /** matches that path"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("/test/folder/**", 1)(
                    Path("/test/foo")), None)

    def test_simple_trailing_slash_match_2(self):
        """Test folder string ending in */**"""
        with patch('duplicity.path.Path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            self.assertEqual(
                path_matches_glob_fn("fold*/**", 1)(
                    Path("folder")), 2)
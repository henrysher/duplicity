# -*- coding: utf-8 -*-
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

import unittest

from duplicity.globmatch import *
from duplicity.path import *
from . import UnitTestCase
from mock import patch


def sel_file(glob_str, include, file_path):
    u"""Returns the selection value for file_path, given the include value,
    returning:
    0 - if the file should be excluded
    1 - if the file should be included
    2 - if the folder should be scanned for any included/excluded files
    None - if the selection function has nothing to say about the file

    Note: including a folder implicitly includes everything within it."""

    select_fn = select_fn_from_glob(glob_str, include)
    selection_value = select_fn(Path(file_path))
    return selection_value


def inc_sel_file(glob_str, file_path):
    u"""Returns result of sel_file with include value set to 1"""
    # Aids readability of the testing code to only have one number (the
    # result of the select function)
    return sel_file(glob_str, 1, file_path)


def exc_sel_file(glob_str, file_path):
    u"""Returns result of sel_file with include value set to 0"""
    return sel_file(glob_str, 0, file_path)


def sel_dir(glob_str, include, file_path):
    u"""As per sel_file, but mocks file_path to be a directory"""
    with patch(u'duplicity.path.Path.isdir') as mock_isdir:
        mock_isdir.return_value = True
        return sel_file(glob_str, include, file_path)


def inc_sel_dir(glob_str, file_path):
    u"""Returns result of sel_dir with include value set to 1"""
    return sel_dir(glob_str, 1, file_path)


def exc_sel_dir(glob_str, file_path):
    u"""Returns result of sel_dir with include value set to 0"""
    return sel_dir(glob_str, 0, file_path)


class TestGlobToRegex(UnitTestCase):
    u"""Test translation of glob strings into regular expressions"""

    def test_glob_to_regex(self):
        u"""test_glob_re - test translation of shell pattern to regular exp"""
        self.assertEqual(glob_to_regex(u"hello"), u"hello")
        self.assertEqual(glob_to_regex(u".e?ll**o"), u"\\.e[^/]ll.*o")
        self.assertEqual(glob_to_regex(u"[abc]el[^de][!fg]h"),
                         u"[abc]el[^de][^fg]h")
        self.assertEqual(glob_to_regex(u"/usr/*/bin/"),
                         u"\\/usr\\/[^/]*\\/bin\\/")
        self.assertEqual(glob_to_regex(u"[a.b/c]"), u"[a.b/c]")
        self.assertEqual(glob_to_regex(u"[a*b-c]e[!]]"), u"[a*b-c]e[^]]")


class TestSelectValuesFromGlobs(UnitTestCase):
    u"""Test the select values returned from various globs"""

    def test_glob_scans_parent_directories(self):
        u"""Test glob scans parent"""
        self.assertEqual(
            inc_sel_dir(u"testfiles/parent/sub", u"testfiles/parent"), 2)
        self.assertEqual(
            inc_sel_dir(u"testfiles/select2/3/3sub2", u"testfiles/select2/3"), 2)

    def test_double_asterisk_include(self):
        u"""Test a few globbing patterns, including **"""
        self.assertEqual(inc_sel_file(u"**", u"foo.txt"), 1)
        self.assertEqual(inc_sel_dir(u"**", u"folder"), 1)

    def test_double_asterisk_extension_include(self):
        u"""Test **.py"""
        self.assertEqual(inc_sel_file(u"**.py", u"what/ever.py"), 1)
        self.assertEqual(inc_sel_file(u"**.py", u"what/ever.py/foo"), 1)
        self.assertEqual(inc_sel_dir(u"**.py", u"foo"), 2)
        self.assertEqual(inc_sel_dir(u"**.py", u"usr/local/bin"), 2)
        self.assertEqual(inc_sel_dir(u"**.py", u"/usr/local/bin"), 2)


class TestTrailingSlash(UnitTestCase):
    u"""Test glob matching where the glob has a trailing slash"""

    def test_trailing_slash_matches_only_dirs(self):
        u"""Test matching where glob includes a trailing slash"""
        # Test the folder named "folder" is included
        self.assertEqual(inc_sel_dir(u"fold*/", u"folder"), 1)

        # Test the file (not folder) named "folder" is not included
        self.assertEqual(inc_sel_file(u"fold*/", u"folder"), None)
        self.assertEqual(inc_sel_file(u"folder/", u"folder"), None)

        # Test miscellaneous file/folder
        self.assertEqual(inc_sel_file(u"fo*/", u"foo.txt"), None)

    def test_included_files_are_matched_no_slash(self):
        u"""Test that files within an included folder are matched"""
        self.assertEqual(inc_sel_file(u"fold*", u"folder/file.txt"), 1)
        self.assertEqual(inc_sel_file(u"fold*", u"folder/file.txt"), 1)
        self.assertEqual(inc_sel_file(u"fold*", u"folder/2/file.txt"), 1)

    def test_included_files_are_matched_no_slash_2(self):
        u"""Test that files within an included folder are matched"""
        self.assertEqual(inc_sel_file(u"folder", u"folder/file.txt"), 1)
        self.assertEqual(inc_sel_file(u"folder/2", u"folder/2/file.txt"), 1)

    def test_included_files_are_matched_slash(self):
        u"""Test that files within an included folder are matched with /"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        self.assertEqual(inc_sel_file(u"folder/", u"folder/file.txt"), 1)

    def test_included_files_are_matched_slash_2(self):
        u"""Test that files within an included folder are matched with /"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        self.assertEqual(inc_sel_file(
            u"testfiles/select2/1/1sub1/1sub1sub1/",
            u"testfiles/select2/1/1sub1/1sub1sub1/1sub1sub1_file.txt"), 1)

    def test_included_files_are_matched_slash_2_parents(self):
        u"""Test that duplicity will scan parent of glob/"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        self.assertEqual(inc_sel_dir(
            u"testfiles/select2/1/1sub1/1sub1sub1/",
            u"testfiles/select2/1/1sub1/1sub1sub1"), 1)
        self.assertEqual(inc_sel_dir(
            u"testfiles/select2/1/1sub1/1sub1sub1/",
            u"testfiles/select2/1/1sub1"), 2)

    def test_included_files_are_matched_slash_wildcard(self):
        u"""Test that files within an included folder are matched with /"""
        # Bug #1624725
        # https://bugs.launchpad.net/duplicity/+bug/1624725
        self.assertEqual(inc_sel_file(u"fold*/", u"folder/file.txt"), 1)

    def test_slash_matches_everything(self):
        u"""Test / matches everything"""
        self.assertEqual(inc_sel_dir(u"/", u"/tmp/testfiles/select/1/2"), 1)
        self.assertEqual(inc_sel_dir(u"/", u"/test/random/path"), 1)
        self.assertEqual(exc_sel_dir(u"/", u"/test/random/path"), 0)
        self.assertEqual(inc_sel_dir(u"/", u"/"), 1)
        self.assertEqual(inc_sel_dir(u"/", u"/var/log"), 1)
        self.assertEqual(inc_sel_file(u"/", u"/var/log/log.txt"), 1)

    def test_slash_star_scans_folder(self):
        u"""Test that folder/* scans folder/"""
        # This behaviour is a bit ambiguous - either include or scan could be
        # argued as most appropriate here, but only an empty folder is at stake
        # so long as test_slash_star_includes_folder_contents passes.
        self.assertEqual(inc_sel_dir(u"folder/*", u"folder"), 2)

    def test_slash_star_includes_folder_contents(self):
        u"""Test that folder/* includes folder contents"""
        self.assertEqual(inc_sel_file(u"folder/*", u"folder/file.txt"), 1)
        self.assertEqual(inc_sel_file(u"folder/*", u"folder/other_file.log"), 1)

    def test_slash_star_star_scans_folder(self):
        u"""Test that folder/** scans folder/"""
        self.assertEqual(inc_sel_dir(u"folder/**", u"folder"), 2)

    def test_simple_trailing_slash_match(self):
        u"""Test that a normal folder string ending in / matches that path"""
        self.assertEqual(inc_sel_dir(u"testfiles/select/1/2/1/",
                                     u"testfiles/select/1/2/1"), 1)

    def test_double_asterisk_string_slash(self):
        u"""Test string starting with ** and ending in /"""
        self.assertEqual(inc_sel_dir(u"**/1/2/", u"testfiles/select/1/2"), 1)

    def test_string_double_asterisk_string_slash(self):
        u"""Test string ** string /"""
        self.assertEqual(inc_sel_dir(u"testfiles**/2/",
                                     u"testfiles/select/1/2"), 1)


class TestDoubleAsterisk(UnitTestCase):
    u"""Test glob matching where the glob finishes with a **"""

    def test_double_asterisk_no_match(self):
        u"""Test that a folder string ending /** does not match other paths"""
        self.assertEqual(inc_sel_dir(u"/test/folder/**", u"/test/foo"), None)

    def test_double_asterisk_match(self):
        u"""Test that a folder string ending in /** matches that path"""
        self.assertEqual(inc_sel_dir(u"/test/folder/**",
                                     u"/test/folder/foo"), 1)
        self.assertEqual(inc_sel_file(u"/test/folder/**",
                                      u"/test/folder/foo.txt"), 1)
        self.assertEqual(inc_sel_dir(u"/test/folder/**",
                                     u"/test/folder/2/foo"), 1)
        self.assertEqual(inc_sel_file(u"/test/folder/**",
                                      u"/test/folder/2/foo.txt"), 1)

    def test_asterisk_slash_double_asterisk(self):
        u"""Test folder string ending in */**"""
        self.assertEqual(inc_sel_dir(u"fold*/**", u"folder"), 2)


class TestSimpleUnicode(UnitTestCase):
    u"""Test simple unicode comparison"""

    def test_simple_unicode(self):
        u"""Test simple unicode comparison"""
        self.assertEqual(inc_sel_file(u"прыклад/пример/例/Παράδειγμα/उदाहरण.txt",
                                      u"прыклад/пример/例/Παράδειγμα/उदाहरण.txt"), 1)


class TestSquareBrackets(UnitTestCase):
    u"""Test glob matching where the glob includes []s and [!]s"""

    def test_square_bracket_options(self):
        u"""Test file including options in []s"""
        self.assertEqual(inc_sel_file(u"/test/f[o,s,p]lder/foo.txt",
                                      u"/test/folder/foo.txt"), 1)
        self.assertEqual(inc_sel_file(u"/test/f[i,s,p]lder/foo.txt",
                                      u"/test/folder/foo.txt"), None)
        self.assertEqual(inc_sel_file(u"/test/f[s,o,p]lder/foo.txt",
                                      u"/test/folder/foo.txt"), 1)

    def test_square_bracket_options_unicode(self):
        u"""Test file including options in []s"""
        self.assertEqual(inc_sel_file(u"прыклад/пр[и,j,l]мер/例/Παράδειγμα/उदाहरण.txt",
                                      u"прыклад/пример/例/Παράδειγμα/उदाहरण.txt"), 1)
        self.assertEqual(inc_sel_file(u"прыклад/п[a,b,c]имер/例/Παράδειγμα/उदाहरण.txt",
                                      u"прыклад/пример/例/Παράδειγμα/उदाहरण.txt"), None)

    def test_not_square_bracket_options(self):
        u"""Test file including options in [!]s"""
        self.assertEqual(inc_sel_file(u"/test/f[!o,s,p]lder/foo.txt",
                                      u"/test/folder/foo.txt"), None)
        self.assertEqual(inc_sel_file(u"/test/f[!i,s,p]lder/foo.txt",
                                      u"/test/folder/foo.txt"), 1)
        self.assertEqual(inc_sel_file(u"/test/f[!s,o,p]lder/foo.txt",
                                      u"/test/folder/foo.txt"), None)

    def test_square_bracket_range(self):
        u"""Test file including range in []s"""
        self.assertEqual(inc_sel_file(u"/test/folder[1-5]/foo.txt",
                                      u"/test/folder4/foo.txt"), 1)
        self.assertEqual(inc_sel_file(u"/test/folder[5-9]/foo.txt",
                                      u"/test/folder4/foo.txt"), None)
        self.assertEqual(inc_sel_file(u"/test/folder[1-5]/foo.txt",
                                      u"/test/folder6/foo.txt"), None)

    def test_square_bracket_not_range(self):
        u"""Test file including range in [!]s"""
        self.assertEqual(inc_sel_file(u"/test/folder[!1-5]/foo.txt",
                                      u"/test/folder4/foo.txt"), None)
        self.assertEqual(inc_sel_file(u"/test/folder[!5-9]/foo.txt",
                                      u"/test/folder4/foo.txt"), 1)
        self.assertEqual(inc_sel_file(u"/test/folder[!1-5]/foo.txt",
                                      u"/test/folder6/foo.txt"), 1)

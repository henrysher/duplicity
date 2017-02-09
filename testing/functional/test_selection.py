# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
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

import os
import sys
import platform

if sys.version_info < (2, 7):
    import unittest2 as unittest  # @UnresolvedImport @UnusedImport
else:
    import unittest  # @Reimport

from . import FunctionalTestCase


class IncludeExcludeFunctionalTest(FunctionalTestCase):
    """
    This contains methods used in the tests below for testing the include, exclude and various filelist features.
    """

    # These tests assume the following files and logic, with:
    # "is" meaning that the file is included specifically
    # "ia" meaning that the file should be included automatically because its parent is included
    # "ic" meaning that the folder is included because its contents are included
    # "es" meaning that the file is excluded specifically
    # "ea" meaning that the file should be excluded automatically because its parent is included
    # select2 (es)
    # --- 1.doc (ea)
    # --- 1.py (is)
    # --- 1 (is)
    # ------ 1sub1 (ia)
    # --------- 1sub1sub1 (ia)
    # ------------ 1sub1sub1_file.txt (ia)
    # --------- 1sub1sub2 (es)
    # ------------ 1sub1sub2_file.txt (ea)
    # --------- 1sub1sub3 (ia)
    # ------------ 1sub1sub3_file.txt (es)
    # ------ 1sub2 (ic)
    # --------- 1sub2sub1 (is)
    # --------- 1sub2sub2 (ea)
    # --------- 1sub2sub3 (es)  # Not necessary as also ea, but to ensure there are no issues doing so
    # ------ 1sub3 (ia)
    # --------- 1sub3sub1 (es)
    # --------- 1sub3sub2 (es)
    # --------- 1sub3sub3 (ia)
    # --- 2 (ic)
    # ------ 2sub1 (is)
    # --------- 2sub1sub1 (ia)
    # ------------ 2sub1sub1_file.txt (ia)
    # --------- 2sub1sub2 (es)
    # --------- 2sub1sub3 (es)
    # ------ 2sub2 (ea)
    # --------- 2sub2sub1 (ea)
    # --------- 2sub2sub2 (ea)
    # --------- 2sub2sub3 (ea)
    # ------ 2sub3 (ea)
    # --------- 2sub3sub1 (ea)
    # --------- 2sub3sub3 (ea)
    # --------- 2sub3sub2 (ea)
    # --- 3 (is)
    # ------ 3sub1 (es)
    # --------- 3sub1sub1 (ea)
    # --------- 3sub1sub2 (ea)
    # --------- 3sub1sub3 (ea)
    # ------ 3sub2 (ia)
    # --------- 3sub2sub1 (ia)
    # --------- 3sub2sub2 (ia)
    # --------- 3sub2sub3 (ia)
    # ------ 3sub3 (is)  # Not necessary as also ia, but to ensure there are no issues doing so
    # --------- 3sub3sub1 (ia)
    # --------- 3sub3sub2 (es, ic)
    # ------------ 3sub3sub2_file.txt (is)
    # --------- 3sub3sub3 (ia)
    # --- trailing_space  (ea)  # Note this is "trailing_space ". Excluded until trailing_space test, when (is)
    # ------ trailing_space sub1 (ea)  # Excluded until trailing_space test, when (ia)
    # ------ trailing_space sub2 (ea)  # Excluded until trailing_space test, when (es, ic)
    # --------- trailing_space sub2_file.txt (ea)  # Excluded until trailing_space test, when (is)

    complete_directory_tree = [
        ['1', '2', '3', 'trailing_space ', '1.doc', '1.py'],
        ['1sub1', '1sub2', '1sub3'],
        ['1sub1sub1', '1sub1sub2', '1sub1sub3'],
        ['1sub1sub1_file.txt'],
        ['1sub1sub2_file.txt'],
        ['1sub1sub3_file.txt'],
        ['1sub2sub1', '1sub2sub2', '1sub2sub3'],
        ['1sub3sub1', '1sub3sub2', '1sub3sub3'],
        ['2sub1', '2sub2', '2sub3'],
        ['2sub1sub1', '2sub1sub2', '2sub1sub3'],
        ['2sub1sub1_file.txt'],
        ['2sub2sub1', '2sub2sub2', '2sub2sub3'],
        ['2sub3sub1', '2sub3sub2', '2sub3sub3'],
        ['3sub1', '3sub2', '3sub3'],
        ['3sub1sub1', '3sub1sub2', '3sub1sub3'],
        ['3sub2sub1', '3sub2sub2', '3sub2sub3'],
        ['3sub3sub1', '3sub3sub2', '3sub3sub3'],
        ['3sub3sub2_file.txt'],
        ['trailing_space sub1', 'trailing_space sub2'],
        ['trailing_space sub2_file.txt']
    ]

    expected_restored_tree = [['1', '2', '3', '1.py'],
                              ['1sub1', '1sub2', '1sub3'],
                              ['1sub1sub1', '1sub1sub3'],
                              ['1sub1sub1_file.txt'],
                              ['1sub2sub1'],
                              ['1sub3sub3'],
                              ['2sub1'],
                              ['2sub1sub1'],
                              ['2sub1sub1_file.txt'],
                              ['3sub2', '3sub3'],
                              ['3sub2sub1', '3sub2sub2', '3sub2sub3'],
                              ['3sub3sub1', '3sub3sub2', '3sub3sub3'],
                              ['3sub3sub2_file.txt']]

    expected_restored_tree_with_trailing_space = [['1', '2', '3', 'trailing_space ', '1.py'],
                                                  ['1sub1', '1sub2', '1sub3'],
                                                  ['1sub1sub1', '1sub1sub3'],
                                                  ['1sub1sub1_file.txt'],
                                                  ['1sub2sub1'],
                                                  ['1sub3sub3'],
                                                  ['2sub1'],
                                                  ['2sub1sub1'],
                                                  ['2sub1sub1_file.txt'],
                                                  ['3sub2', '3sub3'],
                                                  ['3sub2sub1', '3sub2sub2', '3sub2sub3'],
                                                  ['3sub3sub1', '3sub3sub2', '3sub3sub3'],
                                                  ['3sub3sub2_file.txt'],
                                                  ['trailing_space sub1', 'trailing_space sub2'],
                                                  ['trailing_space sub2_file.txt']]

    def directory_tree_to_list_of_lists(self, parent_directory):
        """
        This takes a folder as an input and returns a list with its contents. If the directory has subdirectories, it
        returns a list of lists with the contents of those subdirectories.
        """
        directory_list = []
        for root, dirs, files in os.walk(parent_directory):
            to_add = []
            if dirs:
                dirs.sort()  # So that we can easily compare to what we expect
                to_add = dirs
            if files:
                files.sort()  # So that we can easily compare to what we expect
                to_add += files
            if to_add:
                directory_list.append(to_add)
        return directory_list


class TestCheckTestFiles(IncludeExcludeFunctionalTest):
    """ Tests the testfiles required by the exclude/include tests are as expected. """

    def test_files_are_as_expected(self):
        """Test that the contents of testfiles/select are as expected."""
        testfiles = self.directory_tree_to_list_of_lists('testfiles/select2')
        # print(testfiles)
        self.assertEqual(testfiles, self.complete_directory_tree)


class TestIncludeExcludeOptions(IncludeExcludeFunctionalTest):
    """ This tests the behaviour of the duplicity binary when the include/exclude options are passed directly """

    def test_include_exclude_basic(self):
        """ Test --include and --exclude work in the basic case """
        self.backup("full", "testfiles/select2",
                    options=["--include", "testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt",
                             "--exclude", "testfiles/select2/3/3sub3/3sub3sub2",
                             "--include", "testfiles/select2/3/3sub2/3sub2sub2",
                             "--include", "testfiles/select2/3/3sub3",
                             "--exclude", "testfiles/select2/3/3sub1",
                             "--exclude", "testfiles/select2/2/2sub1/2sub1sub3",
                             "--exclude", "testfiles/select2/2/2sub1/2sub1sub2",
                             "--include", "testfiles/select2/2/2sub1",
                             "--exclude", "testfiles/select2/1/1sub3/1sub3sub2",
                             "--exclude", "testfiles/select2/1/1sub3/1sub3sub1",
                             "--exclude", "testfiles/select2/1/1sub2/1sub2sub3",
                             "--include", "testfiles/select2/1/1sub2/1sub2sub1",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub2",
                             "--exclude", "testfiles/select2/1/1sub2",
                             "--include", "testfiles/select2/1.py",
                             "--include", "testfiles/select2/3",
                             "--include", "testfiles/select2/1",
                             "--exclude", "testfiles/select2/**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_include_exclude_trailing_whitespace(self):
        """Test that folders with trailing whitespace in the names work correctly when passing as include/exclude"""
        # Note that, because this only passes items in as a list of options, this test does not test whether duplicity
        # would correctly interpret commandline options with spaces. However, bin/duplicity uses sys.argv[1:], which
        # should return a list of strings after having correctly processed quotes etc.
        self.backup("full", "testfiles/select2",
                    options=["--include",
                             "testfiles/select2/trailing_space /trailing_space sub2/trailing_space sub2_file.txt",
                             "--exclude", "testfiles/select2/trailing_space /trailing_space sub2",
                             "--include", "testfiles/select2/trailing_space ",
                             "--include", "testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt",
                             "--exclude", "testfiles/select2/3/3sub3/3sub3sub2",
                             "--include", "testfiles/select2/3/3sub2/3sub2sub2",
                             "--include", "testfiles/select2/3/3sub3",
                             "--exclude", "testfiles/select2/3/3sub1",
                             "--exclude", "testfiles/select2/2/2sub1/2sub1sub3",
                             "--exclude", "testfiles/select2/2/2sub1/2sub1sub2",
                             "--include", "testfiles/select2/2/2sub1",
                             "--exclude", "testfiles/select2/1/1sub3/1sub3sub2",
                             "--exclude", "testfiles/select2/1/1sub3/1sub3sub1",
                             "--exclude", "testfiles/select2/1/1sub2/1sub2sub3",
                             "--include", "testfiles/select2/1/1sub2/1sub2sub1",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub2",
                             "--exclude", "testfiles/select2/1/1sub2",
                             "--include", "testfiles/select2/1.py",
                             "--include", "testfiles/select2/3",
                             "--include", "testfiles/select2/1",
                             "--exclude", "testfiles/select2/**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree_with_trailing_space)


class TestExcludeFilelistTest(IncludeExcludeFunctionalTest):
    """
    Test --exclude-filelist using duplicity binary.
    """

    def test_exclude_filelist(self):
        """Test that exclude filelist works in the basic case """
        # As this is an exclude filelist any lines with no +/- modifier should be treated as if they have a -.
        # Create a filelist
        with open('testfiles/exclude.txt', 'w') as f:
            f.write('+ testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    'testfiles/select2/3/3sub3/3sub3sub2\n'
                    '+ testfiles/select2/3/3sub2/3sub2sub2\n'
                    '+ testfiles/select2/3/3sub3\n'
                    '- testfiles/select2/3/3sub1\n'  # - added to ensure it makes no difference
                    'testfiles/select2/2/2sub1/2sub1sub3\n'
                    'testfiles/select2/2/2sub1/2sub1sub2\n'
                    '+ testfiles/select2/2/2sub1\n'
                    'testfiles/select2/1/1sub3/1sub3sub2\n'
                    'testfiles/select2/1/1sub3/1sub3sub1\n'
                    'testfiles/select2/1/1sub2/1sub2sub3\n'
                    '+ testfiles/select2/1/1sub2/1sub2sub1\n'
                    'testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    'testfiles/select2/1/1sub1/1sub1sub2\n'
                    '- testfiles/select2/1/1sub2\n'  # - added to ensure it makes no difference
                    '+ testfiles/select2/1.py\n'
                    '+ testfiles/select2/3\n'
                    '+ testfiles/select2/1\n'
                    'testfiles/select2/**')
        self.backup("full", "testfiles/select2", options=["--exclude-filelist=testfiles/exclude.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_exclude_filelist_combined_imperfections(self):
        """Test that exclude filelist works with imperfections in the input file"""
        # This is a combined test for speed reasons. The individual imperfections are tested as unittests in
        # unit/test_selection.
        # Imperfections tested are;
        # * Leading space/spaces before the modifier
        # * Trailing space/spaces after the filename (but before the newline)
        # * Blank lines (newline character only)
        # * Line only containing spaces
        # * Full-line comments with # as the first character and with leading/trailing spaces
        # * Unnecessarily quoted filenames with/without modifier (both " and ')

        # Create a filelist
        with open('testfiles/exclude.txt', 'w') as f:
            f.write('+ testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    'testfiles/select2/3/3sub3/3sub3sub2\n'
                    '+ testfiles/select2/3/3sub2/3sub2sub2\n'
                    ' + testfiles/select2/3/3sub3\n'  # Note leading space added here
                    '- testfiles/select2/3/3sub1\n'
                    '  testfiles/select2/2/2sub1/2sub1sub3\n'  # Note leading spaces added here
                    '\n'
                    'testfiles/select2/2/2sub1/2sub1sub2\n'
                    ' + testfiles/select2/2/2sub1 \n'  # Note added trailing/leading space here
                    '- "testfiles/select2/1/1sub3/1sub3sub2"\n'  # Unnecessary quotes
                    '# Testing a full-line comment\n'
                    "'testfiles/select2/1/1sub3/1sub3sub1'  \n"  # Note added spaces and quotes here
                    'testfiles/select2/1/1sub2/1sub2sub3\n'
                    '    \n'
                    '+ testfiles/select2/1/1sub2/1sub2sub1\n'
                    '- testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    'testfiles/select2/1/1sub1/1sub1sub2\n'
                    '     # Testing a full-line comment with leading and trailing spaces     \n'
                    'testfiles/select2/1/1sub2  \n'  # Note added spaces here
                    '+ testfiles/select2/1.py\n'
                    '+ testfiles/select2/3 \n'  # Note added space here
                    '+ testfiles/select2/1\n'
                    '- testfiles/select2/**')
        self.backup("full", "testfiles/select2", options=["--exclude-filelist=testfiles/exclude.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_exclude_globbing_filelist_combined_imperfections(self):
        """Test that exclude globbing filelist works with imperfections in the input file"""
        # Identical to test_exclude_filelist_combined_imperfections and included to ensure that
        # the deprecated --exclude-globbing-filelist function works as expected until it is deliberately removed.
        # This is a combined test for speed reasons. The individual imperfections are tested as unittests in
        # unit/test_selection.
        # Imperfections tested are;
        # * Leading space/spaces before the modifier
        # * Trailing space/spaces after the filename (but before the newline)
        # * Blank lines (newline character only)
        # * Line only containing spaces
        # * Full-line comments with # as the first character and with leading/trailing spaces
        # * Unnecessarily quoted filenames with/without modifier (both " and ')

        # Create a filelist
        with open('testfiles/exclude.txt', 'w') as f:
            f.write('+ testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    'testfiles/select2/3/3sub3/3sub3sub2\n'
                    '+ testfiles/select2/3/3sub2/3sub2sub2\n'
                    ' + testfiles/select2/3/3sub3\n'  # Note leading space added here
                    '- testfiles/select2/3/3sub1\n'
                    '  testfiles/select2/2/2sub1/2sub1sub3\n'  # Note leading spaces added here
                    '\n'
                    'testfiles/select2/2/2sub1/2sub1sub2\n'
                    ' + testfiles/select2/2/2sub1 \n'  # Note added trailing/leading space here
                    '- "testfiles/select2/1/1sub3/1sub3sub2"\n'  # Unnecessary quotes
                    '# Testing a full-line comment\n'
                    "'testfiles/select2/1/1sub3/1sub3sub1'  \n"  # Note added spaces and quotes here
                    'testfiles/select2/1/1sub2/1sub2sub3\n'
                    '    \n'
                    '+ testfiles/select2/1/1sub2/1sub2sub1\n'
                    '- testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    'testfiles/select2/1/1sub1/1sub1sub2\n'
                    '     # Testing a full-line comment with leading and trailing spaces     \n'
                    'testfiles/select2/1/1sub2  \n'  # Note added spaces here
                    '+ testfiles/select2/1.py\n'
                    '+ testfiles/select2/3 \n'  # Note added space here
                    '+ testfiles/select2/1\n'
                    '- testfiles/select2/**')
        self.backup("full", "testfiles/select2", options=["--exclude-globbing-filelist=testfiles/exclude.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_exclude_filelist_trailing_whitespace_folders_work_with_quotes(self):
        """Test that folders with trailing whitespace in the names work correctly if they are enclosed in quotes"""
        # Create a filelist
        with open('testfiles/exclude.txt', 'w') as f:
            f.write('+ "testfiles/select2/trailing_space /trailing_space sub2/trailing_space sub2_file.txt"\n'  # New
                    '- "testfiles/select2/trailing_space /trailing_space sub2"\n'  # New
                    '+ "testfiles/select2/trailing_space "\n'  # New
                    '+ testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    'testfiles/select2/3/3sub3/3sub3sub2\n'
                    '+ testfiles/select2/3/3sub2/3sub2sub2\n'
                    '+ testfiles/select2/3/3sub3\n'
                    '- testfiles/select2/3/3sub1\n'
                    'testfiles/select2/2/2sub1/2sub1sub3\n'
                    'testfiles/select2/2/2sub1/2sub1sub2\n'
                    '+ testfiles/select2/2/2sub1\n'
                    'testfiles/select2/1/1sub3/1sub3sub2\n'
                    'testfiles/select2/1/1sub3/1sub3sub1\n'
                    'testfiles/select2/1/1sub2/1sub2sub3\n'
                    '+ testfiles/select2/1/1sub2/1sub2sub1\n'
                    'testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    'testfiles/select2/1/1sub1/1sub1sub2\n'
                    '- testfiles/select2/1/1sub2\n'
                    '+ testfiles/select2/1.py\n'
                    '+ testfiles/select2/3\n'
                    '+ testfiles/select2/1\n'
                    'testfiles/select2/**')
        self.backup("full", "testfiles/select2", options=["--exclude-filelist=testfiles/exclude.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree_with_trailing_space)

    def test_exclude_filelist_progress_option(self):
        """Test that exclude filelist is unaffected by the --progress option"""
        # Regression test for Bug #1264744 (https://bugs.launchpad.net/duplicity/+bug/1264744)
        # Create a filelist identical to that used in test_exclude_filelist
        with open('testfiles/exclude.txt', 'w') as f:
            f.write('+ testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    'testfiles/select2/3/3sub3/3sub3sub2\n'
                    '+ testfiles/select2/3/3sub2/3sub2sub2\n'
                    '+ testfiles/select2/3/3sub3\n'
                    '- testfiles/select2/3/3sub1\n'  # - added to ensure it makes no difference
                    'testfiles/select2/2/2sub1/2sub1sub3\n'
                    'testfiles/select2/2/2sub1/2sub1sub2\n'
                    '+ testfiles/select2/2/2sub1\n'
                    'testfiles/select2/1/1sub3/1sub3sub2\n'
                    'testfiles/select2/1/1sub3/1sub3sub1\n'
                    'testfiles/select2/1/1sub2/1sub2sub3\n'
                    '+ testfiles/select2/1/1sub2/1sub2sub1\n'
                    'testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    'testfiles/select2/1/1sub1/1sub1sub2\n'
                    '- testfiles/select2/1/1sub2\n'  # - added to ensure it makes no difference
                    '+ testfiles/select2/1.py\n'
                    '+ testfiles/select2/3\n'
                    '+ testfiles/select2/1\n'
                    'testfiles/select2/**')

        # Backup the files exactly as in test_exclude_filelist, but with the --progress option
        self.backup("full", "testfiles/select2", options=["--exclude-filelist=testfiles/exclude.txt",
                                                          "--progress"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        # The restored files should match those restored in test_exclude_filelist
        self.assertEqual(restored, self.expected_restored_tree)


class TestIncludeFilelistTest(IncludeExcludeFunctionalTest):
    """
    Test --include-filelist using duplicity binary.
    """

    def test_include_filelist(self):
        """Test that include filelist works in the basic case"""
        # See test_exclude_filelist above for explanation of what is expected. As this is an include filelist
        # any lines with no +/- modifier should be treated as if they have a +.
        # Create a filelist
        with open('testfiles/include.txt', 'w') as f:
            f.write('testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    '- testfiles/select2/3/3sub3/3sub3sub2\n'
                    'testfiles/select2/3/3sub2/3sub2sub2\n'
                    '+ testfiles/select2/3/3sub3\n'  # + added to ensure it makes no difference
                    '- testfiles/select2/3/3sub1\n'
                    '- testfiles/select2/2/2sub1/2sub1sub3\n'
                    '- testfiles/select2/2/2sub1/2sub1sub2\n'
                    'testfiles/select2/2/2sub1\n'
                    '- testfiles/select2/1/1sub3/1sub3sub2\n'
                    '- testfiles/select2/1/1sub3/1sub3sub1\n'
                    '- testfiles/select2/1/1sub2/1sub2sub3\n'
                    '+ testfiles/select2/1/1sub2/1sub2sub1\n'  # + added to ensure it makes no difference
                    '- testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    '- testfiles/select2/1/1sub1/1sub1sub2\n'
                    '- testfiles/select2/1/1sub2\n'
                    'testfiles/select2/1.py\n'
                    'testfiles/select2/3\n'
                    'testfiles/select2/1\n'
                    '- testfiles/select2/**')
        self.backup("full", "testfiles/select2", options=["--include-filelist=testfiles/include.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_include_filelist_combined_imperfections(self):
        """Test that include filelist works with imperfections in the input file"""
        # This is a combined test for speed reasons. The individual imperfections are tested as unittests in
        # unit/test_selection.
        # Imperfections tested are;
        # * Leading space/spaces before the modifier
        # * Trailing space/spaces after the filename (but before the newline)
        # * Blank lines (newline character only)
        # * Line only containing spaces
        # * Full-line comments with # as the first character and with leading/trailing spaces
        # * Unnecessarily quoted filenames with/without modifier  (both " and ')
        # Create a filelist
        with open('testfiles/include.txt', 'w') as f:
            f.write('testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    '- testfiles/select2/3/3sub3/3sub3sub2\n'
                    '"testfiles/select2/3/3sub2/3sub2sub2"\n'
                    '  + testfiles/select2/3/3sub3\n'  # + added to ensure it makes no difference
                    '- testfiles/select2/3/3sub1\n'
                    '- testfiles/select2/2/2sub1/2sub1sub3\n'
                    ' - "testfiles/select2/2/2sub1/2sub1sub2"\n'
                    'testfiles/select2/2/2sub1  \n'
                    '\n'
                    '- testfiles/select2/1/1sub3/1sub3sub2\n'
                    '- testfiles/select2/1/1sub3/1sub3sub1 \n'
                    "- 'testfiles/select2/1/1sub2/1sub2sub3'\n"
                    '             \n'
                    ' + testfiles/select2/1/1sub2/1sub2sub1 \n'  # + added to ensure it makes no difference
                    '- testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    '  - testfiles/select2/1/1sub1/1sub1sub2  \n'
                    '# Testing full-line comment\n'
                    '- testfiles/select2/1/1sub2\n'
                    "'testfiles/select2/1.py'\n"
                    'testfiles/select2/3\n'
                    '        #  Testing another full-line comment      \n'
                    'testfiles/select2/1\n'
                    '- testfiles/select2/**')
        self.backup("full", "testfiles/select2", options=["--include-filelist=testfiles/include.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_include_filelist_workaround_combined_imperfections_no_wildcards(self):
        """Test that include filelist works with imperfections in the input file"""
        # This is a modified version of test_include_filelist that passes, despite Bug #1408411
        # It is still a valid test, it just does not test as many selection features as the above.
        # This is a combined test for speed reasons. The individual imperfections are tested as unittests in
        # unit/test_selection.
        # Imperfections tested are;
        # * Leading space/spaces before the modifier
        # * Trailing space/spaces after the filename (but before the newline)
        # * Blank lines (newline character only)
        # * Line only containing spaces
        # * Full-line comments with # as the first character and with leading/trailing spaces
        # * Unnecessarily quoted filenames with/without modifier  (both " and ')
        # Create a filelist
        with open('testfiles/include.txt', 'w') as f:
            f.write('testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    'testfiles/select2/3/3sub2/3sub2sub2 \n'
                    '  + testfiles/select2/3/3sub3\n'  # + added to ensure it makes no difference
                    ' - testfiles/select2/3/3sub1  \n'
                    '- testfiles/select2/2/2sub1/2sub1sub3\n'
                    '- testfiles/select2/2/2sub1/2sub1sub2\n'
                    '"testfiles/select2/2/2sub1"\n'
                    '   - testfiles/select2/2/2sub3 \n'  # Added because of Bug #1408411
                    '- testfiles/select2/2/2sub2\n'  # Added because of Bug #1408411
                    "- 'testfiles/select2/1/1sub3/1sub3sub2'\n"
                    '\n'
                    '- testfiles/select2/1/1sub3/1sub3sub1\n'
                    '- testfiles/select2/1/1sub2/1sub2sub3\n'
                    '- "testfiles/select2/1/1sub2/1sub2sub2"\n'  # Added because of Bug #1408411
                    '# This is a full-line comment\n'
                    '+ testfiles/select2/1/1sub2/1sub2sub1  \n'  # + added to ensure it makes no difference
                    '- testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    '          \n'
                    '- testfiles/select2/1/1sub1/1sub1sub2\n'
                    #  '- testfiles/select2/1/1sub2\n'  # Commented out because of Bug #1408411
                    "'testfiles/select2/1.py'\n"
                    '       # This is another full-line comment, with spaces     \n'
                    'testfiles/select2/3\n'
                    #  '- testfiles/select2/2\n' # Commented out because of Bug #1408411
                    'testfiles/select2/1\n'
                    '- "testfiles/select2/trailing_space "\n'  # es instead of ea as no wildcard - **
                    '- testfiles/select2/1.doc')  # es instead of ea as no wildcard - **
        self.backup("full", "testfiles/select2", options=["--include-filelist=testfiles/include.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_include_globbing_filelist_combined_imperfections(self):
        """Test that include globbing filelist works with imperfections in the input file"""
        # Identical to test_include_filelist_combined_imperfections and included to ensure that
        # the deprecated --include-globbing-filelist function works as expected until it is deliberately removed.
        # This is a combined test for speed reasons. The individual imperfections are tested as unittests in
        # unit/test_selection.
        # Imperfections tested are;
        # * Leading space/spaces before the modifier
        # * Trailing space/spaces after the filename (but before the newline)
        # * Blank lines (newline character only)
        # * Line only containing spaces
        # * Full-line comments with # as the first character and with leading/trailing spaces
        # * Unnecessarily quoted filenames with/without modifier  (both " and ')
        # Create a filelist
        with open('testfiles/include.txt', 'w') as f:
            f.write('testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    '- testfiles/select2/3/3sub3/3sub3sub2\n'
                    '"testfiles/select2/3/3sub2/3sub2sub2"\n'
                    '  + testfiles/select2/3/3sub3\n'  # + added to ensure it makes no difference
                    '- testfiles/select2/3/3sub1\n'
                    '- testfiles/select2/2/2sub1/2sub1sub3\n'
                    ' - "testfiles/select2/2/2sub1/2sub1sub2"\n'
                    'testfiles/select2/2/2sub1  \n'
                    '\n'
                    '- testfiles/select2/1/1sub3/1sub3sub2\n'
                    '- testfiles/select2/1/1sub3/1sub3sub1 \n'
                    "- 'testfiles/select2/1/1sub2/1sub2sub3'\n"
                    '             \n'
                    ' + testfiles/select2/1/1sub2/1sub2sub1 \n'  # + added to ensure it makes no difference
                    '- testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    '  - testfiles/select2/1/1sub1/1sub1sub2  \n'
                    '# Testing full-line comment\n'
                    '- testfiles/select2/1/1sub2\n'
                    "'testfiles/select2/1.py'\n"
                    'testfiles/select2/3\n'
                    '        #  Testing another full-line comment      \n'
                    'testfiles/select2/1\n'
                    '- testfiles/select2/**')
        self.backup("full", "testfiles/select2", options=["--include-globbing-filelist=testfiles/include.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)


class TestIncludeExcludedForContents(IncludeExcludeFunctionalTest):
    """ Test to check that folders that are excluded are included if they contain includes of higher priority.
     Exhibits the issue reported in Bug #1408411 (https://bugs.launchpad.net/duplicity/+bug/1408411). """

    def write_filelist(self, filelist_name):
        """Used by the below tests to write the filelist"""
        assert filelist_name is not None
        with open(filelist_name, 'w') as f:
            f.write("+ testfiles/select/1/2/1\n"
                    "- testfiles/select/1/2\n"
                    "- testfiles/select/1/1\n"
                    "- testfiles/select/1/3")

    def restore_and_check(self):
        """Restores the backup and compares to what was expected (based on the filelist in write_filelist)"""
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['2'], ['1']])

    def test_commandline_include_exclude(self):
        """test an excluded folder is included for included contents when using commandline includes and excludes"""
        self.backup("full", "testfiles/select/1",
                    options=["--include", "testfiles/select/1/2/1",
                             "--exclude", "testfiles/select/1/2",
                             "--exclude", "testfiles/select/1/1",
                             "--exclude", "testfiles/select/1/3"])
        self.restore_and_check()

    def test_include_globbing_filelist(self):
        """test an excluded folder is included for included contents with an include-globbing-filelist """
        # Deprecated, but include for now to ensure it keeps working until it is deliberately removed.
        self.write_filelist("testfiles/include.txt")
        self.backup("full", "testfiles/select/1", options=["--include-globbing-filelist=testfiles/include.txt"])
        self.restore_and_check()

    def test_exclude_globbing_filelist(self):
        """test an excluded folder is included for included contents with an exclude-globbing-filelist """
        # Deprecated, but include for now to ensure it keeps working until it is deliberately removed.
        self.write_filelist("testfiles/exclude.txt")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/exclude.txt"])
        self.restore_and_check()

    def test_include_filelist(self):
        """test an excluded folder is included for included contents with an include-filelist (non-globbing) """
        # Regression test for Bug #1408411 (https://bugs.launchpad.net/duplicity/+bug/1408411)
        self.write_filelist("testfiles/include.txt")
        self.backup("full", "testfiles/select/1", options=["--include-filelist=testfiles/include.txt"])
        self.restore_and_check()

    def test_exclude_filelist(self):
        """test an excluded folder is included for included contents with an exclude-filelist  (non-globbing) """
        # Regression test for Bug #1408411 (https://bugs.launchpad.net/duplicity/+bug/1408411)
        self.write_filelist("testfiles/exclude.txt")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/exclude.txt"])
        self.restore_and_check()


class TestAsterisks(IncludeExcludeFunctionalTest):
    """ Test to check that asterisks work as expected
     Exhibits the issue reported in Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371).
     See the unit tests for more granularity on the issue."""

    def restore_and_check(self):
        """Restores the backup and compares to what is expected."""
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['2'], ['1']])

    def test_exclude_filelist_asterisks_none(self):
        """Basic exclude filelist."""
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1\n"
                    "- testfiles/select/1/2\n"
                    "- testfiles/select/1/1\n"
                    "- testfiles/select/1/3")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_exclude_filelist_asterisks_single(self):
        """Exclude filelist with asterisks replacing folders."""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ */select/1/2/1\n"
                    "- */select/1/2\n"
                    "- testfiles/*/1/1\n"
                    "- */*/1/3")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_exclude_filelist_asterisks_double_asterisks(self):
        """Exclude filelist with double asterisks replacing folders."""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ **/1/2/1\n"
                    "- **/1/2\n"
                    "- **/select/1/1\n"
                    "- testfiles/select/1/3")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_commandline_asterisks_single_excludes_only(self):
        """test_commandline_include_exclude with single asterisks on exclude lines."""
        self.backup("full", "testfiles/select/1",
                    options=["--include", "testfiles/select/1/2/1",
                             "--exclude", "testfiles/*/1/2",
                             "--exclude", "*/select/1/1",
                             "--exclude", "*/select/1/3"])
        self.restore_and_check()

    def test_commandline_asterisks_single_both(self):
        """test_commandline_include_exclude with single asterisks on both exclude and include lines."""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.backup("full", "testfiles/select/1",
                    options=["--include", "*/select/1/2/1",
                             "--exclude", "testfiles/*/1/2",
                             "--exclude", "*/select/1/1",
                             "--exclude", "*/select/1/3"])
        self.restore_and_check()

    def test_commandline_asterisks_double_exclude_only(self):
        """test_commandline_include_exclude with double asterisks on exclude lines."""
        self.backup("full", "testfiles/select/1",
                    options=["--include", "testfiles/select/1/2/1",
                             "--exclude", "**/1/2",
                             "--exclude", "**/1/1",
                             "--exclude", "**/1/3"])
        self.restore_and_check()

    def test_commandline_asterisks_double_both(self):
        """test_commandline_include_exclude with double asterisks on both exclude and include lines."""
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.backup("full", "testfiles/select/1",
                    options=["--include", "**/1/2/1",
                             "--exclude", "**/1/2",
                             "--exclude", "**/1/1",
                             "--exclude", "**/1/3"])
        self.restore_and_check()

    def test_single_and_double_asterisks(self):
        """This compares a backup using --include-globbing-filelist with a single and double *."""
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select2/*\n"
                    "- testfiles/select")
        self.backup("full", "testfiles/", options=["--include-globbing-filelist=testfiles/filelist.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir + "/select2")
        with open("testfiles/filelist2.txt", 'w') as f:
            f.write("+ testfiles/select2/**\n"
                    "- testfiles/select")
        self.backup("full", "testfiles/", options=["--include-globbing-filelist=testfiles/filelist2.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored2 = self.directory_tree_to_list_of_lists(restore_dir + "/select2")
        self.assertEqual(restored, restored2)

    def test_single_and_double_asterisks_includes_excludes(self):
        """This compares a backup using --includes/--excludes with a single and double *."""
        self.backup("full", "testfiles/",
                    options=["--include", "testfiles/select2/*",
                             "--exclude", "testfiles/select"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir + "/select2")
        self.backup("full", "testfiles/",
                    options=["--include", "testfiles/select2/**",
                             "--exclude", "testfiles/select"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored2 = self.directory_tree_to_list_of_lists(restore_dir + "/select2")
        self.assertEqual(restored, restored2)


class TestTrailingSlash(IncludeExcludeFunctionalTest):
    """ Test to check that a trailing slash works as expected
     Exhibits the issue reported in Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)."""

    def restore_and_check(self):
        """Restores the backup and compares to what is expected."""
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['2'], ['1']])

    def test_exclude_filelist_trailing_slashes(self):
        """test_exclude_filelist_asterisks_none with trailing slashes."""
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1/\n"
                    "- testfiles/select/1/2/\n"
                    "- testfiles/select/1/1/\n"
                    "- testfiles/select/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_exclude_filelist_trailing_slashes_single_wildcards_excludes(self):
        """test_exclude_filelist_trailing_slashes with single wildcards in excludes."""
        # Regression test for Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1/\n"
                    "- */select/1/2/\n"
                    "- testfiles/*/1/1/\n"
                    "- */*/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_exclude_filelist_trailing_slashes_double_wildcards_excludes(self):
        """test_exclude_filelist_trailing_slashes with double wildcards in excludes."""
        # Regression test for Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1/\n"
                    "- **/1/2/\n"
                    "- **/1/1/\n"
                    "- **/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_exclude_filelist_trailing_slashes_double_wildcards_excludes_2(self):
        """second test_exclude_filelist_trailing_slashes with double wildcards in excludes."""
        # Regression test for Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482) and
        # Regression test for Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ **/1/2/1/\n"
                    "- **/1/2/\n"
                    "- **/1/1/\n"
                    "- **/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_exclude_filelist_trailing_slashes_wildcards(self):
        """test_commandline_asterisks_single_excludes_only with trailing slashes."""
        # Regression test for Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        self.backup("full", "testfiles/select/1",
                    options=["--include", "testfiles/select/1/2/1/",
                             "--exclude", "testfiles/*/1/2/",
                             "--exclude", "*/select/1/1/",
                             "--exclude", "*/select/1/3/"])
        self.restore_and_check()


class TestTrailingSlash2(IncludeExcludeFunctionalTest):
    """ This tests the behaviour of globbing strings with a trailing slash"""
    # See Bug #1479545 (https://bugs.launchpad.net/duplicity/+bug/1479545)

    def test_no_trailing_slash(self):
        """ Test that including 1.py works as expected"""
        self.backup("full", "testfiles/select2",
                    options=["--include", "testfiles/select2/1.py",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1.py']])

    def test_trailing_slash(self):
        """ Test that globs with a trailing slash only match directories"""
        # Regression test for Bug #1479545
        # (https://bugs.launchpad.net/duplicity/+bug/1479545)
        self.backup("full", "testfiles/select2",
                    options=["--include", "testfiles/select2/1.py/",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [])

    def test_include_files_not_subdirectories(self):
        """ Test that a trailing slash glob followed by a * glob only matches
        files and not subdirectories"""
        self.backup("full", "testfiles/select2",
                    options=["--exclude", "testfiles/select2/*/",
                             "--include", "testfiles/select2/*",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1.doc', '1.py']])

    def test_include_subdirectories_not_files(self):
        """ Test that a trailing slash glob only matches directories"""
        self.backup("full", "testfiles/select2",
                    options=["--include", "testfiles/select2/1/1sub1/**/",
                             "--exclude", "testfiles/select2/1/1sub1/**",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1'], ['1sub1'],
                                    ['1sub1sub1', '1sub1sub2', '1sub1sub3']])


class TestGlobbingReplacement(IncludeExcludeFunctionalTest):
    """ This tests the behaviour of the extended shell globbing pattern replacement functions."""
    # See the manual for a description of behaviours, but in summary:
    # * can be expanded to any string of characters not containing "/"
    # ? expands to any character except "/" and
    # [...] expands to a single character of those characters specified (ranges are acceptable).
    # The new special pattern, **, expands to any string of characters whether or not it contains "/".
    # Furthermore, if the pattern starts with "ignorecase:" (case insensitive), then this prefix will be
    # removed and any character in the string can be replaced with an upper- or lowercase version of itself.

    def test_globbing_replacement_in_includes(self):
        """ Test behaviour of the extended shell globbing pattern replacement functions in both include and exclude"""
        # Identical to test_include_exclude_basic with globbing characters added to both include and exclude lines
        # Exhibits the issue reported in Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371).
        # See above and the unit tests for more granularity on the issue.
        self.backup("full", "testfiles/select2",
                    options=["--include", "testfiles/select2/**/3sub3sub2/3sub3su?2_file.txt",  # Note ** and ? added
                             "--exclude", "testfiles/select2/*/3s*1",  # Note * added in both directory and filename
                             "--exclude", "testfiles/select2/**/2sub1sub3",  # Note ** added
                             "--exclude", "ignorecase:testfiles/select2/2/2sub1/2Sub1Sub2",  # Note ignorecase added
                             "--include", "ignorecase:testfiles/sel[w,u,e,q]ct2/2/2S?b1",    # Note ignorecase, [] and
                             # ? added
                             "--exclude", "testfiles/select2/1/1sub3/1s[w,u,p,q]b3sub2",  # Note [] added
                             "--exclude", "testfiles/select2/1/1sub[1-4]/1sub3sub1",  # Note [range] added
                             "--include", "testfiles/select2/*/1sub2/1s[w,u,p,q]b2sub1",  # Note * and [] added
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub3/1su?1sub3_file.txt",  # Note ? added
                             "--exclude", "testfiles/select2/1/1*1/1sub1sub2",  # Note * added
                             "--exclude", "testfiles/select2/1/1sub2",
                             "--include", "testfiles/select[2-4]/*.py",  # Note * and [range] added
                             "--include", "testfiles/*2/3",  # Note * added
                             "--include", "**/select2/1",  # Note ** added
                             "--exclude", "testfiles/select2/**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)


class TestExcludeIfPresent(IncludeExcludeFunctionalTest):
    """ This tests the behaviour of duplicity's --exclude-if-present option"""

    def test_exclude_if_present_baseline(self):
        """ Test that duplicity normally backs up files"""
        with open("testfiles/select2/1/1sub1/1sub1sub1/.nobackup", "w") as tag:
            tag.write("Files in this folder should not be backed up.")
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--include", "testfiles/select2/1/1sub1/1sub1sub1/*",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1sub1sub1'],
                                    ['.nobackup', '1sub1sub1_file.txt']])

    def test_exclude_if_present_excludes(self):
        """ Test that duplicity excludes files with relevant tag"""
        with open("testfiles/select2/1/1sub1/1sub1sub1/.nobackup", "w") as tag:
            tag.write("Files in this folder should not be backed up.")
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--exclude-if-present", ".nobackup",
                             "--include", "testfiles/select2/1/1sub1/1sub1sub1/*",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [])

    def test_exclude_if_present_excludes_2(self):
        """ Test that duplicity excludes files with relevant tag"""
        with open("testfiles/select2/1/1sub1/1sub1sub1/EXCLUDE.tag", "w") as tag:
            tag.write("Files in this folder should also not be backed up.")
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--exclude-if-present", "EXCLUDE.tag",
                             "--include", "testfiles/select2/1/1sub1/1sub1sub1/*",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [])


class TestLockedFoldersNoError(IncludeExcludeFunctionalTest):
    """ This tests that inaccessible folders do not cause an error"""

    @unittest.skipUnless(platform.platform().startswith('Linux'),
                         'Skip on non-Linux systems')
    def test_locked_baseline(self):
        """ Test no error if locked in path but excluded"""
        folder_to_lock = "testfiles/select2/1/1sub1/1sub1sub3"
        initial_mode = os.stat(folder_to_lock).st_mode
        os.chmod(folder_to_lock, 0o0000)
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--include", "testfiles/select2/1/1sub1/1sub1sub1/*",
                             "--exclude", "**"])
        os.chmod(folder_to_lock, initial_mode)
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1sub1sub1'],
                                    ['1sub1sub1_file.txt']])

    @unittest.skipUnless(platform.platform().startswith('Linux'),
                         'Skip on non-Linux systems')
    def test_locked_excl_if_present(self):
        """ Test no error if excluded locked with --exclude-if-present"""
        # Regression test for Bug #1620085
        # https://bugs.launchpad.net/duplicity/+bug/1620085
        folder_to_lock = "testfiles/select2/1/1sub1/1sub1sub3"
        initial_mode = os.stat(folder_to_lock).st_mode
        os.chmod(folder_to_lock, 0o0000)
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--exclude-if-present", "EXCLUDE.tag",
                             "--include", "testfiles/select2/1/1sub1/1sub1sub1/*",
                             "--exclude", "**"])
        os.chmod(folder_to_lock, initial_mode)
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1sub1sub1'],
                                    ['1sub1sub1_file.txt']])


class TestFolderIncludesFiles(IncludeExcludeFunctionalTest):
    """ This tests that including a folder includes the files within it"""
    # https://bugs.launchpad.net/duplicity/+bug/1624725

    def test_includes_files(self):
        """This tests that including a folder includes the files within it"""
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--include", "testfiles/select2/1/1sub1/1sub1sub1",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1sub1sub1'],
                                    ['1sub1sub1_file.txt']])

    def test_includes_files_trailing_slash(self):
        """This tests that including a folder includes the files within it"""
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--include", "testfiles/select2/1/1sub1/1sub1sub1/",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1sub1sub1'],
                                    ['1sub1sub1_file.txt']])

    def test_includes_files_trailing_slash_globbing_chars(self):
        """Tests folder includes with globbing char and /"""
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--include", "testfiles/s?lect2/1/1sub1/1sub1sub1/",
                             "--exclude", "**"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['1sub1sub1'],
                                    ['1sub1sub1_file.txt']])

    def test_excludes_files_no_trailing_slash(self):
        """This tests that excluding a folder excludes the files within it"""
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--exclude", "testfiles/select2/1/1sub1/1sub1sub1",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub2",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub3",
                             "--include", "testfiles/select2/1/1sub1/1sub1**",
                             "--exclude", "testfiles/select2/1/1sub1/irrelevant.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [])

    def test_excludes_files_trailing_slash(self):
        """Excluding a folder excludes the files within it, if ends with /"""
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--exclude", "testfiles/select2/1/1sub1/1sub1sub1/",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub2/",
                             "--exclude", "testfiles/select2/1/1sub1/1sub1sub3/",
                             "--include", "testfiles/select2/1/1sub1/1sub1**",
                             "--exclude", "testfiles/select2/1/1sub1/irrelevant.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [])

    def test_excludes_files_trailing_slash_globbing_chars(self):
        """Tests folder excludes with globbing char and /"""
        self.backup("full", "testfiles/select2/1/1sub1",
                    options=["--exclude", "testfiles/sel?ct2/1/1sub1/1sub1sub1/",
                             "--exclude", "testfiles/sel[e,f]ct2/1/1sub1/1sub1sub2/",
                             "--exclude", "testfiles/sel*t2/1/1sub1/1sub1sub3/",
                             "--include", "testfiles/select2/1/1sub1/1sub1**",
                             "--exclude", "testfiles/select2/1/1sub1/irrelevant.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [])

if __name__ == "__main__":
    unittest.main()

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
import os.path
import unittest

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


class TestExcludeGlobbingFilelistTest(IncludeExcludeFunctionalTest):
    """
    Test --exclude-globbing-filelist using duplicity binary.
    """

    def test_exclude_globbing_filelist(self):
        """Test that exclude globbing filelist works in the basic case """
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
        self.backup("full", "testfiles/select2", options=["--exclude-globbing-filelist=testfiles/exclude.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_exclude_globbing_filelist_combined_imperfections(self):
        """Test that exclude globbing filelist works with imperfections in the input file"""
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

    def test_exclude_globbing_filelist_trailing_whitespace_folders_work_with_quotes(self):
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
        self.backup("full", "testfiles/select2", options=["--exclude-globbing-filelist=testfiles/exclude.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree_with_trailing_space)

    @unittest.expectedFailure
    def test_exclude_globbing_filelist_progress_option(self):
        """Test that exclude globbing filelist is unaffected by the --progress option"""
        # ToDo - currently fails. Bug #1264744 (https://bugs.launchpad.net/duplicity/+bug/1264744)
        # Create a filelist identical to that used in test_exclude_globbing_filelist
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

        # Backup the files exactly as in test_exclude_globbing_filelist, but with the --progress option
        self.backup("full", "testfiles/select2", options=["--exclude-globbing-filelist=testfiles/exclude.txt",
                                                          "--progress"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        # The restored files should match those restored in test_exclude_globbing_filelist
        self.assertEqual(restored, self.expected_restored_tree)

class TestIncludeGlobbingFilelistTest(IncludeExcludeFunctionalTest):
    """
    Test --include-globbing-filelist using duplicity binary.
    """

    def test_include_globbing_filelist(self):
        """Test that include globbing filelist works in the basic case"""
        # See test_exclude_globbing_filelist above for explanation of what is expected. As this is an include filelist
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
        self.backup("full", "testfiles/select2", options=["--include-globbing-filelist=testfiles/include.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_include_globbing_filelist_combined_imperfections(self):
        """Test that include globbing filelist works with imperfections in the input file"""
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


class TestIncludeFilelistTest(IncludeExcludeFunctionalTest):
    """
    Test --include-filelist using duplicity binary.
    """
    def test_include_filelist(self):
        """Test that include filelist works in the basic case"""
        # See test_exclude_globbing_filelist above for explanation of what is expected. As this is an include filelist
        # any lines with no +/- modifier should be treated as if they have a +.
        # Regression test for Bug #1408411 (https://bugs.launchpad.net/duplicity/+bug/1408411)
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
                    '- testfiles/select2/2\n'  # es instead of ea as no globbing - **
                    'testfiles/select2/1\n'
                    '- "testfiles/select2/trailing_space "\n'  # es instead of ea as no globbing - **
                    '- testfiles/select2/1.doc')  # es instead of ea as no globbing - **
        self.backup("full", "testfiles/select2", options=["--include-filelist=testfiles/include.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_include_filelist_workaround(self):
        """Test that include filelist works in the basic case"""
        # This is a modified version of test_include_filelist that passes, despite Bug #1408411
        # It is still a valid test, it just does not test as many selection features as the above.
        # Create a filelist
        with open('testfiles/include.txt', 'w') as f:
            f.write('testfiles/select2/3/3sub3/3sub3sub2/3sub3sub2_file.txt\n'
                    #  '- testfiles/select2/3/3sub3/3sub3sub2\n'  # Commented out because of Bug #1408411
                    'testfiles/select2/3/3sub2/3sub2sub2\n'
                    '+ testfiles/select2/3/3sub3\n'  # + added to ensure it makes no difference
                    '- testfiles/select2/3/3sub1\n'
                    '- testfiles/select2/2/2sub1/2sub1sub3\n'
                    '- testfiles/select2/2/2sub1/2sub1sub2\n'
                    'testfiles/select2/2/2sub1\n'
                    '- testfiles/select2/2/2sub3\n'  # Added because of Bug #1408411
                    '- testfiles/select2/2/2sub2\n'  # Added because of Bug #1408411
                    '- testfiles/select2/1/1sub3/1sub3sub2\n'
                    '- testfiles/select2/1/1sub3/1sub3sub1\n'
                    '- testfiles/select2/1/1sub2/1sub2sub3\n'
                    '- testfiles/select2/1/1sub2/1sub2sub2\n'  # Added because of Bug #1408411
                    '+ testfiles/select2/1/1sub2/1sub2sub1\n'  # + added to ensure it makes no difference
                    '- testfiles/select2/1/1sub1/1sub1sub3/1sub1sub3_file.txt\n'
                    '- testfiles/select2/1/1sub1/1sub1sub2\n'
                    #  '- testfiles/select2/1/1sub2\n'  # Commented out because of Bug #1408411
                    'testfiles/select2/1.py\n'
                    'testfiles/select2/3\n'
                    #  '- testfiles/select2/2\n' # Commented out because of Bug #1408411
                    'testfiles/select2/1\n'
                    '- "testfiles/select2/trailing_space "\n'  # es instead of ea as no globbing - **
                    '- testfiles/select2/1.doc')  # es instead of ea as no globbing - **
        self.backup("full", "testfiles/select2", options=["--include-filelist=testfiles/include.txt"])
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, self.expected_restored_tree)

    def test_include_filelist_workaround_combined_imperfections(self):
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
                    '- "testfiles/select2/trailing_space "\n'  # es instead of ea as no globbing - **
                    '- testfiles/select2/1.doc')  # es instead of ea as no globbing - **
        self.backup("full", "testfiles/select2", options=["--include-filelist=testfiles/include.txt"])
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
        self.write_filelist("testfiles/include.txt")
        self.backup("full", "testfiles/select/1", options=["--include-globbing-filelist=testfiles/include.txt"])
        self.restore_and_check()

    def test_exclude_globbing_filelist(self):
        """test an excluded folder is included for included contents with an exclude-globbing-filelist """
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

    def test_exclude_globbing_filelist_asterisks_none(self):
        """Basic exclude globbing filelist."""
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1\n"
                    "- testfiles/select/1/2\n"
                    "- testfiles/select/1/1\n"
                    "- testfiles/select/1/3")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    @unittest.expectedFailure
    def test_exclude_globbing_filelist_asterisks_single(self):
        """Exclude globbing filelist with asterisks replacing folders."""
        # Todo: Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ */select/1/2/1\n"
                    "- */select/1/2\n"
                    "- testfiles/*/1/1\n"
                    "- */*/1/3")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    @unittest.expectedFailure
    def test_exclude_globbing_filelist_asterisks_double_asterisks(self):
        """Exclude globbing filelist with double asterisks replacing folders."""
        # Todo: Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ **/1/2/1\n"
                    "- **/1/2\n"
                    "- **/select/1/1\n"
                    "- testfiles/select/1/3")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    def test_commandline_asterisks_single_excludes_only(self):
        """test_commandline_include_exclude with single asterisks on exclude lines."""
        self.backup("full", "testfiles/select/1",
                    options=["--include", "testfiles/select/1/2/1",
                             "--exclude", "testfiles/*/1/2",
                             "--exclude", "*/select/1/1",
                             "--exclude", "*/select/1/3"])
        self.restore_and_check()

    @unittest.expectedFailure
    def test_commandline_asterisks_single_both(self):
        """test_commandline_include_exclude with single asterisks on both exclude and include lines."""
        # Todo: Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
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

    @unittest.expectedFailure
    def test_commandline_asterisks_double_both(self):
        """test_commandline_include_exclude with double asterisks on both exclude and include lines."""
        # Todo: Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        self.backup("full", "testfiles/select/1",
                    options=["--include", "**/1/2/1",
                             "--exclude", "**/1/2",
                             "--exclude", "**/1/1",
                             "--exclude", "**/1/3"])
        self.restore_and_check()

class TestTrailingSlash(IncludeExcludeFunctionalTest):
    """ Test to check that a trailing slash works as expected
     Exhibits the issue reported in Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)."""

    def restore_and_check(self):
        """Restores the backup and compares to what is expected."""
        self.restore()
        restore_dir = 'testfiles/restore_out'
        restored = self.directory_tree_to_list_of_lists(restore_dir)
        self.assertEqual(restored, [['2'], ['1']])

    def test_exclude_globbing_filelist_trailing_slashes(self):
        """test_exclude_globbing_filelist_asterisks_none with trailing slashes."""
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1/\n"
                    "- testfiles/select/1/2/\n"
                    "- testfiles/select/1/1/\n"
                    "- testfiles/select/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    @unittest.expectedFailure
    def test_exclude_globbing_filelist_trailing_slashes_single_wildcards_excludes(self):
        """test_exclude_globbing_filelist_trailing_slashes with single wildcards in excludes."""
        # Todo: Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1/\n"
                    "- */select/1/2/\n"
                    "- testfiles/*/1/1/\n"
                    "- */*/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    @unittest.expectedFailure
    def test_exclude_globbing_filelist_trailing_slashes_double_wildcards_excludes(self):
        """test_exclude_globbing_filelist_trailing_slashes with double wildcards in excludes."""
        # Todo: Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ testfiles/select/1/2/1/\n"
                    "- **/1/2/\n"
                    "- **/1/1/\n"
                    "- **/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    @unittest.expectedFailure
    def test_exclude_globbing_filelist_trailing_slashes_double_wildcards_excludes(self):
        """test_exclude_globbing_filelist_trailing_slashes with double wildcards in excludes."""
        # Todo: Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482) and likely
        # Todo: Bug #884371 (https://bugs.launchpad.net/duplicity/+bug/884371)
        with open("testfiles/filelist.txt", 'w') as f:
            f.write("+ **/1/2/1/\n"
                    "- **/1/2/\n"
                    "- **/1/1/\n"
                    "- **/1/3/")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/filelist.txt"])
        self.restore_and_check()

    @unittest.expectedFailure
    def test_exclude_globbing_filelist_trailing_slashes_wildcards(self):
        """test_commandline_asterisks_single_excludes_only with trailing slashes."""
         # Todo: Bug #932482 (https://bugs.launchpad.net/duplicity/+bug/932482)
        self.backup("full", "testfiles/select/1",
                    options=["--include", "testfiles/select/1/2/1/",
                             "--exclude", "testfiles/*/1/2/",
                             "--exclude", "*/select/1/1/",
                             "--exclude", "*/select/1/3/"])
        self.restore_and_check()



if __name__ == "__main__":
    unittest.main()

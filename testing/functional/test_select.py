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

class TestIncludeExcludedForContents(FunctionalTestCase):
    """ Test to check that folders that are excluded are included if they contain includes of higher priority.
     Exhibits the issue reported in Bug #1408411 (https://bugs.launchpad.net/duplicity/+bug/1408411). """

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
        """test that simple test works with commandline includes and excludes"""
        self.backup("full", "testfiles/select/1",
                    options=["--include", "testfiles/select/1/2/1",
                             "--exclude", "testfiles/select/1/2",
                             "--exclude", "testfiles/select/1/1",
                             "--exclude", "testfiles/select/1/3"])
        self.restore_and_check()

    def test_include_globbing_filelist(self):
        """test that the same test works with an include-globbing-filelist """
        self.write_filelist("testfiles/include.txt")
        self.backup("full", "testfiles/select/1", options=["--include-globbing-filelist=testfiles/include.txt"])
        self.restore_and_check()

    def test_exclude_globbing_filelist(self):
        """test that the same test works with an exclude-globbing-filelist """
        self.write_filelist("testfiles/exclude.txt")
        self.backup("full", "testfiles/select/1", options=["--exclude-globbing-filelist=testfiles/exclude.txt"])
        self.restore_and_check()

    # def test_include_filelist(self):
    #     """test that the same test works with an include-filelist (non-globbing) """
    #     # ToDo - currently fails - Bug #1408411 (https://bugs.launchpad.net/duplicity/+bug/1408411)
    #     self.write_filelist("testfiles/include.txt")
    #     self.backup("full", "testfiles/select/1", options=["--include-filelist=testfiles/include.txt"])
    #     self.restore_and_check()
    #
    # def test_exclude_filelist(self):
    #     """test that the same test works with an exclude-filelist  (non-globbing) """
    #     # ToDo - currently fails - Bug #1408411 (https://bugs.launchpad.net/duplicity/+bug/1408411)
    #     self.write_filelist("testfiles/exclude.txt")
    #     self.backup("full", "testfiles/select/1", options=["--exclude-filelist=testfiles/exclude.txt"])
    #     self.restore_and_check()

if __name__ == "__main__":
    unittest.main()

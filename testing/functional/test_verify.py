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

import os
import unittest

from duplicity import path
from . import CmdError, FunctionalTestCase


class VerifyTest(FunctionalTestCase):
    """
    Test verify using duplicity binary
    """
    def runtest(self, dirlist, backup_options = [], restore_options = []):
        """Run backup/restore test on directories in dirlist
        This is identical to test_final.runtest"""
        assert len(dirlist) >= 1

        # Back up directories to local backend
        current_time = 100000
        self.backup("full", dirlist[0], current_time = current_time,
                    options = backup_options)
        for new_dir in dirlist[1:]:
            current_time += 100000
            self.backup("inc", new_dir, current_time = current_time,
                        options = backup_options)

        # Restore each and compare them
        for i in range(len(dirlist)):
            dirname = dirlist[i]
            current_time = 100000*(i + 1)
            self.restore(time = current_time, options = restore_options)
            self.check_same(dirname, "testfiles/restore_out")
            self.verify(dirname,
                        time = current_time, options = restore_options)

    def check_same(self, filename1, filename2):
        """Verify two filenames are the same
        This is identical to test_final.check_same"""
        path1, path2 = path.Path(filename1), path.Path(filename2)
        assert path1.compare_recursive(path2, verbose = 1)

    def test_verify(self, backup_options = [], restore_options = []):
        """Test that verify works in the basic case"""
        self.runtest(["testfiles/dir1",
                      "testfiles/dir2"],
                     backup_options = backup_options,
                     restore_options = restore_options)

        # Test verify for various sub files
        for filename, dir in [('new_file', 'dir2'),
                              ('executable', 'dir1')]:
            self.verify('testfiles/%s/%s' % (dir, filename),
                        file_to_verify = filename, options = restore_options)

    # def test_verify_compare_data(self, backup_options = [], restore_options = []):
    #     """Test that verify works in the basic case when the --compare-data option is used"""
    #     self.runtest(["testfiles/dir1",
    #                   "testfiles/dir2"],
    #                  backup_options = backup_options,
    #                  restore_options = restore_options)
    #
    #     # Test verify for various sub files with --compare-data
    #     restore_options.extend("--compare-data")
    #     for filename, dir in [('new_file', 'dir2'),
    #                           ('executable', 'dir1')]:
    #         self.verify('testfiles/%s/%s' % (dir, filename),
    #                     file_to_verify = filename, options = restore_options)

    def test_verify_changed_source_file(self, backup_options = [], restore_options = []):
        """Test verify gives no error if a source files is changed (without --compare-data)"""
        self.runtest(["testfiles/dir1",
                      "testfiles/dir2"],
                     backup_options = backup_options,
                     restore_options = restore_options)

        # Edit source file for one of the files.
        f = open('testfiles/dir2/new_file', 'w')
        f.write('This changes a source file.')

        # Test verify for various sub files
        for filename, dir in [('new_file', 'dir2'),
                              ('executable', 'dir1')]:
            self.verify('testfiles/%s/%s' % (dir, filename),
                        file_to_verify = filename, options = restore_options)

if __name__ == "__main__":
    unittest.main()

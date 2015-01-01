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

from . import CmdError, FunctionalTestCase


class VerifyTest(FunctionalTestCase):
    """
    Test verify using duplicity binary
    """
    def test_verify(self):
        """Test that verify (without --compare-data) works in the basic case"""
        self.backup("full", "testfiles/various_file_types", options=[])
        self.verify('testfiles/various_file_types/executable', file_to_verify='executable', options=[])

    def test_verify_changed_source_file(self):
        """Test verify (without --compare-data) gives no error if a source file is changed"""
        # This test was made to pass in fixing Bug #1354880
        self.backup("full", "testfiles/various_file_types", options=[])

        # Edit source file
        with open('testfiles/various_file_types/executable', 'r+') as f:
            f.write('This changes a source file.')

        # Test verify for the file
        self.verify('testfiles/various_file_types/executable', file_to_verify='executable', options=[])

    def test_verify_changed_source_file_adjust_mtime(self):
        """Test verify (without --compare-data) gives no error if a source file is changed and the mtime is changed
        (changing anything about the source files shouldn't matter)"""

        # Get the atime and mtime of the file
        file_info = os.stat('testfiles/various_file_types/executable')

        # Set the atime and mtime of the file to the time that we collected, as on some systems
        # the times from a stat call don't match what a utime will set.
        os.utime('testfiles/various_file_types/executable', (file_info.st_atime, file_info.st_mtime))

        self.backup("full", "testfiles/various_file_types", options=[])

        # Edit source file
        with open('testfiles/various_file_types/executable', 'r+') as f:
            f.write('This changes a source file.')

        # Set the atime and mtime for the file back to what it was prior to the edit
        os.utime('testfiles/various_file_types/executable', (file_info.st_atime, file_info.st_mtime))

        # Test verify for the file
        self.verify('testfiles/various_file_types/executable', file_to_verify='executable', options=[])

    def test_verify_compare_data(self):
        """Test that verify works in the basic case when the --compare-data option is used"""
        self.backup("full", "testfiles/various_file_types", options=[])

        # Test verify for the file with --compare-data
        self.verify('testfiles/various_file_types/executable', file_to_verify='executable',
                    options=["--compare-data"])

    def test_verify_compare_data_changed_source_file(self):
        """Test verify with --compare-data gives an error if a source file is changed"""
        self.backup("full", "testfiles/various_file_types", options=[])

        # Edit source file
        with open('testfiles/various_file_types/executable', 'r+') as f:
            f.write('This changes a source file.')

        # Test verify for edited file fails with --compare-data
        try:
            self.verify('testfiles/various_file_types/executable', file_to_verify='executable',
                        options=["--compare-data"])
        except CmdError as e:
            self.assertEqual(e.exit_status, 1, str(e))
        else:
            self.fail('Expected CmdError not thrown')

    def test_verify_compare_data_changed_source_file_adjust_mtime(self):
        """Test verify with --compare-data gives an error if a source file is changed, even if the mtime is changed"""

        # Get the atime and mtime of the file
        file_info = os.stat('testfiles/various_file_types/executable')

        # Set the atime and mtime of the file to the time that we collected, as on some systems
        # the times from a stat call don't match what a utime will set
        os.utime('testfiles/various_file_types/executable', (file_info.st_atime, file_info.st_mtime))

        self.backup("full", "testfiles/various_file_types", options=[])
        # Edit source file
        with open('testfiles/various_file_types/executable', 'r+') as f:
            f.write('This changes a source file.')

        # Set the atime and mtime for the file back to what it was prior to the edit
        os.utime('testfiles/various_file_types/executable', (file_info.st_atime, file_info.st_mtime))

        # Test verify for edited file fails with --compare-data
        try:
            self.verify('testfiles/various_file_types/executable', file_to_verify='executable',
                        options=["--compare-data"])
        except CmdError as e:
            self.assertEqual(e.exit_status, 1, str(e))
        else:
            self.fail('Expected CmdError not thrown')

    def test_verify_corrupt_archive(self):
        """Test verify (without --compare-data) gives an error if the archive is corrupted"""
        self.backup("full", "testfiles/various_file_types", options=[])
        output_files = os.listdir("testfiles/output")
        archives = [elem for elem in output_files if "vol" in elem]
        for archive in archives:
            # Edit source file
            with open("testfiles/output/" + archive, 'r+') as f:
                f.write('This writes text into each archive file to corrupt it.')
        # Test verify for the file
        try:
            self.verify('testfiles/various_file_types/executable', file_to_verify='executable', options=[])
        except CmdError as e:
            # Should return a 21 error code for "hash mismatch"
            self.assertEqual(e.exit_status, 21, str(e))
        else:
            self.fail('Expected Hash Mismatch Error not thrown')

    def test_verify_corrupt_archive_compare_data(self):
        """Test verify with --compare-data gives an error if the archive is corrupted"""
        self.backup("full", "testfiles/various_file_types", options=[])
        output_files = os.listdir("testfiles/output")
        archives = [elem for elem in output_files if "vol" in elem]
        for archive in archives:
            # Edit source file
            with open("testfiles/output/" + archive, 'r+') as f:
                f.write('This writes text into each archive file to corrupt it.')
        # Test verify for the file
        try:
            self.verify('testfiles/various_file_types/executable', file_to_verify='executable',
                        options=["--compare-data"])
        except CmdError as e:
            # Should return a 21 error code for "hash mismatch"
            self.assertEqual(e.exit_status, 21, str(e))
        else:
            self.fail('Expected Hash Mismatch Error not thrown')

if __name__ == "__main__":
    unittest.main()

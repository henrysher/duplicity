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

import os
import unittest

from duplicity import path
from . import CmdError, FunctionalTestCase


class ReplicateTest(FunctionalTestCase):
    """
    Test backup/replicate/restore using duplicity binary
    """

    def runtest(self, dirlist, backup_options=[], replicate_options=[], restore_options=[]):
        # Back up directories to local backend
        current_time = 100000
        self.backup("full", dirlist[0], current_time=current_time,
                    options=backup_options)
        for new_dir in dirlist[1:]:
            current_time += 100000
            self.backup("inc", new_dir, current_time=current_time,
                        options=backup_options)

        # Replicate to other backend
        source_url = self.backend_url
        target_url = "file://testfiles/replicate_out"
        self.run_duplicity(options=["replicate"] +
                           replicate_options + [source_url, target_url])

        self.backend_url = target_url

        # Restore each and compare them
        for i in range(len(dirlist)):
            dirname = dirlist[i]
            current_time = 100000 * (i + 1)
            self.restore(time=current_time, options=restore_options)
            self.check_same(dirname, "testfiles/restore_out")
            self.verify(dirname,
                        time=current_time, options=restore_options)

    def check_same(self, filename1, filename2):
        """Verify two filenames are the same"""
        path1, path2 = path.Path(filename1), path.Path(filename2)
        assert path1.compare_recursive(path2, verbose=1)

    def test_replicate(self):
        """Test replication"""
        self.runtest(["testfiles/dir1", "testfiles/dir2"])

    def test_replicate_noencryption(self):
        """Test replication with decryption"""
        self.runtest(["testfiles/dir1", "testfiles/dir2"],
                     replicate_options=["--no-encryption"])

    def test_replicate_asym(self):
        """Test replication with reencryption"""
        asym_options = ["--encrypt-key", self.encrypt_key1]
        self.runtest(["testfiles/dir1", "testfiles/dir2"],
                     replicate_options=asym_options, restore_options=asym_options)

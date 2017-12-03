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


class FinalTest(FunctionalTestCase):
    """
    Test backup/restore using duplicity binary
    """
    def runtest(self, dirlist, backup_options=[], restore_options=[]):
        """Run backup/restore test on directories in dirlist"""
        assert len(dirlist) >= 1

        # Back up directories to local backend
        current_time = 100000
        self.backup(u"full", dirlist[0], current_time=current_time,
                    options=backup_options)
        for new_dir in dirlist[1:]:
            current_time += 100000
            self.backup(u"inc", new_dir, current_time=current_time,
                        options=backup_options)

        # Restore each and compare them
        for i in range(len(dirlist)):
            dirname = dirlist[i]
            current_time = 100000 * (i + 1)
            self.restore(time=current_time, options=restore_options)
            self.check_same(dirname, u"testfiles/restore_out")
            self.verify(dirname,
                        time=current_time, options=restore_options)

    def check_same(self, filename1, filename2):
        """Verify two filenames are the same"""
        path1, path2 = path.Path(filename1), path.Path(filename2)
        assert path1.compare_recursive(path2, verbose=1)

    def test_basic_cycle(self, backup_options=[], restore_options=[]):
        """Run backup/restore test on basic directories"""
        self.runtest([u"testfiles/dir1",
                      u"testfiles/dir2",
                      u"testfiles/dir3"],
                     backup_options=backup_options,
                     restore_options=restore_options)

        # Test restoring various sub files
        for filename, time, dir in [(u'symbolic_link', 99999, u'dir1'),
                                    (u'directory_to_file', 100100, u'dir1'),
                                    (u'directory_to_file', 200100, u'dir2'),
                                    (u'largefile', 300000, u'dir3')]:
            self.restore(filename, time, options=restore_options)
            self.check_same(u'testfiles/%s/%s' % (dir, filename),
                            u'testfiles/restore_out')
            self.verify(u'testfiles/%s/%s' % (dir, filename),
                        file_to_verify=filename, time=time,
                        options=restore_options)

    def test_asym_cycle(self):
        """Like test_basic_cycle but use asymmetric encryption and signing"""
        backup_options = [u"--encrypt-key", self.encrypt_key1,
                          u"--sign-key", self.sign_key]
        restore_options = [u"--encrypt-key", self.encrypt_key1,
                           u"--sign-key", self.sign_key]
        self.test_basic_cycle(backup_options=backup_options,
                              restore_options=restore_options)

    def test_asym_with_hidden_recipient_cycle(self):
        """Like test_basic_cycle but use asymmetric encryption (hiding key id) and signing"""
        backup_options = [u"--hidden-encrypt-key", self.encrypt_key1,
                          u"--sign-key", self.sign_key]
        restore_options = [u"--hidden-encrypt-key", self.encrypt_key1,
                           u"--sign-key", self.sign_key]
        self.test_basic_cycle(backup_options=backup_options,
                              restore_options=restore_options)

    def test_single_regfile(self):
        """Test backing and restoring up a single regular file"""
        self.runtest([u"testfiles/various_file_types/regular_file"])

    def test_empty_backup(self):
        """Make sure backup works when no files change"""
        self.backup(u"full", u"testfiles/empty_dir")
        self.backup(u"inc", u"testfiles/empty_dir")

    def test_long_filenames(self):
        """Test backing up a directory with long filenames in it"""
        # Note that some versions of ecryptfs (at least through Ubuntu 11.10)
        # have a bug where they treat the max path segment length as 143
        # instead of 255.  So make sure that these segments don't break that.
        lf_dir = path.Path(u"testfiles/long_filenames")
        if lf_dir.exists():
            lf_dir.deltree()
        lf_dir.mkdir()
        lf1 = lf_dir.append("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        lf1.mkdir()
        lf2 = lf1.append("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
        lf2.mkdir()
        lf3 = lf2.append("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
        lf3.mkdir()
        lf4 = lf3.append("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        lf4.touch()
        lf4_1 = lf3.append("SYMLINK--------------------------------------------------------------------------------------------")
        os.symlink("SYMLINK-DESTINATION-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------", lf4_1.name)
        lf4_1.setdata()
        assert lf4_1.issym()
        lf4_2 = lf3.append("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        fp = lf4_2.open("wb")
        fp.write("hello" * 1000)
        assert not fp.close()

        self.runtest([u"testfiles/empty_dir", lf_dir.uc_name,
                      u"testfiles/empty_dir", lf_dir.uc_name])

    def test_empty_restore(self):
        """Make sure error raised when restore doesn't match anything"""
        self.backup(u"full", u"testfiles/dir1")
        self.assertRaises(CmdError, self.restore, u"this_file_does_not_exist")
        self.backup(u"inc", u"testfiles/empty_dir")
        self.assertRaises(CmdError, self.restore, u"this_file_does_not_exist")

    def test_remove_older_than(self):
        """Test removing old backup chains"""
        first_chain = self.backup(u"full", u"testfiles/dir1", current_time=10000)
        first_chain |= self.backup(u"inc", u"testfiles/dir2", current_time=20000)
        second_chain = self.backup(u"full", u"testfiles/dir1", current_time=30000)
        second_chain |= self.backup(u"inc", u"testfiles/dir3", current_time=40000)

        self.assertEqual(self.get_backend_files(), first_chain | second_chain)

        self.run_duplicity(options=[u"remove-older-than", u"35000", u"--force", self.backend_url])
        self.assertEqual(self.get_backend_files(), second_chain)

        # Now check to make sure we can't delete only chain
        self.run_duplicity(options=[u"remove-older-than", u"50000", u"--force", self.backend_url])
        self.assertEqual(self.get_backend_files(), second_chain)

    def test_piped_password(self):
        """Make sure that prompting for a password works"""
        self.set_environ(u"PASSPHRASE", None)
        self.backup(u"full", u"testfiles/empty_dir",
                    passphrase_input=[self.sign_passphrase, self.sign_passphrase])
        self.restore(passphrase_input=[self.sign_passphrase])


class OldFilenamesFinalTest(FinalTest):

    def setUp(self):
        super(OldFilenamesFinalTest, self).setUp()
        self.class_args.extend([u"--old-filenames"])


class ShortFilenamesFinalTest(FinalTest):

    def setUp(self):
        super(ShortFilenamesFinalTest, self).setUp()
        self.class_args.extend([u"--short-filenames"])

if __name__ == "__main__":
    unittest.main()

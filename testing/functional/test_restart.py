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

import glob
import os
import platform
import subprocess
import unittest

from . import FunctionalTestCase


class RestartTest(FunctionalTestCase):
    """
    Test checkpoint/restart using duplicity binary
    """
    def test_basic_checkpoint_restart(self):
        """
        Test basic Checkpoint/Restart
        """
        self.make_largefiles()
        self.backup("full", "testfiles/largefiles", fail=1)
        self.backup("full", "testfiles/largefiles")
        self.verify("testfiles/largefiles")

    def test_multiple_checkpoint_restart(self):
        """
        Test multiple Checkpoint/Restart
        """
        self.make_largefiles()
        self.backup("full", "testfiles/largefiles", fail=1)
        self.backup("full", "testfiles/largefiles", fail=2)
        self.backup("full", "testfiles/largefiles", fail=3)
        self.backup("full", "testfiles/largefiles")
        self.verify("testfiles/largefiles")

    def test_first_volume_failure(self):
        """
        Test restart when no volumes are available on the remote.
        Caused when duplicity fails before the first transfer.
        """
        self.make_largefiles()
        self.backup("full", "testfiles/largefiles", fail=1)
        assert not os.system("rm testfiles/output/duplicity-full*difftar*")
        self.backup("full", "testfiles/largefiles")
        self.verify("testfiles/largefiles")

    def test_multi_volume_failure(self):
        """
        Test restart when fewer volumes are available on the remote
        than the local manifest has on record.  Caused when duplicity
        fails the last queued transfer(s).
        """
        self.make_largefiles()
        self.backup("full", "testfiles/largefiles", fail=3)
        assert not os.system("rm testfiles/output/duplicity-full*vol[23].difftar*")
        self.backup("full", "testfiles/largefiles")
        self.verify("testfiles/largefiles")

    def test_restart_sign_and_encrypt(self):
        """
        Test restarting a backup using same key for sign and encrypt
        https://bugs.launchpad.net/duplicity/+bug/946988
        """
        self.make_largefiles()
        enc_opts = ["--sign-key", self.sign_key, "--encrypt-key", self.sign_key]
        self.backup("full", "testfiles/largefiles", options=enc_opts, fail=2)
        self.backup("full", "testfiles/largefiles", options=enc_opts)
        self.verify("testfiles/largefiles")

    def test_restart_sign_and_hidden_encrypt(self):
        """
        Test restarting a backup using same key for sign and encrypt (hidden key id)
        https://bugs.launchpad.net/duplicity/+bug/946988
        """
        self.make_largefiles()
        enc_opts = ["--sign-key", self.sign_key, "--hidden-encrypt-key", self.sign_key]
        self.backup("full", "testfiles/largefiles", options=enc_opts, fail=2)
        self.backup("full", "testfiles/largefiles", options=enc_opts)
        self.verify("testfiles/largefiles")

    def test_last_file_missing_in_middle(self):
        """
        Test restart when the last file being backed up is missing on restart.
        Caused when the user deletes a file after a failure.  This test puts
        the file in the middle of the backup, with files following.
        """
        self.make_largefiles()
        self.backup("full", "testfiles/largefiles", fail=3)
        assert not os.system("rm testfiles/largefiles/file2")
        self.backup("full", "testfiles/largefiles")
        # TODO: we can't verify but we need to to check for other errors that might show up
        # there should be 2 differences found, one missing file, one mtime change
        # self.verify("testfiles/largefiles")

    def test_last_file_missing_at_end(self):
        """
        Test restart when the last file being backed up is missing on restart.
        Caused when the user deletes a file after a failure.  This test puts
        the file at the end of the backup, with no files following.
        """
        self.make_largefiles()
        self.backup("full", "testfiles/largefiles", fail=6)
        assert not os.system("rm testfiles/largefiles/file3")
        self.backup("full", "testfiles/largefiles")
        # TODO: we can't verify but we need to to check for other errors that might show up
        # there should be 2 differences found, one missing file, one mtime change
        # self.verify("testfiles/largefiles")

    def test_restart_incremental(self):
        """
        Test restarting an incremental backup
        """
        self.make_largefiles()
        self.backup("full", "testfiles/dir1")
        self.backup("inc", "testfiles/largefiles", fail=2)
        self.backup("inc", "testfiles/largefiles")
        self.verify("testfiles/largefiles")

    def make_fake_second_volume(self, name):
        """
        Takes a successful backup and pretend that we interrupted a backup
        after two-volumes.  (This is because we want to be able to model
        restarting the second volume and duplicity deletes the last volume
        found because it may have not finished uploading.)
        """
        # First, confirm that we have signs of a successful backup
        self.assertEqual(len(glob.glob("testfiles/output/*.manifest*")), 1)
        self.assertEqual(len(glob.glob("testfiles/output/*.sigtar*")), 1)
        self.assertEqual(len(glob.glob("testfiles/cache/%s/*" % name)), 3)
        self.assertEqual(len(glob.glob(
            "testfiles/cache/%s/*.manifest*" % name)), 1)
        self.assertEqual(len(glob.glob(
            "testfiles/cache/%s/*.sigtar*" % name)), 1)
        # Alright, everything is in order; fake a second interrupted volume
        assert not os.system("rm testfiles/output/*.manifest*")
        assert not os.system("rm testfiles/output/*.sigtar*")
        assert not os.system("rm -f testfiles/output/*.vol[23456789].*")
        assert not os.system("rm -f testfiles/output/*.vol1[^.]+.*")
        self.assertEqual(len(glob.glob("testfiles/output/*.difftar*")), 1)
        assert not os.system("rm testfiles/cache/%s/*.sigtar*" % name)
        assert not os.system("cp testfiles/output/*.difftar* "
                             "`ls testfiles/output/*.difftar* | "
                             " sed 's|vol1|vol2|'`")
        assert not os.system("head -n6 testfiles/cache/%s/*.manifest > "
                             "testfiles/cache/%s/"
                             "`basename testfiles/cache/%s/*.manifest`"
                             ".part" % (name, name, name))
        assert not os.system("rm testfiles/cache/%s/*.manifest" % name)
        assert not os.system("""echo 'Volume 2:
    StartingPath   foo
    EndingPath     bar
    Hash SHA1 sha1' >> testfiles/cache/%s/*.manifest.part""" % name)

    def test_split_after_small(self):
        """
        If we restart right after a volume that ended with a small
        (one-block) file, make sure we restart in the right place.
        """
        source = 'testfiles/largefiles'
        assert not os.system("mkdir -p %s" % source)
        assert not os.system("echo hello > %s/file1" % source)
        self.backup("full", source, options=["--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume("backup1")
        # Add new file
        assert not os.system("cp %s/file1 %s/newfile" % (source, source))
        # 'restart' the backup
        self.backup("full", source, options=["--name=backup1"])
        # Confirm we actually resumed the previous backup
        self.assertEqual(len(os.listdir("testfiles/output")), 4)
        # Now make sure everything is byte-for-byte the same once restored
        self.restore()
        assert not os.system("diff -r %s testfiles/restore_out" % source)

    def test_split_after_large(self):
        """
        If we restart right after a volume that ended with a large
        (multi-block) file, make sure we restart in the right place.
        """
        source = 'testfiles/largefiles'
        self.make_largefiles(count=1, size=1)
        self.backup("full", source, options=["--volsize=5", "--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume("backup1")
        # Add new file
        assert not os.system("cp %s/file1 %s/newfile" % (source, source))
        # 'restart' the backup
        self.backup("full", source, options=["--volsize=5", "--name=backup1"])
        # Confirm we actually resumed the previous backup
        self.assertEqual(len(os.listdir("testfiles/output")), 4)
        # Now make sure everything is byte-for-byte the same once restored
        self.restore()
        assert not os.system("diff -r %s testfiles/restore_out" % source)

    def test_split_inside_large(self):
        """
        If we restart right after a volume that ended inside of a large
        (multi-block) file, make sure we restart in the right place.
        """
        source = 'testfiles/largefiles'
        self.make_largefiles(count=1, size=3)
        self.backup("full", source, options=["--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume("backup1")
        # 'restart' the backup
        self.backup("full", source, options=["--name=backup1"])
        # Now make sure everything is byte-for-byte the same once restored
        self.restore()
        assert not os.system("diff -r %s testfiles/restore_out" % source)

    def test_new_file(self):
        """
        If we restart right after a volume, but there are new files that would
        have been backed up earlier in the volume, make sure we don't wig out.
        (Expected result is to ignore new, ealier files, but pick up later
        ones.)
        """
        source = 'testfiles/largefiles'
        self.make_largefiles(count=1, size=1)
        self.backup("full", source, options=["--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume("backup1")
        # Add new files, earlier and later in filename sort order
        assert not os.system("echo hello > %s/a" % source)
        assert not os.system("echo hello > %s/z" % source)
        # 'restart' the backup
        self.backup("full", source, options=["--name=backup1"])
        # Now make sure everything is the same once restored, except 'a'
        self.restore()
        assert not os.system("test ! -e testfiles/restore_out/a")
        assert not os.system("diff %s/file1 testfiles/restore_out/file1" % source)
        assert not os.system("diff %s/z testfiles/restore_out/z" % source)

    def test_changed_source_dangling_manifest_volume(self):
        """
        If we restart but find remote volumes missing, we can easily end up
        with a manifest that lists "vol1, vol2, vol3, vol2", leaving a dangling
        vol3.  Make sure we can gracefully handle that.  This will only happen
        if the source data changes to be small enough to not create a vol3 on
        restart.
        """
        source = 'testfiles/largefiles'
        self.make_largefiles(count=5, size=1)
        self.backup("full", source, fail=3)
        # now delete the last volume on remote end and some source files
        assert not os.system("rm testfiles/output/duplicity-full*vol3.difftar*")
        assert not os.system("rm %s/file[2345]" % source)
        assert not os.system("echo hello > %s/z" % source)
        # finish backup
        self.backup("full", source)
        # and verify we can restore
        self.restore()

    def test_changed_source_file_disappears(self):
        """
        Make sure we correctly handle restarting a backup when a file
        disappears when we had been in the middle of backing it up.  It's
        possible that the first chunk of the next file will be skipped unless
        we're careful.
        """
        source = 'testfiles/largefiles'
        self.make_largefiles(count=1)
        self.backup("full", source, fail=2)
        # now remove starting source data and make sure we add something after
        assert not os.system("rm %s/*" % source)
        assert not os.system("echo hello > %s/z" % source)
        # finish backup
        self.backup("full", source)
        # and verify we can restore
        self.restore()
        assert not os.system("diff %s/z testfiles/restore_out/z" % source)


# Note that this class duplicates all the tests in RestartTest
class RestartTestWithoutEncryption(RestartTest):

    def setUp(self):
        super(RestartTestWithoutEncryption, self).setUp()
        self.class_args.extend(["--no-encryption"])

    def test_no_write_double_snapshot(self):
        """
        Test that restarting a full backup does not write duplicate entries
        into the sigtar, causing problems reading it back in older
        versions.
        https://launchpad.net/bugs/929067
        """
        self.make_largefiles()
        self.backup("full", "testfiles/largefiles", fail=2)
        self.backup("full", "testfiles/largefiles")
        # Now check sigtar
        sigtars = glob.glob("testfiles/output/duplicity-full*.sigtar.gz")
        self.assertEqual(1, len(sigtars))
        sigtar = sigtars[0]
        output = subprocess.Popen(["tar", "t", "--file=%s" % sigtar], stdout=subprocess.PIPE).communicate()[0]
        self.assertEqual(1, output.split("\n").count("snapshot/"))

    def test_ignore_double_snapshot(self):
        """
        Test that we gracefully ignore double snapshot entries in a signature
        file.  This winds its way through duplicity as a deleted base dir,
        which doesn't make sense and should be ignored.  An older version of
        duplicity accidentally created such files as a result of a restart.
        https://launchpad.net/bugs/929067
        """

        if platform.system().startswith('Linux'):
            tarcmd = "tar"
        elif platform.system().startswith('Darwin'):
            tarcmd = "gtar"
        elif platform.system().endswith('BSD'):
            tarcmd = "gtar"
        else:
            raise Exception("Platform %s not supported by tar/gtar." % platform.platform())

        # Intial normal backup
        self.backup("full", "testfiles/blocktartest")
        # Create an exact clone of the snapshot folder in the sigtar already.
        # Permissions and mtime must match.
        os.mkdir("testfiles/snapshot", 0o755)
        os.utime("testfiles/snapshot", (1030384548, 1030384548))
        # Adjust the sigtar.gz file to have a bogus second snapshot/ entry
        # at the beginning.
        sigtars = glob.glob("testfiles/output/duplicity-full*.sigtar.gz")
        self.assertEqual(1, len(sigtars))
        sigtar = sigtars[0]
        self.assertEqual(0, os.system("%s c --file=testfiles/snapshot.sigtar -C testfiles snapshot" % (tarcmd,)))
        self.assertEqual(0, os.system("gunzip -c %s > testfiles/full.sigtar" % sigtar))
        self.assertEqual(0, os.system("%s A --file=testfiles/snapshot.sigtar testfiles/full.sigtar" % (tarcmd,)))
        self.assertEqual(0, os.system("gzip testfiles/snapshot.sigtar"))
        os.remove(sigtar)
        os.rename("testfiles/snapshot.sigtar.gz", sigtar)
        # Clear cache so our adjusted sigtar will be sync'd back into the cache
        self.assertEqual(0, os.system("rm -r testfiles/cache"))
        # Try a follow on incremental (which in buggy versions, would create
        # a deleted entry for the base dir)
        self.backup("inc", "testfiles/blocktartest")
        self.assertEqual(1, len(glob.glob("testfiles/output/duplicity-new*.sigtar.gz")))
        # Confirm we can restore it (which in buggy versions, would fail)
        self.restore()

if __name__ == "__main__":
    unittest.main()

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

import helper
import sys, os, unittest
import glob
import subprocess

import duplicity.backend
from duplicity import path

helper.setup()

# This can be changed to select the URL to use
backend_url = "file://testfiles/output"

# Extra arguments to be passed to duplicity
other_args = ["-v0", "--no-print-statistics"]
#other_args = ["--short-filenames"]
#other_args = ["--ssh-command 'ssh -v'", "--scp-command 'scp -C'"]

# If this is set to true, after each backup, verify contents
verify = 1

class CmdError(Exception):
    """Indicates an error running an external command"""
    def __init__(self, code):
        Exception.__init__(self, code)
        self.exit_status = code

class RestartTest(unittest.TestCase):
    """
    Test checkpoint/restart using duplicity binary
    """
    def setUp(self):
        self.class_args = []
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")
        assert not os.system("rm -rf testfiles/output testfiles/largefiles "
                             "testfiles/restore_out testfiles/cache")
        assert not os.system("mkdir testfiles/output testfiles/cache")
        backend = duplicity.backend.get_backend(backend_url)
        bl = backend.list()
        if bl:
            backend.delete(backend.list())
        backend.close()

    def tearDown(self):
        helper.set_environ("PASSPHRASE", None)
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def run_duplicity(self, arglist, options = [], current_time = None):
        """
        Run duplicity binary with given arguments and options
        """
        options.append("--archive-dir testfiles/cache")
        # We run under setsid and take input from /dev/null (below) because
        # this way we force a failure if duplicity tries to read from the
        # console (like for gpg password or such).
        cmd_list = ["setsid", "duplicity"]
        cmd_list.extend(options + ["--allow-source-mismatch"])
        if current_time:
            cmd_list.append("--current-time %s" % (current_time,))
        if other_args:
            cmd_list.extend(other_args)
        cmd_list.extend(self.class_args)
        cmd_list.extend(arglist)
        cmd_list.extend(["<", "/dev/null"])
        cmdline = " ".join(cmd_list)
        #print "Running '%s'." % cmdline
        helper.set_environ('PASSPHRASE', helper.sign_passphrase)
#        print "CMD: %s" % cmdline
        return_val = os.system(cmdline)
        if return_val:
            raise CmdError(os.WEXITSTATUS(return_val))

    def backup(self, type, input_dir, options = [], current_time = None):
        """Run duplicity backup to default directory"""
        options = options[:]
        if type == "full":
            options.insert(0, 'full')
        args = [input_dir, "'%s'" % backend_url]
        self.run_duplicity(args, options, current_time)

    def restore(self, file_to_restore = None, time = None, options = [],
                current_time = None):
        options = options[:] # just nip any mutability problems in bud
        assert not os.system("rm -rf testfiles/restore_out")
        args = ["'%s'" % backend_url, "testfiles/restore_out"]
        if file_to_restore:
            options.extend(['--file-to-restore', file_to_restore])
        if time:
            options.extend(['--restore-time', str(time)])
        self.run_duplicity(args, options, current_time)

    def verify(self, dirname, file_to_verify = None, time = None, options = [],
               current_time = None):
        options = ["verify"] + options[:]
        args = ["'%s'" % backend_url, dirname]
        if file_to_verify:
            options.extend(['--file-to-restore', file_to_verify])
        if time:
            options.extend(['--restore-time', str(time)])
        self.run_duplicity(args, options, current_time)

    def runtest(self, dirlist, backup_options = [], restore_options = []):
        """
        Run backup/restore test on directories in dirlist
        """
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
            if verify:
                self.verify(dirname,
                            time = current_time, options = restore_options)

    def make_largefiles(self, count=3, size=2):
        """
        Makes a number of large files in testfiles/largefiles that each are
        the specified number of megabytes.
        """
        assert not os.system("mkdir testfiles/largefiles")
        for n in range(count):
            assert not os.system("dd if=/dev/urandom of=testfiles/largefiles/file%d bs=1024 count=%d > /dev/null 2>&1" % (n + 1, size * 1024))

    def check_same(self, filename1, filename2):
        """
        Verify two filenames are the same
        """
        path1, path2 = path.Path(filename1), path.Path(filename2)
        assert path1.compare_recursive(path2, verbose = 1)

    def test_basic_checkpoint_restart(self):
        """
        Test basic Checkpoint/Restart
        """
        excludes = ["--exclude '**/output'",
                    "--exclude '**/cache'",]
        # we know we're going to fail this one, its forced
        try:
            self.backup("full", "testfiles", options = ["--vol 1", "--fail 1"] + excludes)
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        # this one should pass OK
        self.backup("full", "testfiles", options = excludes)
        self.verify("testfiles", options = excludes)

    def test_multiple_checkpoint_restart(self):
        """
        Test multiple Checkpoint/Restart
        """
        excludes = ["--exclude '**/output'",
                    "--exclude '**/cache'",]
        self.make_largefiles()
        # we know we're going to fail these, they are forced
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 1"] + excludes)
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 2"] + excludes)
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 3"] + excludes)
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        # this one should pass OK
        self.backup("full", "testfiles/largefiles", options = excludes)
        self.verify("testfiles/largefiles", options = excludes)

    def test_first_volume_failure(self):
        """
        Test restart when no volumes are available on the remote.
        Caused when duplicity fails before the first transfer.
        """
        excludes = ["--exclude '**/output'",
                    "--exclude '**/cache'",]
        # we know we're going to fail these, they are forced
        try:
            self.backup("full", "testfiles", options = ["--vol 1", "--fail 1"] + excludes)
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        assert not os.system("rm testfiles/output/duplicity-full*difftar*")
        # this one should pass OK
        self.backup("full", "testfiles", options = excludes)
        self.verify("testfiles", options = excludes)

    def test_multi_volume_failure(self):
        """
        Test restart when fewer volumes are available on the remote
        than the local manifest has on record.  Caused when duplicity
        fails the last queued transfer(s).
        """
        self.make_largefiles()
        # we know we're going to fail these, they are forced
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 3"])
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        assert not os.system("rm testfiles/output/duplicity-full*vol[23].difftar*")
        # this one should pass OK
        self.backup("full", "testfiles/largefiles", options = ["--vol 1"])
        self.verify("testfiles/largefiles")

    def test_restart_sign_and_encrypt(self):
        """
        Test restarting a backup using same key for sign and encrypt
        https://bugs.launchpad.net/duplicity/+bug/946988
        """
        self.make_largefiles()
        enc_opts = ["--sign-key " + helper.sign_key, "--encrypt-key " + helper.sign_key]
        # Force a failure partway through
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vols 1", "--fail 2"] + enc_opts)
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        # Now finish that backup
        self.backup("full", "testfiles/largefiles", options = enc_opts)
        self.verify("testfiles/largefiles")

    def test_restart_sign_and_hidden_encrypt(self):
        """
        Test restarting a backup using same key for sign and encrypt (hidden key id)
        https://bugs.launchpad.net/duplicity/+bug/946988
        """
        self.make_largefiles()
        enc_opts = ["--sign-key " + helper.sign_key, "--hidden-encrypt-key " + helper.sign_key]
        # Force a failure partway through
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vols 1", "--fail 2"] + enc_opts)
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        # Now finish that backup
        self.backup("full", "testfiles/largefiles", options = enc_opts)
        self.verify("testfiles/largefiles")

    def test_last_file_missing_in_middle(self):
        """
        Test restart when the last file being backed up is missing on restart.
        Caused when the user deletes a file after a failure.  This test puts
        the file in the middle of the backup, with files following.
        """
        self.make_largefiles()
        # we know we're going to fail, it's forced
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 3"])
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        assert not os.system("rm testfiles/largefiles/file2")
        # this one should pass OK
        self.backup("full", "testfiles/largefiles", options = ["--vol 1"])
        #TODO: we can't verify but we need to to check for other errors that might show up
        # there should be 2 differences found, one missing file, one mtime change
        #self.verify("testfiles/largefiles")

    def test_last_file_missing_at_end(self):
        """
        Test restart when the last file being backed up is missing on restart.
        Caused when the user deletes a file after a failure.  This test puts
        the file at the end of the backup, with no files following.
        """
        self.make_largefiles()
        # we know we're going to fail, it's forced
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 6"])
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        assert not os.system("rm testfiles/largefiles/file3")
        # this one should pass OK
        self.backup("full", "testfiles/largefiles", options = ["--vol 1"])
        #TODO: we can't verify but we need to to check for other errors that might show up
        # there should be 2 differences found, one missing file, one mtime change
        #self.verify("testfiles/largefiles")

    def test_restart_incremental(self):
        """
        Test restarting an incremental backup
        """
        # Make first normal full backup
        self.backup("full", "testfiles/dir1")
        self.make_largefiles()
        # Force a failure partway through
        try:
            self.backup("inc", "testfiles/largefiles", options = ["--vols 1", "--fail 2"])
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        # Now finish that incremental
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
        self.assertEqual(len(glob.glob("testfiles/cache/%s/*" % name)), 2)
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

    def test_split_inside_large(self):
        """
        If we restart right after a volume that ended inside of a large
        (multi-block) file, make sure we restart in the right place.
        """
        source = 'testfiles/largefiles'
        self.make_largefiles(count=1, size=3)
        self.backup("full", source, options=["--vols 1", "--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume("backup1")
        # 'restart' the backup
        self.backup("full", source, options=["--vols 1", "--name=backup1"])
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


# Note that this class duplicates all the tests in RestartTest
class RestartTestWithoutEncryption(RestartTest):
    def setUp(self):
        RestartTest.setUp(self)
        self.class_args.extend(["--no-encryption"])

    def test_no_write_double_snapshot(self):
        """
        Test that restarting a full backup does not write duplicate entries
        into the sigtar, causing problems reading it back in older
        versions.
        https://launchpad.net/bugs/929067
        """
        self.make_largefiles()
        # Start backup
        try:
            self.backup("full", "testfiles/largefiles", options = ["--fail 2", "--vols 1"])
            self.fail()
        except CmdError, e:
            self.assertEqual(30, e.exit_status)
        # Finish it
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
        # Intial normal backup
        self.backup("full", "testfiles/blocktartest")
        # Create an exact clone of the snapshot folder in the sigtar already.
        # Permissions and mtime must match.
        os.mkdir("testfiles/snapshot", 0755)
        os.utime("testfiles/snapshot", (1030384548, 1030384548))
        # Adjust the sigtar.gz file to have a bogus second snapshot/ entry
        # at the beginning.
        sigtars = glob.glob("testfiles/output/duplicity-full*.sigtar.gz")
        self.assertEqual(1, len(sigtars))
        sigtar = sigtars[0]
        self.assertEqual(0, os.system("tar c --file=testfiles/snapshot.sigtar -C testfiles snapshot"))
        self.assertEqual(0, os.system("gunzip -c %s > testfiles/full.sigtar" % sigtar))
        self.assertEqual(0, os.system("tar A --file=testfiles/snapshot.sigtar testfiles/full.sigtar"))
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

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

import duplicity.backend
from duplicity import path

helper.setup()

# This can be changed to select the URL to use
backend_url = "file://testfiles/output"

# Extra arguments to be passed to duplicity
other_args = ["-v0", "--no-print-statistics"]
#other_args = ["--short-filenames"]
#other_args = ["--ssh-command 'ssh -v'", "--scp-command 'scp -C'"]
#other_args = ['--no-encryption']

# If this is set to true, after each backup, verify contents
verify = 1

class CmdError(Exception):
    """Indicates an error running an external command"""
    pass

class RestartTest(unittest.TestCase):
    """
    Test checkpoint/restart using duplicity binary
    """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def run_duplicity(self, arglist, options = [], current_time = None):
        """
        Run duplicity binary with given arguments and options
        """
        options.append("--archive-dir testfiles/cache")
        cmd_list = ["duplicity"]
        cmd_list.extend(options + ["--allow-source-mismatch"])
        if current_time:
            cmd_list.append("--current-time %s" % (current_time,))
        if other_args:
            cmd_list.extend(other_args)
        cmd_list.extend(arglist)
        cmdline = " ".join(cmd_list)
        #print "Running '%s'." % cmdline
        if not os.environ.has_key('PASSPHRASE'):
            os.environ['PASSPHRASE'] = 'foobar'
#        print "CMD: %s" % cmdline
        return_val = os.system(cmdline)
        if return_val:
            raise CmdError(return_val)

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

    def deltmp(self):
        """
        Delete temporary directories
        """
        assert not os.system("rm -rf testfiles/output "
                             "testfiles/restore_out testfiles/cache")
        assert not os.system("mkdir testfiles/output testfiles/cache")
        backend = duplicity.backend.get_backend(backend_url)
        bl = backend.list()
        if bl:
            backend.delete(backend.list())
        backend.close()

    def runtest(self, dirlist, backup_options = [], restore_options = []):
        """
        Run backup/restore test on directories in dirlist
        """
        assert len(dirlist) >= 1
        self.deltmp()

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
        excludes = ["--exclude **/output",
                    "--exclude **/cache",]
        self.deltmp()
        # we know we're going to fail this one, its forced
        try:
            self.backup("full", "testfiles", options = ["--vol 1", "--fail 1"] + excludes)
        except CmdError:
            pass
        # this one should pass OK
        self.backup("full", "testfiles", options = excludes)
        self.verify("testfiles", options = excludes)

    def test_multiple_checkpoint_restart(self):
        """
        Test multiple Checkpoint/Restart
        """
        excludes = ["--exclude **/output",
                    "--exclude **/cache",]
        self.deltmp()
        # we know we're going to fail these, they are forced
        try:
            self.backup("full", "testfiles", options = ["--vol 1", "--fail 1"] + excludes)
        except CmdError:
            pass
        try:
            self.backup("full", "testfiles", options = ["--vol 1", "--fail 2"] + excludes)
        except CmdError:
            pass
        try:
            self.backup("full", "testfiles", options = ["--vol 1", "--fail 3"] + excludes)
        except CmdError:
            pass
        # this one should pass OK
        self.backup("full", "testfiles", options = excludes)
        self.verify("testfiles", options = excludes)

    def test_first_volume_failure(self):
        """
        Test restart when no volumes are available on the remote.
        Caused when duplicity fails before the first transfer.
        """
        excludes = ["--exclude **/output",
                    "--exclude **/cache",]
        self.deltmp()
        # we know we're going to fail these, they are forced
        try:
            self.backup("full", "testfiles", options = ["--vol 1", "--fail 1"] + excludes)
        except CmdError:
            pass
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
        self.deltmp()
        # we know we're going to fail these, they are forced
        try:
            self.backup("full", "/bin", options = ["--vol 1", "--fail 3"])
        except CmdError:
            pass
        assert not os.system("rm testfiles/output/duplicity-full*vol[23].difftar*")
        # this one should pass OK
        self.backup("full", "/bin", options = ["--vol 1"])
        self.verify("/bin")

    def test_last_file_missing_in_middle(self):
        """
        Test restart when the last file being backed up is missing on restart.
        Caused when the user deletes a file after a failure.  This test puts
        the file in the middle of the backup, with files following.
        """
        self.deltmp()
        # create 3 2M files
        assert not os.system("mkdir testfiles/largefiles")
        for n in (1,2,3):
            assert not os.system("dd if=/dev/urandom of=testfiles/largefiles/file%d bs=1024 count=2048 > /dev/null 2>&1" % n)
        # we know we're going to fail, it's forced
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 3"])
        except CmdError:
            pass
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
        self.deltmp()
        # create 3 2M files
        assert not os.system("mkdir testfiles/largefiles")
        for n in (1,2,3):
            assert not os.system("dd if=/dev/urandom of=testfiles/largefiles/file%d bs=1024 count=2048 > /dev/null 2>&1" % n)
        # we know we're going to fail, it's forced
        try:
            self.backup("full", "testfiles/largefiles", options = ["--vol 1", "--fail 6"])
        except CmdError:
            pass
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
        # create 3 2M files
        assert not os.system("mkdir testfiles/largefiles")
        for n in (1,2,3):
            assert not os.system("dd if=/dev/urandom of=testfiles/largefiles/file%d bs=1024 count=2048 > /dev/null 2>&1" % n)
        # Force a failure partway through
        try:
            self.backup("inc", "testfiles/largefiles", options = ["--vols 1", "--fail 2"])
            assert False # shouldn't get this far
        except CmdError, e:
            pass
        # Now finish that incremental
        self.backup("inc", "testfiles/largefiles")
        self.verify("testfiles/largefiles")

if __name__ == "__main__":
    unittest.main()

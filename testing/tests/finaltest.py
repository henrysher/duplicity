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
from duplicity import collections
from duplicity import commandline
from duplicity import globals

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

class FinalTest:
    """
    Test backup/restore using duplicity binary
    """
    def run_duplicity(self, arglist, options = [], current_time = None):
        """Run duplicity binary with given arguments and options"""
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
        """Delete temporary directories"""
        assert not os.system("rm -rf testfiles/output "
                             "testfiles/restore_out testfiles/cache")
        assert not os.system("mkdir testfiles/output testfiles/cache")
        backend = duplicity.backend.get_backend(backend_url)
        bl = backend.list()
        if bl:
            backend.delete(backend.list())
        backend.close()

    def runtest(self, dirlist, backup_options = [], restore_options = []):
        """Run backup/restore test on directories in dirlist"""
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
        """Verify two filenames are the same"""
        path1, path2 = path.Path(filename1), path.Path(filename2)
        assert path1.compare_recursive(path2, verbose = 1)

    def test_basic_cycle(self, backup_options = [], restore_options = []):
        """Run backup/restore test on basic directories"""
        self.runtest(["testfiles/dir1",
                      "testfiles/dir2",
                      "testfiles/dir3"],
                     backup_options = backup_options,
                     restore_options = restore_options)

        # Test restoring various sub files
        for filename, time, dir in [('symbolic_link', 99999, 'dir1'),
                                    ('directory_to_file', 100100, 'dir1'),
                                    ('directory_to_file', 200100, 'dir2'),
                                    ('largefile', 300000, 'dir3')]:
            self.restore(filename, time, options = restore_options)
            self.check_same('testfiles/%s/%s' % (dir, filename),
                            'testfiles/restore_out')
            if verify:
                self.verify('testfiles/%s/%s' % (dir, filename),
                            file_to_verify = filename, time = time,
                            options = restore_options)

    def test_asym_cycle(self):
        """Like test_basic_cycle but use asymmetric encryption and signing"""
        backup_options = ["--encrypt-key " + helper.encrypt_key1,
                          "--sign-key " + helper.sign_key]
        restore_options = ["--encrypt-key " + helper.encrypt_key1,
                           "--sign-key " + helper.sign_key]
        helper.set_environ("SIGN_PASSPHRASE", helper.sign_passphrase)
        self.test_basic_cycle(backup_options = backup_options,
                              restore_options = restore_options)

    def test_asym_with_hidden_recipient_cycle(self):
        """Like test_basic_cycle but use asymmetric encryption (hidding key id) and signing"""
        backup_options = ["--hidden-encrypt-key " + helper.encrypt_key1,
                          "--sign-key " + helper.sign_key]
        restore_options = ["--hidden-encrypt-key " + helper.encrypt_key1,
                           "--sign-key " + helper.sign_key]
        helper.set_environ("SIGN_PASSPHRASE", helper.sign_passphrase)
        self.test_basic_cycle(backup_options = backup_options,
                              restore_options = restore_options)

    def test_single_regfile(self):
        """Test backing and restoring up a single regular file"""
        self.runtest(["testfiles/various_file_types/regular_file"])

    def test_empty_backup(self):
        """Make sure backup works when no files change"""
        self.backup("full", "testfiles/empty_dir")
        self.backup("inc", "testfiles/empty_dir")

    def test_long_filenames(self):
        """Test backing up a directory with long filenames in it"""
        # Note that some versions of ecryptfs (at least through Ubuntu 11.10)
        # have a bug where they treat the max path segment length as 143
        # instead of 255.  So make sure that these segments don't break that.
        lf_dir = path.Path("testfiles/long_filenames")
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

        self.runtest(["testfiles/empty_dir", lf_dir.name,
                      "testfiles/empty_dir", lf_dir.name])

    def test_empty_restore(self):
        """Make sure error raised when restore doesn't match anything"""
        self.deltmp()
        self.backup("full", "testfiles/dir1")
        self.assertRaises(CmdError, self.restore, "this_file_does_not_exist")
        self.backup("inc", "testfiles/empty_dir")
        self.assertRaises(CmdError, self.restore, "this_file_does_not_exist")

    def test_remove_older_than(self):
        """Test removing old backup chains"""
        self.deltmp()
        self.backup("full", "testfiles/dir1", current_time = 10000)
        self.backup("inc", "testfiles/dir2", current_time = 20000)
        self.backup("full", "testfiles/dir1", current_time = 30000)
        self.backup("inc", "testfiles/dir3", current_time = 40000)

        b = duplicity.backend.get_backend(backend_url)
        commandline.set_archive_dir("testfiles/cache")
        cs = collections.CollectionsStatus(b, globals.archive_dir).set_values()
        assert len(cs.all_backup_chains) == 2, cs.all_backup_chains
        assert cs.matched_chain_pair

        self.run_duplicity(["--force", backend_url], options=["remove-older-than 35000"])
        cs2 = collections.CollectionsStatus(b, globals.archive_dir).set_values()
        assert len(cs2.all_backup_chains) == 1, cs.all_backup_chains
        assert cs2.matched_chain_pair
        chain = cs2.all_backup_chains[0]
        assert chain.start_time == 30000, chain.start_time
        assert chain.end_time == 40000, chain.end_time

        # Now check to make sure we can't delete only chain
        self.run_duplicity(["--force", backend_url], options=["remove-older-than 50000"])
        cs3 = collections.CollectionsStatus(b, globals.archive_dir).set_values()
        assert len(cs3.all_backup_chains) == 1
        assert cs3.matched_chain_pair
        chain = cs3.all_backup_chains[0]
        assert chain.start_time == 30000, chain.start_time
        assert chain.end_time == 40000, chain.end_time

class FinalTest1(FinalTest, unittest.TestCase):
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    globals.old_filenames = False

class FinalTest2(FinalTest, unittest.TestCase):
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    globals.old_filenames = True

if __name__ == "__main__":
    unittest.main()

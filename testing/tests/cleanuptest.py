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
import sys, os, unittest, time

import duplicity.backend
from duplicity import path

helper.setup()

# Extra arguments to be passed to duplicity
other_args = ["-v0", "--no-print-statistics"]
#other_args = []

class CmdError(Exception):
    """Indicates an error running an external command"""
    pass

class CleanupTest(unittest.TestCase):
    """
    Test cleanup using duplicity binary
    """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")
        self.deltmp()

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def run_duplicity(self, arglist, options = [], current_time = None):
        """
        Run duplicity binary with given arguments and options
        """
        before_files = set(os.listdir("testfiles/output"))
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
        after_files = set(os.listdir("testfiles/output"))
        return after_files - before_files

    def backup(self, type, input_dir, options = [], current_time = None):
        """
        Run duplicity backup to default directory
        """
        options = options[:]
        if type == "full":
            options.insert(0, 'full')
        args = [input_dir, "file://testfiles/output"]
        new_files = self.run_duplicity(args, options, current_time)
        # If a chain ends with time X and the next full chain begins at time X,
        # we may trigger an assert in collections.py.  This way, we avoid
        # such problems
        time.sleep(1)
        return new_files

    def verify(self, dirname, file_to_verify = None, time = None, options = [],
               current_time = None):
        options = ["verify"] + options[:]
        args = ["file://testfiles/output", dirname]
        if file_to_verify:
            options.extend(['--file-to-restore', file_to_verify])
        if time:
            options.extend(['--restore-time', str(time)])
        return self.run_duplicity(args, options, current_time)

    def cleanup(self, options = []):
        """
        Run duplicity cleanup to default directory
        """
        options = ["cleanup"] + options[:]
        args = ["file://testfiles/output"]
        return self.run_duplicity(args, options)

    def deltmp(self):
        """
        Delete temporary directories
        """
        assert not os.system("rm -rf testfiles/output testfiles/cache")
        assert not os.system("mkdir testfiles/output testfiles/cache")
        backend = duplicity.backend.get_backend("file://testfiles/output")
        bl = backend.list()
        if bl:
            backend.delete(backend.list())
        backend.close()

    def test_cleanup_after_partial(self):
        """
        Regression test for https://bugs.launchpad.net/bugs/409593
        where duplicity deletes all the signatures during a cleanup
        after a failed backup.
        """
        good_files = self.backup("full", "/bin", options = ["--vol 1"])
        good_files |= self.backup("inc", "/bin", options = ["--vol 1"])
        good_files |= self.backup("inc", "/bin", options = ["--vol 1"])
        # we know we're going to fail these, they are forced
        try:
            self.backup("full", "/bin", options = ["--vol 1", "--fail 1"])
            self.fail("Not supposed to reach this far")
        except CmdError:
            bad_files = set(os.listdir("testfiles/output"))
            bad_files -= good_files
            self.assertNotEqual(bad_files, set())
        # the cleanup should go OK
        self.cleanup(options = ["--force"])
        leftovers = set(os.listdir("testfiles/output"))
        self.assertEqual(good_files, leftovers)
        self.backup("inc", "/bin", options = ["--vol 1"])
        self.verify("/bin")

    def test_remove_all_but_n(self):
        """
        Test that remove-all-but-n works in the simple case.
        """
        full1_files = self.backup("full", "testfiles/empty_dir")
        full2_files = self.backup("full", "testfiles/empty_dir")
        self.run_duplicity(["file://testfiles/output"],
                           ["remove-all-but-n", "1", "--force"])
        leftovers = set(os.listdir("testfiles/output"))
        self.assertEqual(full2_files, leftovers)

    def test_remove_all_inc_of_but_n(self):
        """
        Test that remove-all-inc-of-but-n-full works in the simple case.
        """
        full1_files = self.backup("full", "testfiles/empty_dir")
        inc1_files = self.backup("inc", "testfiles/empty_dir")
        full2_files = self.backup("full", "testfiles/empty_dir")
        self.run_duplicity(["file://testfiles/output"],
                           ["remove-all-inc-of-but-n-full", "1", "--force"])
        leftovers = set(os.listdir("testfiles/output"))
        self.assertEqual(full1_files | full2_files, leftovers)


if __name__ == "__main__":
    unittest.main()

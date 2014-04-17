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
import time
import unittest

from duplicity import backend
from duplicity import globals
from duplicity import log
from duplicity import pexpect

sign_key = '56538CCF'
sign_passphrase = 'test'
encrypt_key1 = 'B5FA894F'
encrypt_key2 = '9B736B2A'

# TODO: remove this method
def setup():
    """ setup for unit tests """
    log.setup()
    log.setverbosity(log.WARNING)
    globals.print_statistics = 0
    backend.import_backends()


class CmdError(Exception):
    """Indicates an error running an external command"""
    def __init__(self, code):
        Exception.__init__(self, code)
        self.exit_status = code


class DuplicityTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.class_args = []
        cls.backend_url = "file://testfiles/output"
        cls.sign_key = sign_key
        cls.sign_passphrase = sign_passphrase
        cls.encrypt_key1 = encrypt_key1
        cls.encrypt_key2 = encrypt_key2        
        setup()

    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")
        assert not os.system("rm -rf testfiles/output testfiles/largefiles "
                             "testfiles/restore_out testfiles/cache")
        assert not os.system("mkdir testfiles/output testfiles/cache")

        backend_inst = backend.get_backend(self.backend_url)
        bl = backend_inst.list()
        if bl:
            backend_inst.delete(backend_inst.list())
        backend_inst.close()

        self.last_backup = None
        self.set_environ('PASSPHRASE', self.sign_passphrase)
        self.set_environ("SIGN_PASSPHRASE", self.sign_passphrase)

    def tearDown(self):
        self.set_environ("PASSPHRASE", None)
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def set_environ(self, varname, value):
        if value is not None:
            os.environ[varname] = value
        else:
            try:
                del os.environ[varname]
            except Exception:
                pass

    def run_duplicity(self, options=[], current_time=None, fail=None,
                      passphrase_input=[]):
        """
        Run duplicity binary with given arguments and options
        """
        # We run under setsid and take input from /dev/null (below) because
        # this way we force a failure if duplicity tries to read from the
        # console unexpectedly (like for gpg password or such).
        cmd_list = ["setsid", "duplicity"]
        cmd_list.extend(options)
        cmd_list.extend(["-v0"])
        cmd_list.extend(["--no-print-statistics"])
        cmd_list.extend(["--allow-source-mismatch"])
        cmd_list.extend(["--archive-dir=testfiles/cache"])
        if current_time:
            cmd_list.extend(["--current-time", current_time])
        cmd_list.extend(self.class_args)
        if fail:
            cmd_list.extend(["--fail", str(fail)])
        cmdline = " ".join(map(lambda x: '"%s"' % x, cmd_list))

        if not passphrase_input:
            cmdline += " < /dev/null"
        child = pexpect.spawn('/bin/sh', ['-c', cmdline])
        for passphrase in passphrase_input:
            child.expect('passphrase.*:')
            child.sendline(passphrase)
        child.wait()
        return_val = child.exitstatus

        #print "Ran duplicity command: ", cmdline, "\n with return_val: ", child.exitstatus
        if fail:
            self.assertEqual(30, child.exitstatus)
        elif return_val:
            raise CmdError(child.exitstatus)

    def backup(self, type, input_dir, options=[], **kwargs):
        """Run duplicity backup to default directory"""
        options = [type, input_dir, self.backend_url, "--volsize", "1"] + options
        before_files = self.get_backend_files()

        # If a chain ends with time X and the next full chain begins at time X,
        # we may trigger an assert in collections.py.  If needed, sleep to
        # avoid such problems
        if self.last_backup == int(time.time()):
            time.sleep(1)

        result = self.run_duplicity(options=options, **kwargs)
        self.last_backup = int(time.time())

        after_files = self.get_backend_files()
        return after_files - before_files

    def restore(self, file_to_restore=None, time=None, options=[], **kwargs):
        assert not os.system("rm -rf testfiles/restore_out")
        options = [self.backend_url, "testfiles/restore_out"] + options
        if file_to_restore:
            options.extend(['--file-to-restore', file_to_restore])
        if time:
            options.extend(['--restore-time', str(time)])
        self.run_duplicity(options=options, **kwargs)

    def verify(self, dirname, file_to_verify=None, time=None, options=[],
               **kwargs):
        options = ["verify", self.backend_url, dirname] + options
        if file_to_verify:
            options.extend(['--file-to-restore', file_to_verify])
        if time:
            options.extend(['--restore-time', str(time)])
        self.run_duplicity(options=options, **kwargs)

    def cleanup(self, options=[]):
        """
        Run duplicity cleanup to default directory
        """
        options = ["cleanup", self.backend_url, "--force"] + options
        self.run_duplicity(options=options)

    def get_backend_files(self):
        backend_inst = backend.get_backend(self.backend_url)
        bl = backend_inst.list()
        backend_inst.close()
        return set(bl)

    def make_largefiles(self, count=3, size=2):
        """
        Makes a number of large files in testfiles/largefiles that each are
        the specified number of megabytes.
        """
        assert not os.system("mkdir testfiles/largefiles")
        for n in range(count):
            assert not os.system("dd if=/dev/urandom of=testfiles/largefiles/file%d bs=1024 count=%d > /dev/null 2>&1" % (n + 1, size * 1024))

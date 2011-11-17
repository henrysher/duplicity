# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2011 Canonical Ltd
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
import os, unittest, sys

helper.setup()

# This can be changed to select the URL to use
backend_url = 'file://testfiles/output'

class CmdError(Exception):
    """Indicates an error running an external command"""
    return_val = -1
    def __init__(self, return_val):
        self.return_val = os.WEXITSTATUS(return_val)

class BadUploadTest(unittest.TestCase):
    """
    Test missing volume upload using duplicity binary
    """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def run_duplicity(self, arglist, options = []):
        """
        Run duplicity binary with given arguments and options
        """
        options.append("--archive-dir testfiles/cache")
        cmd_list = ["duplicity"]
        cmd_list.extend(options + ["--allow-source-mismatch"])
        cmd_list.extend(arglist)
        cmdline = " ".join(cmd_list)
        if not os.environ.has_key('PASSPHRASE'):
            os.environ['PASSPHRASE'] = 'foobar'
        return_val = os.system(cmdline)
        if return_val:
            raise CmdError(return_val)

    def backup(self, type, input_dir, options = []):
        """Run duplicity backup to default directory"""
        options = options[:]
        if type == "full":
            options.insert(0, 'full')
        args = [input_dir, "'%s'" % backend_url]
        self.run_duplicity(args, options)

    def test_missing_file(self):
        """
        Test basic lost file
        """
        # we know we're going to fail this one, its forced
        try:
            self.backup("full", "testfiles/dir1", options = ["--skip-volume 1"])
            assert False # shouldn't get this far
        except CmdError, e:
            assert e.return_val == 44, e.return_val

if __name__ == "__main__":
    unittest.main()

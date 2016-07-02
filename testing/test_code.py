# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2014 Michael Terry <michael.terry@canonical.com>
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
import sys
import subprocess

if sys.version_info < (2, 7):
    import unittest2 as unittest  # @UnresolvedImport @UnusedImport
else:
    import unittest  # @Reimport

from . import _top_dir, DuplicityTestCase  # @IgnorePep8


class CodeTest(DuplicityTestCase):

    def run_checker(self, cmd, returncodes=[0]):
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output = process.communicate()[0]
        self.assertTrue(process.returncode in returncodes, output)
        self.assertEqual("", output, output)

    @unittest.skipUnless(os.getenv('RUN_CODE_TESTS', None) == '1',
                         'Must set environment var RUN_CODE_TESTS=1')
    def test_2to3(self):
        # As we modernize the source code, we can remove more and more nofixes
        self.run_checker([
            "2to3",
            "--nofix=next",
            "--nofix=types",
            "--nofix=unicode",
            # The following fixes we don't want to remove, since they are false
            # positives, things we don't care about, or real incompatibilities
            # but which 2to3 can fix for us better automatically.
            "--nofix=callable",
            "--nofix=dict",
            "--nofix=future",
            "--nofix=imports",
            "--nofix=print",
            "--nofix=raw_input",
            "--nofix=urllib",
            "--nofix=xrange",
            _top_dir])

    @unittest.skipUnless(os.getenv('RUN_CODE_TESTS', None) == '1',
                         'Must set environment var RUN_CODE_TESTS=1')
    def test_pylint(self):
        """Pylint test (requires pylint to be installed to pass)"""
        self.run_checker([
            "pylint",
            "-E",
            "--msg-template={msg_id}: {line}: {msg}",
            "--disable=E0203",  # Access to member before its definition line
            "--disable=E0602",  # Undefined variable
            "--disable=E0611",  # No name in module
            "--disable=E1101",  # Has no member
            "--disable=E1103",  # Maybe has no member
            "--disable=E0712",  # Catching an exception which doesn't inherit from BaseException
            "--ignore=_librsync.so",
            "--msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}'",
            os.path.join(_top_dir, 'duplicity'),
            os.path.join(_top_dir, 'bin/duplicity'),
            os.path.join(_top_dir, 'bin/rdiffdir')],
            # Allow usage errors, older versions don't have
            # --msg-template
            [0, 32])

    @unittest.skipUnless(os.getenv('RUN_CODE_TESTS', None) == '1',
                         'Must set environment var RUN_CODE_TESTS=1')
    def test_pep8(self):
        ignores = [
            "E402",  # module level import not at top of file
            "E731",  # do not assign a lambda expression, use a def
        ]
        self.run_checker(["pep8",
                          "--ignore=" + ','.join(ignores),
                          "--max-line-length=120",
                          os.path.join(_top_dir, 'duplicity'),
                          os.path.join(_top_dir, 'bin/duplicity'),
                          os.path.join(_top_dir, 'bin/rdiffdir')])


if __name__ == "__main__":
    unittest.main()

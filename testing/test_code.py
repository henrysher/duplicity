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
import subprocess
import pytest
import fnmatch
import os

if os.getenv(u'RUN_CODE_TESTS', None) == u'1':
    # Make conditional so that we do not have to import in environments that
    # do not run the tests (e.g. the build servers)
    import pycodestyle

from . import _top_dir, DuplicityTestCase  # @IgnorePep8
from . import find_unadorned_strings

skipCodeTest = pytest.mark.skipif(not os.getenv(u'RUN_CODE_TESTS', None) == u'1',
                                  reason=u'Must set environment var RUN_CODE_TESTS=1')


class CodeTest(DuplicityTestCase):

    def run_checker(self, cmd, returncodes=[0]):
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output = process.communicate()[0]
        self.assertTrue(process.returncode in returncodes, output)
        self.assertEqual(u"", output, output)

    @skipCodeTest
    def test_2to3(self):
        # As we modernize the source code, we can remove more and more nofixes
        self.run_checker([
            u"2to3",
            u"--nofix=next",
            u"--nofix=types",
            u"--nofix=unicode",
            # The following fixes we don't want to remove, since they are false
            # positives, things we don't care about, or real incompatibilities
            # but which 2to3 can fix for us better automatically.
            u"--nofix=callable",
            u"--nofix=dict",
            u"--nofix=future",
            u"--nofix=imports",
            u"--nofix=print",
            u"--nofix=raw_input",
            u"--nofix=urllib",
            u"--nofix=xrange",
            _top_dir])

    @skipCodeTest
    def test_pylint(self):
        u"""Pylint test (requires pylint to be installed to pass)"""
        self.run_checker([
            u"pylint",
            u"-E",
            u"--msg-template={msg_id}: {line}: {msg}",
            u"--disable=E0203",  # Access to member before its definition line
            u"--disable=E0602",  # Undefined variable
            u"--disable=E0611",  # No name in module
            u"--disable=E1101",  # Has no member
            u"--disable=E1103",  # Maybe has no member
            u"--disable=E0712",  # Catching an exception which doesn't inherit from BaseException
            u"--ignore=_librsync.so",
            u"--msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}'",
            os.path.join(_top_dir, u'duplicity'),
            os.path.join(_top_dir, u'bin/duplicity'),
            os.path.join(_top_dir, u'bin/rdiffdir')],
            # Allow usage errors, older versions don't have
            # --msg-template
            [0, 32])

    @skipCodeTest
    def test_pep8(self):
        u"""Test that we conform to PEP-8 using pycodestyle."""
        # Note that the settings, ignores etc for pycodestyle are set in tox.ini, not here
        style = pycodestyle.StyleGuide(config_file=os.path.join(_top_dir, u'tox.ini'))
        result = style.check_files([os.path.join(_top_dir, u'duplicity'),
                                    os.path.join(_top_dir, u'bin/duplicity'),
                                    os.path.join(_top_dir, u'bin/rdiffdir')])
        self.assertEqual(result.total_errors, 0,
                         u"Found %s code style errors (and warnings)." % result.total_errors)

    @skipCodeTest
    def test_unadorned_string_literals(self):
        u"""For predictable results in python2/3 all string literals need to be marked as unicode, bytes or raw"""

        ignored_files = [os.path.join(_top_dir, u'.tox', u'*'), # These are not source files we want to check
                         os.path.join(_top_dir, u'.eggs', u'*'),
                         # TODO Every file from here down needs to be fixed and the exclusion removed
                         os.path.join(_top_dir, u'setup.py'),
                         os.path.join(_top_dir, u'docs', u'conf.py'),
                         os.path.join(_top_dir, u'duplicity', u'__init__.py'),
                         os.path.join(_top_dir, u'duplicity', u'asyncscheduler.py'),
                         os.path.join(_top_dir, u'duplicity', u'backend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'__init__.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'_boto_multi.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'_boto_single.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'_cf_cloudfiles.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'_cf_pyrax.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'acdclibackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'adbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'azurebackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'b2backend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'botobackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'cfbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'dpbxbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'gdocsbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'giobackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'hsibackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'hubicbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'imapbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'jottacloudbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'lftpbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'localbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'mediafirebackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'megabackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'multibackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'ncftpbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'onedrivebackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'par2backend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'pcabackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'pydrivebackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'pyrax_identity', u'__init__.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'pyrax_identity', u'hubic.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'rsyncbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'ssh_paramiko_backend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'ssh_pexpect_backend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'swiftbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'sxbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'tahoebackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'backends', u'webdavbackend.py'),
                         os.path.join(_top_dir, u'duplicity', u'cached_ops.py'),
                         os.path.join(_top_dir, u'duplicity', u'collections.py'),
                         os.path.join(_top_dir, u'duplicity', u'commandline.py'),
                         os.path.join(_top_dir, u'duplicity', u'compilec.py'),
                         os.path.join(_top_dir, u'duplicity', u'diffdir.py'),
                         os.path.join(_top_dir, u'duplicity', u'dup_temp.py'),
                         os.path.join(_top_dir, u'duplicity', u'dup_threading.py'),
                         os.path.join(_top_dir, u'duplicity', u'dup_time.py'),
                         os.path.join(_top_dir, u'duplicity', u'errors.py'),
                         os.path.join(_top_dir, u'duplicity', u'file_naming.py'),
                         os.path.join(_top_dir, u'duplicity', u'filechunkio.py'),
                         os.path.join(_top_dir, u'duplicity', u'globals.py'),
                         os.path.join(_top_dir, u'duplicity', u'gpg.py'),
                         os.path.join(_top_dir, u'duplicity', u'gpginterface.py'),
                         os.path.join(_top_dir, u'duplicity', u'lazy.py'),
                         os.path.join(_top_dir, u'duplicity', u'librsync.py'),
                         os.path.join(_top_dir, u'duplicity', u'log.py'),
                         os.path.join(_top_dir, u'duplicity', u'manifest.py'),
                         os.path.join(_top_dir, u'duplicity', u'patchdir.py'),
                         os.path.join(_top_dir, u'duplicity', u'path.py'),
                         os.path.join(_top_dir, u'duplicity', u'progress.py'),
                         os.path.join(_top_dir, u'duplicity', u'robust.py'),
                         os.path.join(_top_dir, u'duplicity', u'statistics.py'),
                         os.path.join(_top_dir, u'duplicity', u'tarfile.py'),
                         os.path.join(_top_dir, u'duplicity', u'tempdir.py'),
                         os.path.join(_top_dir, u'duplicity', u'util.py'),
                         os.path.join(_top_dir, u'testing', u'__init__.py'),
                         os.path.join(_top_dir, u'testing', u'find_unadorned_strings.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'__init__.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_badupload.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_cleanup.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_final.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_log.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_rdiffdir.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_replicate.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_restart.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_selection.py'),
                         os.path.join(_top_dir, u'testing', u'functional', u'test_verify.py'),
                         os.path.join(_top_dir, u'testing', u'manual', u'__init__.py'),
                         os.path.join(_top_dir, u'testing', u'overrides', u'__init__.py'),
                         os.path.join(_top_dir, u'testing', u'overrides', u'gettext.py'),
                         os.path.join(_top_dir, u'testing', u'test_unadorned.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'__init__.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_backend_instance.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_backend.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_collections.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_diffdir.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_dup_temp.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_dup_time.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_file_naming.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_gpg.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_gpginterface.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_lazy.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_manifest.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_patchdir.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_path.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_selection.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_statistics.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_tarfile.py'),
                         os.path.join(_top_dir, u'testing', u'unit', u'test_tempdir.py')]


        # Find all the .py files in the duplicity tree
        # We cannot use glob.glob recursive until we drop support for Python < 3.5
        matches = []

        def multi_filter(names, patterns):
            u"""Generator function which yields the names that match one or more of the patterns."""
            for name in names:
                if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
                    yield name

        for root, dirnames, filenames in os.walk(_top_dir):
            for filename in fnmatch.filter(filenames, u'*.py'):
                matches.append(os.path.join(root, filename))

        excluded = multi_filter(matches, ignored_files) if ignored_files else []
        matches = list(set(matches) - set(excluded))

        for python_source_file in matches:
            # Check each of the relevant python sources for unadorned string literals
            unadorned_string_list = find_unadorned_strings.check_file_for_unadorned(python_source_file)
            self.assertEqual([], unadorned_string_list,
                             u"Found %s unadorned strings: \n %s" % (len(unadorned_string_list), unadorned_string_list))


if __name__ == u"__main__":
    unittest.main()

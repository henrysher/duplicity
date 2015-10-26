#!/usr/bin/env python2
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

import sys
import os
from setuptools import setup, Extension
from setuptools.command.test import test
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from distutils.command.build_scripts import build_scripts

version_string = "$version"

if sys.version_info[:2] < (2, 6):
    print("Sorry, duplicity requires version 2.6 or later of python")
    sys.exit(1)

incdir_list = libdir_list = None

if os.name == 'posix':
    LIBRSYNC_DIR = os.environ.get('LIBRSYNC_DIR', '')
    args = sys.argv[:]
    for arg in args:
        if arg.startswith('--librsync-dir='):
            LIBRSYNC_DIR = arg.split('=')[1]
            sys.argv.remove(arg)
    if LIBRSYNC_DIR:
        incdir_list = [os.path.join(LIBRSYNC_DIR, 'include')]
        libdir_list = [os.path.join(LIBRSYNC_DIR, 'lib')]

data_files = [('share/man/man1',
               ['bin/duplicity.1',
                'bin/rdiffdir.1']),
              ('share/doc/duplicity-%s' % version_string,
               ['COPYING',
                'README',
                'README-REPO',
                'README-LOG',
                'CHANGELOG']),
              ]

top_dir = os.path.dirname(os.path.abspath(__file__))
assert os.path.exists(os.path.join(top_dir, "po")), "Missing 'po' directory."
for root, dirs, files in os.walk(os.path.join(top_dir, "po")):
    for file in files:
        path = os.path.join(root, file)
        if path.endswith("duplicity.mo"):
            lang = os.path.split(root)[-1]
            data_files.append(
                ('share/locale/%s/LC_MESSAGES' % lang,
                 ["po/%s/duplicity.mo" % lang]))


class TestCommand(test):
    def run(self):
        # Make sure all modules are ready
        build_cmd = self.get_finalized_command("build_py")
        build_cmd.run()
        # And make sure our scripts are ready
        build_scripts_cmd = self.get_finalized_command("build_scripts")
        build_scripts_cmd.run()

        # make symlinks for test data
        if build_cmd.build_lib != top_dir:
            for path in ['testfiles.tar.gz', 'gnupg']:
                src = os.path.join(top_dir, 'testing', path)
                target = os.path.join(build_cmd.build_lib, 'testing', path)
                try:
                    os.symlink(src, target)
                except Exception:
                    pass

        os.environ['PATH'] = "%s:%s" % (
            os.path.abspath(build_scripts_cmd.build_dir),
            os.environ.get('PATH'))

        test.run(self)


class InstallCommand(install):
    def run(self):
        # Normally, install will call build().  But we want to delete the
        # testing dir between building and installing.  So we manually build
        # and mark ourselves to skip building when we run() for real.
        self.run_command('build')
        self.skip_build = True

        # This should always be true, but just to make sure!
        if self.build_lib != top_dir:
            testing_dir = os.path.join(self.build_lib, 'testing')
            os.system("rm -rf %s" % testing_dir)

        install.run(self)


# TODO: move logic from dist/makedist inline
class SDistCommand(sdist):
    def run(self):
        version = version_string
        if version[0] == '$':
            version = "0"
        os.system(os.path.join(top_dir, "dist", "makedist") + " " + version)
        os.system("rm -f duplicity.spec")
        os.system("mkdir -p " + self.dist_dir)
        os.system("mv duplicity-" + version + ".tar.gz " + self.dist_dir)

# don't touch my shebang
class BSCommand (build_scripts):
    def run(self):
        """
        Copy, chmod each script listed in 'self.scripts'
        essentially this is the stripped 
         distutils.command.build_scripts.copy_scripts()
        routine
        """
        from stat import ST_MODE
        from distutils.dep_util import newer
        from distutils import log

        self.mkpath(self.build_dir)
        outfiles = []
        for script in self.scripts:
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            outfiles.append(outfile)

            if not self.force and not newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                continue

            log.info("copying and NOT adjusting %s -> %s", script,
                         self.build_dir)
            self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 0o7777
                    newmode = (oldmode | 0o555) & 0o7777
                    if newmode != oldmode:
                        log.info("changing mode of %s from %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)

setup(name="duplicity",
      version=version_string,
      description="Encrypted backup using rsync algorithm",
      author="Ben Escoto <ben@emerose.org>",
      author_email="bescoto@stanford.edu",
      maintainer="Kenneth Loafman <kenneth@loafman.com>",
      maintainer_email="kenneth@loafman.com",
      url="http://duplicity.nongnu.org/index.html",
      packages=['duplicity',
                  'duplicity.backends',
                  'duplicity.backends.pyrax_identity',
                  'testing',
                  'testing.functional',
                  'testing.overrides',
                  'testing.unit'],
      package_dir={"duplicity": "duplicity",
                   "duplicity.backends": "duplicity/backends", },
      ext_modules=[Extension("duplicity._librsync",
                             ["duplicity/_librsyncmodule.c"],
                             include_dirs=incdir_list,
                             library_dirs=libdir_list,
                             libraries=["rsync"])],
      scripts=['bin/rdiffdir', 'bin/duplicity'],
      data_files=data_files,
      tests_require=['lockfile', 'mock', 'pexpect'],
      test_suite='testing',
      cmdclass={'test': TestCommand,
                'install': InstallCommand,
                'sdist': SDistCommand,
                'build_scripts': BSCommand},
      )

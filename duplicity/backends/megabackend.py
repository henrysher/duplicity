# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2017 Tomas Vondra (Launchpad id: tomas-v)
# Copyright 2017 Kenneth Loafman <kenneth@loafman.com>
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

import duplicity.backend
from duplicity import log
from duplicity.errors import BackendException

import os
import subprocess


class MegaBackend(duplicity.backend.Backend):
    """Connect to remote store using Mega.co.nz API"""

    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        # ensure all the necessary megatools binaries exist
        self._check_binary_exists('megals')
        self._check_binary_exists('megamkdir')
        self._check_binary_exists('megaget')
        self._check_binary_exists('megaput')
        self._check_binary_exists('megarm')

        # store some basic info
        self._hostname = parsed_url.hostname

        if parsed_url.password is None:
            self._megarc = os.getenv('HOME') + '/.megarc'
        else:
            self._megarc = False
            self._username = parsed_url.username
            self._password = self.get_password()

        # remote folder (Can we assume /Root prefix?)
        self._root = '/Root'
        self._folder = self._root + '/' + parsed_url.path[1:]

        # make sure the remote folder exists (the whole path)
        self._makedir_recursive(parsed_url.path[1:].split('/'))

    def _check_binary_exists(self, cmd):
        'checks that a specified command exists in the current path'

        try:
            # ignore the output, we only need the return code
            subprocess.check_output(['which', cmd])
        except Exception as e:
            raise BackendException("command '%s' not found, make sure megatools are installed" % (cmd,))

    def _makedir(self, path):
        'creates a remote directory'

        if self._megarc:
            cmd = ['megamkdir', '--config', self._megarc, path]
        else:
            cmd = ['megamkdir', '-u', self._username, '-p', self._password, path]

        self.subprocess_popen(cmd)

    def _makedir_recursive(self, path):
        'creates a remote directory (recursively the whole path), ingores errors'

        print ("mkdir: %s" % ('/'.join(path),))

        p = self._root

        for folder in path:
            p = p + '/' + folder
            try:
                self._make_dir(p)
            except:
                pass

    def _put(self, source_path, remote_filename):
        'uploads file to Mega (deletes it first, to ensure it does not exist)'

        try:
            self.delete(remote_filename)
        except Exception:
            pass

        self.upload(local_file=source_path.get_canonical(), remote_file=remote_filename)

    def _get(self, remote_filename, local_path):
        'downloads file from Mega'

        self.download(remote_file=remote_filename, local_file=local_path.name)

    def _list(self):
        'list files in the backup folder'

        return self.folder_contents(files_only=True)

    def _delete(self, filename):
        'deletes remote '

        self.delete(remote_file=filename)

    def folder_contents(self, files_only=False):
        'lists contents of a folder, optionally ignoring subdirectories'

        print ("megals: %s" % (self._folder,))

        if self._megarc:
            cmd = ['megals', '--config', self._megarc, self._folder]
        else:
            cmd = ['megals', '-u', self._username, '-p', self._password, self._folder]

        files = subprocess.check_output(cmd)
        files = files.strip().split('\n')

        # remove the folder name, including the path separator
        files = [f[len(self._folder) + 1:] for f in files]

        # optionally ignore entries containing path separator (i.e. not files)
        if files_only:
            files = [f for f in files if '/' not in f]

        return files

    def download(self, remote_file, local_file):

        print ("megaget: %s" % (remote_file,))

        if self._megarc:
            cmd = ['megaget', '--config', self._megarc, '--no-progress',
                   '--path', local_file, self._folder + '/' + remote_file]
        else:
            cmd = ['megaget', '-u', self._username, '-p', self._password, '--no-progress',
                   '--path', local_file, self._folder + '/' + remote_file]

        self.subprocess_popen(cmd)

    def upload(self, local_file, remote_file):

        print ("megaput: %s" % (remote_file,))

        if self._megarc:
            cmd = ['megaput', '--config', self._megarc, '--no-progress',
                   '--path', self._folder + '/' + remote_file, local_file]
        else:
            cmd = ['megaput', '-u', self._username, '-p', self._password, '--no-progress',
                   '--path', self._folder + '/' + remote_file, local_file]

        self.subprocess_popen(cmd)

    def delete(self, remote_file):

        print ("megarm: %s" % (remote_file,))

        if self._megarc:
            cmd = ['megarm', '--config', self._megarc, self._folder + '/' + remote_file]
        else:
            cmd = ['megarm', '-u', self._username, '-p', self._password, self._folder + '/' + remote_file]

        self.subprocess_popen(cmd)


duplicity.backend.register_backend('mega', MegaBackend)
duplicity.backend.uses_netloc.extend(['mega'])

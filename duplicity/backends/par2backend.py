# Copyright 2013 Germar Reitze <germar.reitze@gmail.com>
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

from future_builtins import filter

import os
import re
from duplicity import backend
from duplicity.errors import BackendException
from duplicity import log
from duplicity import globals


class Par2Backend(backend.Backend):
    """This backend wrap around other backends and create Par2 recovery files
    before the file and the Par2 files are transfered with the wrapped backend.

    If a received file is corrupt it will try to repair it on the fly.
    """
    def __init__(self, parsed_url):
        backend.Backend.__init__(self, parsed_url)
        self.parsed_url = parsed_url
        try:
            self.redundancy = globals.par2_redundancy
        except AttributeError:
            self.redundancy = 10

        try:
            self.common_options = globals.par2_options + " -q -q"
        except AttributeError:
            self.common_options = "-q -q"

        self.wrapped_backend = backend.get_backend_object(parsed_url.url_string)

        for attr in ['_get', '_put', '_list', '_delete', '_delete_list',
                     '_query', '_query_list', '_retry_cleanup', '_error_code',
                     '_move', '_close']:
            if hasattr(self.wrapped_backend, attr):
                setattr(self, attr, getattr(self, attr[1:]))

        # always declare _delete_list support because _delete queries file
        # list for every call
        self._delete_list = self.delete_list

    def transfer(self, method, source_path, remote_filename):
        """create Par2 files and transfer the given file and the Par2 files
        with the wrapped backend.

        Par2 must run on the real filename or it would restore the
        temp-filename later on. So first of all create a tempdir and symlink
        the soure_path with remote_filename into this.
        """
        import pexpect

        par2temp = source_path.get_temp_in_same_dir()
        par2temp.mkdir()
        source_symlink = par2temp.append(remote_filename)
        source_target = source_path.get_canonical()
        if not os.path.isabs(source_target):
            source_target = os.path.join(os.getcwd(), source_target)
        os.symlink(source_target, source_symlink.get_canonical())
        source_symlink.setdata()

        log.Info("Create Par2 recovery files")
        par2create = 'par2 c -r%d -n1 %s %s' % (self.redundancy, self.common_options, source_symlink.get_canonical())
        out, returncode = pexpect.run(par2create, None, True)

        source_symlink.delete()
        files_to_transfer = []
        if not returncode:
            for file in par2temp.listdir():
                files_to_transfer.append(par2temp.append(file))

        method(source_path, remote_filename)
        for file in files_to_transfer:
            method(file, file.get_filename())

        par2temp.deltree()

    def put(self, local, remote):
        self.transfer(self.wrapped_backend._put, local, remote)

    def move(self, local, remote):
        self.transfer(self.wrapped_backend._move, local, remote)

    def get(self, remote_filename, local_path):
        """transfer remote_filename and the related .par2 file into
        a temp-dir. remote_filename will be renamed into local_path before
        finishing.

        If "par2 verify" detect an error transfer the Par2-volumes into the
        temp-dir and try to repair.
        """
        import pexpect
        par2temp = local_path.get_temp_in_same_dir()
        par2temp.mkdir()
        local_path_temp = par2temp.append(remote_filename)

        self.wrapped_backend._get(remote_filename, local_path_temp)

        try:
            par2file = par2temp.append(remote_filename + '.par2')
            self.wrapped_backend._get(par2file.get_filename(), par2file)

            par2verify = 'par2 v %s %s %s' % (self.common_options,
                                              par2file.get_canonical(),
                                              local_path_temp.get_canonical())
            out, returncode = pexpect.run(par2verify, None, True)

            if returncode:
                log.Warn("File is corrupt. Try to repair %s" % remote_filename)
                par2volumes = filter(re.compile(r'%s\.vol[\d+]*\.par2' % remote_filename).match,
                                     self.wrapped_backend._list())

                for filename in par2volumes:
                    file = par2temp.append(filename)
                    self.wrapped_backend._get(filename, file)

                par2repair = 'par2 r %s %s %s' % (self.common_options,
                                                  par2file.get_canonical(),
                                                  local_path_temp.get_canonical())
                out, returncode = pexpect.run(par2repair, None, True)

                if returncode:
                    log.Error("Failed to repair %s" % remote_filename)
                else:
                    log.Warn("Repair successful %s" % remote_filename)
        except BackendException:
            # par2 file not available
            pass
        finally:
            local_path_temp.rename(local_path)
            par2temp.deltree()

    def delete(self, filename):
        """delete given filename and its .par2 files
        """
        self.wrapped_backend._delete(filename)

        remote_list = self.unfiltered_list()

        c = re.compile(r'%s(?:\.vol[\d+]*)?\.par2' % filename)
        for remote_filename in remote_list:
            if c.match(remote_filename):
                self.wrapped_backend._delete(remote_filename)

    def delete_list(self, filename_list):
        """delete given filename_list and all .par2 files that belong to them
        """
        remote_list = self.unfiltered_list()

        for filename in filename_list[:]:
            c = re.compile(r'%s(?:\.vol[\d+]*)?\.par2' % filename)
            for remote_filename in remote_list:
                if c.match(remote_filename):
                    # insert here to make sure par2 files will be removed first
                    filename_list.insert(0, remote_filename)

        if hasattr(self.wrapped_backend, '_delete_list'):
            return self.wrapped_backend._delete_list(filename_list)
        else:
            for filename in filename_list:
                self.wrapped_backend._delete(filename)

    def list(self):
        """
        Return list of filenames (byte strings) present in backend

        Files ending with ".par2" will be excluded from the list.
        """
        remote_list = self.wrapped_backend._list()

        c = re.compile(r'(?!.*\.par2$)')
        filtered_list = []
        for filename in remote_list:
            if c.match(filename):
                filtered_list.append(filename)
        return filtered_list

    def unfiltered_list(self):
        return self.wrapped_backend._list()

    def retry_cleanup(self):
        self.wrapped_backend._retry_cleanup()

    def error_code(self, operation, e):
        return self.wrapped_backend._error_code(operation, e)

    def query(self, filename):
        return self.wrapped_backend._query(filename)

    def query_list(self, filename_list):
        return self.wrapped_backend._query(filename_list)

    def close(self):
        self.wrapped_backend._close()

backend.register_backend_prefix('par2', Par2Backend)

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

import os
import re
from duplicity import backend
from duplicity.errors import UnsupportedBackendScheme, BackendException
from duplicity import log
from duplicity import globals

class Par2WrapperBackend(backend.Backend):
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
            url_string = self.parsed_url.url_string.lstrip('par2+')
            self.wrapped_backend = backend.get_backend(url_string)
        except:
            raise UnsupportedBackendScheme(self.parsed_url.url_string)

        for attr in ['_get', '_put', '_list', '_delete', '_delete_list',
                     '_query', '_query_list', '_retry_cleanup', '_error_code',
                     '_move', '_close']:
            if hasattr(self.wrapped_backend, attr):
                setattr(self, attr, getattr(self, '_' + attr))

    def put(self, source_path, remote_filename = None):
        """create Par2 files and transfer the given file and the Par2 files
        with the wrapped backend.
        
        Par2 must run on the real filename or it would restore the
        temp-filename later on. So first of all create a tempdir and symlink
        the soure_path with remote_filename into this. 
        """
        import pexpect
        if remote_filename is None:
            remote_filename = source_path.get_filename()

        par2temp = source_path.get_temp_in_same_dir()
        par2temp.mkdir()
        source_symlink = par2temp.append(remote_filename)
        os.symlink(source_path.get_canonical(), source_symlink.get_canonical())
        source_symlink.setdata()

        log.Info("Create Par2 recovery files")
        par2create = 'par2 c -r%d -n1 -q -q %s' % (self.redundancy, source_symlink.get_canonical())
        out, returncode = pexpect.run(par2create, -1, True)
        source_symlink.delete()
        files_to_transfer = []
        if not returncode:
            for file in par2temp.listdir():
                files_to_transfer.append(par2temp.append(file))

        ret = self.wrapped_backend.put(source_path, remote_filename)
        for file in files_to_transfer:
            self.wrapped_backend.put(file, file.get_filename())

        par2temp.deltree()
        return ret

    def move(self, source_path, remote_filename = None):
        self.put(source_path, remote_filename)
        source_path.delete()

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

        ret = self.wrapped_backend.get(remote_filename, local_path_temp)

        try:
            par2file = par2temp.append(remote_filename + '.par2')
            self.wrapped_backend.get(par2file.get_filename(), par2file)

            par2verify = 'par2 v -q -q %s %s' % (par2file.get_canonical(), local_path_temp.get_canonical())
            out, returncode = pexpect.run(par2verify, -1, True)

            if returncode:
                log.Warn("File is corrupt. Try to repair %s" % remote_filename)
                par2volumes = self.list(re.compile(r'%s\.vol[\d+]*\.par2' % remote_filename))

                for filename in par2volumes:
                    file = par2temp.append(filename)
                    self.wrapped_backend.get(filename, file)

                par2repair = 'par2 r -q -q %s %s' % (par2file.get_canonical(), local_path_temp.get_canonical())
                out, returncode = pexpect.run(par2repair, -1, True)

                if returncode:
                    log.Error("Failed to repair %s" % remote_filename)
                else:
                    log.Warn("Repair successful %s" % remote_filename)
        except BackendException:
            #par2 file not available
            pass
        finally:
            local_path_temp.rename(local_path)
            par2temp.deltree()
        return ret

    def list(self, filter = re.compile(r'(?!.*\.par2$)')):
        """default filter all files that ends with ".par"
        filter can be a re.compile instance or False for all remote files
        """
        list = self.wrapped_backend.list()
        if not filter:
            return list
        filtered_list = []
        for item in list:
            if filter.match(item):
                filtered_list.append(item)
        return filtered_list

    def delete(self, filename_list):
        """delete given filename_list and all .par2 files that belong to them
        """
        remote_list = self.list(False)

        for filename in filename_list[:]:
            c =  re.compile(r'%s(?:\.vol[\d+]*)?\.par2' % filename)
            for remote_filename in remote_list:
                if c.match(remote_filename):
                    filename_list.append(remote_filename)

        return self.wrapped_backend.delete(filename_list)

    """just return the output of coresponding wrapped backend
    for all other functions
    """
    def query_list(self, filename_list, raise_errors=True):
        return self.wrapped_backend.query_info(filename_list, raise_errors)

    def _close(self):
        return self.wrapped_backend._close()

"""register this backend with leading "par2+" for all already known backends

files must be sorted in duplicity.backend.import_backends to catch
all supported backends
"""
for item in backend._backends.keys():
    backend.register_backend('par2+' + item, Par2WrapperBackend)

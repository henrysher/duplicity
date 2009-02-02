# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
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
import os.path
import tempfile

import duplicity.backend
from duplicity.errors import *
from duplicity import tempdir

class RsyncBackend(duplicity.backend.Backend):
    """Connect to remote store using rsync

    rsync backend contributed by Sebastian Wilhelmi <seppi@seppi.de>

    """
    def __init__(self, parsed_url):
        """rsyncBackend initializer"""
        duplicity.backend.Backend.__init__(self, parsed_url)
        user, host = parsed_url.netloc.split('@')
        if parsed_url.password:
            user = user.split(':')[0]
        mynetloc = '%s@%s' % (user, host)
        # module url: rsync://user@host::/modname/path
        # rsync via ssh/rsh: rsync://user@host//some_absolute_path
        #      -or-          rsync://user@host/some_relative_path
        if parsed_url.netloc.endswith("::"):
            # its a module path
            self.url_string = "%s%s" % (mynetloc, parsed_url.path.lstrip('/'))
        elif parsed_url.path.startswith("//"):
            # its an absolute path
            self.url_string = "%s:/%s" % (mynetloc.rstrip(':'), parsed_url.path.lstrip('/'))
        else:
            # its a relative path
            self.url_string = "%s:%s" % (mynetloc.rstrip(':'), parsed_url.path.lstrip('/'))
        if self.url_string[-1] != '/':
            self.url_string += '/'

    def put(self, source_path, remote_filename = None):
        """Use rsync to copy source_dir/filename to remote computer"""
        if not remote_filename: remote_filename = source_path.get_filename()
        remote_path = os.path.join(self.url_string, remote_filename)
        commandline = "rsync %s %s" % (source_path.name, remote_path)
        self.run_command(commandline)

    def get(self, remote_filename, local_path):
        """Use rsync to get a remote file"""
        remote_path = os.path.join (self.url_string, remote_filename)
        commandline = "rsync %s %s" % (remote_path, local_path.name)
        self.run_command(commandline)
        local_path.setdata()
        if not local_path.exists():
            raise BackendException("File %s not found" % local_path.name)

    def list(self):
        """List files"""
        def split (str):
            line = str.split ()
            if len (line) > 4 and line[4] != '.':
                return line[4]
            else:
                return None
        commandline = "rsync %s" % self.url_string
        return filter(lambda x: x, map (split, self.popen(commandline).split('\n')))

    def delete(self, filename_list):
        """Delete files."""
        delete_list = filename_list
        dont_delete_list = []
        for file in self.list ():
            if file in delete_list:
                delete_list.remove (file)
            else:
                dont_delete_list.append (file)
        if len (delete_list) > 0:
            raise BackendException("Files %s not found" % str (delete_list))

        dir = tempfile.mkdtemp()
        exclude, exclude_name = tempdir.default().mkstemp_file()
        to_delete = [exclude_name]
        for file in dont_delete_list:
            path = os.path.join (dir, file)
            to_delete.append (path)
            f = open (path, 'w')
            print >>exclude, file
            f.close()
        exclude.close()
        commandline = ("rsync --recursive --delete --exclude-from=%s %s/ %s" %
                                   (exclude_name, dir, self.url_string))
        self.run_command(commandline)
        for file in to_delete:
            os.unlink (file)
        os.rmdir (dir)

duplicity.backend.register_backend("rsync", RsyncBackend)

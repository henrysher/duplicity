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

import os, re
import tempfile

import duplicity.backend
from duplicity.errors import * #@UnusedWildImport
from duplicity import globals, tempdir, util

class RsyncBackend(duplicity.backend.Backend):
    """Connect to remote store using rsync

    rsync backend contributed by Sebastian Wilhelmi <seppi@seppi.de>
    rsyncd auth, alternate port support
        Copyright 2010 by Edgar Soldin <edgar.soldin@web.de>

    """
    def __init__(self, parsed_url):
        """rsyncBackend initializer"""
        duplicity.backend.Backend.__init__(self, parsed_url)
        """
        rsyncd module url: rsync://[user:password@]host[:port]::[/]modname/path
                      Note: 3.0.7 is picky about syntax use either 'rsync://' or '::'
                      cmd: rsync [--port=port] host::modname/path
        -or-
        rsync via ssh/rsh url: rsync://user@host[:port]://some_absolute_path
             -or-              rsync://user@host[:port]:/some_relative_path
                          cmd: rsync -e 'ssh [-p=port]' [user@]host:[/]path
        """
        host = parsed_url.hostname
        port = ""
        # RSYNC_RSH from calling shell might conflict with our settings
        if 'RSYNC_RSH' in os.environ:
            del os.environ['RSYNC_RSH']
        if self.over_rsyncd():
            # its a module path
            (path, port) = self.get_rsync_path()
            self.url_string = "%s::%s" % (host, path.lstrip('/:'))
            if port:
                port = " --port=%s" % port
        else:
            if parsed_url.path.startswith("//"):
                # its an absolute path
                self.url_string = "%s:/%s" % (host, parsed_url.path.lstrip('/'))
            else:
                # its a relative path
                self.url_string = "%s:%s" % (host, parsed_url.path.lstrip('/'))
            if parsed_url.port:
                port = " -p %s" % parsed_url.port
        # add trailing slash if missing
        if self.url_string[-1] != '/':
            self.url_string += '/'
        # user?
        if parsed_url.username:
            if self.over_rsyncd():
                os.environ['USER'] = parsed_url.username
            else:
                self.url_string = parsed_url.username + "@" + self.url_string
        # password?, don't ask if none was given
        self.use_getpass = False
        password = self.get_password()
        if password:
            os.environ['RSYNC_PASSWORD'] = password
        if self.over_rsyncd():
            portOption = port
        else:
            portOption = " -e 'ssh -oBatchMode=yes%s'" % port
        rsyncOptions = globals.rsync_options
        if rsyncOptions:
            rsyncOptions= " " + rsyncOptions
        # build cmd
        self.cmd = "rsync%s%s" % (portOption, rsyncOptions)

    def over_rsyncd(self):
        url = self.parsed_url.url_string
        if re.search('::[^:]*$', url):
            return True
        else:
            return False

    def get_rsync_path(self):
        url = self.parsed_url.url_string
        m = re.search("(:\d+|)?::([^:]*)$", url)
        if m:
            return m.group(2), m.group(1).lstrip(':')
        raise InvalidBackendURL("Could not determine rsync path: %s"
                                    "" % self.munge_password( url ) )

    def run_command(self, commandline):
        result, stdout, stderr = self.subprocess_popen_persist(commandline)
        return result, stdout

    def put(self, source_path, remote_filename = None):
        """Use rsync to copy source_dir/filename to remote computer"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        remote_path = os.path.join(self.url_string, remote_filename)
        commandline = "%s %s %s" % (self.cmd, source_path.name, remote_path)
        self.run_command(commandline)

    def get(self, remote_filename, local_path):
        """Use rsync to get a remote file"""
        remote_path = os.path.join (self.url_string, remote_filename)
        commandline = "%s %s %s" % (self.cmd, remote_path, local_path.name)
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
        commandline = "%s %s" % (self.cmd, self.url_string)
        result, stdout = self.run_command(commandline)
        return filter(lambda x: x, map (split, stdout.split('\n')))

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
        commandline = ("%s --recursive --delete --exclude-from=%s %s/ %s" %
                                   (self.cmd, exclude_name, dir, self.url_string))
        self.run_command(commandline)
        for file in to_delete:
            util.ignore_missing(os.unlink, file)
        os.rmdir (dir)

duplicity.backend.register_backend("rsync", RsyncBackend)

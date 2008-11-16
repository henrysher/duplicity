# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto
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
import urllib

import duplicity.backend
import duplicity.globals as globals
import duplicity.log     as log
from duplicity.errors import *
from duplicity         import tempdir

class FTPBackend(duplicity.backend.Backend):
    """Connect to remote store using File Transfer Protocol"""
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        # we expect an error return, so go low-level and ignore it
        try:
            p = os.popen("ncftpls -v")
            fout = p.read()
            ret = p.close()
        except:
            pass
        # the expected error is 8 in the high-byte and some output
        if ret != 0x0800 or not fout:
            log.FatalError("NcFTP not found:  Please install NcFTP version 3.1.9 or later")

        # version is the second word of the first line
        version = fout.split('\n')[0].split()[1]
        if version < "3.1.9":
            log.FatalError("NcFTP too old:  Duplicity requires NcFTP version 3.1.9 or later")
        log.Log("NcFTP version is %s" % version, 4)

        self.parsed_url = parsed_url

        self.url_string = duplicity.backend.strip_auth_from_url(self.parsed_url)

        # Use an explicit directory name.
        if self.url_string[-1] != '/':
            self.url_string += '/'

        self.password = self.get_password()

        if globals.ftp_connection == 'regular':
            self.conn_opt = '-E'
        else:
            self.conn_opt = '-F'

        self.tempfile, self.tempname = tempdir.default().mkstemp()
        os.write(self.tempfile, "host %s\n" % self.parsed_url.hostname)
        os.write(self.tempfile, "user %s\n" % self.parsed_url.username)
        os.write(self.tempfile, "pass %s\n" % self.password)
        os.close(self.tempfile)
        self.flags = "-f %s %s -t %s" % \
            (self.tempname, self.conn_opt, globals.timeout)
        if parsed_url.port != None and parsed_url.port != 21:
            self.flags += " -P '%s'" % (parsed_url.port)

    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        remote_path = os.path.join(urllib.unquote(self.parsed_url.path.lstrip('/')), remote_filename).rstrip()
        commandline = "ncftpput %s -m -V -C '%s' '%s'" % \
            (self.flags, source_path.name, remote_path)
        self.run_command_persist(commandline)

    def get(self, remote_filename, local_path):
        """Get remote filename, saving it to local_path"""
        remote_path = os.path.join(urllib.unquote(self.parsed_url.path), remote_filename).rstrip()
        commandline = "ncftpget %s -V -C '%s' '%s' '%s'" % \
            (self.flags, self.parsed_url.hostname, remote_path.lstrip('/'), local_path.name)
        self.run_command_persist(commandline)
        local_path.setdata()

    def list(self):
        """List files in directory"""
        # try for a long listing to avoid connection reset
        commandline = "ncftpls %s -l '%s'" % \
            (self.flags, self.url_string)
        l = self.popen_persist(commandline).split('\n')
        l = filter(lambda x: x, l)
        if not l:
            return l
        # if long list is not empty, get short list of names only
        commandline = "ncftpls -x '' %s '%s'" % \
            (self.flags, self.url_string)
        l = self.popen_persist(commandline).split('\n')
        l = [x.split()[-1] for x in l if x]
        return l

    def delete(self, filename_list):
        """Delete files in filename_list"""
        for filename in filename_list:
            commandline = "ncftpls -x '' %s -X 'DELE %s' '%s'" % \
                (self.flags, filename, self.url_string)
            self.popen_persist(commandline)

duplicity.backend.register_backend("ftp", FTPBackend)


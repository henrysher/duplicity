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

import os.path
import urllib

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport
from duplicity import tempdir

class FTPBackend(duplicity.backend.Backend):
    """Connect to remote store using File Transfer Protocol"""
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        # we expect an error return, so go low-level and ignore it
        try:
            p = os.popen("ncftpls -v")
            fout = p.read()
            ret = p.close()
        except Exception:
            pass
        # the expected error is 8 in the high-byte and some output
        if ret != 0x0800 or not fout:
            log.FatalError("NcFTP not found:  Please install NcFTP version 3.1.9 or later",
                           log.ErrorCode.ftp_ncftp_missing)

        # version is the second word of the first line
        version = fout.split('\n')[0].split()[1]
        if version < "3.1.9":
            log.FatalError("NcFTP too old:  Duplicity requires NcFTP version 3.1.9,"
                           "3.2.1 or later.  Version 3.2.0 will not work properly.",
                           log.ErrorCode.ftp_ncftp_too_old)
        elif version == "3.2.0":
            log.Warn("NcFTP (ncftpput) version 3.2.0 may fail with duplicity.\n"
                     "see: http://www.ncftpd.com/ncftp/doc/changelog.html\n"
                     "If you have trouble, please upgrade to 3.2.1 or later",
                     log.WarningCode.ftp_ncftp_v320)
        log.Notice("NcFTP version is %s" % version)

        self.parsed_url = parsed_url

        self.url_string = duplicity.backend.strip_auth_from_url(self.parsed_url)

        # This squelches the "file not found" result from ncftpls when
        # the ftp backend looks for a collection that does not exist.
        # version 3.2.2 has error code 5, 1280 is some legacy value
        self.popen_persist_breaks[ 'ncftpls' ] = [ 5, 1280 ]

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
        self.flags = "-f %s %s -t %s -o useCLNT=0,useHELP_SITE=0 " % \
            (self.tempname, self.conn_opt, globals.timeout)
        if parsed_url.port != None and parsed_url.port != 21:
            self.flags += " -P '%s'" % (parsed_url.port)

    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
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

    def _list(self):
        """List files in directory"""
        # Do a long listing to avoid connection reset
        commandline = "ncftpls %s -l '%s'" % (self.flags, self.url_string)
        l = self.popen_persist(commandline).split('\n')
        l = filter(lambda x: x, l)
        # Look for our files as the last element of a long list line
        return [x.split()[-1] for x in l if not x.startswith("total ")]

    def delete(self, filename_list):
        """Delete files in filename_list"""
        for filename in filename_list:
            commandline = "ncftpls %s -l -X 'DELE %s' '%s'" % \
                (self.flags, filename, self.url_string)
            self.popen_persist(commandline)

duplicity.backend.register_backend("ftp", FTPBackend)

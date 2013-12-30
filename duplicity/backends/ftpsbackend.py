# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2010 Marcel Pennewiss <opensource@pennewiss.de>
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
import os.path
import urllib
import re

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import *
from duplicity import tempdir

class FTPSBackend(duplicity.backend.Backend):
    """Connect to remote store using File Transfer Protocol"""
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        # we expect an output
        try:
            p = os.popen("lftp --version")
            fout = p.read()
            ret = p.close()
        except Exception:
            pass
        # there is no output if lftp not found
        if not fout:
            log.FatalError("LFTP not found:  Please install LFTP.",
                           log.ErrorCode.ftps_lftp_missing)

        # version is the second word of the second part of the first line
        version = fout.split('\n')[0].split(' | ')[1].split()[1]
        log.Notice("LFTP version is %s" % version)

        self.parsed_url = parsed_url

        self.url_string = duplicity.backend.strip_auth_from_url(self.parsed_url)

        # Use an explicit directory name.
        if self.url_string[-1] != '/':
            self.url_string += '/'

        self.password = self.get_password()

        if globals.ftp_connection == 'regular':
            self.conn_opt = 'off'
        else:
            self.conn_opt = 'on'

        if parsed_url.port != None and parsed_url.port != 21:
            self.portflag = " -p '%s'" % (parsed_url.port)
        else:
            self.portflag = ""

        self.tempfile, self.tempname = tempdir.default().mkstemp()
        os.write(self.tempfile, "set ftp:ssl-allow true\n")
        os.write(self.tempfile, "set ftp:ssl-protect-data true\n")
        os.write(self.tempfile, "set ftp:ssl-protect-list true\n")
        os.write(self.tempfile, "set net:timeout %s\n" % globals.timeout)
        os.write(self.tempfile, "set net:max-retries %s\n" % globals.num_retries)
        os.write(self.tempfile, "set ftp:passive-mode %s\n" % self.conn_opt)
        os.write(self.tempfile, "open %s %s\n" % (self.portflag, self.parsed_url.hostname))
        # allow .netrc auth by only setting user/pass when user was actually given
        if self.parsed_url.username:
            os.write(self.tempfile, "user %s %s\n" % (self.parsed_url.username, self.password))
        os.close(self.tempfile)

        self.flags = "-f %s" % self.tempname

    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        remote_path = os.path.join(urllib.unquote(self.parsed_url.path.lstrip('/')), remote_filename).rstrip()
        commandline = "lftp -c 'source %s;put \'%s\' -o \'%s\''" % \
            (self.tempname, source_path.name, remote_path)
        l = self.run_command_persist(commandline)

    def get(self, remote_filename, local_path):
        """Get remote filename, saving it to local_path"""
        remote_path = os.path.join(urllib.unquote(self.parsed_url.path), remote_filename).rstrip()
        commandline = "lftp -c 'source %s;get %s -o %s'" % \
            (self.tempname, remote_path.lstrip('/'), local_path.name)
        self.run_command_persist(commandline)
        local_path.setdata()

    def _list(self):
        """List files in directory"""
        # Do a long listing to avoid connection reset
        remote_dir = urllib.unquote(self.parsed_url.path.lstrip('/')).rstrip()
        commandline = "lftp -c 'source %s;ls \'%s\''" % (self.tempname, remote_dir)
        l = self.popen_persist(commandline).split('\n')
        l = filter(lambda x: x, l)
        # Look for our files as the last element of a long list line
        return [x.split()[-1] for x in l]

    def delete(self, filename_list):
        """Delete files in filename_list"""
        filelist = ""
        for filename in filename_list:
            filelist += "\'%s\' " % filename
        if filelist.rstrip():
            remote_dir = urllib.unquote(self.parsed_url.path.lstrip('/')).rstrip()
            commandline = "lftp -c 'source %s;cd \'%s\';rm %s'" % (self.tempname, remote_dir, filelist.rstrip())
            self.popen_persist(commandline)

duplicity.backend.register_backend("ftps", FTPSBackend)

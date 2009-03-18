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
import urllib
import time
import re
from types import *

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import *
from duplicity import tempdir
from duplicity import pexpect

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
            log.FatalError("NcFTP not found:  Please install NcFTP version 3.1.9 or later",
                           log.ErrorCode.ftp_ncftp_missing)

        # version is the second word of the first line
        version = fout.split('\n')[0].split()[1]
        if version < "3.1.9":
            log.FatalError("NcFTP too old:  Duplicity requires NcFTP version 3.1.9 or later",
                           log.ErrorCode.ftp_ncftp_too_old)
        log.Log("NcFTP version is %s" % version, 4)

        self.parsed_url = parsed_url

        self.url_string = duplicity.backend.strip_auth_from_url(self.parsed_url)

        # Use an explicit directory name.
        if self.url_string[-1] != '/':
            self.url_string += '/'

        self.password = self.get_password()

        if globals.ftp_connection == 'regular':
            self.passive = "no"
        else:
            self.passive = "yes"

        self.flags = "-u %s" % parsed_url.username

        if parsed_url.port != None and parsed_url.port != 21:
            self.flags += " -P '%s'" % (parsed_url.port)

        self.commandline = "ncftp %s %s" % (self.flags, parsed_url.hostname)

    def run_ftp_command_list(self, commands):
        """
        Run an ftp command list, responding to password prompts
        Each list is prefixed by a cd to the remote dir and
        suffixed by a quit so each command list runs on a single
        invocation of the ftp client.
        """
        def filter_ansi(str):
            """Filter ANSI control strings used by NcFTP"""
            str = re.sub("\x0d", '', str)
            return re.sub("\x1b\[[01]m", '', str)

        res = ''
        err = False
        remote_dir = urllib.unquote(self.parsed_url.path.lstrip('/'))
        prefix = ["set yes-i-know-about-NcFTPd yes",
                  "set autosave-bookmark-changes no",
                  "set confirm-close no",
                  "set auto-resume yes",
                  "type binary",
                  "set passive %s" % self.passive,
                  "mkdir %s" % remote_dir,
                  "cd %s" % remote_dir,]
        command_list = prefix + commands

        for n in range(1, globals.num_retries+1):
            if n > 1:
                # sleep before retry
                time.sleep(30)
            log.Log("Running '%s' (attempt #%d)" % (self.commandline, n), 5)
            child = pexpect.spawn(self.commandline, timeout = None)
            cmdloc = 0
            state = "authorizing"
            while 1:
                if state == "authorizing":
                    match = child.expect([pexpect.EOF,
                                          pexpect.TIMEOUT,
                                          "(?i)unknown host",
                                          "(?i)password:",],
                                          globals.timeout)
                    log.Log("State = %s, Before = '%s'" % (state, filter_ansi(child.before)), 9)
                    if match in (0, 1):
                        log.Log("No response from host", 1)
                        err = True
                        break
                    elif match == 2:
                        log.Log("Unknown host %s" % self.parsed_url.hostname, 1)
                        err = True
                        break
                    elif match == 3:
                        child.sendline(self.password)
                        state = "running"

                elif state == "running":
                    match = child.expect([pexpect.EOF,
                                          pexpect.TIMEOUT,
                                          "(?i)ncftp.*>",
                                          "(?i)cannot open local file .* for reading",
                                          "(?i)cannot open local file .* for writing",
                                          "(?i)get .*: server said: .*: no such file or directory",
                                          "(?i)put .*: server said: .*: no such file or directory",
                                          "(?i)could not write to control stream: Broken pipe.",
                                          "(?i)login incorrect",
                                          "(?i)could not open",],
                                          globals.timeout)
                    log.Log("State = %s, Before = '%s'" % (state, filter_ansi(child.before)), 9)
                    if match == 0:
                        break
                    elif match == 1:
                        log.Log("Timeout waiting for response", 1)
                        err = True
                        break
                    elif match == 2:
                        if cmdloc < len(command_list):
                            command = command_list[cmdloc]
                            log.Log("ftp command: '%s'" % (command,), 5)
                            child.sendline(command)
                            cmdloc += 1
                        else:
                            command = 'quit'
                            log.Log("ftp command: '%s'" % (command,), 5)
                            child.sendline(command)
                            res = filter_ansi(child.before)
                    elif match in (3, 4):
                        log.Log("Cannot open local file", 1)
                        err = True
                        break
                    elif match in (5, 6):
                        log.Log("Cannot open remote file", 1)
                        err = True
                        break
                    elif match == 7:
                        log.Log("Could not write to control stream", 1)
                        err = True
                        break
                    elif match in (8, 9):
                        log.Log("Incorrect login / could not open host", 1)
                        err = True
                        break

            child.close(force = True)
            if (not err) and (child.exitstatus == 0):
                return res
            log.Log("Running '%s' failed (attempt #%d)" % (self.commandline, n), 5)
            err = False
        log.Log("Giving up trying to execute '%s' after %d attempts" % (self.commandline, globals.num_retries), 1)
        raise BackendException("Error running '%s'" % self.commandline)

    def put(self, source_path, remote_filename):
        """Transfer source_path to remote_filename"""
        commands = ["put -z %s %s" % (source_path.name, remote_filename),]
        res = self.run_ftp_command_list(commands)

    def get(self, remote_filename, local_path):
        """Get remote filename, saving it to local_path"""
        commands = ["get -z %s %s" % (remote_filename, local_path.name),]
        res = self.run_ftp_command_list(commands)
        local_path.setdata()

    def list(self):
        """List files in directory"""
        commands = ["ls -1",]
        res = self.run_ftp_command_list(commands)
        lst = [x.strip() for x in res.split('\n') if x]
        lst = [x for x in lst[1:] if x and x[0] != '\x1b']
        return lst

    def delete(self, filename_list):
        """Delete files in filename_list"""
        assert type(filename_list) in (TupleType, ListType), type(filename_list)
        commands = ["rm %s" % fn for fn in filename_list]
        if commands:
            res = self.run_ftp_command_list(commands)
        else:
            res = ""

duplicity.backend.register_backend("ftp", FTPBackend)

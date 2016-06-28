# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2010 Marcel Pennewiss <opensource@pennewiss.de>
# Copyright 2014 Edgar Soldin
#                 - webdav, fish, sftp support
#                 - https cert verification switches
#                 - debug output
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
import re
import urllib
try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity import tempdir


class LFTPBackend(duplicity.backend.Backend):
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

        self.scheme = duplicity.backend.strip_prefix(parsed_url.scheme, 'lftp').lower()
        self.scheme = re.sub('^webdav', 'http', self.scheme)
        self.url_string = self.scheme + '://' + parsed_url.hostname
        if parsed_url.port:
            self.url_string += ":%s" % parsed_url.port

        self.remote_path = re.sub('^/', '', parsed_url.path)

        # Fix up an empty remote path
        if len(self.remote_path) == 0:
            self.remote_path = '/'

        # Use an explicit directory name.
        if self.remote_path[-1] != '/':
            self.remote_path += '/'

        self.authflag = ''
        if self.parsed_url.username:
            self.username = self.parsed_url.username
            self.password = self.get_password()
            self.authflag = "-u '%s,%s'" % (self.username, self.password)

        if globals.ftp_connection == 'regular':
            self.conn_opt = 'off'
        else:
            self.conn_opt = 'on'

        # check for cacert file if https
        self.cacert_file = globals.ssl_cacert_file
        if self.scheme == 'https' and not globals.ssl_no_check_certificate:
            cacert_candidates = ["~/.duplicity/cacert.pem",
                                 "~/duplicity_cacert.pem",
                                 "/etc/duplicity/cacert.pem"]
            # look for a default cacert file
            if not self.cacert_file:
                for path in cacert_candidates:
                    path = os.path.expanduser(path)
                    if (os.path.isfile(path)):
                        self.cacert_file = path
                        break

        # save config into a reusable temp file
        self.tempfile, self.tempname = tempdir.default().mkstemp()
        os.write(self.tempfile, "set ssl:verify-certificate " +
                 ("false" if globals.ssl_no_check_certificate else "true") + "\n")
        if self.cacert_file:
            os.write(self.tempfile, "set ssl:ca-file " + cmd_quote(self.cacert_file) + "\n")
        if globals.ssl_cacert_path:
            os.write(self.tempfile, "set ssl:ca-path " + cmd_quote(globals.ssl_cacert_path) + "\n")
        if self.parsed_url.scheme == 'ftps':
            os.write(self.tempfile, "set ftp:ssl-allow true\n")
            os.write(self.tempfile, "set ftp:ssl-protect-data true\n")
            os.write(self.tempfile, "set ftp:ssl-protect-list true\n")
        elif self.parsed_url.scheme == 'ftpes':
            os.write(self.tempfile, "set ftp:ssl-force on\n")
            os.write(self.tempfile, "set ftp:ssl-protect-data on\n")
            os.write(self.tempfile, "set ftp:ssl-protect-list on\n")
        else:
            os.write(self.tempfile, "set ftp:ssl-allow false\n")
        os.write(self.tempfile, "set http:use-propfind true\n")
        os.write(self.tempfile, "set net:timeout %s\n" % globals.timeout)
        os.write(self.tempfile, "set net:max-retries %s\n" % globals.num_retries)
        os.write(self.tempfile, "set ftp:passive-mode %s\n" % self.conn_opt)
        if log.getverbosity() >= log.DEBUG:
            os.write(self.tempfile, "debug\n")
        if self.parsed_url.scheme == 'ftpes':
            os.write(self.tempfile, "open %s %s\n" % (self.authflag, self.url_string.replace('ftpes', 'ftp')))
        else:
            os.write(self.tempfile, "open %s %s\n" % (self.authflag, self.url_string))
        os.close(self.tempfile)
        # print settings in debug mode
        if log.getverbosity() >= log.DEBUG:
            f = open(self.tempname, 'r')
            log.Debug("SETTINGS: \n"
                      "%s" % f.read())

    def _put(self, source_path, remote_filename):
        commandline = "lftp -c \"source %s; mkdir -p %s; put %s -o %s\"" % (
            self.tempname,
            cmd_quote(self.remote_path),
            cmd_quote(source_path.name),
            cmd_quote(self.remote_path) + remote_filename
        )
        log.Debug("CMD: %s" % commandline)
        s, l, e = self.subprocess_popen(commandline)
        log.Debug("STATUS: %s" % s)
        log.Debug("STDERR:\n"
                  "%s" % (e))
        log.Debug("STDOUT:\n"
                  "%s" % (l))

    def _get(self, remote_filename, local_path):
        commandline = "lftp -c \"source %s; get %s -o %s\"" % (
            cmd_quote(self.tempname),
            cmd_quote(self.remote_path) + remote_filename,
            cmd_quote(local_path.name)
        )
        log.Debug("CMD: %s" % commandline)
        _, l, e = self.subprocess_popen(commandline)
        log.Debug("STDERR:\n"
                  "%s" % (e))
        log.Debug("STDOUT:\n"
                  "%s" % (l))

    def _list(self):
        # Do a long listing to avoid connection reset
        # remote_dir = urllib.unquote(self.parsed_url.path.lstrip('/')).rstrip()
        remote_dir = urllib.unquote(self.parsed_url.path)
        # print remote_dir
        quoted_path = cmd_quote(self.remote_path)
        # failing to cd into the folder might be because it was not created already
        commandline = "lftp -c \"source %s; ( cd %s && ls ) || ( mkdir -p %s && cd %s && ls )\"" % (
            cmd_quote(self.tempname),
            quoted_path, quoted_path, quoted_path
        )
        log.Debug("CMD: %s" % commandline)
        _, l, e = self.subprocess_popen(commandline)
        log.Debug("STDERR:\n"
                  "%s" % (e))
        log.Debug("STDOUT:\n"
                  "%s" % (l))

        # Look for our files as the last element of a long list line
        return [x.split()[-1] for x in l.split('\n') if x]

    def _delete(self, filename):
        commandline = "lftp -c \"source %s; cd %s; rm %s\"" % (
            cmd_quote(self.tempname),
            cmd_quote(self.remote_path),
            cmd_quote(filename)
        )
        log.Debug("CMD: %s" % commandline)
        _, l, e = self.subprocess_popen(commandline)
        log.Debug("STDERR:\n"
                  "%s" % (e))
        log.Debug("STDOUT:\n"
                  "%s" % (l))

duplicity.backend.register_backend("ftp", LFTPBackend)
duplicity.backend.register_backend("ftps", LFTPBackend)
duplicity.backend.register_backend("fish", LFTPBackend)
duplicity.backend.register_backend("ftpes", LFTPBackend)

duplicity.backend.register_backend("lftp+ftp", LFTPBackend)
duplicity.backend.register_backend("lftp+ftps", LFTPBackend)
duplicity.backend.register_backend("lftp+fish", LFTPBackend)
duplicity.backend.register_backend("lftp+ftpes", LFTPBackend)
duplicity.backend.register_backend("lftp+sftp", LFTPBackend)
duplicity.backend.register_backend("lftp+webdav", LFTPBackend)
duplicity.backend.register_backend("lftp+webdavs", LFTPBackend)
duplicity.backend.register_backend("lftp+http", LFTPBackend)
duplicity.backend.register_backend("lftp+https", LFTPBackend)

duplicity.backend.uses_netloc.extend(['ftp', 'ftps', 'fish', 'ftpes',
                                      'lftp+ftp', 'lftp+ftps',
                                      'lftp+fish', 'lftp+ftpes',
                                      'lftp+sftp',
                                      'lftp+webdav', 'lftp+webdavs',
                                      'lftp+http', 'lftp+https']
                                     )

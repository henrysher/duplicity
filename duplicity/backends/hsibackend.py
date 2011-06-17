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

import os

import duplicity.backend
from duplicity.errors import * #@UnusedWildImport

hsi_command = "hsi"
class HSIBackend(duplicity.backend.Backend):
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        self.host_string = parsed_url.hostname
        self.remote_dir = parsed_url.path
        if self.remote_dir:
            self.remote_prefix = self.remote_dir + "/"
        else:
            self.remote_prefix = ""

    def put(self, source_path, remote_filename = None):
        if not remote_filename:
            remote_filename = source_path.get_filename()
        commandline = '%s "put %s : %s%s"' % (hsi_command,source_path.name,self.remote_prefix,remote_filename)
        try:
            self.run_command(commandline)
        except Exception:
            print commandline

    def get(self, remote_filename, local_path):
        commandline = '%s "get %s : %s%s"' % (hsi_command, local_path.name, self.remote_prefix, remote_filename)
        self.run_command(commandline)
        local_path.setdata()
        if not local_path.exists():
            raise BackendException("File %s not found" % local_path.name)

    def list(self):
        commandline = '%s "ls -l %s"' % (hsi_command, self.remote_dir)
        l = os.popen3(commandline)[2].readlines()[3:]
        for i in range(0,len(l)):
            l[i] = l[i].split()[-1]
        print filter(lambda x: x, l)
        return filter(lambda x: x, l)

    def delete(self, filename_list):
        assert len(filename_list) > 0
        for fn in filename_list:
            commandline = '%s "rm %s%s"' % (hsi_command, self.remote_prefix, fn)
            self.run_command(commandline)

duplicity.backend.register_backend("hsi", HSIBackend)



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

    def _put(self, source_path, remote_filename):
        commandline = '%s "put %s : %s%s"' % (hsi_command, source_path.name, self.remote_prefix, remote_filename)
        self.subprocess_popen(commandline)

    def _get(self, remote_filename, local_path):
        commandline = '%s "get %s : %s%s"' % (hsi_command, local_path.name, self.remote_prefix, remote_filename)
        self.subprocess_popen(commandline)

    def _list(self):
        import sys
        commandline = '%s "ls -l %s"' % (hsi_command, self.remote_dir)
        l = self.subprocess_popen(commandline)[2]
        l = l.split(os.linesep)[3:]
        for i in range(0, len(l)):
            if l[i]:
                l[i] = l[i].split()[-1]
        return [x for x in l if x]

    def _delete(self, filename):
        commandline = '%s "rm %s%s"' % (hsi_command, self.remote_prefix, filename)
        self.subprocess_popen(commandline)

duplicity.backend.register_backend("hsi", HSIBackend)
duplicity.backend.uses_netloc.extend(['hsi'])

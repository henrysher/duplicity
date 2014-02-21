# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2008 Francois Deppierraz
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

import duplicity.backend
from duplicity import log
from duplicity.errors import * #@UnusedWildImport

from commands import getstatusoutput

class TAHOEBackend(duplicity.backend.Backend):
    """
    Backend for the Tahoe file system
    """

    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        url = parsed_url.path.strip('/').split('/')

        self.alias = url[0]

        if len(url) > 2:
            self.directory = "/".join(url[1:])
        elif len(url) == 2:
            self.directory = url[1]
        else:
            self.directory = ""

        log.Debug("tahoe: %s -> %s:%s" % (url, self.alias, self.directory))

    def get_remote_path(self, filename=None):
        if filename == None:
            if self.directory != "":
                return "%s:%s" % (self.alias, self.directory)
            else:
                return "%s:" % self.alias

        if self.directory != "":
            return "%s:%s/%s" % (self.alias, self.directory, filename)
        else:
            return "%s:%s" % (self.alias, filename)

    def run(self, *args):
        cmd = " ".join(args)
        log.Debug("tahoe execute: %s" % cmd)
        (status, output) = getstatusoutput(cmd)

        if status != 0:
            raise BackendException("Error running %s" % cmd)
        else:
            return output

    def put(self, source_path, remote_filename=None):
        self.run("tahoe", "cp", source_path.name, self.get_remote_path(remote_filename))

    def get(self, remote_filename, local_path):
        self.run("tahoe", "cp", self.get_remote_path(remote_filename), local_path.name)
        local_path.setdata()

    def _list(self):
        log.Debug("tahoe: List")
        return self.run("tahoe", "ls", self.get_remote_path()).split('\n')

    def delete(self, filename_list):
        log.Debug("tahoe: delete(%s)" % filename_list)
        for filename in filename_list:
            self.run("tahoe", "rm", self.get_remote_path(filename))

duplicity.backend.register_backend("tahoe", TAHOEBackend)

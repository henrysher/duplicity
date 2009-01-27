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
import types

import duplicity.backend
import duplicity.log as log
import duplicity.path as path
from duplicity.errors import *

class LocalBackend(duplicity.backend.Backend):
    """Use this backend when saving to local disk
    
    Urls look like file://testfiles/output.  Relative to root can be
    gotten with extra slash (file:///usr/local).
    
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        # The URL form "file:MyFile" is not a valid duplicity target.
        if not parsed_url.path.startswith( '//' ):
            raise BackendException( "Bad file:// path syntax." )
        self.remote_pathdir = path.Path(parsed_url.path[2:])

    def put(self, source_path, remote_filename = None, rename = None):
        """If rename is set, try that first, copying if doesn't work"""
        if not remote_filename: remote_filename = source_path.get_filename()
        target_path = self.remote_pathdir.append(remote_filename)
        log.Log("Writing %s" % target_path.name, 6)
        if rename:
            try:
                source_path.rename(target_path)
            except OSError:
                pass
            else:
                return
        target_path.writefileobj(source_path.open("rb"))

    def get(self, filename, local_path):
        """Get file and put in local_path (Path object)"""
        source_path = self.remote_pathdir.append(filename)
        local_path.writefileobj(source_path.open("rb"))

    def list(self):
        """List files in that directory"""
        try:
                os.makedirs(self.remote_pathdir.base)
        except:
                pass
        return self.remote_pathdir.listdir()

    def delete(self, filename_list):
        """Delete all files in filename list"""
        assert type(filename_list) is not types.StringType
        try:
                for filename in filename_list:
                        self.remote_pathdir.append(filename).delete()
        except OSError, e:
            raise BackendException(str(e))


duplicity.backend.register_backend("file", LocalBackend)

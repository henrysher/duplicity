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
import errno

import duplicity.backend
from duplicity import log
from duplicity import path
from duplicity import util
from duplicity.errors import * #@UnusedWildImport


class LocalBackend(duplicity.backend.Backend):
    """Use this backend when saving to local disk

    Urls look like file://testfiles/output.  Relative to root can be
    gotten with extra slash (file:///usr/local).

    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        # The URL form "file:MyFile" is not a valid duplicity target.
        if not parsed_url.path.startswith('//'):
            raise BackendException("Bad file:// path syntax.")
        self.remote_pathdir = path.Path(parsed_url.path[2:])

    def handle_error(self, e, op, file1 = None, file2 = None):
        code = log.ErrorCode.backend_error
        if hasattr(e, 'errno'):
            if e.errno == errno.EACCES:
                code = log.ErrorCode.backend_permission_denied
            elif e.errno == errno.ENOENT:
                code = log.ErrorCode.backend_not_found
            elif e.errno == errno.ENOSPC:
                code = log.ErrorCode.backend_no_space
        extra = ' '.join([util.escape(x) for x in [file1, file2] if x])
        extra = ' '.join([op, extra])
        if op != 'delete' and op != 'query':
            log.FatalError(str(e), code, extra)
        else:
            log.Warn(str(e), code, extra)

    def move(self, source_path, remote_filename = None):
        self.put(source_path, remote_filename, rename_instead = True)

    def put(self, source_path, remote_filename = None, rename_instead = False):
        if not remote_filename:
            remote_filename = source_path.get_filename()
        target_path = self.remote_pathdir.append(remote_filename)
        log.Info("Writing %s" % target_path.name)
        """Try renaming first (if allowed to), copying if doesn't work"""
        if rename_instead:
            try:
                source_path.rename(target_path)
            except OSError:
                pass
            except Exception, e:
                self.handle_error(e, 'put', source_path.name, target_path.name)
            else:
                return
        try:
            target_path.writefileobj(source_path.open("rb"))
        except Exception, e:
            self.handle_error(e, 'put', source_path.name, target_path.name)

        """If we get here, renaming failed previously"""
        if rename_instead:
            """We need to simulate its behaviour"""
            source_path.delete()

    def get(self, filename, local_path):
        """Get file and put in local_path (Path object)"""
        source_path = self.remote_pathdir.append(filename)
        try:
            local_path.writefileobj(source_path.open("rb"))
        except Exception, e:
            self.handle_error(e, 'get', source_path.name, local_path.name)

    def _list(self):
        """List files in that directory"""
        try:
                os.makedirs(self.remote_pathdir.base)
        except Exception:
                pass
        try:
            return self.remote_pathdir.listdir()
        except Exception, e:
            self.handle_error(e, 'list', self.remote_pathdir.name)

    def delete(self, filename_list):
        """Delete all files in filename list"""
        assert type(filename_list) is not types.StringType
        for filename in filename_list:
            try:
                self.remote_pathdir.append(filename).delete()
            except Exception, e:
                self.handle_error(e, 'delete', self.remote_pathdir.append(filename).name)

    def _query_file_info(self, filename):
        """Query attributes on filename"""
        try:
            target_file = self.remote_pathdir.append(filename)
            if not os.path.exists(target_file.name):
                return {'size': -1}
            target_file.setdata()
            size = target_file.getsize()
            return {'size': size}
        except Exception, e:
            self.handle_error(e, 'query', target_file.name)
            return {'size': None}

duplicity.backend.register_backend("file", LocalBackend)

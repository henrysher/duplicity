# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2009 Michael Terry <mike@mterry.name>
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
import subprocess
import atexit
import signal
import gio
import glib

import duplicity.backend
from duplicity import log
from duplicity import globals
from duplicity.errors import *
from duplicity.util import exception_traceback 

def ensure_dbus():
    # GIO requires a dbus session bus which can start the gvfs daemons
    # when required.  So we make sure that such a bus exists and that our
    # environment points to it.
    if 'DBUS_SESSION_BUS_ADDRESS' not in os.environ:
        output = subprocess.Popen(['dbus-launch'], stdout=subprocess.PIPE).communicate()[0]
        lines = output.split('\n')
        for line in lines:
            parts = line.split('=', 1)
            if len(parts) == 2:
                if parts[0] == 'DBUS_SESSION_BUS_PID': # cleanup at end
                    atexit.register(os.kill, int(parts[1]), signal.SIGTERM)
                os.environ[parts[0]] = parts[1]

class DupMountOperation(gio.MountOperation):
    """A simple MountOperation that grabs the password from the environment
       or the user.
    """
    def __init__(self, backend):
        gio.MountOperation.__init__(self)
        self.backend = backend
        self.connect('ask-password', self.ask_password)

    def ask_password(self, *args, **kwargs):
        self.set_password(self.backend.get_password())
        self.reply(gio.MOUNT_OPERATION_HANDLED)

class GIOBackend(duplicity.backend.Backend):
    """Use this backend when saving to a GIO URL.
       This is a bit of a meta-backend, in that it can handle multiple schemas.
       URLs look like schema://user@server/path.
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        ensure_dbus()

        self.remote_file = gio.File(uri=parsed_url.url_string)

        # Now we make sure the location is mounted
        op = DupMountOperation(self)
        loop = glib.MainLoop()
        self.remote_file.mount_enclosing_volume(op, self.done_with_mount,
                                                0, user_data=loop)
        loop.run() # halt program until we're done mounting

    def done_with_mount(self, fileobj, result, loop):
        try:
            fileobj.mount_enclosing_volume_finish(result)
        except gio.Error, e:
            # check for NOT_SUPPORTED because some schemas (e.g. file://) validly don't
            if e.code != gio.ERROR_ALREADY_MOUNTED and e.code != gio.ERROR_NOT_SUPPORTED:
                log.FatalError(_("Connection failed, please check your password: %s")
                               % str(e), log.ErrorCode.connection_failed)
        loop.quit()

    def copy_progress(self, *args, **kwargs):
        pass

    def copy_file(self, source, target):
        for n in range(1, globals.num_retries+1):
            log.Info(_("Writing %s") % target.get_parse_name())
            try:
                source.copy(target, self.copy_progress,
                            gio.FILE_COPY_OVERWRITE | gio.FILE_COPY_NOFOLLOW_SYMLINKS)
                return
            except Exception, e:
                log.Warn("Write of '%s' failed (attempt %s): %s: %s"
                        % (target.get_parse_name(), n, e.__class__.__name__, str(e)))
                log.Debug("Backtrace of previous error: %s"
                          % exception_traceback())
        raise BackendException(_("Could not copy %s to %s") % (source.get_parse_name(),
                                                               target.get_parse_name()))

    def put(self, source_path, remote_filename = None):
        """Copy file to remote"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        source_file = gio.File(path=source_path.name)
        target_file = self.remote_file.get_child_for_display_name(remote_filename)
        self.copy_file(source_file, target_file)

    def get(self, filename, local_path):
        """Get file and put in local_path (Path object)"""
        source_file = self.remote_file.get_child_for_display_name(filename)
        target_file = gio.File(path=local_path.name)
        self.copy_file(source_file, target_file)
        local_path.setdata()

    def list(self):
        """List files in that directory"""
        enum = self.remote_file.enumerate_children(gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME,
                                                   gio.FILE_QUERY_INFO_NOFOLLOW_SYMLINKS)
        files = []
        try:
            info = enum.next_file()
            while info:
                files.append(info.get_display_name())
                info = enum.next_file()
            return files
        except Exception, e:
            raise BackendException(str(e))

    def delete(self, filename_list):
        """Delete all files in filename list"""
        assert type(filename_list) is not types.StringType
        try:
                for filename in filename_list:
                        self.remote_file.get_child_for_display_name(filename).delete()
        except Exception, e:
            raise BackendException(str(e))

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
from gi.repository import Gio #@UnresolvedImport
from gi.repository import GLib #@UnresolvedImport

import duplicity.backend
from duplicity.backend import retry
from duplicity import log
from duplicity import util
from duplicity.errors import * #@UnusedWildImport

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

class DupMountOperation(Gio.MountOperation):
    """A simple MountOperation that grabs the password from the environment
       or the user.
    """
    def __init__(self, backend):
        Gio.MountOperation.__init__(self)
        self.backend = backend
        self.connect('ask-password', self.ask_password_cb)
        self.connect('ask-question', self.ask_question_cb)

    def ask_password_cb(self, *args, **kwargs):
        self.set_password(self.backend.get_password())
        self.reply(Gio.MountOperationResult.HANDLED)

    def ask_question_cb(self, *args, **kwargs):
        # Obviously just always answering with the first choice is a naive
        # approach.  But there's no easy way to allow for answering questions
        # in duplicity's typical run-from-cron mode with environment variables.
        # And only a couple gvfs backends ask questions: 'sftp' does about
        # new hosts and 'afc' does if the device is locked.  0 should be a
        # safe choice.
        self.set_choice(0)
        self.reply(Gio.MountOperationResult.HANDLED)

class GIOBackend(duplicity.backend.Backend):
    """Use this backend when saving to a GIO URL.
       This is a bit of a meta-backend, in that it can handle multiple schemas.
       URLs look like schema://user@server/path.
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        ensure_dbus()

        self.remote_file = Gio.File.new_for_uri(parsed_url.url_string)

        # Now we make sure the location is mounted
        op = DupMountOperation(self)
        loop = GLib.MainLoop()
        self.remote_file.mount_enclosing_volume(Gio.MountMountFlags.NONE,
                                                op, None, self.done_with_mount,
                                                loop)
        loop.run() # halt program until we're done mounting

        # Now make the directory if it doesn't exist
        try:
            self.remote_file.make_directory_with_parents(None)
        except GLib.GError, e:
            if e.code != Gio.IOErrorEnum.EXISTS:
                raise

    def done_with_mount(self, fileobj, result, loop):
        try:
            fileobj.mount_enclosing_volume_finish(result)
        except GLib.GError, e:
            # check for NOT_SUPPORTED because some schemas (e.g. file://) validly don't
            if e.code != Gio.IOErrorEnum.ALREADY_MOUNTED and e.code != Gio.IOErrorEnum.NOT_SUPPORTED:
                log.FatalError(_("Connection failed, please check your password: %s")
                               % str(e), log.ErrorCode.connection_failed)
        loop.quit()

    def handle_error(self, raise_error, e, op, file1=None, file2=None):
        if raise_error:
            raise e
        code = log.ErrorCode.backend_error
        if isinstance(e, GLib.GError):
            if e.code == Gio.IOErrorEnum.PERMISSION_DENIED:
                code = log.ErrorCode.backend_permission_denied
            elif e.code == Gio.IOErrorEnum.NOT_FOUND:
                code = log.ErrorCode.backend_not_found
            elif e.code == Gio.IOErrorEnum.NO_SPACE:
                code = log.ErrorCode.backend_no_space
        extra = ' '.join([util.escape(x) for x in [file1, file2] if x])
        extra = ' '.join([op, extra])
        log.FatalError(str(e), code, extra)

    def copy_progress(self, *args, **kwargs):
        pass

    @retry
    def copy_file(self, op, source, target, raise_errors=False):
        log.Info(_("Writing %s") % target.get_parse_name())
        try:
            source.copy(target,
                        Gio.FileCopyFlags.OVERWRITE | Gio.FileCopyFlags.NOFOLLOW_SYMLINKS,
                        None, self.copy_progress, None)
        except Exception, e:
            self.handle_error(raise_errors, e, op, source.get_parse_name(),
                              target.get_parse_name())

    def put(self, source_path, remote_filename = None):
        """Copy file to remote"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        source_file = Gio.File.new_for_path(source_path.name)
        target_file = self.remote_file.get_child(remote_filename)
        self.copy_file('put', source_file, target_file)

    def get(self, filename, local_path):
        """Get file and put in local_path (Path object)"""
        source_file = self.remote_file.get_child(filename)
        target_file = Gio.File.new_for_path(local_path.name)
        self.copy_file('get', source_file, target_file)
        local_path.setdata()

    @retry
    def list(self, raise_errors=False):
        """List files in that directory"""
        files = []
        try:
            enum = self.remote_file.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_NAME,
                                                       Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS,
                                                       None)
            info = enum.next_file(None)
            while info:
                files.append(info.get_name())
                info = enum.next_file(None)
        except Exception, e:
            self.handle_error(raise_errors, e, 'list',
                              self.remote_file.get_parse_name())
        return files

    @retry
    def delete(self, filename_list, raise_errors=False):
        """Delete all files in filename list"""
        assert type(filename_list) is not types.StringType
        for filename in filename_list:
            target_file = self.remote_file.get_child(filename)
            try:
                target_file.delete(None)
            except Exception, e:
                if isinstance(e, GLib.GError):
                    if e.code == Gio.IOErrorEnum.NOT_FOUND:
                        continue
                self.handle_error(raise_errors, e, 'delete',
                                  target_file.get_parse_name())
                return

    @retry
    def _query_file_info(self, filename, raise_errors=False):
        """Query attributes on filename"""
        target_file = self.remote_file.get_child(filename)
        attrs = Gio.FILE_ATTRIBUTE_STANDARD_SIZE
        try:
            info = target_file.query_info(attrs, Gio.FileQueryInfoFlags.NONE,
                                          None)
            return {'size': info.get_size()}
        except Exception, e:
            if isinstance(e, GLib.GError):
                if e.code == Gio.IOErrorEnum.NOT_FOUND:
                    return {'size': -1} # early exit, no need to retry
            if raise_errors:
                raise e
            else:
                return {'size': None}

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
import subprocess
import atexit
import signal

import duplicity.backend
from duplicity import log
from duplicity import util


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
                if parts[0] == 'DBUS_SESSION_BUS_PID':  # cleanup at end
                    atexit.register(os.kill, int(parts[1]), signal.SIGTERM)
                os.environ[parts[0]] = parts[1]


class GIOBackend(duplicity.backend.Backend):
    """Use this backend when saving to a GIO URL.
       This is a bit of a meta-backend, in that it can handle multiple schemas.
       URLs look like schema://user@server/path.
    """
    def __init__(self, parsed_url):
        from gi.repository import Gio  # @UnresolvedImport
        from gi.repository import GLib  # @UnresolvedImport

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

        duplicity.backend.Backend.__init__(self, parsed_url)

        ensure_dbus()

        self.remote_file = Gio.File.new_for_uri(parsed_url.url_string)

        # Now we make sure the location is mounted
        op = DupMountOperation(self)
        loop = GLib.MainLoop()
        self.remote_file.mount_enclosing_volume(Gio.MountMountFlags.NONE,
                                                op, None,
                                                self.__done_with_mount, loop)
        loop.run()  # halt program until we're done mounting

        # Now make the directory if it doesn't exist
        try:
            self.remote_file.make_directory_with_parents(None)
        except GLib.GError as e:
            if e.code != Gio.IOErrorEnum.EXISTS:
                raise

    def __done_with_mount(self, fileobj, result, loop):
        from gi.repository import Gio  # @UnresolvedImport
        from gi.repository import GLib  # @UnresolvedImport
        try:
            fileobj.mount_enclosing_volume_finish(result)
        except GLib.GError as e:
            # check for NOT_SUPPORTED because some schemas (e.g. file://) validly don't
            if e.code != Gio.IOErrorEnum.ALREADY_MOUNTED and e.code != Gio.IOErrorEnum.NOT_SUPPORTED:
                log.FatalError(_("Connection failed, please check your password: %s")
                               % util.uexc(e), log.ErrorCode.connection_failed)
        loop.quit()

    def __copy_progress(self, *args, **kwargs):
        pass

    def __copy_file(self, source, target):
        from gi.repository import Gio  # @UnresolvedImport
        source.copy(target,
                    Gio.FileCopyFlags.OVERWRITE | Gio.FileCopyFlags.NOFOLLOW_SYMLINKS,
                    None, self.__copy_progress, None)

    def _error_code(self, operation, e):
        from gi.repository import Gio  # @UnresolvedImport
        from gi.repository import GLib  # @UnresolvedImport
        if isinstance(e, GLib.GError):
            if e.code == Gio.IOErrorEnum.FAILED and operation == 'delete':
                # Sometimes delete will return a generic failure on a file not
                # found (notably the FTP does that)
                return log.ErrorCode.backend_not_found
            elif e.code == Gio.IOErrorEnum.PERMISSION_DENIED:
                return log.ErrorCode.backend_permission_denied
            elif e.code == Gio.IOErrorEnum.NOT_FOUND:
                return log.ErrorCode.backend_not_found
            elif e.code == Gio.IOErrorEnum.NO_SPACE:
                return log.ErrorCode.backend_no_space

    def _put(self, source_path, remote_filename):
        from gi.repository import Gio  # @UnresolvedImport
        source_file = Gio.File.new_for_path(source_path.name)
        target_file = self.remote_file.get_child(remote_filename)
        self.__copy_file(source_file, target_file)

    def _get(self, filename, local_path):
        from gi.repository import Gio  # @UnresolvedImport
        source_file = self.remote_file.get_child(filename)
        target_file = Gio.File.new_for_path(local_path.name)
        self.__copy_file(source_file, target_file)

    def _list(self):
        from gi.repository import Gio  # @UnresolvedImport
        files = []
        enum = self.remote_file.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_NAME,
                                                   Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS,
                                                   None)
        info = enum.next_file(None)
        while info:
            files.append(info.get_name())
            info = enum.next_file(None)
        return files

    def _delete(self, filename):
        target_file = self.remote_file.get_child(filename)
        target_file.delete(None)

    def _query(self, filename):
        from gi.repository import Gio  # @UnresolvedImport
        target_file = self.remote_file.get_child(filename)
        info = target_file.query_info(Gio.FILE_ATTRIBUTE_STANDARD_SIZE,
                                      Gio.FileQueryInfoFlags.NONE, None)
        return {'size': info.get_size()}

duplicity.backend.register_backend_prefix('gio', GIOBackend)

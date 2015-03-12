# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2011 Carlos Abalde <carlos.abalde@gmail.com>
# for gdocsbackend.py on which megabackend.py is based on
#
# Copyright 2013 Christian Kornacker <christian.kornacker@gmail.com>
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

import duplicity.backend
from duplicity import log
from duplicity.errors import BackendException


class MegaBackend(duplicity.backend.Backend):
    """Connect to remote store using Mega.co.nz API"""

    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        try:
            from mega import Mega
        except ImportError:
            raise BackendException('Mega.co.nz backend requires Mega.co.nz APIs Python Module'
                                   '(see https://github.com/richardasaurus/mega.py).')

        # Setup client instance.
        self.client = Mega()
        self.client.domain = parsed_url.hostname
        self.__authorize(parsed_url.username, self.get_password())

        # Fetch destination folder entry (and crete hierarchy if required).
        folder_names = parsed_url.path[1:].split('/')
        files = self.client.get_files()

        parent_folder = self.client.root_id
        for folder_name in folder_names:
            entries = self.__filter_entries(files, parent_folder, folder_name, 'folder')
            if len(entries):
                # use first matching folder as new parent
                parent_folder = entries.keys()[0]
            else:
                # create subfolder if folder doesn't exist and use its handle as parent
                folder_node = self.client.create_folder(folder_name, parent_folder)
                parent_folder = self.client.get_id_from_obj(folder_node)
                # update filelist after creating new folder
                files = self.client.get_files()

        self.folder = parent_folder

    def _put(self, source_path, remote_filename):
        try:
            self._delete(remote_filename)
        except Exception:
            pass
        self.client.upload(source_path.get_canonical(), self.folder, dest_filename=remote_filename)

    def _get(self, remote_filename, local_path):
        files = self.client.get_files()
        entries = self.__filter_entries(files, self.folder, remote_filename, 'file')
        if len(entries):
            # get first matching remote file
            entry = entries.keys()[0]
            self.client.download((entry, entries[entry]), dest_filename=local_path.name)
        else:
            raise BackendException("Failed to find file '%s' in remote folder '%s'"
                                   % (remote_filename, self.__get_node_name(self.folder)),
                                   code=log.ErrorCode.backend_not_found)

    def _list(self):
        entries = self.client.get_files_in_node(self.folder)
        return [self.client.get_name_from_file({entry: entries[entry]}) for entry in entries]

    def _delete(self, filename):
        files = self.client.get_files()
        entries = self.__filter_entries(files, self.folder, filename, 'file')
        if len(entries):
            self.client.destroy(entries.keys()[0])
        else:
            raise BackendException("Failed to find file '%s' in remote folder '%s'"
                                   % (filename, self.__get_node_name(self.folder)),
                                   code=log.ErrorCode.backend_not_found)

    def __get_node_name(self, handle):
        """get node name from public handle"""
        files = self.client.get_files()
        return self.client.get_name_from_file({handle: files[handle]})

    def __authorize(self, email, password):
        self.client.login(email, password)

    def __filter_entries(self, entries, parent_id=None, title=None, type=None):
        result = {}
        type_map = {'folder': 1, 'file': 0}

        for k, v in entries.items():
            try:
                if parent_id is not None:
                    assert(v['p'] == parent_id)
                if title is not None:
                    assert(v['a']['n'] == title)
                if type is not None:
                    assert(v['t'] == type_map[type])
            except AssertionError:
                continue

            result.update({k: v})

        return result

duplicity.backend.register_backend('mega', MegaBackend)
duplicity.backend.uses_netloc.extend(['mega'])

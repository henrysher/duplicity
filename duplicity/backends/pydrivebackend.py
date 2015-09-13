# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2015 Yigal Asnis
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# It is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import string
import os

import duplicity.backend
from duplicity.errors import BackendException


class PyDriveBackend(duplicity.backend.Backend):
    """Connect to remote store using PyDrive API"""

    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        try:
            global pydrive
            import httplib2
            from apiclient.discovery import build
            from oauth2client.client import SignedJwtAssertionCredentials
            from pydrive.auth import GoogleAuth
            from pydrive.drive import GoogleDrive
        except ImportError:
            raise BackendException('PyDrive backend requires PyDrive installation'
                                   'Please read the manpage to fix.')

        if 'GOOGLE_DRIVE_ACCOUNT_KEY' in os.environ:
            account_key = os.environ['GOOGLE_DRIVE_ACCOUNT_KEY']
            credentials = SignedJwtAssertionCredentials(parsed_url.username + '@' + parsed_url.hostname, account_key, scope='https://www.googleapis.com/auth/drive')
            credentials.authorize(httplib2.Http())
            gauth = GoogleAuth()
            gauth.credentials = credentials
        elif 'GOOGLE_DRIVE_SETTINGS' in os.environ:
            gauth = GoogleAuth(settings_file=os.environ['GOOGLE_DRIVE_SETTINGS'])
            gauth.CommandLineAuth()
        else:
            raise BackendException('GOOGLE_DRIVE_ACCOUNT_KEY or GOOGLE_DRIVE_SETTINGS environment variable not set. Please read the manpage to fix.')
        self.drive = GoogleDrive(gauth)

        # Dirty way to find root folder id
        file_list = self.drive.ListFile({'q': "'Root' in parents and trashed=false"}).GetList()
        if file_list:
            parent_folder_id = file_list[0]['parents'][0]['id']
        else:
            file_in_root = self.drive.CreateFile({'title': 'i_am_in_root'})
            file_in_root.Upload()
            parent_folder_id = file_in_root['parents'][0]['id']

        # Fetch destination folder entry and create hierarchy if required.
        folder_names = string.split(parsed_url.path, '/')
        for folder_name in folder_names:
            if not folder_name:
                continue
            file_list = self.drive.ListFile({'q': "'" + parent_folder_id + "' in parents and trashed=false"}).GetList()
            folder = next((item for item in file_list if item['title'] == folder_name and item['mimeType'] == 'application/vnd.google-apps.folder'), None)
            if folder is None:
                folder = self.drive.CreateFile({'title': folder_name, 'mimeType': "application/vnd.google-apps.folder", 'parents': [{'id': parent_folder_id}]})
                folder.Upload()
            parent_folder_id = folder['id']
        self.folder = parent_folder_id
        self.id_cache = {}

    def file_by_name(self, filename):
        from pydrive.files import ApiRequestError
        if filename in self.id_cache:
            # It might since have been locally moved, renamed or deleted, so we
            # need to validate the entry.
            file_id = self.id_cache[filename]
            drive_file = self.drive.CreateFile({'id': file_id})
            try:
                if drive_file['title'] == filename and not drive_file['labels']['trashed']:
                    for parent in drive_file['parents']:
                        if parent['id'] == self.folder:
                            log.Info("PyDrive backend: found file '%s' with id %s in ID cache" % (filename, file_id))
                            return drive_file
            except ApiRequestError as error:
                # A 404 occurs if the ID is no longer valid
                if error.args[0].resp.status != 404:
                    raise
            # If we get here, the cache entry is invalid
            log.Info("PyDrive backend: invalidating '%s' (previously ID %s) from ID cache" % (filename, file_id))
            del self.id_cache[filename]

        # Not found in the cache, so use directory listing. This is less
        # reliable because there is no strong consistency.
        q = "title='%s' and '%s' in parents and trashed=false" % (filename, self.folder)
        fields = 'items(title,id,fileSize,downloadUrl,exportLinks),nextPageToken'
        flist = self.drive.ListFile({'q': q, 'fields': fields}).GetList()
        if len(flist) > 1:
            log.FatalError(_("PyDrive backend: multiple files called '%s'.") % (filename,))
        elif flist:
            file_id = flist[0]['id']
            self.id_cache[filename] = flist[0]['id']
            log.Info("PyDrive backend: found file '%s' with id %s on server, adding to cache" % (filename, file_id))
            return flist[0]
        log.Info("PyDrive backend: file '%s' not found in cache or on server" % (filename,))
        return None

    def id_by_name(self, filename):
        try:
            return next(item for item in self.FilesList() if item['title'] == filename)['id']
        except:
            return ''

    def _put(self, source_path, remote_filename):
        drive_file = self.file_by_name(remote_filename)
        if drive_file is None:
            # No existing file, make a new one
            drive_file = self.drive.CreateFile({'title': remote_filename, 'parents': [{"kind": "drive#fileLink", "id": self.folder}]})
            log.Info("PyDrive backend: creating new file '%s'" % (remote_filename,))
        else:
            log.Info("PyDrive backend: replacing existing file '%s' with id '%s'" % (
                remote_filename, drive_file['id']))
        drive_file.SetContentFile(source_path.name)
        drive_file.Upload()

    def _get(self, remote_filename, local_path):
        drive_file = self.drive.CreateFile({'id': self.id_by_name(remote_filename)})
        drive_file.GetContentFile(local_path.name)

    def _list(self):
        return [item['title'] for item in self.FilesList()]

    def _delete(self, filename):
        file_id = self.id_by_name(filename)
        drive_file = self.drive.CreateFile({'id': file_id})
        drive_file.auth.service.files().delete(fileId=drive_file['id']).execute()

    def _query(self, filename):
        try:
            size = int((item for item in self.FilesList() if item['title'] == filename).next()['fileSize'])
        except:
            size = -1
        return {'size': size}

duplicity.backend.register_backend('pydrive', PyDriveBackend)
""" pydrive is an alternate way to access gdocs """
duplicity.backend.register_backend('pydrive+gdocs', PyDriveBackend)
""" register pydrive as the default way to access gdocs """
duplicity.backend.register_backend('gdocs', PyDriveBackend)

duplicity.backend.uses_netloc.extend(['pydrive', 'pydrive+gdocs', 'gdocs'])

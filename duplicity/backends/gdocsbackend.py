# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2011 Carlos Abalde <carlos.abalde@gmail.com>
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

import os.path
import string
import urllib;

import duplicity.backend
from duplicity import log
from duplicity import globals
from duplicity.errors import * #@UnusedWildImport

class GDocsBackend(duplicity.backend.Backend):
    """Connect to remote store using Google Google Documents List API"""

    ROOT_FOLDER_ID = 'folder%3Aroot'
    BACKUP_DOCUMENT_TYPE = 'application/binary'

    def __init__(self, parsed_url):
      duplicity.backend.Backend.__init__(self, parsed_url)

      # Import Google Data APIs libraries.
      try:
        global atom
        global gdata
        import atom.data
        import gdata.client
        import gdata.docs.client
        import gdata.docs.data
      except ImportError:
        raise BackendException('Google Docs backend requires Google Data APIs Python '
                               'Client Library (see http://code.google.com/p/gdata-python-client/).')

      # Setup client instance.
      self.client = gdata.docs.client.DocsClient(source = 'duplicity $version')
      self.client.ssl = True
      self.client.http_client.debug = False
      self.__authorize(parsed_url.username + '@' + parsed_url.hostname, parsed_url.password)

      # Fetch destination folder entry (and crete hierarchy if required).
      folder_names = string.split(parsed_url.path[1:], '/')
      parent_folder = None
      parent_folder_id = GDocsBackend.ROOT_FOLDER_ID
      for folder_name in folder_names:
        entries = self.__fetch_entries(parent_folder_id, 'folder', folder_name)
        if entries is not None:
          if len(entries) == 1:
            parent_folder = entries[0]
          elif len(entries) == 0:
            parent_folder = self.client.create(gdata.docs.data.FOLDER_LABEL, folder_name, parent_folder)
          else:
            parent_folder = None
          if parent_folder:
            parent_folder_id = parent_folder.resource_id.text
          else:
            raise BackendException("Error while creating destination folder '%s'." % folder_name)
        else:
          raise BackendException("Error while fetching destination folder '%s'." % folder_name)
      self.folder = parent_folder

    def put(self, source_path, remote_filename = None):
      """Transfer source_path to remote_filename"""
      # Default remote file name.
      if not remote_filename:
        remote_filename = source_path.get_filename()

      # Upload!
      for n in range(0, globals.num_retries):
        # If remote file already exists in destination folder, remove it.
        entries = self.__fetch_entries(self.folder.resource_id.text, GDocsBackend.BACKUP_DOCUMENT_TYPE, remote_filename)
        for entry in entries:
          self.client.delete(entry.get_edit_link().href + '?delete=true', force = True)

        # Set uploader instance. Note that resumable uploads are required in order to
        # enable uploads for all file types.
        # (see http://googleappsdeveloper.blogspot.com/2011/05/upload-all-file-types-to-any-google.html)
        file = source_path.open()
        uploader = gdata.client.ResumableUploader(
          self.client, file, GDocsBackend.BACKUP_DOCUMENT_TYPE, os.path.getsize(file.name),
          chunk_size = gdata.client.ResumableUploader.DEFAULT_CHUNK_SIZE,
          desired_class = gdata.docs.data.DocsEntry)
        if uploader:
          # Chunked upload.
          entry = gdata.docs.data.DocsEntry(title = atom.data.Title(text = remote_filename))
          uri = '/feeds/upload/create-session/default/private/full?convert=false'
          entry = uploader.UploadFile(uri, entry = entry)
          if entry:
            # Move to destination folder.
            # TODO: any ideas on how to avoid this step?
            if self.client.Move(entry, self.folder):
              assert not file.close()
              return
            else:
              log.Warn("[%d/%d] Failed to move uploaded file '%s' to destination remote folder '%s'"
                       % (n + 1, globals.num_retries, source_path.get_filename(), self.folder.title.text))
          else:
            log.Warn("[%d/%d] Failed to upload file '%s' to remote folder '%s'" 
                     % (n + 1, globals.num_retries, source_path.get_filename(), self.folder.title.text))
        else:
          log.Warn("[%d/%d] Failed to initialize upload of file '%s' to remote folder '%s'"
                   % (n + 1, globals.num_retries, source_path.get_filename(), self.folder.title.text))
        assert not file.close()

      ## Error!
      raise BackendException("Error uploading file '%s' to remote folder '%s'"
                             % (source_path.get_filename(), self.folder.title.text))

    def get(self, remote_filename, local_path):
      """Get remote filename, saving it to local_path"""
      for n in range(0, globals.num_retries):
        entries = self.__fetch_entries(self.folder.resource_id.text, GDocsBackend.BACKUP_DOCUMENT_TYPE, remote_filename)
        if len(entries) == 1:
          entry = entries[0]
          try:
            self.client.Download(entry, local_path.name)
            local_path.setdata()
            return
          except gdata.client.RequestError:
            log.Warn("[%d/%d] Failed to download file '%s' in remote folder '%s'"
                     % (n + 1, globals.num_retries, remote_filename, self.folder.title.text))
        else:
          log.Warn("[%d/%d] Failed to find file '%s' in remote folder '%s'"
                  % (n + 1, globals.num_retries, remote_filename, self.folder.title.text))
      raise BackendException("Failed to download file '%s' in remote folder '%s'"
                             % (remote_filename, self.folder.title.text))

    def list(self):
      """List files in folder"""
      for n in range(0, globals.num_retries):
        try:
          entries = self.__fetch_entries(self.folder.resource_id.text, GDocsBackend.BACKUP_DOCUMENT_TYPE)
          return [entry.title.text for entry in entries]
        except Exception:
          log.Warn("[%d/%d] Failed to fetch list of files in remote folder '%s'"
                   % (n + 1, globals.num_retries, self.folder.title.text))
      raise BackendException("Error listing files in remote folder '%s'"
                             % (self.folder.title.text))

    def delete(self, filename_list):
      """Delete files in filename_list"""
      for filename in filename_list:
        for n in range(0, globals.num_retries):
          entries = self.__fetch_entries(self.folder.resource_id.text, GDocsBackend.BACKUP_DOCUMENT_TYPE, filename)
          if len(entries) > 0:
            success = True
            for entry in entries:
              if not self.client.delete(entry.get_edit_link().href + '?delete=true', force = True):
                success = False
            if success:
              break
            else:
              log.Warn("[%d/%d] Failed to remove file '%s' in remote folder '%s'"
                       % (n + 1, globals.num_retries, filename, self.folder.title.text))
          else:
            log.Warn("Failed to fetch & remove file '%s' in remote folder '%s'"
                     % (filename, self.folder.title.text))
            break
          if n == globals.num_retries:
            raise BackendException("Error removing file '%s' in remote folder '%s'"
                                   % (filename, self.folder.title.text))

    def __authorize(self, email, password, captcha_token = None, captcha_response = None):
      try:
        self.client.client_login(email, password,
                                 source = 'duplicity',
                                 service = 'writely',
                                 captcha_token = captcha_token,
                                 captcha_response = captcha_response)
      except gdata.client.CaptchaChallenge, challenge:
        print('A captcha challenge in required. Please visit ' + challenge.captcha_url)
        answer = None
        while not answer:
          answer = raw_input('Answer to the challenge? ')
        self.__authorize(email, password, challenge.captcha_token, answer)
      except gdata.client.BadAuthentication:
        raise BackendException('Invalid user credentials given. Be aware that accounts '
                               'that use 2-step verification require creating an application specific '
                               'access code for using this Duplicity backend. Follow the instrucction in '
                               'http://www.google.com/support/accounts/bin/static.py?page=guide.cs&guide=1056283&topic=1056286 '
                               'and create your application-specific password to run duplicity backups.')
      except Exception, e:
        raise BackendException('Error while authenticating client: %s.' % str(e))

    def __fetch_entries(self, folder_id, type, title = None):
      # Build URI.
      uri = '/feeds/default/private/full/%s/contents' % folder_id
      if type == 'folder':
        uri += '/-/folder?showfolders=true'
      elif type == GDocsBackend.BACKUP_DOCUMENT_TYPE:
        uri += '?showfolders=false'
      else:
        uri += '?showfolders=true'
      if title:
        uri += '&title=' + urllib.quote(title) + '&title-exact=true'

      # Fetch entries
      entries = self.client.get_everything(uri = uri)

      # When filtering by entry title, API is returning (don't know why) documents in other
      # folders (apart from folder_id) matching the title, so some extra filtering is required.
      if title:
        result = []
        for entry in entries:
          if (not type) or (entry.get_document_type() == type):
            if folder_id != GDocsBackend.ROOT_FOLDER_ID:
              for link in entry.in_folders():
                folder_entry = self.client.get_entry(link.href, None, None,
                                                     desired_class = gdata.docs.data.DocsEntry)
                if folder_entry and (folder_entry.resource_id.text == folder_id):
                  result.append(entry)
            elif len(entry.in_folders()) == 0:
              result.append(entry)
      else:
        result = entries

      # Done!
      return result

duplicity.backend.register_backend('gdocs', GDocsBackend)

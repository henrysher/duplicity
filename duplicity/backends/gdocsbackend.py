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

import duplicity.backend
from duplicity import log
from duplicity import globals
from duplicity.errors import * #@UnusedWildImport

class GDocsBackend(duplicity.backend.Backend):
    """Connect to remote store using Google Google Documents List API"""

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
      # TODO: handle gdata.client.CaptchaRequired exception.
      try:
        email = parsed_url.username + '@' + parsed_url.hostname
        password = parsed_url.password
        self.client = gdata.docs.client.DocsClient(source = 'duplicity')
        self.client.ssl = True
        self.client.http_client.debug = False
        self.client.client_login(email, password, source = 'duplicity', service = 'writely')
      except gdata.client.BadAuthentication:
        log.FatalError('Google Docs error: Invalid user credentials given.')
      except Exception, e:
        log.FatalError('Google Docs error: %s.' % str(e))

      # Fetch/create folder entry.
      folder_name = parsed_url.path[1:]
      feed = self.client.GetDocList(uri = '/feeds/default/private/full/-/folder?title=' +
                                          folder_name + '&title-exact=true')
      if (len(feed.entry) == 1):
        self.folder = feed.entry[0]
      else:
        self.folder = self.client.Create(gdata.docs.data.FOLDER_LABEL, folder_name)
        if not self.folder:
          log.FatalError('Google Docs error: Invalid folder name.')

    def put(self, source_path, remote_filename = None):
      """Transfer source_path to remote_filename"""
      # Default remote file name.
      if not remote_filename:
        remote_filename = source_path.get_filename()

      # Upload!
      for n in range(0, globals.num_retries):
        # If remote file already exists in destination folder, remove it.
        feed = self.client.GetDocList(uri = self.folder.content.src + '?title=' +
                                      remote_filename + '&title-exact=true')
        if feed:
          for entry in feed.entry:
            self.client.Delete(entry.GetEditLink().href + '?delete=true', force = True)

        # Set uploader instance. Note that resumable uploads are required in order to
        # enable uploads for all file types.
        # (see http://googleappsdeveloper.blogspot.com/2011/05/upload-all-file-types-to-any-google.html)
        file = source_path.open()
        uploader = gdata.client.ResumableUploader(
          self.client, file, 'application/binary', os.path.getsize(file.name),
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
              log.Warn("Failed to move uploaded file '%s' to destination remote folder '%s'"
                       % (source_path.get_filename(), self.folder.title.text))
          else:
            log.Warn("Failed to upload file '%s' to remote folder '%s'" 
                     % (source_path.get_filename(), self.folder.title.text))
        else:
          log.Warn("Failed to initialize upload of file '%s' to remote folder '%s'"
                   % (source_path.get_filename(), self.folder.title.text))
        assert not file.close()

      ## Error!
      raise BackendException("Error uploading file '%s' to remote folder '%s'"
                             % (source_path.get_filename(), self.folder.title.text))

    def get(self, remote_filename, local_path):
      """Get remote filename, saving it to local_path"""
      for n in range(0, globals.num_retries):
        feed = self.client.GetDocList(uri = self.folder.content.src + '?title=' +
                                      remote_filename + '&title-exact=true')
        if feed and (len(feed.entry) == 1):
          entry = feed.entry[0]
          try:
            self.client.Download(entry, local_path.name)
            local_path.setdata()
            return
          except gdata.client.RequestError:
            log.Warn("Failed to download file '%s' in remote folder '%s'"
                     % (remote_filename, self.folder.title.text))
        else:
          log.Warn("Failed to find file '%s' in remote folder '%s'"
                  % (remote_filename, self.folder.title.text))
      raise BackendException("Failed to download file '%s' in remote folder '%s'"
                             % (remote_filename, self.folder.title.text))

    def list(self):
      """List files in folder"""
      for n in range(0, globals.num_retries):
        feed = self.client.GetDocList(uri = self.folder.content.src)
        if feed:
          return [entry.title.text for entry in feed.entry]
        else:
          log.Warn("Failed to fetch list of files in remote folder '%s'"
                   % (self.folder.title.text))
      raise BackendException("Error listing files in remote folder '%s'"
                             % (self.folder.title.text))

    def delete(self, filename_list):
      """Delete files in filename_list"""
      for filename in filename_list:
        for n in range(0, globals.num_retries):
          feed = self.client.GetDocList(uri = self.folder.content.src + '?title=' +
                                              filename + '&title-exact=true')
          if feed and (len(feed.entry) == 1):
            entry = feed.entry[0]
            if self.client.Delete(entry.GetEditLink().href + '?delete=true', force = True):
              break
          else:
            log.Warn("Failed to fetch & remove file '%s' in remote folder '%s'"
                     % (filename, self.folder.title.text))
            break
          if n == globals.num_retries:
            raise BackendException("Error removing file '%s' in remote folder '%s'"
                                   % (filename, self.folder.title.text))

duplicity.backend.register_backend('gdocs', GDocsBackend)

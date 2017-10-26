#
# Copyright (c) 2015 Matthew Bentley
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import hashlib

import duplicity.backend
from duplicity.errors import BackendException, FatalBackendException
from duplicity import log
from duplicity import progress


class B2ProgressListener:
    def set_total_bytes(self, total_byte_count):
        self.total_byte_count = total_byte_count

    def bytes_completed(self, byte_count):
        progress.report_transfer(byte_count, self.total_byte_count)

    def close(self):
        pass


class B2Backend(duplicity.backend.Backend):
    """
    Backend for BackBlaze's B2 storage service
    """

    def __init__(self, parsed_url):
        """
        Authorize to B2 api and set up needed variables
        """
        duplicity.backend.Backend.__init__(self, parsed_url)

        # Import B2 API
        try:
            global b2
            import b2
            import b2.api
            import b2.account_info
            import b2.download_dest
            import b2.file_version
        except ImportError:
            raise BackendException('B2 backend requires B2 Python APIs (pip install b2)')

        self.service = b2.api.B2Api(b2.account_info.InMemoryAccountInfo())
        self.parsed_url.hostname = 'B2'

        account_id = parsed_url.username
        account_key = self.get_password()

        self.url_parts = [
            x for x in parsed_url.path.replace("@", "/").split('/') if x != ''
        ]
        if self.url_parts:
            self.username = self.url_parts.pop(0)
            bucket_name = self.url_parts.pop(0)
        else:
            raise BackendException("B2 requires a bucket name")
        self.path = "".join([url_part + "/" for url_part in self.url_parts])
        self.service.authorize_account('production', account_id, account_key)

        log.Log("B2 Backend (path= %s, bucket= %s, minimum_part_size= %s)" %
                (self.path, bucket_name, self.service.account_info.get_minimum_part_size()), log.INFO)
        try:
            self.bucket = self.service.get_bucket_by_name(bucket_name)
            log.Log("Bucket found", log.INFO)
        except b2.exception.NonExistentBucket:
            try:
                log.Log("Bucket not found, creating one", log.INFO)
                self.bucket = self.service.create_bucket(bucket_name, 'allPrivate')
            except:
                raise FatalBackendException("Bucket cannot be created")

    def _get(self, remote_filename, local_path):
        """
        Download remote_filename to local_path
        """
        log.Log("Get: %s -> %s" % (self.path + remote_filename, local_path.name), log.INFO)
        self.bucket.download_file_by_name(self.path + remote_filename,
                                          b2.download_dest.DownloadDestLocalFile(local_path.name))

    def _put(self, source_path, remote_filename):
        """
        Copy source_path to remote_filename
        """
        log.Log("Put: %s -> %s" % (source_path.name, self.path + remote_filename), log.INFO)
        self.bucket.upload_local_file(source_path.name, self.path + remote_filename,
                                      content_type='application/pgp-encrypted',
                                      progress_listener=B2ProgressListener())

    def _list(self):
        """
        List files on remote server
        """
        return [file_version_info.file_name[len(self.path):]
                for (file_version_info, folder_name) in self.bucket.ls(self.path)]

    def _delete(self, filename):
        """
        Delete filename from remote server
        """
        log.Log("Delete: %s" % self.path + filename, log.INFO)
        file_version_info = self.file_info(self.path + filename)
        self.bucket.delete_file_version(file_version_info.id_, file_version_info.file_name)

    def _query(self, filename):
        """
        Get size info of filename
        """
        log.Log("Query: %s" % self.path + filename, log.INFO)
        file_version_info = self.file_info(self.path + filename)
        return {'size': file_version_info.size
                if file_version_info is not None and file_version_info.size is not None else -1}

    def file_info(self, filename):
        response = self.bucket.list_file_names(filename, 1)
        for entry in response['files']:
            file_version_info = b2.file_version.FileVersionInfoFactory.from_api_response(entry)
            if file_version_info.file_name == filename:
                return file_version_info
        raise BackendException('File not found')


duplicity.backend.register_backend("b2", B2Backend)

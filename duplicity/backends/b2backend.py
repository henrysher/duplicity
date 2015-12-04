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

import json
import urllib2
import base64


class B2Backend(duplicity.backend.Backend):
    """
    Backend for BackBlaze's B2 storage service
    """

    def __init__(self, parsed_url):
        """
        Authorize to B2 api and set up needed variables
        """
        duplicity.backend.Backend.__init__(self, parsed_url)

        self.account_id = parsed_url.username
        account_key = self.get_password()

        self.url_parts = [
            x for x in parsed_url.path.replace("@", "/").split('/') if x != ''
        ]
        if self.url_parts:
            self.username = self.url_parts.pop(0)
            self.bucket_name = self.url_parts.pop(0)
        else:
            raise BackendException("B2 requires a bucket name")
        self.path = "/".join(self.url_parts)

        id_and_key = self.account_id + ":" + account_key
        basic_auth_string = 'Basic ' + base64.b64encode(id_and_key)
        headers = {'Authorization': basic_auth_string}

        request = urllib2.Request(
            'https://api.backblaze.com/b2api/v1/b2_authorize_account',
            headers=headers
        )

        response = urllib2.urlopen(request)
        response_data = json.loads(response.read())
        response.close()

        self.auth_token = response_data['authorizationToken']
        self.api_url = response_data['apiUrl']
        self.download_url = response_data['downloadUrl']

        try:
            self.find_or_create_bucket(self.bucket_name)
        except urllib2.HTTPError:
            raise FatalBackendException("Bucket cannot be created")

    def _get(self, remote_filename, local_path):
        """
        Download remote_filename to local_path
        """
        remote_filename = self.full_filename(remote_filename)
        url = self.download_url + \
            '/file/' + self.bucket_name + '/' + \
            remote_filename
        resp = self.get_or_post(url, None)

        to_file = open(local_path.name, 'wb')
        to_file.write(resp)
        to_file.close()

    def _put(self, source_path, remote_filename):
        """
        Copy source_path to remote_filename
        """
        self._delete(remote_filename)
        digest = self.hex_sha1_of_file(source_path)
        content_type = 'application/pgp-encrypted'
        remote_filename = self.full_filename(remote_filename)

        info = self.get_upload_info(self.bucket_id)
        url = info['uploadUrl']

        headers = {
            'Authorization': info['authorizationToken'],
            'X-Bz-File-Name': remote_filename,
            'Content-Type': content_type,
            'X-Bz-Content-Sha1': digest,
            'Content-Length': str(os.path.getsize(source_path.name)),
        }
        data_file = source_path.open()
        self.get_or_post(url, None, headers, data_file=data_file)

    def _list(self):
        """
        List files on remote server
        """
        endpoint = 'b2_list_file_names'
        url = self.formatted_url(endpoint)
        params = {
            'bucketId': self.bucket_id,
            'maxFileCount': 1000,
        }
        try:
            resp = self.get_or_post(url, params)
        except urllib2.HTTPError:
            return []

        files = [x['fileName'].split('/')[-1] for x in resp['files']]

        next_file = resp['nextFileName']
        while next_file:
            params['startFileName'] = next_file
            try:
                resp = self.get_or_post(url, params)
            except urllib2.HTTPError:
                return files

            files += [x['fileName'].split('/')[-1] for x in resp['files']]
            next_file = resp['nextFileName']

        return files

    def _delete(self, filename):
        """
        Delete filename from remote server
        """
        endpoint = 'b2_delete_file_version'
        url = self.formatted_url(endpoint)
        fileid = self.get_file_id(filename)
        if fileid is None:
            return
        filename = self.full_filename(filename)
        params = {'fileName': filename, 'fileId': fileid}
        try:
            self.get_or_post(url, params)
        except urllib2.HTTPError as e:
            if e.code == 400:
                return
            else:
                raise e

    def _query(self, filename):
        """
        Get size info of filename
        """
        info = self.get_file_info(filename)
        if not info:
            return {'size': -1}

        return {'size': info['size']}

    def _error_code(self, operation, e):
        if isinstance(e, urllib2.HTTPError):
            if e.code == 400:
                return log.ErrorCode.bad_request
            if e.code == 500:
                return log.ErrorCode.backed_error
            if e.code == 403:
                return log.ErrorCode.backed_permission_denied

    def find_or_create_bucket(self, bucket_name):
        """
        Find a bucket with name bucket_name and save its id.
        If it doesn't exist, create it
        """
        endpoint = 'b2_list_buckets'
        url = self.formatted_url(endpoint)

        params = {'accountId': self.account_id}
        resp = self.get_or_post(url, params)

        bucket_names = [x['bucketName'] for x in resp['buckets']]

        if bucket_name not in bucket_names:
            self.create_bucket(bucket_name)
        else:
            self.bucket_id = {
                x[
                    'bucketName'
                ]: x['bucketId'] for x in resp['buckets']
            }[bucket_name]

    def create_bucket(self, bucket_name):
        """
        Create a bucket with name bucket_name and save its id
        """
        endpoint = 'b2_create_bucket'
        url = self.formatted_url(endpoint)
        params = {
            'accountId': self.account_id,
            'bucketName': bucket_name,
            'bucketType': 'allPrivate'
        }
        resp = self.get_or_post(url, params)

        self.bucket_id = resp['bucketId']

    def formatted_url(self, endpoint):
        """
        Return the full api endpoint from just the last part
        """
        return '%s/b2api/v1/%s' % (self.api_url, endpoint)

    def get_upload_info(self, bucket_id):
        """
        Get an upload url for a bucket
        """
        endpoint = 'b2_get_upload_url'
        url = self.formatted_url(endpoint)
        return self.get_or_post(url, {'bucketId': bucket_id})

    def get_or_post(self, url, data, headers=None, data_file=None):
        """
        Sends the request, either get or post.
        If data and data_file are None, send a get request.
        data_file takes precedence over data.
        If headers are not supplied, just send with an auth key
        """
        if headers is None:
            headers = {'Authorization': self.auth_token}
        if data_file is not None:
            data = data_file
        else:
            data = json.dumps(data) if data else None

        encoded_headers = dict(
            (k, urllib2.quote(v.encode('utf-8')))
            for (k, v) in headers.iteritems()
        )

        with OpenUrl(url, data, encoded_headers) as resp:
            out = resp.read()
            try:
                return json.loads(out)
            except ValueError:
                return out

    def get_file_info(self, filename):
        """
        Get a file info from filename
        """
        endpoint = 'b2_list_file_names'
        url = self.formatted_url(endpoint)
        filename = self.full_filename(filename)
        params = {
            'bucketId': self.bucket_id,
            'maxFileCount': 1,
            'startFileName': filename,
        }
        resp = self.get_or_post(url, params)

        try:
            return resp['files'][0]
        except IndexError:
            return None
        except TypeError:
            return None

    def get_file_id(self, filename):
        """
        Get a file id form filename
        """
        try:
            return self.get_file_info(filename)['fileId']
        except IndexError:
            return None
        except TypeError:
            return None

    def full_filename(self, filename):
        if self.path:
            return self.path + '/' + filename
        else:
            return filename

    @staticmethod
    def hex_sha1_of_file(path):
        """
        Calculate the sha1 of a file to upload
        """
        f = path.open()
        block_size = 1024 * 1024
        digest = hashlib.sha1()
        while True:
            data = f.read(block_size)
            if len(data) == 0:
                break
            digest.update(data)
        f.close()
        return digest.hexdigest()


class OpenUrl(object):
    """
    Context manager that handles an open urllib2.Request, and provides
    the file-like object that is the response.
    """

    def __init__(self, url, data, headers):
        self.url = url
        self.data = data
        self.headers = headers
        self.file = None

    def __enter__(self):
        request = urllib2.Request(self.url, self.data, self.headers)
        self.file = urllib2.urlopen(request)
        return self.file

    def __exit__(self, exception_type, exception, traceback):
        if self.file is not None:
            self.file.close()


duplicity.backend.register_backend("b2", B2Backend)

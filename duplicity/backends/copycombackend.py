# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; coding: utf-8 -*-
#
# Copyright 2014 Marco Trevisan (Treviño) <mail@3v1n0.net>
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
import sys

import duplicity.backend
from duplicity import log
from duplicity.errors import BackendException


class CoPyCloud:
    API_URI = 'https://api.copy.com'
    DEFAULT_ENCODING = 'latin-1'
    DEFAULT_HEADERS = {'X-Client-Type': 'api', 'X-Api-Version': '1.0',
                       'X-Authorization': '', 'Accept': 'application/json'}

    PART_MAX_SIZE = 1024 * 1024
    PARTS_HEADER_FMT = '!IIIIII'
    PARTS_HEADER_SIG = 0xba5eba11
    PARTS_HEADER_VERSION = 1
    PART_ITEM_FMT = '!IIII73sIIII'
    PART_ITEM_SIG = 0xcab005e5
    PART_ITEM_VERSION = 1

    class Error(Exception):
        def __init__(self, message):
            Exception.__init__(self, message)

    def __init__(self, username, password):
        import urllib3
        self.http = urllib3.connection_from_url(self.API_URI, block=True, maxsize=1)
        res = self.__post_req('auth_user', {'username': username, 'password': password})

        if not res or 'auth_token' not in res:
            raise CoPyCloud.Error("Invalid Login")

        self.DEFAULT_HEADERS['X-Authorization'] = res['auth_token'].encode('ascii', 'ignore')

    def __req(self, req_type, method, params={}, headers={}):
        import json
        headers.update(self.DEFAULT_HEADERS)
        method = '/' + method if method[0] != '/' else method

        if isinstance(params, dict):
            res = self.http.request_encode_body(req_type, method, {'data': json.dumps(params)},
                                                headers, encode_multipart=False)
        else:
            res = self.http.urlopen(req_type, method, params, headers)

        if res.status != 200:
            raise CoPyCloud.Error("Got HTTP error " + str(res.status))

        try:
            if 'content-type' in res.headers and res.headers['content-type'] == 'application/json' \
               or res.data.startswith('{'):
                jd = json.loads(res.data.decode(self.DEFAULT_ENCODING), self.DEFAULT_ENCODING)

                if jd and 'result' in jd and jd['result'] == 'error':
                    raise CoPyCloud.Error("Error %s: %s" % (jd['error_code'], jd['error_string']))

                return jd
        except ValueError:
            pass

        return res.data

    def __post_req(self, method, params={}, headers={}):
        return self.__req('POST', method, params, headers)

    def __get_req(self, method, headers={}):
        return self.__req('GET', method, headers)

    def __binary_parts_req(self, method, parts, share_id=0, headers={}):
        if not len(parts):
            return

        import struct
        invalid_parts = []
        header_size = struct.calcsize(self.PARTS_HEADER_FMT)
        item_base_size = struct.calcsize(self.PART_ITEM_FMT)
        items_data_size = sum([p['size'] if 'data' in p else 0 for p in parts])
        buf = bytearray(header_size + item_base_size * len(parts) + items_data_size)
        error_code = 0
        padding = 0
        pos = 0

        struct.pack_into(self.PARTS_HEADER_FMT, buf, pos, self.PARTS_HEADER_SIG, header_size,
                         self.PARTS_HEADER_VERSION, len(buf) - header_size, len(parts), error_code)
        pos += header_size

        for part in parts:
            data_size = part['size'] if 'data' in part else 0
            part_size = item_base_size + data_size
            fingerprint = bytes(part['fingerprint'].encode(self.DEFAULT_ENCODING))
            struct.pack_into(self.PART_ITEM_FMT, buf, pos, self.PART_ITEM_SIG, part_size,
                             self.PART_ITEM_VERSION, share_id, fingerprint, part['size'],
                             data_size, error_code, padding)

            pos += item_base_size

            if data_size > 0:
                buf[pos:pos + data_size] = part['data']
                pos += data_size

        ret = self.__post_req(method, buf, {'Content-Type': 'application/octet-stream'})

        pos = 0
        r = (sig, header_size, version, parts_size, parts_num, error) = \
            struct.unpack_from(self.PARTS_HEADER_FMT, ret, pos)
        pos += header_size

        if sig != self.PARTS_HEADER_SIG:
            raise CoPyCloud.Error("Invalid binary header signature from server")
        if error != 0:
            raise CoPyCloud.Error("Invalid binary response from server: " + str(ret[pos:]))
        if header_size != struct.calcsize(self.PARTS_HEADER_FMT):
            raise CoPyCloud.Error("Invalid binary header size from server")
        if version != self.PARTS_HEADER_VERSION:
            raise CoPyCloud.Error("Binary header version mismatch")
        if parts_num != len(parts):
            raise CoPyCloud.Error("Part count mismatch")

        for part in parts:
            (sig, item_size, version, share_id, fingerprint, remote_size, data_size, error, padding) = \
                struct.unpack_from(self.PART_ITEM_FMT, ret, pos)

            if sig != self.PART_ITEM_SIG:
                raise CoPyCloud.Error("Invalid binary part item header signature from server")
            if version != self.PART_ITEM_VERSION:
                raise CoPyCloud.Error("Binary part item version mismatch")
            if fingerprint[:-1] != bytes(part['fingerprint'].encode(self.DEFAULT_ENCODING)):
                raise CoPyCloud.Error("Part %u fingerprint mismatch" % part['offset'])

            if 'data' in part:
                if error != 0:
                    offset = pos + item_base_size
                    raise CoPyCloud.Error("Invalid binary part item: " + str(ret[offset:offset + data_size]))
                if item_size != item_base_size:
                    raise CoPyCloud.Error("Invalid binary part item size received from server")
                if remote_size != part['size']:
                    raise CoPyCloud.Error("Part %u local/remote size mismatch" % part['offset'])
            else:
                if error != 0 or remote_size != part['size']:
                    invalid_parts.append(part)

            pos += item_base_size

        return invalid_parts

    def __update_objects(self, parameters):
        p = [parameters] if isinstance(parameters, dict) else parameters
        self.__post_req('update_objects', {'meta': p})

    def __sanitize_path(self, path):
        path = '/' if not path or not len(path) else path
        return '/' + path if path[0] != '/' else path

    def __get_file_parts(self, f):
        import hashlib
        parts = []
        size = os.path.getsize(f.name)

        while f.tell() < size:
            offset = f.tell()
            part_data = f.read(self.PART_MAX_SIZE)
            fingerprint = hashlib.md5(part_data).hexdigest() + hashlib.sha1(part_data).hexdigest()
            parts.append({'fingerprint': fingerprint, 'offset': offset, 'size': len(part_data)})

        if f.tell() != size:
            raise CoPyCloud.Error("Impossible to generate full parts for file " + f.name)

        return parts

    def __fill_file_parts(self, f, parts):
        for part in parts:
            f.seek(part['offset'])
            part['data'] = f.read(part['size'])

    def list_files(self, path=None, max_items=sys.maxsize):
        path = path = self.__sanitize_path(path)
        parameters = {'path': path, 'max_items': max_items}
        res = self.__post_req('list_objects', parameters)

        if not res or 'children' not in res:
            raise CoPyCloud.Error("Impossible to retrieve the files")

        if 'object' in res and 'type' in res['object'] and res['object']['type'] == 'file':
            return res['object']

        return res['children']

    def remove(self, paths):
        if isinstance(paths, str):
            if not len(paths):
                raise CoPyCloud.Error("Impossible to remove a file with an empty path")
            paths = [paths]
        if paths is None:
            raise CoPyCloud.Error("Impossible to remove files with invalid path")

        self.__update_objects([{'action': 'remove', 'path': self.__sanitize_path(p)} for p in paths])

    def download(self, path):
        if not path or not len(path):
            raise CoPyCloud.Error("Impossible to download a file with an empty path")

        if not len(self.list_files(path, max_items=1)):
            raise CoPyCloud.Error("Impossible to download '" + path + "'")

        return self.__post_req('download_object', {'path': path})

    def upload(self, source, dest, parallel=5, share_id=0):
        try:
            f = open(source, 'rb')
        except Exception as e:
            raise CoPyCloud.Error("Impossible to open source file " + str(e))

        parts = self.__get_file_parts(f)
        parts_chunks = [parts[i:i + parallel] for i in range(0, len(parts), parallel)]

        for parts_chunk in parts_chunks:
            missing_parts = self.__binary_parts_req('has_object_parts', parts_chunk)

            if len(missing_parts):
                self.__fill_file_parts(f, missing_parts)
                self.__binary_parts_req('send_object_parts', missing_parts)

                for part in parts_chunk:
                    del(part['data'])

        update_params = {'action': 'create', 'object_type': 'file', 'path': self.__sanitize_path(dest),
                         'size': os.path.getsize(f.name), 'parts': parts}
        self.__update_objects(update_params)

        f.close()


class CopyComBackend(duplicity.backend.Backend):
    """Copy.com duplicity backend"""

    def __init__(self, parsed_url):
        """Connect to Copy.com"""
        duplicity.backend.Backend.__init__(self, parsed_url)
        try:
            self.copy = CoPyCloud(parsed_url.username, self.get_password())
        except CoPyCloud.Error as e:
            raise BackendException(e)

        [self.folder] = parsed_url.path[1:].split('/')

    def _list(self):
        """List files in folder"""
        try:
            return [os.path.basename(f['path']) for f in self.copy.list_files(self.folder)]
        except CoPyCloud.Error as e:
            raise BackendException(e)

    def _query(self, filename):
        try:
            file_info = self.copy.list_files(os.path.join(self.folder, filename))
            return {'size': int(file_info['size']) if 'size' in file_info else -1}
        except CoPyCloud.Error as e:
            raise BackendException(e)

    def _put(self, source_path, remote_filename):
        """Upload local file to cloud"""
        try:
            self.copy.upload(source_path.get_canonical(), os.path.join(self.folder, remote_filename))
        except CoPyCloud.Error as e:
            raise BackendException(e)

    def _get(self, remote_filename, local_path):
        """Save cloud file locally"""
        try:
            raw = self.copy.download(os.path.join(self.folder, remote_filename))
        except CoPyCloud.Error as e:
            raise BackendException(e)

        f = local_path.open(mode='wb')
        f.write(raw)
        f.close()

    def _delete(self, filename):
        """Delete a file"""
        try:
            self.copy.remove(os.path.join(self.folder, filename))
        except CoPyCloud.Error as e:
            raise BackendException(e)

''' This must be disabled here, because if a file in list does not exist, the
    Copy server will stop deleting the subsequent stuff, raising an error,
    making test_delete_list to fail.
    def _delete_list(self, filenames):
        """Delete list of files"""
        try:
            self.copy.remove([os.path.join(self.folder, f) for f in filenames])
        except CoPyCloud.Error as e:
            if 'Error 1024' in e:
                pass # "Ignore file can't be located error, in this case"
'''

duplicity.backend.register_backend('copy', CopyComBackend)
duplicity.backend.uses_netloc.extend(['copy'])

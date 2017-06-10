# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2013 Matthieu Huin <mhu@enovance.com>
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

import duplicity.backend
from duplicity import log
from duplicity import util
from duplicity.errors import BackendException


class SwiftBackend(duplicity.backend.Backend):
    """
    Backend for Swift
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        try:
            from swiftclient import Connection
            from swiftclient import ClientException
        except ImportError as e:
            raise BackendException("""\
Swift backend requires the python-swiftclient library.
Exception: %s""" % str(e))

        self.resp_exc = ClientException
        conn_kwargs = {}

        # if the user has already authenticated
        if 'SWIFT_PREAUTHURL' in os.environ and 'SWIFT_PREAUTHTOKEN' in os.environ:
            conn_kwargs['preauthurl'] = os.environ['SWIFT_PREAUTHURL']
            conn_kwargs['preauthtoken'] = os.environ['SWIFT_PREAUTHTOKEN']

        else:
            if 'SWIFT_USERNAME' not in os.environ:
                raise BackendException('SWIFT_USERNAME environment variable '
                                       'not set.')

            if 'SWIFT_PASSWORD' not in os.environ:
                raise BackendException('SWIFT_PASSWORD environment variable '
                                       'not set.')

            if 'SWIFT_AUTHURL' not in os.environ:
                raise BackendException('SWIFT_AUTHURL environment variable '
                                       'not set.')

            conn_kwargs['user'] = os.environ['SWIFT_USERNAME']
            conn_kwargs['key'] = os.environ['SWIFT_PASSWORD']
            conn_kwargs['authurl'] = os.environ['SWIFT_AUTHURL']

        os_options = {}

        if 'SWIFT_AUTHVERSION' in os.environ:
            conn_kwargs['auth_version'] = os.environ['SWIFT_AUTHVERSION']
            if os.environ['SWIFT_AUTHVERSION'] == '3':
                if 'SWIFT_USER_DOMAIN_NAME' in os.environ:
                    os_options.update({'user_domain_name': os.environ['SWIFT_USER_DOMAIN_NAME']})
                if 'SWIFT_USER_DOMAIN_ID' in os.environ:
                    os_options.update({'user_domain_id': os.environ['SWIFT_USER_DOMAIN_ID']})
                if 'SWIFT_PROJECT_DOMAIN_NAME' in os.environ:
                    os_options.update({'project_domain_name': os.environ['SWIFT_PROJECT_DOMAIN_NAME']})
                if 'SWIFT_PROJECT_DOMAIN_ID' in os.environ:
                    os_options.update({'project_domain_id': os.environ['SWIFT_PROJECT_DOMAIN_ID']})
                if 'SWIFT_TENANTNAME' in os.environ:
                    os_options.update({'tenant_name': os.environ['SWIFT_TENANTNAME']})
                if 'SWIFT_ENDPOINT_TYPE' in os.environ:
                    os_options.update({'endpoint_type': os.environ['SWIFT_ENDPOINT_TYPE']})
                if 'SWIFT_USERID' in os.environ:
                    os_options.update({'user_id': os.environ['SWIFT_USERID']})
                if 'SWIFT_TENANTID' in os.environ:
                    os_options.update({'tenant_id': os.environ['SWIFT_TENANTID']})
                if 'SWIFT_REGIONNAME' in os.environ:
                    os_options.update({'region_name': os.environ['SWIFT_REGIONNAME']})

        else:
            conn_kwargs['auth_version'] = '1'
        if 'SWIFT_TENANTNAME' in os.environ:
            conn_kwargs['tenant_name'] = os.environ['SWIFT_TENANTNAME']
        if 'SWIFT_REGIONNAME' in os.environ:
            os_options.update({'region_name': os.environ['SWIFT_REGIONNAME']})

        conn_kwargs['os_options'] = os_options

        # This folds the null prefix and all null parts, which means that:
        #  //MyContainer/ and //MyContainer are equivalent.
        #  //MyContainer//My/Prefix/ and //MyContainer/My/Prefix are equivalent.
        url_parts = [x for x in parsed_url.path.split('/') if x != '']

        self.container = url_parts.pop(0)
        if url_parts:
            self.prefix = '%s/' % '/'.join(url_parts)
        else:
            self.prefix = ''

        container_metadata = None
        try:
            self.conn = Connection(**conn_kwargs)
            container_metadata = self.conn.head_container(self.container)
        except ClientException:
            pass
        except Exception as e:
            log.FatalError("Connection failed: %s %s"
                           % (e.__class__.__name__, str(e)),
                           log.ErrorCode.connection_failed)

        if container_metadata is None:
            log.Info("Creating container %s" % self.container)
            try:
                self.conn.put_container(self.container)
            except Exception as e:
                log.FatalError("Container creation failed: %s %s"
                               % (e.__class__.__name__, str(e)),
                               log.ErrorCode.connection_failed)

    def _error_code(self, operation, e):
        if isinstance(e, self.resp_exc):
            if e.http_status == 404:
                return log.ErrorCode.backend_not_found

    def _put(self, source_path, remote_filename):
        self.conn.put_object(self.container, self.prefix + remote_filename,
                             file(source_path.name))

    def _get(self, remote_filename, local_path):
        headers, body = self.conn.get_object(self.container, self.prefix + remote_filename, resp_chunk_size=1024)
        with open(local_path.name, 'wb') as f:
            for chunk in body:
                f.write(chunk)

    def _list(self):
        headers, objs = self.conn.get_container(self.container, full_listing=True, path=self.prefix)
        # removes prefix from return values. should check for the prefix ?
        return [o['name'][len(self.prefix):] for o in objs]

    def _delete(self, filename):
        self.conn.delete_object(self.container, self.prefix + filename)

    def _query(self, filename):
        sobject = self.conn.head_object(self.container, self.prefix + filename)
        return {'size': int(sobject['content-length'])}


duplicity.backend.register_backend("swift", SwiftBackend)

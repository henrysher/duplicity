# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2013 Matthieu Huin <mhu@enovance.com>
# Copyright 2017 Xavier Lucas <xavier.lucas@corp.ovh.com>
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
import time


class PCABackend(duplicity.backend.Backend):
    """
    Backend for OVH PCA
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        try:
            from swiftclient import Connection
            from swiftclient import ClientException
        except ImportError as e:
            raise BackendException("""\
PCA backend requires the python-swiftclient library.
Exception: %s""" % str(e))

        self.resp_exc = ClientException
        self.conn_cls = Connection
        conn_kwargs = {}

        # if the user has already authenticated
        if 'PCA_PREAUTHURL' in os.environ and 'PCA_PREAUTHTOKEN' in os.environ:
            conn_kwargs['preauthurl'] = os.environ['PCA_PREAUTHURL']
            conn_kwargs['preauthtoken'] = os.environ['PCA_PREAUTHTOKEN']

        else:
            if 'PCA_USERNAME' not in os.environ:
                raise BackendException('PCA_USERNAME environment variable '
                                       'not set.')

            if 'PCA_PASSWORD' not in os.environ:
                raise BackendException('PCA_PASSWORD environment variable '
                                       'not set.')

            if 'PCA_AUTHURL' not in os.environ:
                raise BackendException('PCA_AUTHURL environment variable '
                                       'not set.')

            conn_kwargs['user'] = os.environ['PCA_USERNAME']
            conn_kwargs['key'] = os.environ['PCA_PASSWORD']
            conn_kwargs['authurl'] = os.environ['PCA_AUTHURL']

        os_options = {}

        if 'PCA_AUTHVERSION' in os.environ:
            conn_kwargs['auth_version'] = os.environ['PCA_AUTHVERSION']
            if os.environ['PCA_AUTHVERSION'] == '3':
                if 'PCA_USER_DOMAIN_NAME' in os.environ:
                    os_options.update({'user_domain_name': os.environ['PCA_USER_DOMAIN_NAME']})
                if 'PCA_USER_DOMAIN_ID' in os.environ:
                    os_options.update({'user_domain_id': os.environ['PCA_USER_DOMAIN_ID']})
                if 'PCA_PROJECT_DOMAIN_NAME' in os.environ:
                    os_options.update({'project_domain_name': os.environ['PCA_PROJECT_DOMAIN_NAME']})
                if 'PCA_PROJECT_DOMAIN_ID' in os.environ:
                    os_options.update({'project_domain_id': os.environ['PCA_PROJECT_DOMAIN_ID']})
                if 'PCA_TENANTNAME' in os.environ:
                    os_options.update({'tenant_name': os.environ['PCA_TENANTNAME']})
                if 'PCA_ENDPOINT_TYPE' in os.environ:
                    os_options.update({'endpoint_type': os.environ['PCA_ENDPOINT_TYPE']})
                if 'PCA_USERID' in os.environ:
                    os_options.update({'user_id': os.environ['PCA_USERID']})
                if 'PCA_TENANTID' in os.environ:
                    os_options.update({'tenant_id': os.environ['PCA_TENANTID']})
                if 'PCA_REGIONNAME' in os.environ:
                    os_options.update({'region_name': os.environ['PCA_REGIONNAME']})

        else:
            conn_kwargs['auth_version'] = '2'
        if 'PCA_TENANTNAME' in os.environ:
            conn_kwargs['tenant_name'] = os.environ['PCA_TENANTNAME']
        if 'PCA_REGIONNAME' in os.environ:
            os_options.update({'region_name': os.environ['PCA_REGIONNAME']})

        conn_kwargs['os_options'] = os_options
        conn_kwargs['retries'] = 0

        self.conn_kwargs = conn_kwargs

        # This folds the null prefix and all null parts, which means that:
        #  //MyContainer/ and //MyContainer are equivalent.
        #  //MyContainer//My/Prefix/ and //MyContainer/My/Prefix are equivalent.
        url_parts = [x for x in parsed_url.path.split('/') if x != '']

        self.container = url_parts.pop(0)
        if url_parts:
            self.prefix = '%s/' % '/'.join(url_parts)
        else:
            self.prefix = ''

        policy = 'PCA'
        policy_header = 'X-Storage-Policy'

        container_metadata = None
        try:
            self.conn = Connection(**self.conn_kwargs)
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
                headers = dict([[policy_header, policy]])
                self.conn.put_container(self.container, headers=headers)
            except Exception as e:
                log.FatalError("Container creation failed: %s %s"
                               % (e.__class__.__name__, str(e)),
                               log.ErrorCode.connection_failed)
        elif policy and container_metadata[policy_header.lower()] != policy:
            log.FatalError("Container '%s' exists but its storage policy is '%s' not '%s'."
                           % (self.container, container_metadata[policy_header.lower()], policy))

    def _error_code(self, operation, e):
        if isinstance(e, self.resp_exc):
            if e.http_status == 404:
                return log.ErrorCode.backend_not_found

    def _put(self, source_path, remote_filename):
        self.conn.put_object(self.container, self.prefix + remote_filename,
                             file(source_path.name))

    def _get(self, remote_filename, local_path):
        body = self.preprocess_download(remote_filename, 60)
        if body:
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

    def preprocess_download(self, remote_filename, retry_period, wait=True):
        body = self.unseal(remote_filename)
        try:
            if wait:
                while not body:
                    time.sleep(retry_period)
                    self.conn = self.conn_cls(**self.conn_kwargs)
                    body = self.unseal(remote_filename)
                    self.conn.close()
        except Exception as e:
            log.FatalError("Connection failed: %s %s" % (e.__class__.__name__, str(e)),
                           log.ErrorCode.connection_failed)
        return body

    def unseal(self, remote_filename):
        try:
            _, body = self.conn.get_object(self.container, self.prefix + remote_filename,
                                           resp_chunk_size=1024)
            log.Info("File %s was successfully unsealed." % remote_filename)
            return body
        except self.resp_exc as e:
            # The object is sealed but being released.
            if e.http_status == 429:
                # The retry-after header contains the remaining duration before
                # the unsealing operation completes.
                duration = int(e.http_response_headers['Retry-After'])
                m, s = divmod(duration, 60)
                h, m = divmod(m, 60)
                eta = "%dh%02dm%02ds" % (h, m, s)
                log.Info("File %s is being unsealed, operation ETA is %s." %
                         (remote_filename, eta))
            else:
                raise


duplicity.backend.register_backend("pca", PCABackend)

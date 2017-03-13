# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2013 J.P. Krauss <jkrauss@asymworks.com>
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


class PyraxBackend(duplicity.backend.Backend):
    """
    Backend for Rackspace's CloudFiles using Pyrax
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        try:
            import pyrax
        except ImportError as e:
            raise BackendException("""\
Pyrax backend requires the pyrax library available from Rackspace.
Exception: %s""" % str(e))

        # Inform Pyrax that we're talking to Rackspace
        # per Jesus Monzon (gsusmonzon)
        pyrax.set_setting("identity_type", "rackspace")

        conn_kwargs = {}

        if 'CLOUDFILES_USERNAME' not in os.environ:
            raise BackendException('CLOUDFILES_USERNAME environment variable'
                                   'not set.')

        if 'CLOUDFILES_APIKEY' not in os.environ:
            raise BackendException('CLOUDFILES_APIKEY environment variable not set.')

        conn_kwargs['username'] = os.environ['CLOUDFILES_USERNAME']
        conn_kwargs['api_key'] = os.environ['CLOUDFILES_APIKEY']

        if 'CLOUDFILES_REGION' in os.environ:
            conn_kwargs['region'] = os.environ['CLOUDFILES_REGION']

        container = parsed_url.path.lstrip('/')

        try:
            pyrax.set_credentials(**conn_kwargs)
        except Exception as e:
            log.FatalError("Connection failed, please check your credentials: %s %s"
                           % (e.__class__.__name__, util.uexc(e)),
                           log.ErrorCode.connection_failed)

        self.client_exc = pyrax.exceptions.ClientException
        self.nso_exc = pyrax.exceptions.NoSuchObject
        self.container = pyrax.cloudfiles.create_container(container)

    def _error_code(self, operation, e):
        if isinstance(e, self.nso_exc):
            return log.ErrorCode.backend_not_found
        elif isinstance(e, self.client_exc):
            if e.code == 404:
                return log.ErrorCode.backend_not_found
        elif hasattr(e, 'http_status'):
            if e.http_status == 404:
                return log.ErrorCode.backend_not_found

    def _put(self, source_path, remote_filename):
        self.container.upload_file(source_path.name, remote_filename)

    def _get(self, remote_filename, local_path):
        sobject = self.container.get_object(remote_filename)
        with open(local_path.name, 'wb') as f:
            f.write(sobject.get())

    def _list(self):
        # Cloud Files will return a max of 10,000 objects.  We have
        # to make multiple requests to get them all.
        objs = self.container.get_object_names()
        keys = objs
        while len(objs) == 10000:
            objs = self.container.get_object_names(marker=keys[-1])
            keys += objs
        return keys

    def _delete(self, filename):
        self.container.delete_object(filename)

    def _query(self, filename):
        sobject = self.container.get_object(filename)
        return {'size': sobject.total_bytes}

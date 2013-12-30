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
import time

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport
from duplicity.util import exception_traceback
from duplicity.backend import retry

class SwiftBackend(duplicity.backend.Backend):
    """
    Backend for Swift
    """
    def __init__(self, parsed_url):
        try:
            from swiftclient import Connection
            from swiftclient import ClientException
        except ImportError:
            raise BackendException("This backend requires "
                                   "the python-swiftclient library.")

        self.resp_exc = ClientException
        conn_kwargs = {}

        # if the user has already authenticated
        if os.environ.has_key('SWIFT_PREAUTHURL') and os.environ.has_key('SWIFT_PREAUTHTOKEN'):
            conn_kwargs['preauthurl'] = os.environ['SWIFT_PREAUTHURL']
            conn_kwargs['preauthtoken'] = os.environ['SWIFT_PREAUTHTOKEN']           
        
        else:
            if not os.environ.has_key('SWIFT_USERNAME'):
                raise BackendException('SWIFT_USERNAME environment variable '
                                       'not set.')

            if not os.environ.has_key('SWIFT_PASSWORD'):
                raise BackendException('SWIFT_PASSWORD environment variable '
                                       'not set.')

            if not os.environ.has_key('SWIFT_AUTHURL'):
                raise BackendException('SWIFT_AUTHURL environment variable '
                                       'not set.')

            conn_kwargs['user'] = os.environ['SWIFT_USERNAME']
            conn_kwargs['key'] = os.environ['SWIFT_PASSWORD']
            conn_kwargs['authurl'] = os.environ['SWIFT_AUTHURL']

        if os.environ.has_key('SWIFT_AUTHVERSION'):
            conn_kwargs['auth_version'] = os.environ['SWIFT_AUTHVERSION']
        else:
            conn_kwargs['auth_version'] = '1'
        if os.environ.has_key('SWIFT_TENANTNAME'):
            conn_kwargs['tenant_name'] = os.environ['SWIFT_TENANTNAME']
            
        self.container = parsed_url.path.lstrip('/')

        try:
            self.conn = Connection(**conn_kwargs)
            self.conn.put_container(self.container)
        except Exception, e:
            log.FatalError("Connection failed: %s %s"
                           % (e.__class__.__name__, str(e)),
                           log.ErrorCode.connection_failed)

    def put(self, source_path, remote_filename = None):
        if not remote_filename:
            remote_filename = source_path.get_filename()

        for n in range(1, globals.num_retries+1):
            log.Info("Uploading '%s/%s' " % (self.container, remote_filename))
            try:
                self.conn.put_object(self.container,
                                     remote_filename, 
                                     file(source_path.name))
                return
            except self.resp_exc, error:
                log.Warn("Upload of '%s' failed (attempt %d): Swift server returned: %s %s"
                         % (remote_filename, n, error.http_status, error.message))
            except Exception, e:
                log.Warn("Upload of '%s' failed (attempt %s): %s: %s"
                        % (remote_filename, n, e.__class__.__name__, str(e)))
                log.Debug("Backtrace of previous error: %s"
                          % exception_traceback())
            time.sleep(30)
        log.Warn("Giving up uploading '%s' after %s attempts"
                 % (remote_filename, globals.num_retries))
        raise BackendException("Error uploading '%s'" % remote_filename)

    def get(self, remote_filename, local_path):
        for n in range(1, globals.num_retries+1):
            log.Info("Downloading '%s/%s'" % (self.container, remote_filename))
            try:
                headers, body = self.conn.get_object(self.container,
                                                     remote_filename)
                f = open(local_path.name, 'w')
                for chunk in body:
                    f.write(chunk)
                local_path.setdata()
                return
            except self.resp_exc, resperr:
                log.Warn("Download of '%s' failed (attempt %s): Swift server returned: %s %s"
                         % (remote_filename, n, resperr.http_status, resperr.message))
            except Exception, e:
                log.Warn("Download of '%s' failed (attempt %s): %s: %s"
                         % (remote_filename, n, e.__class__.__name__, str(e)))
                log.Debug("Backtrace of previous error: %s"
                          % exception_traceback())
            time.sleep(30)
        log.Warn("Giving up downloading '%s' after %s attempts"
                 % (remote_filename, globals.num_retries))
        raise BackendException("Error downloading '%s/%s'"
                               % (self.container, remote_filename))

    def _list(self):
        for n in range(1, globals.num_retries+1):
            log.Info("Listing '%s'" % (self.container))
            try:
                # Cloud Files will return a max of 10,000 objects.  We have
                # to make multiple requests to get them all.
                headers, objs = self.conn.get_container(self.container)
                return [ o['name'] for o in objs ]
            except self.resp_exc, resperr:
                log.Warn("Listing of '%s' failed (attempt %s): Swift server returned: %s %s"
                         % (self.container, n, resperr.http_status, resperr.message))
            except Exception, e:
                log.Warn("Listing of '%s' failed (attempt %s): %s: %s"
                         % (self.container, n, e.__class__.__name__, str(e)))
                log.Debug("Backtrace of previous error: %s"
                          % exception_traceback())
            time.sleep(30)
        log.Warn("Giving up listing of '%s' after %s attempts"
                 % (self.container, globals.num_retries))
        raise BackendException("Error listing '%s'"
                               % (self.container))

    def delete_one(self, remote_filename):
        for n in range(1, globals.num_retries+1):
            log.Info("Deleting '%s/%s'" % (self.container, remote_filename))
            try:
                self.conn.delete_object(self.container, remote_filename)
                return
            except self.resp_exc, resperr:
                if n > 1 and resperr.http_status == 404:
                    # We failed on a timeout, but delete succeeded on the server
                    log.Warn("Delete of '%s' missing after retry - must have succeded earlier" % remote_filename )
                    return
                log.Warn("Delete of '%s' failed (attempt %s): Swift server returned: %s %s"
                         % (remote_filename, n, resperr.http_status, resperr.message))
            except Exception, e:
                log.Warn("Delete of '%s' failed (attempt %s): %s: %s"
                         % (remote_filename, n, e.__class__.__name__, str(e)))
                log.Debug("Backtrace of previous error: %s"
                          % exception_traceback())
            time.sleep(30)
        log.Warn("Giving up deleting '%s' after %s attempts"
                 % (remote_filename, globals.num_retries))
        raise BackendException("Error deleting '%s/%s'"
                               % (self.container, remote_filename))

    def delete(self, filename_list):
        for file in filename_list:
            self.delete_one(file)
            log.Debug("Deleted '%s/%s'" % (self.container, file))

    @retry
    def _query_file_info(self, filename, raise_errors=False):
        try:
            sobject = self.conn.head_object(self.container, filename)
            return {'size': long(sobject['content-length'])}
        except self.resp_exc:
            return {'size': -1}
        except Exception, e:
            log.Warn("Error querying '%s/%s': %s"
                     "" % (self.container,
                           filename,
                           str(e)))
            if raise_errors:
                raise e
            else:
                return {'size': None}

duplicity.backend.register_backend("swift", SwiftBackend)

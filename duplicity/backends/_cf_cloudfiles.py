# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2009 Eric EJ Johnson <ej.johnson@rackspace.com>
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

class CloudFilesBackend(duplicity.backend.Backend):
    """
    Backend for Rackspace's CloudFiles
    """
    def __init__(self, parsed_url):
        try:
            from cloudfiles import Connection
            from cloudfiles.errors import ResponseError
            from cloudfiles import consts
        except ImportError:
            raise BackendException("This backend requires the cloudfiles "
                                   "library available from Rackspace.")

        self.resp_exc = ResponseError
        conn_kwargs = {}

        if not os.environ.has_key('CLOUDFILES_USERNAME'):
            raise BackendException('CLOUDFILES_USERNAME environment variable'
                                   'not set.')

        if not os.environ.has_key('CLOUDFILES_APIKEY'):
            raise BackendException('CLOUDFILES_APIKEY environment variable not set.')

        conn_kwargs['username'] = os.environ['CLOUDFILES_USERNAME']
        conn_kwargs['api_key'] = os.environ['CLOUDFILES_APIKEY']

        if os.environ.has_key('CLOUDFILES_AUTHURL'):
            conn_kwargs['authurl'] = os.environ['CLOUDFILES_AUTHURL']
        else:
            conn_kwargs['authurl'] = consts.default_authurl

        container = parsed_url.path.lstrip('/')

        try:
            conn = Connection(**conn_kwargs)
        except Exception, e:
            log.FatalError("Connection failed, please check your credentials: %s %s"
                           % (e.__class__.__name__, str(e)),
                           log.ErrorCode.connection_failed)
        self.container = conn.create_container(container)

    def put(self, source_path, remote_filename = None):
        if not remote_filename:
            remote_filename = source_path.get_filename()

        for n in range(1, globals.num_retries+1):
            log.Info("Uploading '%s/%s' " % (self.container, remote_filename))
            try:
                sobject = self.container.create_object(remote_filename)
                sobject.load_from_filename(source_path.name)
                return
            except self.resp_exc, error:
                log.Warn("Upload of '%s' failed (attempt %d): CloudFiles returned: %s %s"
                         % (remote_filename, n, error.status, error.reason))
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
                sobject = self.container.create_object(remote_filename)
                f = open(local_path.name, 'w')
                for chunk in sobject.stream():
                    f.write(chunk)
                local_path.setdata()
                return
            except self.resp_exc, resperr:
                log.Warn("Download of '%s' failed (attempt %s): CloudFiles returned: %s %s"
                         % (remote_filename, n, resperr.status, resperr.reason))
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

    def list(self):
        for n in range(1, globals.num_retries+1):
            log.Info("Listing '%s'" % (self.container))
            try:
                # Cloud Files will return a max of 10,000 objects.  We have
                # to make multiple requests to get them all.
                objs = self.container.list_objects()
                keys = objs
                while len(objs) == 10000:
                    objs = self.container.list_objects(marker=keys[-1])
                    keys += objs
                return keys
            except self.resp_exc, resperr:
                log.Warn("Listing of '%s' failed (attempt %s): CloudFiles returned: %s %s"
                         % (self.container, n, resperr.status, resperr.reason))
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
                self.container.delete_object(remote_filename)
                return
            except self.resp_exc, resperr:
                if n > 1 and resperr.status == 404:
                    # We failed on a timeout, but delete succeeded on the server
                    log.Warn("Delete of '%s' missing after retry - must have succeded earler" % remote_filename )
                    return
                log.Warn("Delete of '%s' failed (attempt %s): CloudFiles returned: %s %s"
                         % (remote_filename, n, resperr.status, resperr.reason))
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
        from cloudfiles.errors import NoSuchObject
        try:
            sobject = self.container.get_object(filename)
            return {'size': sobject.size}
        except NoSuchObject:
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

duplicity.backend.register_backend("cf+http", CloudFilesBackend)

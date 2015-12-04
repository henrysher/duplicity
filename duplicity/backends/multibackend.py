# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2015 Steve Tynor <steve.tynor@gmail.com>
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

#

import os
import os.path
import string
import urllib
import json

import duplicity.backend
from duplicity.errors import BackendException
from duplicity import log


class MultiBackend(duplicity.backend.Backend):
    """Store files across multiple remote stores. URL is a path to a local file containing URLs/other config defining the remote store"""

    # the stores we are managing
    __stores = []

    # when we write, we "stripe" via a simple round-robin across
    # remote stores.  It's hard to get too much more sophisticated
    # since we can't rely on the backend to give us any useful meta
    # data (e.g. sizes of files, capacity of the store (quotas)) to do
    # a better job of balancing load across stores.
    __write_cursor = 0

    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        # Init each of the wrapped stores
        #
        # config file is a json formatted collection of values, one for
        # each backend.  We will 'stripe' data across all the given stores:
        #
        #  'url'  - the URL used for the backend store
        #  'env' - an optional list of enviroment variable values to set
        #      during the intialization of the backend
        #
        # Example:
        #
        # [
        #  {
        #   "url": "abackend://myuser@domain.com/backup",
        #   "env": [
        #     {
        #      "name" : "MYENV",
        #      "value" : "xyz"
        #     },
        #     {
        #      "name" : "FOO",
        #      "value" : "bar"
        #     }
        #    ]
        #  },
        #  {
        #   "url": "file:///path/to/dir"
        #  }
        # ]

        try:
            with open(parsed_url.path) as f:
                configs = json.load(f)
        except IOError as e:
            log.Log(_("MultiBackend: Could not load config file %s: %s ")
                    % (parsed_url.path, e),
                    log.ERROR)
            raise BackendException('Could not load config file')

        for config in configs:
            url = config['url']
            log.Log(_("MultiBackend: use store %s")
                    % (url),
                    log.INFO)
            if 'env' in config:
                for env in config['env']:
                    log.Log(_("MultiBackend: set env %s = %s")
                            % (env['name'], env['value']),
                            log.INFO)
                    os.environ[env['name']] = env['value']

            store = duplicity.backend.get_backend(url)
            self.__stores.append(store)
            # store_list = store.list()
            # log.Log(_("MultiBackend: at init, store %s has %s files")
            #         % (url, len(store_list)),
            #         log.INFO)

    def _put(self, source_path, remote_filename):
        first = self.__write_cursor
        while True:
            store = self.__stores[self.__write_cursor]
            try:
                next = self.__write_cursor + 1
                if (next > len(self.__stores) - 1):
                    next = 0
                log.Log(_("MultiBackend: _put: write to store #%s (%s)")
                        % (self.__write_cursor, store.backend.parsed_url.url_string),
                        log.DEBUG)
                store.put(source_path, remote_filename)
                self.__write_cursor = next
                break
            except Exception as e:
                log.Log(_("MultiBackend: failed to write to store #%s (%s), try #%s, Exception: %s")
                        % (self.__write_cursor, store.backend.parsed_url.url_string, next, e),
                        log.INFO)
                self.__write_cursor = next

                if (self.__write_cursor == first):
                    log.Log(_("MultiBackend: failed to write %s. Tried all backing stores and none succeeded")
                            % (source_path),
                            log.ERROR)
                    raise BackendException("failed to write")

    def _get(self, remote_filename, local_path):
        # since the backend operations will be retried, we can't
        # simply try to get from the store, if not found, move to the
        # next store (since each failure will be retried n times
        # before finally giving up).  So we need to get the list first
        # before we try to fetch
        # ENHANCEME: maintain a cached list for each store
        for s in self.__stores:
            list = s.list()
            if remote_filename in list:
                s.get(remote_filename, local_path)
                return
            log.Log(_("MultiBackend: failed to get %s to %s from %s")
                    % (remote_filename, local_path, s.backend.parsed_url.url_string),
                    log.INFO)
        log.Log(_("MultiBackend: failed to get %s. Tried all backing stores and none succeeded")
                % (remote_filename),
                log.ERROR)
        raise BackendException("failed to get")

    def _list(self):
        lists = []
        for s in self.__stores:
            l = s.list()
            log.Log(_("MultiBackend: list from %s: %s")
                    % (s.backend.parsed_url.url_string, l),
                    log.DEBUG)
            lists.append(s.list())
        # combine the lists into a single flat list:
        result = [item for sublist in lists for item in sublist]
        log.Log(_("MultiBackend: combined list: %s")
                % (result),
                log.DEBUG)
        return result

    def _delete(self, filename):
        # since the backend operations will be retried, we can't
        # simply try to get from the store, if not found, move to the
        # next store (since each failure will be retried n times
        # before finally giving up).  So we need to get the list first
        # before we try to delete
        # ENHANCEME: maintain a cached list for each store
        for s in self.__stores:
            list = s.list()
            if filename in list:
                s._do_delete(filename)
                return
            log.Log(_("MultiBackend: failed to delete %s from %s")
                    % (filename, s.backend.parsed_url.url_string),
                    log.INFO)
        log.Log(_("MultiBackend: failed to delete %s. Tried all backing stores and none succeeded")
                % (filename),
                log.ERROR)
#        raise BackendException("failed to delete")

duplicity.backend.register_backend('multi', MultiBackend)

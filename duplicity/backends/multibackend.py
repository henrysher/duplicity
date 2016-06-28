# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2015 Steve Tynor <steve.tynor@gmail.com>
# Copyright 2016 Thomas Harning Jr <harningt@gmail.com>
#                  - mirror/stripe modes
#                  - write error modes
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
import urlparse
import json

import duplicity.backend
from duplicity.errors import BackendException
from duplicity import log


class MultiBackend(duplicity.backend.Backend):
    """Store files across multiple remote stores. URL is a path to a local file
    containing URLs/other config defining the remote store"""

    # the stores we are managing
    __stores = []

    # Set of known query paramaters
    __knownQueryParameters = frozenset([
        'mode',
        'onfail',
    ])

    # the mode of operation to follow
    # can be one of 'stripe' or 'mirror' currently
    __mode = 'stripe'
    __mode_allowedSet = frozenset([
        'mirror',
        'stripe',
    ])

    # the write error handling logic
    # can be one of the following:
    # * continue - default, on failure continues to next source
    # * abort - stop all further operations
    __onfail_mode = 'continue'
    __onfail_mode_allowedSet = frozenset([
        'abort',
        'continue',
    ])

    # when we write in stripe mode, we "stripe" via a simple round-robin across
    # remote stores.  It's hard to get too much more sophisticated
    # since we can't rely on the backend to give us any useful meta
    # data (e.g. sizes of files, capacity of the store (quotas)) to do
    # a better job of balancing load across stores.
    __write_cursor = 0

    @staticmethod
    def get_query_params(parsed_url):
        # Reparse so the query string is available
        reparsed_url = urlparse.urlparse(parsed_url.geturl())
        if len(reparsed_url.query) == 0:
            return dict()
        try:
            queryMultiDict = urlparse.parse_qs(reparsed_url.query, strict_parsing=True)
        except ValueError as e:
            log.Log(_("MultiBackend: Could not parse query string %s: %s ")
                    % (reparsed_url.query, e),
                    log.ERROR)
            raise BackendException('Could not parse query string')
        queryDict = dict()
        # Convert the multi-dict to a single dictionary
        # while checking to make sure that no unrecognized values are found
        for name, valueList in queryMultiDict.items():
            if len(valueList) != 1:
                log.Log(_("MultiBackend: Invalid query string %s: more than one value for %s")
                        % (reparsed_url.query, name),
                        log.ERROR)
                raise BackendException('Invalid query string')
            if name not in MultiBackend.__knownQueryParameters:
                log.Log(_("MultiBackend: Invalid query string %s: unknown parameter %s")
                        % (reparsed_url.query, name),
                        log.ERROR)
                raise BackendException('Invalid query string')

            queryDict[name] = valueList[0]
        return queryDict

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

        queryParams = MultiBackend.get_query_params(parsed_url)

        if 'mode' in queryParams:
            self.__mode = queryParams['mode']

        if 'onfail' in queryParams:
            self.__onfail_mode = queryParams['onfail']

        if self.__mode not in MultiBackend.__mode_allowedSet:
            log.Log(_("MultiBackend: illegal value for %s: %s")
                    % ('mode', self.__mode), log.ERROR)
            raise BackendException("MultiBackend: invalid mode value")

        if self.__onfail_mode not in MultiBackend.__onfail_mode_allowedSet:
            log.Log(_("MultiBackend: illegal value for %s: %s")
                    % ('onfail', self.__onfail_mode), log.ERROR)
            raise BackendException("MultiBackend: invalid onfail value")

        try:
            with open(parsed_url.path) as f:
                configs = json.load(f)
        except IOError as e:
            log.Log(_("MultiBackend: Url %s")
                    % (parsed_url.geturl()),
                    log.ERROR)

            log.Log(_("MultiBackend: Could not load config file %s: %s ")
                    % (parsed_url.path, e),
                    log.ERROR)
            raise BackendException('Could not load config file')

        for config in configs:
            url = config['url']
            # Fix advised in bug #1471795
            url = url.encode('utf-8')
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
        # Store an indication of whether any of these passed
        passed = False
        # Mirror mode always starts at zero
        if self.__mode == 'mirror':
            self.__write_cursor = 0

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
                passed = True
                self.__write_cursor = next
                # No matter what, if we loop around, break this loop
                if next == 0:
                    break
                # If in stripe mode, don't continue to the next
                if self.__mode == 'stripe':
                    break
            except Exception as e:
                log.Log(_("MultiBackend: failed to write to store #%s (%s), try #%s, Exception: %s")
                        % (self.__write_cursor, store.backend.parsed_url.url_string, next, e),
                        log.INFO)
                self.__write_cursor = next

                # If we consider write failure as abort, abort
                if self.__onfail_mode == 'abort':
                    log.Log(_("MultiBackend: failed to write %s. Aborting process.")
                            % (source_path),
                            log.ERROR)
                    raise BackendException("failed to write")

                # If we've looped around, and none of them passed, fail
                if (self.__write_cursor == first) and not passed:
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
        # combine the lists into a single flat list w/o duplicates via set:
        result = list({item for sublist in lists for item in sublist})
        log.Log(_("MultiBackend: combined list: %s")
                % (result),
                log.DEBUG)
        return result

    def _delete(self, filename):
        # Store an indication on whether any passed
        passed = False
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
                passed = True
                # In stripe mode, only one item will have the file
                if self.__mode == 'stripe':
                    return
            log.Log(_("MultiBackend: failed to delete %s from %s")
                    % (filename, s.backend.parsed_url.url_string),
                    log.INFO)
        if not passed:
            log.Log(_("MultiBackend: failed to delete %s. Tried all backing stores and none succeeded")
                    % (filename),
                    log.ERROR)
#           raise BackendException("failed to delete")

duplicity.backend.register_backend('multi', MultiBackend)

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

import os.path
import string
import urllib

import duplicity.backend
from duplicity.errors import BackendException
from duplicity import log

class MultiBackend(duplicity.backend.Backend):
    """Store files across multiple remote stores. URL is a path to a local file containing URLs defining the remote store"""

    # the stores we are managing
    __stores = []

    # when we write, we "stripe" via a simple round-robin across remote
    # stores.  It's hard to get too much more sophisticated since we
    # can't rely on the backend to give us any useful meta data
    # (e.g. sizes of files) to do a better job of balancing load
    # across stores.
    __write_cursor = 0

    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        
        # Init each of the wrapped stores
	    filename = parsed_url.path
        # URL is path to config file, contaning one url per line to describe each remote
        urls = [line.rstrip('\n') for line in open(filename)]

        for url in urls:            
            log.Log(_("MultiBackend: use store %s")
                    % (url),
                    log.INFO)
            store = duplicity.backend.get_backend(url)
        	self.__stores.append(store)
            store_list = store.list()
            log.Log(_("MultiBackend: at init, store %s has %s files")
                    % (url, len(store_list)),
                    log.INFO)
    
    def _put(self, source_path, remote_filename):
        first = self.__write_cursor
        while True:
            store = self.__stores[self.__write_cursor]
            try:
                next = self.__write_cursor + 1;
                if (next > len(self.__stores) -1):
                    next = 0
                log.Log(_("MultiBackend: _put: write to store #%s (%s)")
                        % (self.__write_cursor, store),
                        log.DEBUG)
                store.put(source_path, remote_filename)
                self.__write_cursor = next
                break
            except Exception, e:            
                log.Log(_("MultiBackend: failed to write to store #%s (%s), try #%s, Exception: %s")
                        % (self.__write_cursor, store, next, e),
                        log.INFO)
                self.__write_cursor = next

                if (self.__write_cursor == first):
                    log.Log(_("MultiBackend: failed to write %s. Tried all backing stores and none succeeded")
                            % (source_path),
                            log.ERROR)
                    raise BackendException("failed to write");
    
    def _get(self, remote_filename, local_path):
        for s in self.__stores:
            try:
                s.get(remote_filename, local_path)
                return
            except Exception, e:
                log.Log(_("MultiBackend: failed to get %s to %s from %s")
                        % (remote_filename, local_path, s),
                        log.INFO)
        log.Log(_("MultiBackend: failed to get %s. Tried all backing stores and none succeeded")
                % (remote_filename),
                log.ERROR)
        raise BackendException("failed to get")

    def _list(self):
        lists = []
        for s in self.__stores:
            lists.append(s.list())
        # combine the lists into a single flat list:
        return [item for sublist in lists for item in sublist]

    def _delete(self, filename):
        for s in self.__stores:
            try:
                s.delete(filename)
                return
            except Exception, e:
                log.Log(_("MultiBackend: failed to delete %s from %s")
                        % (filename, s),
                        log.INFO)
        log.Log(_("MultiBackend: failed to delete %s. Tried all backing stores and none succeeded")
                % (filename),
                log.ERROR)
        raise BackendException("failed to delete")
    
duplicity.backend.register_backend('multi', MultiBackend)


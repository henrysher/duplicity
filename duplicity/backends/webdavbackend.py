# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
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

import base64
import httplib
import re
import urllib
import xml.dom.minidom

import duplicity.backend
import duplicity.globals as globals
import duplicity.log as log
from duplicity.errors import *

class WebDAVBackend(duplicity.backend.Backend):
    """Backend for accessing a WebDAV repository.

    webdav backend contributed in 2006 by Jesper Zedlitz <jesper@zedlitz.de>
    """
    listbody = """\
<?xml version="1.0" encoding="utf-8" ?>
<D:propfind xmlns:D="DAV:">
<D:allprop/>
</D:propfind>

"""

    """Connect to remote store using WebDAV Protocol"""
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        self.headers = {}
        self.parsed_url = parsed_url


        if parsed_url.path:
            foldpath = re.compile('/+')
            self.directory = foldpath.sub('/', parsed_url.path + '/' )
        else:
            self.directory = '/'

        log.Log("Using WebDAV host %s" % (parsed_url.hostname,), 5)
        log.Log("Using WebDAV directory %s" % (self.directory,), 5)
        log.Log("Using WebDAV protocol %s" % (globals.webdav_proto,), 5)

        password = self.get_password()

        if parsed_url.scheme == 'webdav':
            self.conn = httplib.HTTPConnection(parsed_url.hostname)
        elif parsed_url.scheme == 'webdavs':
            self.conn = httplib.HTTPSConnection(parsed_url.hostname)
        else:
            raise BackendException("Unknown URI scheme: %s" % (parsed_url.scheme))

        self.headers['Authorization'] = 'Basic ' + base64.encodestring(parsed_url.username+':'+ password).strip()

        # check password by connection to the server
        self.conn.request("OPTIONS", self.directory, None, self.headers)
        response = self.conn.getresponse()
        response.read()
        if response.status !=  200:
            raise BackendException((response.status, response.reason))

    def _getText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def close(self):
        self.conn.close()

    def list(self):
        """List files in directory"""
        for n in range(1, globals.num_retries+1):
            log.Log("Listing directory %s on WebDAV server" % (self.directory,), 5)
            self.headers['Depth'] = "1"
            self.conn.request("PROPFIND", self.directory, self.listbody, self.headers)
            del self.headers['Depth']
            response = self.conn.getresponse()
            if response.status == 207:
                document = response.read()
                break
            log.Log("WebDAV PROPFIND attempt #%d failed: %s %s" % (n, response.status, response.reason), 5)
            if n == globals.num_retries +1:
                log.Log("WebDAV backend giving up after %d attempts to PROPFIND %s" % (globals.num_retries, self.directory), 1)
                raise BackendException((response.status, response.reason))

        log.Log("%s" % (document,), 6)
        dom = xml.dom.minidom.parseString(document)
        result = []
        for href in dom.getElementsByTagName('D:href'):
            filename = self.__taste_href(href)
            if not filename is None:
                result.append(filename)
        return result

    def __taste_href(self, href):
        """
        Internal helper to taste the given href node and, if
        it is a duplicity file, collect it as a result file.

        @returns A matching filename, or None if the href did
                 not match.
        """
        raw_filename = self._getText(href.childNodes).strip()
        parsed_url = urlparser.urlparse(urllib.unquote(raw_filename))
        filename = parsed_url.path
        log.Debug("webdav path decoding and translation: "
                  "%s -> %s" % (raw_filename, filename))

        # at least one WebDAV server returns files in the form
        # of full URL:s. this may or may not be
        # according to the standard, but regardless we
        # feel we want to bail out if the hostname
        # does not match until someone has looked into
        # what the WebDAV protocol mandages.
        if not parsed_url.hostname is None \
           and not (parsed_url.hostname == self.parsed_url.hostname):
            m = "Received filename was in the form of a "\
                "full url, but the hostname (%s) did "\
                "not match that of the webdav backend "\
                "url (%s) - aborting as a conservative "\
                "safety measure. If this happens to you, "\
                "please report the problem"\
                "" % (parsed_url.hostname,
                      self.parsed_url.hostname)
            raise BackendException(m)

        if filename.startswith(self.directory):
            filename = filename.replace(self.directory,'',1)
            return filename
        else:
            return None

    def get(self, remote_filename, local_path):
        """Get remote filename, saving it to local_path"""
        url = self.directory + remote_filename
        target_file = local_path.open("wb")
        for n in range(1, globals.num_retries+1):
            log.Log("Retrieving %s from WebDAV server" % (url ,), 5)
            self.conn.request("GET", url, None, self.headers)
            response = self.conn.getresponse()		
            if response.status == 200:
                target_file.write(response.read())
                assert not target_file.close()
                local_path.setdata()
                return
            log.Log("WebDAV GET attempt #%d failed: %s %s" % (n, response.status, response.reason), 5)
        log.Log("WebDAV backend giving up after %d attempts to GET %s" % (globals.num_retries, url), 1)
        raise BackendException((response.status, response.reason))

    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        if not remote_filename: 
            remote_filename = source_path.get_filename()
        url = self.directory + remote_filename
        source_file = source_path.open("rb")
        for n in range(1, globals.num_retries+1):
            log.Log("Saving %s on WebDAV server" % (url ,), 5)
            self.conn.request("PUT", url, source_file.read(), self.headers)
            response = self.conn.getresponse()
            if response.status == 201:
                response.read()
                assert not source_file.close()
                return
            log.Log("WebDAV PUT attempt #%d failed: %s %s" % (n, response.status, response.reason), 5)
        log.Log("WebDAV backend giving up after %d attempts to PUT %s" % (globals.num_retries, url), 1)
        raise BackendException((response.status, response.reason))

    def delete(self, filename_list):
        """Delete files in filename_list"""
        for filename in filename_list:
            url = self.directory + filename
            for n in range(1, globals.num_retries+1):
                log.Log("Deleting %s from WebDAV server" % (url ,), 5)
                self.conn.request("DELETE", url, None, self.headers)
                response = self.conn.getresponse()
                if response.status == 204:
                    response.read()
                    break
                log.Log("WebDAV DELETE attempt #%d failed: %s %s" % (n, response.status, response.reason), 5)
                if n == globals.num_retries +1:
                    log.Log("WebDAV backend giving up after %d attempts to DELETE %s" % (globals.num_retries, url), 1)
                    raise BackendException((response.status, response.reason))

duplicity.backend.register_backend("webdav", WebDAVBackend)
duplicity.backend.register_backend("webdavs", WebDAVBackend)

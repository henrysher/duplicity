# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
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

import base64
import httplib
import re
import urllib
import urllib2
import xml.dom.minidom

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport
from duplicity import urlparse_2_5 as urlparser

class CustomMethodRequest(urllib2.Request):
    """
    This request subclass allows explicit specification of
    the HTTP request method. Basic urllib2.Request class
    chooses GET or POST depending on self.has_data()
    """
    def __init__(self, method, *args, **kwargs):
        self.method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self.method


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
        self.headers = {'Connection': 'keep-alive'}
        self.parsed_url = parsed_url
        self.digest_challenge = None
        self.digest_auth_handler = None

        if parsed_url.path:
            foldpath = re.compile('/+')
            self.directory = foldpath.sub('/', parsed_url.path + '/' )
        else:
            self.directory = '/'

        log.Info("Using WebDAV host %s" % (parsed_url.hostname,))
        log.Info("Using WebDAV directory %s" % (self.directory,))
        log.Info("Using WebDAV protocol %s" % (globals.webdav_proto,))

        if parsed_url.scheme == 'webdav':
            self.conn = httplib.HTTPConnection(parsed_url.hostname)
        elif parsed_url.scheme == 'webdavs':
            self.conn = httplib.HTTPSConnection(parsed_url.hostname)
        else:
            raise BackendException("Unknown URI scheme: %s" % (parsed_url.scheme))

    def _getText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def close(self):
        self.conn.close()

    def request(self, method, path, data=None):
        """
        Wraps the connection.request method to retry once if authentication is
        required
        """
        quoted_path = urllib.quote(path)

        if self.digest_challenge is not None:
            self.headers['Authorization'] = self.get_digest_authorization(path)
        self.conn.request(method, quoted_path, data, self.headers)
        response = self.conn.getresponse()
        if response.status == 401:
            response.close()
            self.headers['Authorization'] = self.get_authorization(response, quoted_path)
            self.conn.request(method, quoted_path, data, self.headers)
            response = self.conn.getresponse()

        return response

    def get_authorization(self, response, path):
        """
        Fetches the auth header based on the requested method (basic or digest)
        """
        try:
            auth_hdr = response.getheader('www-authenticate', '')
            token, challenge = auth_hdr.split(' ', 1)
        except ValueError:
            return None
        if token.lower() == 'basic':
            return self.get_basic_authorization()
        else:
            self.digest_challenge = self.parse_digest_challenge(challenge)
            return self.get_digest_authorization(path)

    def parse_digest_challenge(self, challenge_string):
        return urllib2.parse_keqv_list(urllib2.parse_http_list(challenge_string))

    def get_basic_authorization(self):
        """
        Returns the basic auth header
        """
        auth_string = '%s:%s' % (self.parsed_url.username, self.get_password())
        return 'Basic %s' % base64.encodestring(auth_string).strip()

    def get_digest_authorization(self, path):
        """
        Returns the digest auth header
        """
        u = self.parsed_url
        if self.digest_auth_handler is None:
            pw_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            pw_manager.add_password(None, self.conn.host, u.username, self.get_password())
            self.digest_auth_handler = urllib2.HTTPDigestAuthHandler(pw_manager)

        # building a dummy request that gets never sent,
        # needed for call to auth_handler.get_authorization
        scheme = u.scheme == 'webdavs' and 'https' or 'http'
        hostname = u.port and "%s:%s" % (u.hostname, u.port) or u.hostname
        dummy_url = "%s://%s%s" % (scheme, hostname, path)
        dummy_req = CustomMethodRequest(self.conn._method, dummy_url)
        auth_string = self.digest_auth_handler.get_authorization(dummy_req, self.digest_challenge)
        return 'Digest %s' % auth_string

    def list(self):
        """List files in directory"""
        for n in range(1, globals.num_retries+1):
            log.Info("Listing directory %s on WebDAV server" % (self.directory,))
            self.headers['Depth'] = "1"
            response = self.request("PROPFIND", self.directory, self.listbody)
            del self.headers['Depth']
            # if the target collection does not exist, create it.
            if response.status == 404:
                log.Info("Directory '%s' being created." % self.directory)
                res = self.request("MKCOL", self.directory)
                log.Info("WebDAV MKCOL status: %s %s" % (res.status, res.reason))
                continue
            if response.status == 207:
                document = response.read()
                break
            log.Info("WebDAV PROPFIND attempt #%d failed: %s %s" % (n, response.status, response.reason))
            if n == globals.num_retries +1:
                log.Warn("WebDAV backend giving up after %d attempts to PROPFIND %s" % (globals.num_retries, self.directory))
                raise BackendException((response.status, response.reason))

        log.Info("%s" % (document,))
        dom = xml.dom.minidom.parseString(document)
        result = []
        for href in dom.getElementsByTagName('D:href'):
            filename = self.__taste_href(href)
            if filename:
                result.append(filename)
        return result

    def __taste_href(self, href):
        """
        Internal helper to taste the given href node and, if
        it is a duplicity file, collect it as a result file.

        @return: A matching filename, or None if the href did not match.
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
            log.Info("Retrieving %s from WebDAV server" % (url ,))
            response = self.request("GET", url)
            if response.status == 200:
                target_file.write(response.read())
                assert not target_file.close()
                local_path.setdata()
                return
            log.Info("WebDAV GET attempt #%d failed: %s %s" % (n, response.status, response.reason))
        log.Warn("WebDAV backend giving up after %d attempts to GET %s" % (globals.num_retries, url))
        raise BackendException((response.status, response.reason))

    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        url = self.directory + remote_filename
        source_file = source_path.open("rb")
        for n in range(1, globals.num_retries+1):
            log.Info("Saving %s on WebDAV server" % (url ,))
            response = self.request("PUT", url, source_file.read())
            if response.status == 201:
                response.read()
                assert not source_file.close()
                return
            log.Info("WebDAV PUT attempt #%d failed: %s %s" % (n, response.status, response.reason))
        log.Warn("WebDAV backend giving up after %d attempts to PUT %s" % (globals.num_retries, url))
        raise BackendException((response.status, response.reason))

    def delete(self, filename_list):
        """Delete files in filename_list"""
        for filename in filename_list:
            url = self.directory + filename
            for n in range(1, globals.num_retries+1):
                log.Info("Deleting %s from WebDAV server" % (url ,))
                response = self.request("DELETE", url)
                if response.status == 204:
                    response.read()
                    break
                log.Info("WebDAV DELETE attempt #%d failed: %s %s" % (n, response.status, response.reason))
                if n == globals.num_retries +1:
                    log.Warn("WebDAV backend giving up after %d attempts to DELETE %s" % (globals.num_retries, url))
                    raise BackendException((response.status, response.reason))

duplicity.backend.register_backend("webdav", WebDAVBackend)
duplicity.backend.register_backend("webdavs", WebDAVBackend)

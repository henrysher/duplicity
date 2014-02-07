# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2013 Edgar Soldin
#                 - ssl cert verification, some robustness enhancements
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
import httplib, os
import re
import urllib
import urllib2
import xml.dom.minidom

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport
from duplicity import urlparse_2_5 as urlparser
from duplicity.backend import retry_fatal

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

class VerifiedHTTPSConnection(httplib.HTTPSConnection):
        def __init__(self, *args, **kwargs):
            try:
                global socket, ssl
                import socket, ssl
            except ImportError:
                raise FatalBackendError("Missing socket or ssl libraries.")
            
            httplib.HTTPSConnection.__init__(self, *args, **kwargs)
            
            self.cacert_file = globals.ssl_cacert_file
            cacert_candidates = [ "~/.duplicity/cacert.pem", \
                             "~/duplicity_cacert.pem", \
                             "/etc/duplicity/cacert.pem" ]
            # 
            if not self.cacert_file:
                for path in cacert_candidates :
                    path = os.path.expanduser(path)
                    if (os.path.isfile(path)):
                        self.cacert_file = path
                        break
            # still no cacert file, inform user
            if not self.cacert_file:
                raise FatalBackendError("""For certificate verification a cacert database file is needed in one of these locations: %s
Hints: 
  Consult the man page, chapter 'SSL Certificate Verification'. 
  Consider using the options --ssl-cacert-file, --ssl-no-check-certificate .""" % ", ".join(cacert_candidates) )
            # check if file is accessible (libssl errors are not very detailed)
            if not os.access(self.cacert_file, os.R_OK):
                raise FatalBackendError("Cacert database file '%s' is not readable." % cacert_file)

        def connect(self):
            # create new socket
            sock = socket.create_connection((self.host, self.port),
                                            self.timeout)
            if self._tunnel_host:
                self.sock = sock
                self._tunnel()

            # wrap the socket in ssl using verification
            self.sock = ssl.wrap_socket(sock,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ca_certs=self.cacert_file,
                                        )
        
        def request(self, *args, **kwargs):
            try:
                return httplib.HTTPSConnection.request(self, *args, **kwargs)
            except ssl.SSLError, e:
                # encapsulate ssl errors
                raise BackendException("SSL failed: %s" % str(e),log.ErrorCode.backend_error)


class WebDAVBackend(duplicity.backend.Backend):
    """Backend for accessing a WebDAV repository.

    webdav backend contributed in 2006 by Jesper Zedlitz <jesper@zedlitz.de>
    """

    """
    for better compatibility we send an empty listbody as described in
    http://www.ietf.org/rfc/rfc4918.txt
    "  A client may choose not to submit a request body.  An empty PROPFIND
       request body MUST be treated as if it were an 'allprop' request.  "
    it was retired because e.g. box.net didn't support <D:allprop/>
    """
    listbody =""

    """Connect to remote store using WebDAV Protocol"""
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        self.headers = {'Connection': 'keep-alive'}
        self.parsed_url = parsed_url
        self.digest_challenge = None
        self.digest_auth_handler = None

        self.username = parsed_url.username
        self.password = self.get_password()
        self.directory = self._sanitize_path(parsed_url.path)

        log.Info("Using WebDAV protocol %s" % (globals.webdav_proto,))
        log.Info("Using WebDAV host %s port %s" % (parsed_url.hostname, parsed_url.port))
        log.Info("Using WebDAV directory %s" % (self.directory,))

        self.conn = None

    def _sanitize_path(self,path):
        if path:
            foldpath = re.compile('/+')
            return foldpath.sub('/', path + '/' )
        else:
            return '/'

    def _getText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    
    def _connect(self, forced=False):
        """
        Connect or re-connect to the server, updates self.conn
        # reconnect on errors as a precaution, there are errors e.g. 
        # "[Errno 32] Broken pipe" or SSl errors that render the connection unusable
        """
        if self.retry_count<=1 and self.conn \
            and self.conn.host == self.parsed_url.hostname: return
        
        log.Info("WebDAV create connection on '%s' (retry %s) " % (self.parsed_url.hostname,self.retry_count) )
        if self.conn: self.conn.close()
        # http schemes needed for redirect urls from servers
        if self.parsed_url.scheme in ['webdav','http']:
            self.conn = httplib.HTTPConnection(self.parsed_url.hostname, self.parsed_url.port)
        elif self.parsed_url.scheme in ['webdavs','https']:
            if globals.ssl_no_check_certificate:
                self.conn = httplib.HTTPSConnection(self.parsed_url.hostname, self.parsed_url.port)
            else:
                self.conn = VerifiedHTTPSConnection(self.parsed_url.hostname, self.parsed_url.port)
        else:
            raise FatalBackendError("WebDAV Unknown URI scheme: %s" % (self.parsed_url.scheme))

    def close(self):
        self.conn.close()

    def request(self, method, path, data=None, redirected=0):
        """
        Wraps the connection.request method to retry once if authentication is
        required
        """
        self._connect()

        quoted_path = urllib.quote(path,"/:~")

        if self.digest_challenge is not None:
            self.headers['Authorization'] = self.get_digest_authorization(path)

        log.Info("WebDAV %s %s request with headers: %s " % (method,quoted_path,self.headers))
        log.Info("WebDAV data length: %s " % len(str(data)) )
        self.conn.request(method, quoted_path, data, self.headers)
        response = self.conn.getresponse()
        log.Info("WebDAV response status %s with reason '%s'." % (response.status,response.reason))
        # resolve redirects and reset url on listing requests (they usually come before everything else)
        if response.status in [301,302] and method == 'PROPFIND':
            redirect_url = response.getheader('location',None)
            response.close()
            if redirect_url:
                log.Notice("WebDAV redirect to: %s " % urllib.unquote(redirect_url) )
                if redirected > 10:
                    raise FatalBackendError("WebDAV redirected 10 times. Giving up.")
                self.parsed_url = duplicity.backend.ParsedUrl(redirect_url)
                self.directory = self._sanitize_path(self.parsed_url.path)
                return self.request(method,self.directory,data,redirected+1)
            else:
                raise FatalBackendError("WebDAV missing location header in redirect response.")
        elif response.status == 401:
            response.close()
            self.headers['Authorization'] = self.get_authorization(response, quoted_path)
            log.Info("WebDAV retry request with authentification headers.")
            log.Info("WebDAV %s %s request2 with headers: %s " % (method,quoted_path,self.headers))
            log.Info("WebDAV data length: %s " % len(str(data)) )
            self.conn.request(method, quoted_path, data, self.headers)
            response = self.conn.getresponse()
            log.Info("WebDAV response2 status %s with reason '%s'." % (response.status,response.reason))
        
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
        auth_string = '%s:%s' % (self.username, self.password)
        return 'Basic %s' % base64.encodestring(auth_string).strip()

    def get_digest_authorization(self, path):
        """
        Returns the digest auth header
        """
        u = self.parsed_url
        if self.digest_auth_handler is None:
            pw_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            pw_manager.add_password(None, self.conn.host, self.username, self.password)
            self.digest_auth_handler = urllib2.HTTPDigestAuthHandler(pw_manager)

        # building a dummy request that gets never sent,
        # needed for call to auth_handler.get_authorization
        scheme = u.scheme == 'webdavs' and 'https' or 'http'
        hostname = u.port and "%s:%s" % (u.hostname, u.port) or u.hostname
        dummy_url = "%s://%s%s" % (scheme, hostname, path)
        dummy_req = CustomMethodRequest(self.conn._method, dummy_url)
        auth_string = self.digest_auth_handler.get_authorization(dummy_req, self.digest_challenge)
        return 'Digest %s' % auth_string

    @retry_fatal
    def _list(self):
        """List files in directory"""
        log.Info("Listing directory %s on WebDAV server" % (self.directory,))
        response = None
        try:
            self.headers['Depth'] = "1"
            response = self.request("PROPFIND", self.directory, self.listbody)
            del self.headers['Depth']
            # if the target collection does not exist, create it.
            if response.status == 404:
                response.close() # otherwise next request fails with ResponseNotReady
                self.makedir()
                # just created an empty folder, so return empty
                return []
            elif response.status in [200, 207]:
                document = response.read()
                response.close()
            else:
                status = response.status
                reason = response.reason
                response.close()
                raise BackendException("Bad status code %s reason %s." % (status,reason))

            log.Debug("%s" % (document,))
            dom = xml.dom.minidom.parseString(document)
            result = []
            for href in dom.getElementsByTagName('d:href') + dom.getElementsByTagName('D:href'):
                filename = self.__taste_href(href)
                if filename:
                    result.append(filename)
            return result
        except Exception, e:
            raise e
        finally:
            if response: response.close()

    def makedir(self):
        """Make (nested) directories on the server."""
        dirs = self.directory.split("/")
        # url causes directory to start with /, but it might be given 
        # with or without trailing / (which is required)
        if dirs[-1] == '':
            dirs=dirs[0:-1]
        for i in range(1,len(dirs)):
            d="/".join(dirs[0:i+1])+"/"
       
            self.close() # or we get previous request's data or exception       
            self.headers['Depth'] = "1"
            response = self.request("PROPFIND", d)
            del self.headers['Depth']

            log.Info("Checking existence dir %s: %d" % (d, response.status))

            if response.status == 404:
                log.Info("Creating missing directory %s" % d)
                self.close() # or we get previous request's data or exception   

                res = self.request("MKCOL", d)
                if res.status != 201:
                    raise BackendException("WebDAV MKCOL %s failed: %s %s" % (d,res.status,res.reason))
                self.close()

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

    @retry_fatal
    def get(self, remote_filename, local_path):
        """Get remote filename, saving it to local_path"""
        url = self.directory + remote_filename
        log.Info("Retrieving %s from WebDAV server" % (url ,))
        response = None
        try:
            target_file = local_path.open("wb")
            response = self.request("GET", url)
            if response.status == 200:
                #data=response.read()
                target_file.write(response.read())
                #import hashlib
                #log.Info("WebDAV GOT %s bytes with md5=%s" % (len(data),hashlib.md5(data).hexdigest()) )
                assert not target_file.close()
                local_path.setdata()
                response.close()
            else:
                status = response.status
                reason = response.reason
                response.close()
                raise BackendException("Bad status code %s reason %s." % (status,reason))
        except Exception, e:
            raise e
        finally:
            if response: response.close()

    @retry_fatal
    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        url = self.directory + remote_filename
        log.Info("Saving %s on WebDAV server" % (url ,))
        response = None
        try:
            source_file = source_path.open("rb")
            response = self.request("PUT", url, source_file.read())
            if response.status in [201, 204]:
                response.read()
                response.close()
            else:
                status = response.status
                reason = response.reason
                response.close()
                raise BackendException("Bad status code %s reason %s." % (status,reason))
        except Exception, e:
            raise e
        finally:
            if response: response.close()

    @retry_fatal
    def delete(self, filename_list):
        """Delete files in filename_list"""
        for filename in filename_list:
            url = self.directory + filename
            log.Info("Deleting %s from WebDAV server" % (url ,))
            response = None
            try:
                response = self.request("DELETE", url)
                if response.status == 204:
                    response.read()
                    response.close()
                else:
                    status = response.status
                    reason = response.reason
                    response.close()
                    raise BackendException("Bad status code %s reason %s." % (status,reason))
            except Exception, e:
                raise e
            finally:
                if response: response.close()

duplicity.backend.register_backend("webdav", WebDAVBackend)
duplicity.backend.register_backend("webdavs", WebDAVBackend)

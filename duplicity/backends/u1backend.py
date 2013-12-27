# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2011 Canonical Ltd
# Authors: Michael Terry <michael.terry@canonical.com>
#          Alexander Zangerl <az@debian.org>
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
# along with duplicity.  If not, see <http://www.gnu.org/licenses/>.

import duplicity.backend
from duplicity.errors import BackendException
from duplicity import log
from duplicity import globals

from urlparse import urlparse, parse_qsl
from json import loads, dumps
# python3 splitted urllib
try:
    import urllib
except ImportError:
    import urllib.request as urllib
import getpass
import os
import sys
import time

class OAuthHttpClient(object):
    """a simple HTTP client with OAuth added on"""
    def __init__(self):
        # lazily import non standard python libs
        global oauth1, Http
        from oauthlib import oauth1
        from httplib2 import Http

        self.consumer_key = None
        self.consumer_secret = None
        self.token = None
        self.token_secret = None
        self.client = Http()

    def set_consumer(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def set_token(self, token, token_secret):
        self.token = token
        self.token_secret = token_secret

    def _get_oauth_request_header(self, url, method):
        """Get an oauth request header given the token and the url"""
        client = oauth1.Client(
            unicode(self.consumer_key),
            client_secret=unicode(self.consumer_secret),
            resource_owner_key=unicode(self.token),
            resource_owner_secret=unicode(self.token_secret))
        url, headers, body = client.sign(
            unicode(url),
            http_method=unicode(method))
        return [url, headers]

    def request(self, url, method="GET", body=None, headers={}, ignore=None):
        url, oauth_header = self._get_oauth_request_header(url, method)
        headers.update(oauth_header)

        for n in range(1, globals.num_retries+1):
            log.Info("making %s request to %s (attempt %d)" % (method,url,n))
            try:
                resp, content = self.client.request(url, method, headers=headers, body=body)
            except Exception, e:
                log.Info("request failed, exception %s" % e);
                log.Debug("Backtrace of previous error: %s"
                          % duplicity.util.exception_traceback())
                if n == globals.num_retries:
                    log.FatalError("Giving up on request after %d attempts, last exception %s" % (n,e))

                if isinstance(body, file):
                    body.seek(0) # Go to the beginning of the file for the retry

                time.sleep(30)
                continue

            log.Info("completed request with status %s %s" % (resp.status,resp.reason))
            oops_id = resp.get('x-oops-id', None)
            if oops_id:
                log.Debug("Server Error: method %s url %s Oops-ID %s" % (method, url, oops_id))

            if resp['content-type'] == 'application/json':
                content = loads(content)

            # were we successful? status either 2xx or code we're told to ignore
            numcode=int(resp.status)
            if (numcode>=200 and numcode<300) or (ignore and numcode in ignore):
                return resp, content

            ecode = log.ErrorCode.backend_error
            if numcode == 402:  # Payment Required
                ecode = log.ErrorCode.backend_no_space
            elif numcode == 404:
                ecode = log.ErrorCode.backend_not_found

            if isinstance(body, file):
                body.seek(0) # Go to the beginning of the file for the retry

            if n < globals.num_retries:
                time.sleep(30)

        log.FatalError("Giving up on request after %d attempts, last status %d %s" % (n,numcode,resp.reason),
                       ecode)


    def get_and_set_token(self,email, password, hostname):
        """Acquire an Ubuntu One access token via OAuth with the Ubuntu SSO service.
        See https://one.ubuntu.com/developer/account_admin/auth/otherplatforms for details.
        """

        # Request new access token from the Ubuntu SSO service
        self.client.add_credentials(email,password)
        resp, content = self.client.request('https://login.ubuntu.com/api/1.0/authentications?'
                                            +'ws.op=authenticate&token_name=Ubuntu%%20One%%20@%%20%s' % hostname)
        if resp.status!=200:
            log.FatalError("Token request failed: Incorrect Ubuntu One credentials",log.ErrorCode.backend_permission_denied)
            self.client.clear_credentials()

        tokendata=loads(content)
        self.set_consumer(tokendata['consumer_key'],tokendata['consumer_secret'])
        self.set_token(tokendata['token'],tokendata['token_secret'])

        # and finally tell Ubuntu One about the token
        resp, content = self.request('https://one.ubuntu.com/oauth/sso-finished-so-get-tokens/')
        if resp.status!=200:
            log.FatalError("Ubuntu One token was not accepted: %s %s" % (resp.status,resp.reason))

        return tokendata

class U1Backend(duplicity.backend.Backend):
    """
    Backend for Ubuntu One, through the use of the REST API.
    See https://one.ubuntu.com/developer/ for REST documentation.
    """
    def __init__(self, url):
        duplicity.backend.Backend.__init__(self, url)

        # u1://dontcare/volname or u1+http:///volname
        path = self.parsed_url.path.lstrip('/')

        self.api_base = "https://one.ubuntu.com/api/file_storage/v1"
        self.content_base = "https://files.one.ubuntu.com"

        self.volume_uri = "%s/volumes/~/%s" % (self.api_base, path)
        self.meta_base = "%s/~/%s/" % (self.api_base, path)

        self.client=OAuthHttpClient();

        if 'FTP_PASSWORD' not in os.environ:
            sys.stderr.write("No Ubuntu One token found in $FTP_PASSWORD, requesting a new one\n")
            email=raw_input('Enter Ubuntu One account email: ')
            password=getpass.getpass("Enter Ubuntu One password: ")
            hostname=os.uname()[1]

            tokendata = self.client.get_and_set_token(email, password, hostname)
            tokenstring = "%s:%s:%s:%s" % (tokendata['consumer_key'], tokendata['consumer_secret'],
                                tokendata['token'], tokendata['token_secret'])
            sys.stderr.write("\nPlease record your new Ubuntu One access token for future use with duplicity:\n"
                             + "FTP_PASSWORD=%s\n\n" % tokenstring)
            os.environ['FTP_PASSWORD'] = tokenstring

        (consumer,consumer_secret,token,token_secret) = os.environ['FTP_PASSWORD'].split(':')
        self.client.set_consumer(consumer, consumer_secret)
        self.client.set_token(token, token_secret)

        resp, content = self.client.request(self.api_base,ignore=[400,401,403])
        if resp['status']!='200':
           log.FatalError("Access failed: Ubuntu One credentials incorrect",
                           log.ErrorCode.user_error)

        # Create volume, but check existence first
        resp, content = self.client.request(self.volume_uri,ignore=[404])
        if resp['status']=='404':
            resp, content = self.client.request(self.volume_uri,"PUT")

    def quote(self, url):
        return urllib.quote(url, safe="/~").replace(" ","%20")

    def put(self, source_path, remote_filename = None):
        """Copy file to remote"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        remote_full = self.meta_base + self.quote(remote_filename)
        # check if it exists already, returns existing content_path
        resp, content = self.client.request(remote_full,ignore=[404])
        if resp['status']=='404':
            # put with path returns new content_path
            resp, content = self.client.request(remote_full,
                                                method="PUT",
                                                headers = { 'content-type': 'application/json' },
                                                body=dumps({"kind":"file"}))
        elif resp['status']!='200':
            raise BackendException("access to %s failed, code %s" % (remote_filename, resp['status']))

        assert(content['content_path'] is not None)
        # content_path allows put of the actual material
        remote_full = self.content_base + self.quote(content['content_path'])
        log.Info("uploading file %s to location %s" % (remote_filename, remote_full))

        size = os.path.getsize(source_path.name)
        fh=open(source_path.name,'rb')

        content_type = 'application/octet-stream'
        headers = {"Content-Length": str(size),
                   "Content-Type": content_type}
        resp, content = self.client.request(remote_full,
                                            method="PUT",
                                            body=fh,
                                            headers=headers)
        fh.close()

    def get(self, filename, local_path):
        """Get file and put in local_path (Path object)"""

        # get with path returns content_path
        remote_full = self.meta_base + self.quote(filename)
        resp, content = self.client.request(remote_full)

        assert(content['content_path'] is not None)
        # now we have content_path to access the actual material
        remote_full = self.content_base + self.quote(content['content_path'])
        log.Info("retrieving file %s from location %s" % (filename, remote_full))
        resp, content = self.client.request(remote_full)

        f = open(local_path.name, 'wb')
        f.write(content)
        f.close()
        local_path.setdata()

    def _list(self):
        """List files in that directory"""
        remote_full = self.meta_base + "?include_children=true"
        resp, content = self.client.request(remote_full)

        filelist = []
        if 'children' in content:
            for child in content['children']:
                path = urllib.unquote(child['path'].lstrip('/'))
                filelist += [path.encode('utf-8')]
        return filelist

    def delete(self, filename_list):
        """Delete all files in filename list"""
        import types
        assert type(filename_list) is not types.StringType

        for filename in filename_list:
            remote_full = self.meta_base + self.quote(filename)
            resp, content = self.client.request(remote_full,method="DELETE")

    def _query_file_info(self, filename):
        """Query attributes on filename"""
        remote_full = self.meta_base + self.quote(filename)
        resp, content = self.client.request(remote_full)

        size = content['size']
        return {'size': size}

duplicity.backend.register_backend("u1", U1Backend)
duplicity.backend.register_backend("u1+http", U1Backend)

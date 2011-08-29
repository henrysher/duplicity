# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2011 Canonical Ltd
# Authors: Michael Terry <michael.terry@canonical.com>
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
from duplicity.backend import retry
from duplicity.errors import BackendException, TemporaryLoadException

def ensure_dbus():
    # GIO requires a dbus session bus which can start the gvfs daemons
    # when required.  So we make sure that such a bus exists and that our
    # environment points to it.
    import atexit
    import os
    import subprocess
    import signal
    if 'DBUS_SESSION_BUS_ADDRESS' not in os.environ:
        output = subprocess.Popen(['dbus-launch'], stdout=subprocess.PIPE).communicate()[0]
        lines = output.split('\n')
        for line in lines:
            parts = line.split('=', 1)
            if len(parts) == 2:
                if parts[0] == 'DBUS_SESSION_BUS_PID': # cleanup at end
                    atexit.register(os.kill, int(parts[1]), signal.SIGTERM)
                os.environ[parts[0]] = parts[1]

class U1Backend(duplicity.backend.Backend):
    """
    Backend for Ubuntu One, through the use of the ubuntone module and a REST
    API.  See https://one.ubuntu.com/developer/ for REST documentation.
    """
    def __init__(self, url):
        duplicity.backend.Backend.__init__(self, url)

        if self.parsed_url.scheme == 'u1+http':
            # Use the default Ubuntu One host
            self.parsed_url.hostname = "one.ubuntu.com"
        else:
            assert self.parsed_url.scheme == 'u1'

        path = self.parsed_url.path.lstrip('/')

        self.api_base = "https://%s/api/file_storage/v1" % self.parsed_url.hostname
        self.volume_uri = "%s/volumes/~/%s" % (self.api_base, path)
        self.meta_base = "%s/~/%s/" % (self.api_base, path)
        # This next line *should* work, but isn't set up correctly server-side yet
        #self.content_base = self.api_base
        self.content_base = "https://files.%s" % self.parsed_url.hostname

        ensure_dbus()

	    if not self.login():
            from duplicity import log
		    log.FatalError(_("Could not obtain Ubuntu One credentials"),
                           log.ErrorCode.backend_error)

        # Create volume in case it doesn't exist yet
        self.create_volume()

    def login(self):
	    from gobject import MainLoop
	    from dbus.mainloop.glib import DBusGMainLoop
	    from ubuntuone.platform.credentials import CredentialsManagementTool

	    self.login_success = False

	    DBusGMainLoop(set_as_default=True)
	    loop = MainLoop()

	    def quit(result):
		    loop.quit()
		    if result:
			    self.login_success = True

	    cd = CredentialsManagementTool()
	    d = cd.login()
	    d.addCallbacks(quit)
	    loop.run()
	    return self.login_success

    def quote(self, url):
        import urllib
        return urllib.quote(url, safe="/~")

    def parse_error(self, headers, ignore=None):
        from duplicity import log

        status = int(headers[0].get('status'))
        if status >= 200 and status < 300:
            return None

        if ignore and status in ignore:
            return None

        if status == 400:
            code = log.ErrorCode.backend_permission_denied
        elif status == 404:
            code = log.ErrorCode.backend_not_found
        elif status == 507:
            code = log.ErrorCode.backend_no_space
        else:
            code = log.ErrorCode.backend_error
        return code

    def handle_error(self, raise_error, op, headers, file1=None, file2=None, ignore=None):
        from duplicity import log
        from duplicity import util
        import json

        code = self.parse_error(headers, ignore)
        if code is None:
            return

        status = int(headers[0].get('status'))

        if file1:
            file1 = file1.encode("utf8")
        else:
            file1 = None
        if file2:
            file2 = file2.encode("utf8")
        else:
            file2 = None
        extra = ' '.join([util.escape(x) for x in [file1, file2] if x])
        extra = ' '.join([op, extra])
        msg = _("Got status code %s") % status
        if headers[0].get('x-oops-id') is not None:
            msg += '\nOops-ID: %s' % headers[0].get('x-oops-id')
        if headers[0].get('content-type') == 'application/json':
            node = json.loads(headers[1])
            if node.get('error'):
                msg = node.get('error')

        if raise_error:
            if status == 503:
                raise TemporaryLoadException(msg)
            else:
                raise BackendException(msg)
        else:
            log.FatalError(msg, code, extra)

    @retry
    def create_volume(self, raise_errors=False):
        import ubuntuone.couch.auth as auth
        answer = auth.request(self.volume_uri, http_method="PUT")
        self.handle_error(raise_errors, 'put', answer, self.volume_uri)

    @retry
    def put(self, source_path, remote_filename = None, raise_errors=False):
        """Copy file to remote"""
        import json
        import ubuntuone.couch.auth as auth
        import mimetypes
        if not remote_filename:
            remote_filename = source_path.get_filename()
        remote_full = self.meta_base + self.quote(remote_filename)
        answer = auth.request(remote_full,
                              http_method="PUT",
                              request_body='{"kind":"file"}')
        self.handle_error(raise_errors, 'put', answer, source_path.name, remote_full)
        node = json.loads(answer[1])

        remote_full = self.content_base + self.quote(node.get('content_path'))
        data = bytearray(open(source_path.name, 'rb').read())
        size = len(data)
        content_type = mimetypes.guess_type(source_path.name)[0]
        content_type = content_type or 'application/octet-stream'
        headers = {"Content-Length": str(size),
    	           "Content-Type": content_type}
        answer = auth.request(remote_full, http_method="PUT",
                              headers=headers, request_body=data)
        self.handle_error(raise_errors, 'put', answer, source_path.name, remote_full)

    @retry
    def get(self, filename, local_path, raise_errors=False):
        """Get file and put in local_path (Path object)"""
        import json
        import ubuntuone.couch.auth as auth
        remote_full = self.meta_base + self.quote(filename)
        answer = auth.request(remote_full)
        self.handle_error(raise_errors, 'get', answer, remote_full, filename)
        node = json.loads(answer[1])

        remote_full = self.content_base + self.quote(node.get('content_path'))
        answer = auth.request(remote_full)
        self.handle_error(raise_errors, 'get', answer, remote_full, filename)
        f = open(local_path.name, 'wb')
        f.write(answer[1])
        local_path.setdata()

    @retry
    def list(self, raise_errors=False):
        """List files in that directory"""
        import json
        import ubuntuone.couch.auth as auth
        import urllib
        remote_full = self.meta_base + "?include_children=true"
        answer = auth.request(remote_full)
        self.handle_error(raise_errors, 'list', answer, remote_full)
        filelist = []
        node = json.loads(answer[1])
        if node.get('has_children') == True:
            for child in node.get('children'):
                path = urllib.unquote(child.get('path')).lstrip('/')
                filelist += [path]
        return filelist

    @retry
    def delete(self, filename_list, raise_errors=False):
        """Delete all files in filename list"""
        import types
        import ubuntuone.couch.auth as auth
        assert type(filename_list) is not types.StringType
        for filename in filename_list:
            remote_full = self.meta_base + self.quote(filename)
    	    answer = auth.request(remote_full, http_method="DELETE")
            self.handle_error(raise_errors, 'delete', answer, remote_full, ignore=[404])

    @retry
    def _query_file_info(self, filename, raise_errors=False):
        """Query attributes on filename"""
        import json
        import ubuntuone.couch.auth as auth
        from duplicity import log
        remote_full = self.meta_base + self.quote(filename)
        answer = auth.request(remote_full)

        code = self.parse_error(answer)
        if code is not None:
            if code == log.ErrorCode.backend_not_found:
                return {'size': -1}
            elif raise_errors:
                self.handle_error(raise_errors, 'query', answer, remote_full, filename)
            else:
                return {'size': None}

        node = json.loads(answer[1])
        size = node.get('size')
        return {'size': size}

duplicity.backend.register_backend("u1", U1Backend)
duplicity.backend.register_backend("u1+http", U1Backend)

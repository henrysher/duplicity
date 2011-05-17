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

_login_success = False
def login():
	from gobject import MainLoop
	from dbus.mainloop.glib import DBusGMainLoop
	from ubuntuone.platform.credentials import CredentialsManagementTool

	global _login_success
	_login_success = False

	DBusGMainLoop(set_as_default=True)
	loop = MainLoop()

	def quit(result):
		global _login_success
		loop.quit()
		if result:
			_login_success = True

	cd = CredentialsManagementTool()
	d = cd.login()
	d.addCallbacks(quit)
	loop.run()
	return _login_success

class U1Backend(duplicity.backend.Backend):
    """
    Backend for Ubuntu One, through the use of the ubuntone module and a REST
    API.  See https://one.ubuntu.com/developer/ for REST documentation.
    """
    def __init__(self, url):
        duplicity.backend.Backend.__init__(self, url)

        if self.scheme == 'u1+http':
            # Use the default Ubuntu One host
            self.hostname = "one.ubuntu.com"
        else:
            assert self.scheme == 'u1'

        self.api_base = "https://%s/api/file_storage/v1" % self.hostname
        self.volume_uri = "%s/volumes/~/%s" % (self.api_base, self.parsed_url.path)
        self.meta_base = "%s/~/%s/" % (self.api_base, self.parsed_url.path)
        self.content_base = "https://files.%s" % self.hostname

        ensure_dbus()

	    if not login():
            from duplicity import log
		    log.FatalError(_("Could not obtain Ubuntu One credentials"),
                           log.ErrorCode.backend_error)

        # Create volume in case it doesn't exist yet
        import ubuntuone.couch.auth as auth
        answer = auth.request(self.volume_uri, http_method="PUT")
        self.handle_error('put', answer[0], self.volume_uri)

    def handle_error(self, op, headers, file1=None, file2=None):
        from duplicity import log
        from duplicity import util

        status = headers.get('status')
        if status = '200':
            return

        if status == '400':
            code = log.ErrorCode.backend_permission_denied
        elif status == '404':
            code = log.ErrorCode.backend_not_found
        elif status == 'XXX':
            code = log.ErrorCode.backend_no_space
        else:
            code = log.ErrorCode.backend_error

        extra = ' '.join([util.escape(x) for x in [file1, file2] if x])
        extra = ' '.join([op, extra])
        log.FatalError(str(e), code, extra)

    def put(self, source_path, remote_filename = None):
        """Copy file to remote"""
        import urllib
        import json
        import ubuntuone.couch.auth as auth
        if not remote_filename:
            remote_filename = source_path.get_filename()
        remote_full = self.meta_base + urllib.quote(remote_filename)
        answer = auth.request(remote_full,
                              http_method="PUT",
                              request_body='{"kind":"file"}')
        self.handle_error('put', answer[0], source_path.name, remote_full)
        node = json.loads(answer[1])

        remote_full = self.content_base + urllib.quote(node.get('content_path'), safe="/~")
        f = open(source_path.name, 'rb')
        data = f.read()
        answer = auth.request(remote_full, http_method="PUT", request_body=data)
        self.handle_error('put', answer[0], source_path.name, remote_full)

    def get(self, filename, local_path):
        """Get file and put in local_path (Path object)"""
        import urllib
        import json
        import ubuntuone.couch.auth as auth
        remote_full = self.meta_base + urllib.quote(filename)
        answer = auth.request(remote_full)
        self.handle_error('get', answer[0], remote_full, source_path.name)
        node = json.loads(answer[1])

        remote_full = self.content_base + urllib.quote(node.get('content_path'), safe="/~")
        answer = auth.request(remote_full)
        self.handle_error('get', answer[0], remote_full, source_path.name)
        f = open(local_path.name, 'wb')
        f.write(answer[1])
        local_path.setdata()

    def list(self):
        """List files in that directory"""
        import urllib
        import json
        import ubuntuone.couch.auth as auth
        remote_full = self.meta_base + "?include_children=true"
        answer = auth.request(remote_full)
        self.handle_error('list', answer[0], remote_full)
        node = json.loads(answer[1])
        if node.get('has_children') != 'True':
            return []
        filelist = []
        for child in node.get('children'):
            child_node = json.loads(child)
            filelist += [urllib.unquote(child_node.get('path'))]
        return filelist

    def delete(self, filename_list):
        """Delete all files in filename list"""
        import types
        import urllib
        import ubuntuone.couch.auth as auth
        assert type(filename_list) is not types.StringType
        for filename in filename_list:
            remote_full = self.meta_base + urllib.quote(filename)
    	    answer = auth.request(remote_full, http_method="DELETE")
            self.handle_error('delete', answer[0], remote_full)

duplicity.backend.register_backend("u1", U1Backend)
duplicity.backend.register_backend("u1+http", U1Backend)

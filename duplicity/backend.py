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

"""
Provides a common interface to all backends and certain sevices
intended to be used by the backends themselves.
"""

import os
import socket
import time
import re
import getpass
import gettext
import urllib

from duplicity import dup_temp
from duplicity import dup_threading
from duplicity import file_naming
from duplicity import globals
from duplicity import log
from duplicity import urlparse_2_5 as urlparser

from duplicity.errors import BackendException
from duplicity.errors import ConflictingScheme
from duplicity.errors import InvalidBackendURL
from duplicity.errors import UnsupportedBackendScheme

# todo: this should really NOT be done here
socket.setdefaulttimeout(globals.timeout)

_backends = {}


def register_backend(scheme, backend_factory):
    """
    Register a given backend factory responsible for URL:s with the
    given scheme.

    The backend must be a callable which, when called with a URL as
    the single parameter, returns an object implementing the backend
    protocol (i.e., a subclass of Backend).

    Typically the callable will be the Backend subclass itself.

    This function is not thread-safe and is intended to be called
    during module importation or start-up.
    """
    global _backends

    assert callable(backend_factory), "backend factory must be callable"

    if scheme in _backends:
        raise ConflictingSchemeError("the scheme %s already has a backend "
                                     "associated with it"
                                     "" % (scheme,))

    _backends[scheme] = backend_factory


def get_backend(url_string):
    """
    Instantiate a backend suitable for the given URL, or return None
    if the given string looks like a local path rather than a URL.

    Raise InvalidBackendURL if the URL is not a valid URL.
    """
    pu = ParsedUrl(url_string)

    # Implicit local path
    if not pu.scheme:
        return None

    global _backends

    if not pu.scheme in _backends:
        raise UnsupportedBackendScheme(url_string)
    else:
        return _backends[pu.scheme](pu)


_urlparser_initialized = False
_urlparser_initialized_lock = dup_threading.threading_module().Lock()

def _ensure_urlparser_initialized():
    """
    Ensure that the appropriate clobbering of variables in the
    urlparser module has been done. In the future, the need for this
    clobbering to begin with should preferably be eliminated.
    """
    def init():
        global _urlparser_initialized

        if not _urlparser_initialized:
            # These URL schemes have a backend with a notion of an RFC "network location".
            # The 'file' and 's3+http' schemes should not be in this list.
            # 'http' and 'https' are not actually used for duplicity backend urls, but are needed
            # in order to properly support urls returned from some webdav servers. adding them here
            # is a hack. we should instead not stomp on the url parsing module to begin with.
            #
            # todo: eliminate the need for backend specific hacking here completely.
            urlparser.uses_netloc = ['ftp',
                                     'hsi',
                                     'rsync',
                                     's3',
                                     'scp', 'ssh',
                                     'webdav', 'webdavs',
                                     'http', 'https',
                                     'imap', 'imaps']

            # Do not transform or otherwise parse the URL path component.
            urlparser.uses_query = []
            urlparser.uses_fragm = []

            _urlparser_initialized = True

    dup_threading.with_lock(_urlparser_initialized_lock, init)

class ParsedUrl:
    """
    Parse the given URL as a duplicity backend URL.

    Returns the data of a parsed URL with the same names as that of
    the standard urlparse.urlparse() except that all values have been
    resolved rather than deferred.  There are no get_* members.  This
    makes sure that the URL parsing errors are detected early.

    Raise InvalidBackendURL on invalid URL's
    """
    def __init__(self, url_string):
        self.url_string = url_string
        _ensure_urlparser_initialized()

        # While useful in some cases, the fact is that the urlparser makes
        # all the properties in the URL deferred or lazy.  This means that
        # problems don't get detected till called.  We'll try to trap those
        # problems here, so they will be caught early.

        try:
            pu = urlparser.urlparse(url_string)
        except:
            raise InvalidBackendURL("Syntax error in: %s" % url_string)

        try:
            self.scheme = pu.scheme
        except:
            raise InvalidBackendURL("Syntax error (scheme) in: %s" % url_string)

        try:
            self.netloc = pu.netloc
        except:
            raise InvalidBackendURL("Syntax error (netloc) in: %s" % url_string)

        try:
            self.path = pu.path
        except:
            raise InvalidBackendURL("Syntax error (path) in: %s" % url_string)

        try:
            self.username = pu.username
        except:
            raise InvalidBackendURL("Syntax error (username) in: %s" % url_string)
        if self.username:
            self.username = urllib.unquote(pu.username)
        else:
            self.username = None

        try:
            self.password = pu.password
        except:
            raise InvalidBackendURL("Syntax error (password) in: %s" % url_string)

        try:
            self.hostname = pu.hostname
        except:
            raise InvalidBackendURL("Syntax error (hostname) in: %s" % url_string)

        if self.scheme not in ['rsync']:
            try:
                self.port = pu.port
            except:
                raise InvalidBackendURL("Syntax error (port) in: %s" % url_string)
        else:
            self.port = None

        # This happens for implicit local paths.
        if not pu.scheme:
            return

        # Our backends do not handle implicit hosts.
        if pu.scheme in urlparser.uses_netloc and not pu.hostname:
            raise InvalidBackendURL("Missing hostname in a backend URL which "
                                    "requires an explicit hostname: %s"
                                    "" % (url_string))

        # Our backends do not handle implicit relative paths.
        if pu.scheme not in urlparser.uses_netloc and not pu.path.startswith('//'):
            raise InvalidBackendURL("missing // - relative paths not supported "
                                    "for scheme %s: %s"
                                    "" % (pu.scheme, url_string))

    def geturl(self):
        return self.url_string


def strip_auth_from_url(parsed_url):
    """Return a URL from a urlparse object without a username or password."""

    # Get a copy of the network location without the username or password.
    straight_netloc = parsed_url.netloc.split('@')[-1]

    # Replace the full network location with the stripped copy.
    return parsed_url.geturl().replace(parsed_url.netloc, straight_netloc, 1)


class Backend:
    """
    Represents a generic duplicity backend, capable of storing and
    retrieving files.

    Concrete sub-classes are expected to implement:

      - put
      - get
      - list
      - delete
      - close (if needed)
    """
    def __init__(self, parsed_url):
        self.parsed_url = parsed_url

    def put(self, source_path, remote_filename = None):
        """
        Transfer source_path (Path object) to remote_filename (string)

        If remote_filename is None, get the filename from the last
        path component of pathname.
        """
        raise NotImplementedError()

    def get(self, remote_filename, local_path):
        """Retrieve remote_filename and place in local_path"""
        raise NotImplementedError()

    def list(self):
        """
        Return list of filenames (strings) present in backend
        """
        raise NotImplementedError()

    def delete(self, filename_list):
        """
        Delete each filename in filename_list, in order if possible.
        """
        raise NotImplementedError()

    def get_password(self):
        """
        Return a password for authentication purposes. The password
        will be obtained from the backend URL, the environment, by
        asking the user, or by some other method. When applicable, the
        result will be cached for future invocations.
        """
        if self.parsed_url.password:
            return self.parsed_url.password

        try:
            password = os.environ['FTP_PASSWORD']
        except KeyError:
            password = getpass.getpass("Password for '%s': " % self.parsed_url.hostname)
            os.environ['FTP_PASSWORD'] = password
        return password

    def munge_password(self, commandline):
        """
        Remove password from commandline by substituting the password
        found in the URL, if any, with a generic place-holder.

        This is intended for display purposes only, and it is not
        guaranteed that the results are correct (i.e., more than just
        the password may be substituted if the password is also a
        substring of another part of the command line).
        """
        if self.parsed_url.password:
            return re.sub(self.parsed_url.password, '<passwd>', commandline)
        else:
            return commandline

    def run_command(self, commandline):
        """
        Execute the given command line, interpreted as a shell
        command, with logging and error detection. If execution fails,
        raise a BackendException.
        """
        private = self.munge_password(commandline)
        log.Info(_("Running '%s'") % private)
        if os.system(commandline):
            raise BackendException("Error running '%s'" % private)

    def run_command_persist(self, commandline):
        """
        Like run_command(), but repeat the attempt several times (with
        a delay in between) if it fails.
        """
        private = self.munge_password(commandline)
        for n in range(1, globals.num_retries+1):
            if n > 1:
                # sleep before retry
                time.sleep(30)
            log.Info(gettext.ngettext("Running '%s' (attempt #%d)",
                                      "Running '%s' (attempt #%d)", n) %
                                      (private, n))
            if not os.system(commandline):
                return
            log.Warn(gettext.ngettext("Running '%s' failed (attempt #%d)",
                                      "Running '%s' failed (attempt #%d)", n) %
                                      (private, n), 1)
        log.Warn(gettext.ngettext("Giving up trying to execute '%s' after %d attempt",
                                 "Giving up trying to execute '%s' after %d attempts",
                                 globals.num_retries) % (private, globals.num_retries))
        raise BackendException("Error running '%s'" % private)

    def popen(self, commandline):
        """
        Like run_command(), but capture stdout and return it (the
        contents read from stdout) as a string.
        """
        private = self.munge_password(commandline)
        log.Info(_("Reading results of '%s'") % private)
        fout = os.popen(commandline)
        results = fout.read()
        if fout.close():
            raise BackendException("Error running '%s'" % private)
        return results

    def popen_persist(self, commandline):
        """
        Like run_command_persist(), but capture stdout and return it
        (the contents read from stdout) as a string.
        """
        private = self.munge_password(commandline)
        for n in range(1, globals.num_retries+1):
            if n > 1:
                # sleep before retry
                time.sleep(30)
            log.Info(_("Reading results of '%s'") % private)
            fout = os.popen(commandline)
            results = fout.read()
            result_status = fout.close()
            if not result_status:
                return results
            elif result_status == 1280 and self.parsed_url.scheme == 'ftp':
                # This squelches the "file not found" result fromm ncftpls when
                # the ftp backend looks for a collection that does not exist.
                return ''
            log.Warn(gettext.ngettext("Running '%s' failed (attempt #%d)",
                                     "Running '%s' failed (attempt #%d)", n) %
                                      (private, n))
        log.Warn(gettext.ngettext("Giving up trying to execute '%s' after %d attempt",
                                  "Giving up trying to execute '%s' after %d attempts",
                                  globals.num_retries) % (private, globals.num_retries))
        raise BackendException("Error running '%s'" % private)

    def get_fileobj_read(self, filename, parseresults = None):
        """
        Return fileobject opened for reading of filename on backend

        The file will be downloaded first into a temp file.  When the
        returned fileobj is closed, the temp file will be deleted.
        """
        if not parseresults:
            parseresults = file_naming.parse(filename)
            assert parseresults, "Filename not correctly parsed"
        tdp = dup_temp.new_tempduppath(parseresults)
        self.get(filename, tdp)
        tdp.setdata()
        return tdp.filtered_open_with_delete("rb")

    def get_fileobj_write(self, filename,
                          parseresults = None,
                          sizelist = None):
        """
        Return fileobj opened for writing, which will cause the file
        to be written to the backend on close().

        The file will be encoded as specified in parseresults (or as
        read from the filename), and stored in a temp file until it
        can be copied over and deleted.

        If sizelist is not None, it should be set to an empty list.
        The number of bytes will be inserted into the list.
        """
        if not parseresults:
            parseresults = file_naming.parse(filename)
            assert parseresults, "Filename %s not correctly parsed" % filename
        tdp = dup_temp.new_tempduppath(parseresults)

        def close_file_hook():
            """This is called when returned fileobj is closed"""
            self.put(tdp, filename)
            if sizelist is not None:
                tdp.setdata()
                sizelist.append(tdp.getsize())
            tdp.delete()

        fh = dup_temp.FileobjHooked(tdp.filtered_open("wb"))
        fh.addhook(close_file_hook)
        return fh

    def get_data(self, filename, parseresults = None):
        """
        Retrieve a file from backend, process it, return contents.
        """
        fin = self.get_fileobj_read(filename, parseresults)
        buf = fin.read()
        assert not fin.close()
        return buf

    def put_data(self, buffer, filename, parseresults = None):
        """
        Put buffer into filename on backend after processing.
        """
        fout = self.get_fileobj_write(filename, parseresults)
        fout.write(buffer)
        assert not fout.close()

    def close(self):
        """
        Close the backend, releasing any resources held and
        invalidating any file objects obtained from the backend.
        """
        pass

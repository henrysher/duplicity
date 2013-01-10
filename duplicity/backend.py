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
import sys
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

from duplicity.util import exception_traceback

from duplicity.errors import BackendException, FatalBackendError
from duplicity.errors import TemporaryLoadException
from duplicity.errors import ConflictingScheme
from duplicity.errors import InvalidBackendURL
from duplicity.errors import UnsupportedBackendScheme

import duplicity.backends


# todo: this should really NOT be done here
socket.setdefaulttimeout(globals.timeout)

_forced_backend = None
_backends = {}


def import_backends():
    """
    Import files in the duplicity/backends directory where
    the filename ends in 'backend.py' and ignore the rest.

    @rtype: void
    @return: void
    """
    path = duplicity.backends.__path__[0]
    assert path.endswith("duplicity/backends"), duplicity.backends.__path__

    files = os.listdir(path)
    for fn in files:
        if fn.endswith("backend.py"):
            fn = fn[:-3]
            imp = "duplicity.backends.%s" % (fn,)
            # ignore gio as it is explicitly loaded in commandline.parse_cmdline_options()
            if fn == "giobackend": continue
            try:
                __import__(imp)
                res = "Succeeded"
                level = log.INFO
            except Exception:
                res = "Failed: " + str(sys.exc_info()[1])
                level = log.WARNING
            log.Log("Import of %s %s" % (imp, res), level)
        else:
            continue


def force_backend(backend):
    """
    Forces the use of a particular backend, regardless of schema
    """
    global _forced_backend
    _forced_backend = backend


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
        raise ConflictingScheme("the scheme %s already has a backend "
                                "associated with it"
                                "" % (scheme,))

    _backends[scheme] = backend_factory


def is_backend_url(url_string):
    """
    @return Whether the given string looks like a backend URL.
    """
    pu = ParsedUrl(url_string)

    # Be verbose to actually return True/False rather than string.
    if pu.scheme:
        return True
    else:
        return False


def get_backend(url_string):
    """
    Instantiate a backend suitable for the given URL, or return None
    if the given string looks like a local path rather than a URL.

    Raise InvalidBackendURL if the URL is not a valid URL.
    """
    if not is_backend_url(url_string):
        return None

    pu = ParsedUrl(url_string)

    # Implicit local path
    assert pu.scheme, "should be a backend url according to is_backend_url"

    global _backends, _forced_backend

    if _forced_backend:
        return _forced_backend(pu)
    elif not pu.scheme in _backends:
        raise UnsupportedBackendScheme(url_string)
    else:
        try:
            return _backends[pu.scheme](pu)
        except ImportError:
            raise BackendException(_("Could not initialize backend: %s") % str(sys.exc_info()[1]))


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
                                     'ftps',
                                     'hsi',
                                     'rsync',
                                     's3',
                                     'u1',
                                     'scp', 'ssh', 'sftp',
                                     'webdav', 'webdavs',
                                     'gdocs',
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
        except Exception:
            raise InvalidBackendURL("Syntax error in: %s" % url_string)

        try:
            self.scheme = pu.scheme
        except Exception:
            raise InvalidBackendURL("Syntax error (scheme) in: %s" % url_string)

        try:
            self.netloc = pu.netloc
        except Exception:
            raise InvalidBackendURL("Syntax error (netloc) in: %s" % url_string)

        try:
            self.path = pu.path
        except Exception:
            raise InvalidBackendURL("Syntax error (path) in: %s" % url_string)

        try:
            self.username = pu.username
        except Exception:
            raise InvalidBackendURL("Syntax error (username) in: %s" % url_string)
        if self.username:
            self.username = urllib.unquote(pu.username)
        else:
            self.username = None

        try:
            self.password = pu.password
        except Exception:
            raise InvalidBackendURL("Syntax error (password) in: %s" % url_string)
        if self.password:
            self.password = urllib.unquote(self.password)
        else:
            self.password = None

        try:
            self.hostname = pu.hostname
        except Exception:
            raise InvalidBackendURL("Syntax error (hostname) in: %s" % url_string)

        # init to None, overwrite with actual value on success
        self.port = None
        try:
            self.port = pu.port
        except Exception:
            # old style rsync://host::[/]dest, are still valid, though they contain no port
            if not ( self.scheme in ['rsync'] and re.search('::[^:]*$', self.url_string)):
                raise InvalidBackendURL("Syntax error (port) in: %s A%s B%s C%s" % (url_string, (self.scheme in ['rsync']), re.search('::[^:]+$', self.netloc), self.netloc ) )

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


# Decorator for backend operation functions to simplify writing one that
# retries.  Make sure to add a keyword argument 'raise_errors' to your function
# and if it is true, raise an exception on an error.  If false, fatal-log it.
def retry(fn):
    def iterate(*args):
        for n in range(1, globals.num_retries):
            try:
                kwargs = {"raise_errors" : True}
                return fn(*args, **kwargs)
            except Exception, e:
                log.Warn("Attempt %s failed: %s: %s"
                         % (n, e.__class__.__name__, str(e)))
                log.Debug("Backtrace of previous error: %s"
                          % exception_traceback())
                if isinstance(e, TemporaryLoadException):
                    time.sleep(30) # wait longer before trying again
                else:
                    time.sleep(10) # wait a bit before trying again
        # Now try one last time, but fatal-log instead of raising errors
        kwargs = {"raise_errors" : False}
        return fn(*args, **kwargs)
    return iterate

# same as above, a bit dumber and always dies fatally if last trial fails
# hence no need for the raise_errors var ;), we really catch everything here
# as we don't know what the underlying code comes up with and we really *do*
# want to retry globals.num_retries times under all circumstances
def retry_fatal(fn):
    def _retry_fatal(self, *args):
        try:
            n = 0
            for n in range(1, globals.num_retries):
                try:
                    self.retry_count = n
                    return fn(self, *args)
                except FatalBackendError, e:
                    # die on fatal errors
                    raise e
                except Exception, e:
                    # retry on anything else
                    log.Warn("Attempt %s failed. %s: %s"
                             % (n, e.__class__.__name__, str(e)))
                    log.Debug("Backtrace of previous error: %s"
                              % exception_traceback())
                    time.sleep(10) # wait a bit before trying again
        # final trial, die on exception
            self.retry_count = n+1
            return fn(self, *args)
        except Exception, e:
            log.FatalError("Giving up after %s attempts. %s: %s"
                         % (self.retry_count, e.__class__.__name__, str(e)),
                          log.ErrorCode.backend_error)
            log.Debug("Backtrace of previous error: %s"
                        % exception_traceback())
        self.retry_count = 0

    return _retry_fatal

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

    Optional:

      - move
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

    def move(self, source_path, remote_filename = None):
        """
        Move source_path (Path object) to remote_filename (string)

        Same as put(), but unlinks source_path in the process.  This allows the
        local backend to do this more efficiently using rename.
        """
        self.put(source_path, remote_filename)
        source_path.delete()

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

    # Should never cause FatalError.
    # Returns a dictionary of dictionaries.  The outer dictionary maps
    # filenames to metadata dictionaries.  Supported metadata are:
    #
    # 'size': if >= 0, size of file
    #         if -1, file is not found
    #         if None, error querying file
    #
    # Returned dictionary is guaranteed to contain a metadata dictionary for
    # each filename, but not all metadata are guaranteed to be present.
    def query_info(self, filename_list, raise_errors=True):
        """
        Return metadata about each filename in filename_list
        """
        info = {}
        if hasattr(self, '_query_list_info'):
            info = self._query_list_info(filename_list)
        elif hasattr(self, '_query_file_info'):
            for filename in filename_list:
                info[filename] = self._query_file_info(filename)

        # Fill out any missing entries (may happen if backend has no support
        # or its query_list support is lazy)
        for filename in filename_list:
            if filename not in info:
                info[filename] = {}

        return info

    """ use getpass by default, inherited backends may overwrite this behaviour """
    use_getpass = True

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
            if self.use_getpass:
                password = getpass.getpass("Password for '%s@%s': " %
                                           (self.parsed_url.username,self.parsed_url.hostname) )
                os.environ['FTP_PASSWORD'] = password
            else:
                password = None
        return password

    def munge_password(self, commandline):
        """
        Remove password from commandline by substituting the password
        found in the URL, if any, with a generic place-holder.

        This is intended for display purposes only, and it is not
        guaranteed that the results are correct (i.e., more than just
        the ':password@' may be substituted.
        """
        if self.parsed_url.password:
            return re.sub( r'(:([^\s:/@]+)@([^\s@]+))', r':*****@\3', commandline )
        else:
            return commandline

    """
    DEPRECATED:
    run_command(_persist) - legacy wrappers for subprocess_popen(_persist)
    """
    def run_command(self, commandline):
        return self.subprocess_popen(commandline)
    def run_command_persist(self, commandline):
        return self.subprocess_popen_persist(commandline)

    """
    DEPRECATED:
    popen(_persist) - legacy wrappers for subprocess_popen(_persist)
    """
    def popen(self, commandline):
        result, stdout, stderr = self.subprocess_popen(commandline)
        return stdout
    def popen_persist(self, commandline):
        result, stdout, stderr = self.subprocess_popen_persist(commandline)
        return stdout

    def _subprocess_popen(self, commandline):
        """
        For internal use.
        Execute the given command line, interpreted as a shell command.
        Returns int Exitcode, string StdOut, string StdErr
        """
        from subprocess import Popen, PIPE
        p = Popen(commandline, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        return p.returncode, stdout, stderr

    def subprocess_popen(self, commandline):
        """
        Execute the given command line with error check.
        Returns int Exitcode, string StdOut, string StdErr

        Raise a BackendException on failure.
        """
        private = self.munge_password(commandline)
        log.Info(_("Reading results of '%s'") % private)
        result, stdout, stderr = self._subprocess_popen(commandline)
        if result != 0:
            raise BackendException("Error running '%s'" % private)
        return result, stdout, stderr

    """ a dictionary for persist breaking exceptions, syntax is
        { 'command' : [ code1, code2 ], ... } see ftpbackend for an example """
    popen_persist_breaks = {}

    def subprocess_popen_persist(self, commandline):
        """
        Execute the given command line with error check.
        Retries globals.num_retries times with 30s delay.
        Returns int Exitcode, string StdOut, string StdErr

        Raise a BackendException on failure.
        """
        private = self.munge_password(commandline)

        for n in range(1, globals.num_retries+1):
            # sleep before retry
            if n > 1:
                time.sleep(30)
            log.Info(_("Reading results of '%s'") % private)
            result, stdout, stderr = self._subprocess_popen(commandline)
            if result == 0:
                return result, stdout, stderr

            try:
                m = re.search("^\s*([\S]+)", commandline)
                cmd = m.group(1)
                ignores = self.popen_persist_breaks[ cmd ]
                ignores.index(result)
                """ ignore a predefined set of error codes """
                return 0, '', ''
            except (KeyError, ValueError):
                pass

            log.Warn(gettext.ngettext("Running '%s' failed with code %d (attempt #%d)",
                                     "Running '%s' failed with code %d (attempt #%d)", n) %
                                      (private, result, n))
            if stdout or stderr:
                    log.Warn(_("Error is:\n%s") % stderr + (stderr and stdout and "\n") + stdout)

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

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

import errno
import os
import sys
import socket
import time
import re
import getpass
import gettext
import re
import types
import urllib
import urlparse

from duplicity import dup_temp
from duplicity import file_naming
from duplicity import globals
from duplicity import log
from duplicity import path
from duplicity import progress
from duplicity import util

from duplicity.util import exception_traceback

from duplicity.errors import BackendException
from duplicity.errors import FatalBackendException
from duplicity.errors import TemporaryLoadException
from duplicity.errors import ConflictingScheme
from duplicity.errors import InvalidBackendURL
from duplicity.errors import UnsupportedBackendScheme

import duplicity.backends


# todo: this should really NOT be done here
socket.setdefaulttimeout(globals.timeout)

_backends = {}
_backend_prefixes = {}

# These URL schemes have a backend with a notion of an RFC "network location".
# The 'file' and 's3+http' schemes should not be in this list.
# 'http' and 'https' are not actually used for duplicity backend urls, but are needed
# in order to properly support urls returned from some webdav servers. adding them here
# is a hack. we should instead not stomp on the url parsing module to begin with.
#
# This looks similar to urlparse's 'uses_netloc' list, but urlparse doesn't use
# that list for parsing, only creating urls.  And doesn't include our custom
# schemes anyway.  So we keep our own here for our own use.
#
# NOTE: this is filled by the respective backends during registering
uses_netloc = []


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
    files.sort()
    for fn in files:
        if fn.endswith("backend.py"):
            fn = fn[:-3]
            imp = "duplicity.backends.%s" % (fn,)
            try:
                __import__(imp)
                res = "Succeeded"
            except Exception:
                res = "Failed: " + str(sys.exc_info()[1])
            log.Log(_("Import of %s %s") % (imp, res), log.INFO)
        else:
            continue


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


def register_backend_prefix(scheme, backend_factory):
    """
    Register a given backend factory responsible for URL:s with the
    given scheme prefix.

    The backend must be a callable which, when called with a URL as
    the single parameter, returns an object implementing the backend
    protocol (i.e., a subclass of Backend).

    Typically the callable will be the Backend subclass itself.

    This function is not thread-safe and is intended to be called
    during module importation or start-up.
    """
    global _backend_prefixes

    assert callable(backend_factory), "backend factory must be callable"

    if scheme in _backend_prefixes:
        raise ConflictingScheme("the prefix %s already has a backend "
                                "associated with it"
                                "" % (scheme,))

    _backend_prefixes[scheme] = backend_factory


def strip_prefix(url_string, prefix_scheme):
    """
    strip the prefix from a string e.g. par2+ftp://... -> ftp://...
    """
    return re.sub('(?i)^' + re.escape(prefix_scheme) + '\+', '', url_string)


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


def get_backend_object(url_string):
    """
    Find the right backend class instance for the given URL, or return None
    if the given string looks like a local path rather than a URL.

    Raise InvalidBackendURL if the URL is not a valid URL.
    """
    if not is_backend_url(url_string):
        return None

    global _backends, _backend_prefixes

    pu = ParsedUrl(url_string)
    assert pu.scheme, "should be a backend url according to is_backend_url"

    factory = None

    for prefix in _backend_prefixes:
        if url_string.startswith(prefix + '+'):
            factory = _backend_prefixes[prefix]
            pu = ParsedUrl(strip_prefix(url_string, prefix))
            break

    if factory is None:
        if pu.scheme not in _backends:
            raise UnsupportedBackendScheme(url_string)
        else:
            factory = _backends[pu.scheme]

    try:
        return factory(pu)
    except ImportError:
        raise BackendException(_("Could not initialize backend: %s") % str(sys.exc_info()[1]))


def get_backend(url_string):
    """
    Instantiate a backend suitable for the given URL, or return None
    if the given string looks like a local path rather than a URL.

    Raise InvalidBackendURL if the URL is not a valid URL.
    """
    if globals.use_gio:
        url_string = 'gio+' + url_string
    obj = get_backend_object(url_string)
    if obj:
        obj = BackendWrapper(obj)
    return obj


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

        # Python < 2.6.5 still examine urlparse.uses_netlock when parsing urls,
        # so stuff our custom list in there before we parse.
        urlparse.uses_netloc = uses_netloc

        # While useful in some cases, the fact is that the urlparser makes
        # all the properties in the URL deferred or lazy.  This means that
        # problems don't get detected till called.  We'll try to trap those
        # problems here, so they will be caught early.

        try:
            pu = urlparse.urlparse(url_string)
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
            if self.path:
                self.path = urllib.unquote(self.path)
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
        except Exception:  # not raised in python2.7+, just returns None
            # old style rsync://host::[/]dest, are still valid, though they contain no port
            if not (self.scheme in ['rsync'] and re.search('::[^:]*$', self.url_string)):
                raise InvalidBackendURL("Syntax error (port) in: %s A%s B%s C%s" %
                                        (url_string, (self.scheme in ['rsync']),
                                         re.search('::[^:]+$', self.netloc), self.netloc))

        # Our URL system uses two slashes more than urlparse's does when using
        # non-netloc URLs.  And we want to make sure that if urlparse assuming
        # a netloc where we don't want one, that we correct it.
        if self.scheme not in uses_netloc:
            if self.netloc:
                self.path = '//' + self.netloc + self.path
                self.netloc = ''
                self.hostname = None
            elif not self.path.startswith('//') and self.path.startswith('/'):
                self.path = '//' + self.path

        # This happens for implicit local paths.
        if not self.scheme:
            return

        # Our backends do not handle implicit hosts.
        if self.scheme in uses_netloc and not self.hostname:
            raise InvalidBackendURL("Missing hostname in a backend URL which "
                                    "requires an explicit hostname: %s"
                                    "" % (url_string))

        # Our backends do not handle implicit relative paths.
        if self.scheme not in uses_netloc and not self.path.startswith('//'):
            raise InvalidBackendURL("missing // - relative paths not supported "
                                    "for scheme %s: %s"
                                    "" % (self.scheme, url_string))

    def geturl(self):
        return self.url_string


def strip_auth_from_url(parsed_url):
    """Return a URL from a urlparse object without a username or password."""

    clean_url = re.sub('^([^:/]+://)(.*@)?(.*)', r'\1\3', parsed_url.geturl())
    return clean_url


def _get_code_from_exception(backend, operation, e):
    if isinstance(e, BackendException) and e.code != log.ErrorCode.backend_error:
        return e.code
    elif hasattr(backend, '_error_code'):
        return backend._error_code(operation, e) or log.ErrorCode.backend_error
    elif hasattr(e, 'errno'):
        # A few backends return such errors (local, paramiko, etc)
        if e.errno == errno.EACCES:
            return log.ErrorCode.backend_permission_denied
        elif e.errno == errno.ENOENT:
            return log.ErrorCode.backend_not_found
        elif e.errno == errno.ENOSPC:
            return log.ErrorCode.backend_no_space
    return log.ErrorCode.backend_error


def retry(operation, fatal=True):
    # Decorators with arguments introduce a new level of indirection.  So we
    # have to return a decorator function (which itself returns a function!)
    def outer_retry(fn):
        def inner_retry(self, *args):
            for n in range(1, globals.num_retries + 1):
                try:
                    return fn(self, *args)
                except FatalBackendException as e:
                    # die on fatal errors
                    raise e
                except Exception as e:
                    # retry on anything else
                    log.Debug(_("Backtrace of previous error: %s")
                              % exception_traceback())
                    at_end = n == globals.num_retries
                    code = _get_code_from_exception(self.backend, operation, e)
                    if code == log.ErrorCode.backend_not_found:
                        # If we tried to do something, but the file just isn't there,
                        # no need to retry.
                        at_end = True
                    if at_end and fatal:
                        def make_filename(f):
                            if isinstance(f, path.ROPath):
                                return util.escape(f.name)
                            else:
                                return util.escape(f)
                        extra = ' '.join([operation] + [make_filename(x) for x in args if x])
                        log.FatalError(_("Giving up after %s attempts. %s: %s")
                                       % (n, e.__class__.__name__,
                                          util.uexc(e)), code=code, extra=extra)
                    else:
                        log.Warn(_("Attempt %s failed. %s: %s")
                                 % (n, e.__class__.__name__, util.uexc(e)))
                    if not at_end:
                        if isinstance(e, TemporaryLoadException):
                            time.sleep(3 * globals.backend_retry_delay)  # wait longer before trying again
                        else:
                            time.sleep(globals.backend_retry_delay)  # wait a bit before trying again
                        if hasattr(self.backend, '_retry_cleanup'):
                            self.backend._retry_cleanup()

        return inner_retry
    return outer_retry


class Backend(object):
    """
    See README in backends directory for information on how to write a backend.
    """
    def __init__(self, parsed_url):
        self.parsed_url = parsed_url

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
                                           (self.parsed_url.username, self.parsed_url.hostname))
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
            return re.sub(r'(:([^\s:/@]+)@([^\s@]+))', r':*****@\3', commandline)
        else:
            return commandline

    def __subprocess_popen(self, commandline):
        """
        For internal use.
        Execute the given command line, interpreted as a shell command.
        Returns int Exitcode, string StdOut, string StdErr
        """
        import shlex
        from subprocess import Popen, PIPE
        args = shlex.split(commandline)
        args[0] = util.which(args[0])
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        return p.returncode, stdout, stderr

    """ a dictionary for breaking exceptions, syntax is
        { 'command' : [ code1, code2 ], ... } see ftpbackend for an example """
    popen_breaks = {}

    def subprocess_popen(self, commandline):
        """
        Execute the given command line with error check.
        Returns int Exitcode, string StdOut, string StdErr

        Raise a BackendException on failure.
        """
        private = self.munge_password(commandline)
        log.Info(_("Reading results of '%s'") % private)
        result, stdout, stderr = self.__subprocess_popen(commandline)
        if result != 0:
            try:
                m = re.search("^\s*([\S]+)", commandline)
                cmd = m.group(1)
                ignores = self.popen_breaks[cmd]
                ignores.index(result)
                """ ignore a predefined set of error codes """
                return 0, '', ''
            except (KeyError, ValueError):
                raise BackendException("Error running '%s': returned %d, with output:\n%s" %
                                       (private, result, stdout + '\n' + stderr))
        return result, stdout, stderr


class BackendWrapper(object):
    """
    Represents a generic duplicity backend, capable of storing and
    retrieving files.
    """

    def __init__(self, backend):
        self.backend = backend

    def __do_put(self, source_path, remote_filename):
        if hasattr(self.backend, '_put'):
            log.Info(_("Writing %s") % util.ufn(remote_filename))
            self.backend._put(source_path, remote_filename)
        else:
            raise NotImplementedError()

    @retry('put', fatal=True)
    def put(self, source_path, remote_filename=None):
        """
        Transfer source_path (Path object) to remote_filename (string)

        If remote_filename is None, get the filename from the last
        path component of pathname.
        """
        if not remote_filename:
            remote_filename = source_path.get_filename()
        self.__do_put(source_path, remote_filename)

    @retry('move', fatal=True)
    def move(self, source_path, remote_filename=None):
        """
        Move source_path (Path object) to remote_filename (string)

        Same as put(), but unlinks source_path in the process.  This allows the
        local backend to do this more efficiently using rename.
        """
        if not remote_filename:
            remote_filename = source_path.get_filename()
        if hasattr(self.backend, '_move'):
            if self.backend._move(source_path, remote_filename) is not False:
                source_path.setdata()
                return
        self.__do_put(source_path, remote_filename)
        source_path.delete()

    @retry('get', fatal=True)
    def get(self, remote_filename, local_path):
        """Retrieve remote_filename and place in local_path"""
        if hasattr(self.backend, '_get'):
            self.backend._get(remote_filename, local_path)
            local_path.setdata()
            if not local_path.exists():
                raise BackendException(_("File %s not found locally after get "
                                         "from backend") % util.ufn(local_path.name))
        else:
            raise NotImplementedError()

    @retry('list', fatal=True)
    def list(self):
        """
        Return list of filenames (byte strings) present in backend
        """
        def tobytes(filename):
            "Convert a (maybe unicode) filename to bytes"
            if isinstance(filename, unicode):
                # There shouldn't be any encoding errors for files we care
                # about, since duplicity filenames are ascii.  But user files
                # may be in the same directory.  So just replace characters.
                return filename.encode(sys.getfilesystemencoding(), 'replace')
            else:
                return filename

        if hasattr(self.backend, '_list'):
            # Make sure that duplicity internals only ever see byte strings
            # for filenames, no matter what the backend thinks it is talking.
            return [tobytes(x) for x in self.backend._list()]
        else:
            raise NotImplementedError()

    def delete(self, filename_list):
        """
        Delete each filename in filename_list, in order if possible.
        """
        assert not isinstance(filename_list, types.StringType)
        if hasattr(self.backend, '_delete_list'):
            self._do_delete_list(filename_list)
        elif hasattr(self.backend, '_delete'):
            for filename in filename_list:
                self._do_delete(filename)
        else:
            raise NotImplementedError()

    @retry('delete', fatal=False)
    def _do_delete_list(self, filename_list):
        while filename_list:
            sublist = filename_list[:100]
            self.backend._delete_list(sublist)
            filename_list = filename_list[100:]

    @retry('delete', fatal=False)
    def _do_delete(self, filename):
        self.backend._delete(filename)

    # Should never cause FatalError.
    # Returns a dictionary of dictionaries.  The outer dictionary maps
    # filenames to metadata dictionaries.  Supported metadata are:
    #
    # 'size': if >= 0, size of file
    #         if -1, file is not found
    #         if None, error querying file
    #
    # Returned dictionary is guaranteed to contain a metadata dictionary for
    # each filename, and all metadata are guaranteed to be present.
    def query_info(self, filename_list):
        """
        Return metadata about each filename in filename_list
        """
        info = {}
        if hasattr(self.backend, '_query_list'):
            info = self._do_query_list(filename_list)
            if info is None:
                info = {}
        elif hasattr(self.backend, '_query'):
            for filename in filename_list:
                info[filename] = self._do_query(filename)

        # Fill out any missing entries (may happen if backend has no support
        # or its query_list support is lazy)
        for filename in filename_list:
            if filename not in info or info[filename] is None:
                info[filename] = {}
            for metadata in ['size']:
                info[filename].setdefault(metadata, None)

        return info

    @retry('query', fatal=False)
    def _do_query_list(self, filename_list):
        info = self.backend._query_list(filename_list)
        if info is None:
            info = {}
        return info

    @retry('query', fatal=False)
    def _do_query(self, filename):
        try:
            return self.backend._query(filename)
        except Exception as e:
            code = _get_code_from_exception(self.backend, 'query', e)
            if code == log.ErrorCode.backend_not_found:
                return {'size': -1}
            else:
                raise e

    def close(self):
        """
        Close the backend, releasing any resources held and
        invalidating any file objects obtained from the backend.
        """
        if hasattr(self.backend, '_close'):
            self.backend._close()

    def get_fileobj_read(self, filename, parseresults=None):
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

    def get_data(self, filename, parseresults=None):
        """
        Retrieve a file from backend, process it, return contents.
        """
        fin = self.get_fileobj_read(filename, parseresults)
        buf = fin.read()
        assert not fin.close()
        return buf

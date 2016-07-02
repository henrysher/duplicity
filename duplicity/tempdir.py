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
Provides temporary file handling cenetered around a single top-level
securely created temporary directory.

The public interface of this module is thread-safe.
"""

import os
import threading
import tempfile

from duplicity import log
from duplicity import util
from duplicity import globals

# Set up state related to managing the default temporary directory
# instance
_defaultLock = threading.Lock()
_defaultInstance = None
# backup the initial tmp dir path because we will force tempfile
# later to use our generated _defaultInstance.dir() as temproot
_initialSystemTempRoot = tempfile.gettempdir()


def default():
    """
    Obtain the global default instance of TemporaryDirectory, creating
    it first if necessary. Failures are propagated to caller. Most
    callers are expected to use this function rather than
    instantiating TemporaryDirectory directly, unless they explicitly
    desdire to have their "own" directory for some reason.

    This function is thread-safe.
    """
    global _defaultLock
    global _defaultInstance

    _defaultLock.acquire()
    try:
        if _defaultInstance is None or _defaultInstance.dir() is None:
            _defaultInstance = TemporaryDirectory(temproot=globals.temproot)
            # set the temp dir to be the default in tempfile module from now on
            tempfile.tempdir = _defaultInstance.dir()
        return _defaultInstance
    finally:
        _defaultLock.release()


class TemporaryDirectory:
    """
    A temporary directory.

    An instance of this class is backed by a directory in the file
    system created securely by the use of tempfile.mkdtemp(). Said
    instance can be used to obtain unique filenames inside of this
    directory for cases where mktemp()-like semantics is desired, or
    (recommended) an fd,filename pair for mkstemp()-like semantics.

    See further below for the security implications of using it.

    Each instance will keep a list of all files ever created by it, to
    faciliate deletion of such files and rmdir() of the directory
    itself. It does this in order to be able to clean out the
    directory without resorting to a recursive delete (ala rm -rf),
    which would be risky. Calling code can optionally (recommended)
    notify an instance of the fact that a tempfile was deleted, and
    thus need not be kept track of anymore.

    This class serves two primary purposes:

    Firstly, it provides a convenient single top-level directory in
    which all the clutter ends up, rather than cluttering up the root
    of the system temp directory itself with many files.

    Secondly, it provides a way to get mktemp() style semantics for
    temporary file creation, with most of the risks
    gone. Specifically, since the directory itself is created
    securely, files in this directory can be (mostly) safely created
    non-atomically without the usual mktemp() security
    implications. However, in the presence of tmpwatch, tmpreaper, or
    similar mechanisms that will cause files in the system tempdir to
    expire, a security risk is still present because the removal of
    the TemporaryDirectory managed directory removes all protection it
    offers.

    For this reason, use of mkstemp() is greatly preferred above use
    of mktemp().

    In addition, since cleanup is in the form of deletion based on a
    list of filenames, completely independently of whether someone
    else already deleted the file, there exists a race here as
    well. The impact should however be limited to the removal of an
    'attackers' file.
    """
    def __init__(self, temproot=None):
        """
        Create a new TemporaryDirectory backed by a unique and
        securely created file system directory.

        tempbase - The temp root directory, or None to use system
        default (recommended).
        """
        if temproot is None:
            if globals.temproot:
                temproot = globals.temproot
            else:
                global _initialSystemTempRoot
                temproot = _initialSystemTempRoot
        self.__dir = tempfile.mkdtemp("-tempdir", "duplicity-", temproot)

        log.Info(_("Using temporary directory %s") % util.ufn(self.__dir))

        # number of mktemp()/mkstemp() calls served so far
        self.__tempcount = 0
        # dict of paths pending deletion; use dict even though we are
        # not concearned with association, because it is unclear whether
        # sets are O(1), while dictionaries are.
        self.__pending = {}

        self.__lock = threading.Lock()  # protect private resources *AND* mktemp/mkstemp calls

    def dir(self):
        """
        Returns the absolute pathname of the temp folder.
        """
        return self.__dir

    def __del__(self):
        """
        Perform cleanup.
        """
        global _defaultInstance
        if _defaultInstance is not None:
            self.cleanup()

    def mktemp(self):
        """
        Return a unique filename suitable for use for a temporary
        file. The file is not created.

        Subsequent calls to this method are guaranteed to never return
        the same filename again. As a result, it is safe to use under
        concurrent conditions.

        NOTE: mkstemp() is greatly preferred.
        """
        filename = None

        self.__lock.acquire()
        try:
            self.__tempcount = self.__tempcount + 1
            suffix = "-%d" % (self.__tempcount,)
            filename = tempfile.mktemp(suffix, "mktemp-", self.__dir)

            log.Debug(_("Registering (mktemp) temporary file %s") % util.ufn(filename))
            self.__pending[filename] = None
        finally:
            self.__lock.release()

        return filename

    def mkstemp(self):
        """
        Returns a filedescriptor and a filename, as per os.mkstemp(),
        but located in the temporary directory and subject to tracking
        and automatic cleanup.
        """
        fd = None
        filename = None

        self.__lock.acquire()
        try:
            self.__tempcount = self.__tempcount + 1
            suffix = "-%d" % (self.__tempcount,)
            fd, filename = tempfile.mkstemp(suffix, "mkstemp-", self.__dir)

            log.Debug(_("Registering (mkstemp) temporary file %s") % util.ufn(filename))
            self.__pending[filename] = None
        finally:
            self.__lock.release()

        return fd, filename

    def mkstemp_file(self):
        """
        Convenience wrapper around mkstemp(), with the file descriptor
        converted into a file object.
        """
        fd, filename = self.mkstemp()

        return os.fdopen(fd, "r+"), filename

    def forget(self, fname):
        """
        Forget about the given filename previously obtained through
        mktemp() or mkstemp(). This should be called *after* the file
        has been deleted, to stop a future cleanup() from trying to
        delete it.

        Forgetting is only needed for scaling purposes; that is, to
        avoid n timefile creations from implying that n filenames are
        kept in memory. Typically this whould never matter in
        duplicity, but for niceness sake callers are recommended to
        use this method whenever possible.
        """
        self.__lock.acquire()
        try:
            if fname in self.__pending:
                log.Debug(_("Forgetting temporary file %s") % util.ufn(fname))
                del(self.__pending[fname])
            else:
                log.Warn(_("Attempt to forget unknown tempfile %s - this is probably a bug.") % util.ufn(fname))
                pass
        finally:
            self.__lock.release()

    def cleanup(self):
        """
        Cleanup any files created in the temporary directory (that
        have not been forgotten), and clean up the temporary directory
        itself.

        On failure they are logged, but this method will not raise an
        exception.
        """
        self.__lock.acquire()
        try:
            if self.__dir is not None:
                for file in self.__pending.keys():
                    try:
                        log.Debug(_("Removing still remembered temporary file %s") % util.ufn(file))
                        util.ignore_missing(os.unlink, file)
                    except Exception:
                        log.Info(_("Cleanup of temporary file %s failed") % util.ufn(file))
                        pass
                try:
                    os.rmdir(self.__dir)
                except Exception:
                    log.Warn(_("Cleanup of temporary directory %s failed - "
                               "this is probably a bug.") % util.ufn(self.__dir))
                    pass
                self.__pending = None
                self.__dir = None
        finally:
            self.__lock.release()

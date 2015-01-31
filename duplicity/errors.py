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
Error/exception classes that do not fit naturally anywhere else.
"""

from duplicity import log


class DuplicityError(Exception):
    pass


class UserError(DuplicityError):
    """
    Subclasses use this in their inheritance hierarchy to signal that
    the error is a user generated one, and that it is therefore
    typically unsuitable to display a full stack trace.
    """
    pass


class NotSupported(DuplicityError):
    """
    Exception raised when an action cannot be completed because some
    particular feature is not supported by the environment.
    """
    pass


class ConflictingScheme(DuplicityError):
    """
    Raised to indicate an attempt was made to register a backend for a
    scheme for which there is already a backend registered.
    """
    pass


class InvalidBackendURL(UserError):
    """
    Raised to indicate a URL was not a valid backend URL.
    """
    pass


class UnsupportedBackendScheme(InvalidBackendURL, UserError):
    """
    Raised to indicate that a backend URL was parsed successfully as a
    URL, but was not supported.
    """
    def __init__(self, url):
        InvalidBackendURL.__init__(self,
                                   ("scheme not supported in url: %s" % (url,)))
        self.url = url


class BackendException(DuplicityError):
    """
    Raised to indicate a backend specific problem.
    """
    def __init__(self, msg, code=log.ErrorCode.backend_error):
        super(BackendException, self).__init__(msg)
        self.code = code


class FatalBackendException(BackendException):
    """
    Raised to indicate a backend failed fatally.
    """
    pass


class TemporaryLoadException(BackendException):
    """
    Raised to indicate a temporary issue on the backend.
    Duplicity should back off for a bit and try again.
    """
    pass

# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2012 Google Inc.
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

"""Cache-wrapped functions for grp and pwd lookups."""

import grp
import pwd


class CachedCall(object):
    """Decorator for caching the results of function calls."""

    def __init__(self, f):
        self.cache = {}
        self.f = f

    def __call__(self, *args):
        try:
            return self.cache[args]
        except (KeyError, TypeError), e:
            result = self.f(*args)
            if not isinstance(e, TypeError):
                # TypeError most likely means that args is not hashable
                self.cache[args] = result
            return result


@CachedCall
def getgrgid(gid):
    return grp.getgrgid(gid)


@CachedCall
def getgrnam(name):
    return grp.getgrnam(name)


@CachedCall
def getpwnam(name):
    return pwd.getpwnam(name)


@CachedCall
def getpwuid(uid):
    return pwd.getpwuid(uid)

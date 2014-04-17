# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2013 Michael Terry <mike@mterry.name>
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

"""Like system tarfile but with caching."""

from __future__ import absolute_import

import tarfile

# Grab all symbols in tarfile, to try to reproduce its API exactly.
# from <> import * wouldn't get everything we want, since tarfile defines
# __all__.  So we do it ourselves.
for sym in dir(tarfile):
    globals()[sym] = getattr(tarfile, sym)

# Now make sure that we cache the grp/pwd ops
from duplicity import cached_ops
grp = pwd = cached_ops

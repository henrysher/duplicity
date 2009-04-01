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
Contains all backends in their respective modules.

This module is responsible for loading all available
sub-modules. Users need only import this module, unless they want to
specifically refer to a particular backend.
"""

import duplicity.backends.botobackend
import duplicity.backends.ftpbackend
import duplicity.backends.imapbackend
import duplicity.backends.hsibackend
import duplicity.backends.localbackend
import duplicity.backends.rsyncbackend
import duplicity.backends.sshbackend
import duplicity.backends.webdavbackend


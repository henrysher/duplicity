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

import os
from duplicity import backend
from duplicity import globals
from duplicity import log

sign_key = '56538CCF'
sign_passphrase = 'test'
encrypt_key1 = 'B5FA894F'
encrypt_key2 = '9B736B2A'

def setup():
    """ setup for unit tests """
    log.setup()
    log.setverbosity(log.WARNING)
    globals.print_statistics = 0
    backend.import_backends()

def set_environ(varname, value):
    if value is not None:
        os.environ[varname] = value
    else:
        try:
            del os.environ[varname]
        except Exception:
            pass

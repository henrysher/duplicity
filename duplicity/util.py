# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
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
Miscellaneous utilities. 
"""

import string
import sys
import traceback

def exception_traceback(limit = 50):
    """
    @return A string representation in typical Python format of the
            currently active/raised exception.
    """
    type, value, tb = sys.exc_info()

    lines = traceback.format_tb(tb, limit)
    lines.extend(traceback.format_exception_only(type, value))
    
    str = "Traceback (innermost last):\n"
    str = str + "%-20s %s" % (string.join(lines[:-1], ""),
                                lines[-1])

    return str

def escape(string):
    return "'%s'" % string.encode("string-escape")


# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2014 Aaron Whitehouse <aaron@whitehouse.kiwi.nz>
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

import unittest
from duplicity.globmatch import *
from . import UnitTestCase


class MatchingTest(UnitTestCase):
    """Test matching of file names against various selection functions"""

    def test_glob_re(self):
        """test_glob_re - test translation of shell pattern to regular exp"""
        assert glob_to_regex("hello") == "hello"
        assert glob_to_regex(".e?ll**o") == "\\.e[^/]ll.*o"
        r = glob_to_regex("[abc]el[^de][!fg]h")
        assert r == "[abc]el[^de][^fg]h", r
        r = glob_to_regex("/usr/*/bin/")
        assert r == "\\/usr\\/[^/]*\\/bin\\/", r
        assert glob_to_regex("[a.b/c]") == "[a.b/c]"
        r = glob_to_regex("[a*b-c]e[!]]")
        assert r == "[a*b-c]e[^]]", r
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2014 Michael Terry <michael.terry@canonical.com>
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

import helper
import os
import subprocess
import unittest

helper.setup()


class Python3ReadinessTest(unittest.TestCase):
    def test_2to3(self):
        _top_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..")

        # As we modernize the source code, we can remove more and more nofixes
        output = subprocess.check_output(["2to3",
                                          "--nofix=apply",
                                          "--nofix=basestring",
                                          "--nofix=callable",
                                          "--nofix=dict",
                                          "--nofix=except",
                                          "--nofix=filter",
                                          "--nofix=future",
                                          "--nofix=has_key",
                                          "--nofix=idioms",
                                          "--nofix=import",
                                          "--nofix=imports",
                                          "--nofix=long",
                                          "--nofix=map",
                                          "--nofix=next",
                                          "--nofix=numliterals",
                                          "--nofix=print",
                                          "--nofix=raise",
                                          "--nofix=raw_input",
                                          "--nofix=reduce",
                                          "--nofix=renames",
                                          "--nofix=types",
                                          "--nofix=unicode",
                                          "--nofix=urllib",
                                          "--nofix=ws_comma",
                                          "--nofix=xrange",
                                          _top_dir],
                                         stderr=subprocess.PIPE)
        self.assertEqual("", output, output)


if __name__ == "__main__":
    unittest.main()

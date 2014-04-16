# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2008 Michael Terry <mike@mterry.name>
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
import os

class LogTest(unittest.TestCase):
    """Test machine-readable functions/classes in log.py"""

    def setUp(self):
        assert not os.system("rm -f /tmp/duplicity.log")

    def tearDown(self):
        assert not os.system("rm -f /tmp/duplicity.log")

    def test_command_line_error(self):
        """Check notification of a simple error code"""

        # Run actual duplicity command (will fail, because no arguments passed)
        os.system("duplicity --log-file=/tmp/duplicity.log >/dev/null 2>&1")

        # The format of the file should be:
        # """ERROR 2
        # . Blah blah blah.
        # . Blah blah blah.
        #
        # """
        f = open('/tmp/duplicity.log', 'r')
        linecount = 0
        lastline = False
        for line in f:
            assert(not lastline)
            linecount += 1
            if linecount == 1:
                assert(line == "ERROR 2\n")
            elif line != "\n":
                assert(line.startswith(". "))
            else:
                lastline = True
        assert(lastline)


if __name__ == "__main__":
    unittest.main()

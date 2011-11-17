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

import helper
import sys, unittest

import duplicity.backend
import duplicity.backends #@UnusedImport
from duplicity.errors import * #@UnusedWildImport

helper.setup()

class ParsedUrlTest(unittest.TestCase):
    """Test the ParsedUrl class"""
    def test_basic(self):
        """Test various url strings"""
        pu = duplicity.backend.ParsedUrl("scp://ben@foo.bar:1234/a/b")
        assert pu.scheme == "scp", pu.scheme
        assert pu.netloc == "ben@foo.bar:1234", pu.netloc
        assert pu.path =="/a/b", pu.path
        assert pu.username == "ben", pu.username
        assert pu.port == 1234, pu.port
        assert pu.hostname == "foo.bar", pu.hostname

        pu = duplicity.backend.ParsedUrl("ftp://foo.bar:1234/")
        assert pu.scheme == "ftp", pu.scheme
        assert pu.netloc == "foo.bar:1234", pu.netloc
        assert pu.path == "/", pu.path
        assert pu.username is None, pu.username
        assert pu.port == 1234, pu.port
        assert pu.hostname == "foo.bar", pu.hostname

        pu = duplicity.backend.ParsedUrl("file:///home")
        assert pu.scheme == "file", pu.scheme
        assert pu.netloc == "", pu.netloc
        assert pu.path == "///home", pu.path
        assert pu.username is None, pu.username
        assert pu.port is None, pu.port

        pu = duplicity.backend.ParsedUrl("ftp://foo@bar:pass@example.com:123/home")
        assert pu.scheme == "ftp", pu.scheme
        assert pu.netloc == "foo@bar:pass@example.com:123", pu.netloc
        assert pu.hostname == "example.com", pu.hostname
        assert pu.path == "/home", pu.path
        assert pu.username == "foo@bar", pu.username
        assert pu.password == "pass", pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl("ftp://foo%40bar:pass@example.com:123/home")
        assert pu.scheme == "ftp", pu.scheme
        assert pu.netloc == "foo%40bar:pass@example.com:123", pu.netloc
        assert pu.hostname == "example.com", pu.hostname
        assert pu.path == "/home", pu.path
        assert pu.username == "foo@bar", pu.username
        assert pu.password == "pass", pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl("imap://foo@bar:pass@example.com:123/home")
        assert pu.scheme == "imap", pu.scheme
        assert pu.netloc == "foo@bar:pass@example.com:123", pu.netloc
        assert pu.hostname == "example.com", pu.hostname
        assert pu.path == "/home", pu.path
        assert pu.username == "foo@bar", pu.username
        assert pu.password == "pass", pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl("imap://foo@bar@example.com:123/home")
        assert pu.scheme == "imap", pu.scheme
        assert pu.netloc == "foo@bar@example.com:123", pu.netloc
        assert pu.hostname == "example.com", pu.hostname
        assert pu.path == "/home", pu.path
        assert pu.username == "foo@bar", pu.username
        assert pu.password == None, pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl("imap://foo@bar@example.com/home")
        assert pu.scheme == "imap", pu.scheme
        assert pu.netloc == "foo@bar@example.com", pu.netloc
        assert pu.hostname == "example.com", pu.hostname
        assert pu.path == "/home", pu.path
        assert pu.username == "foo@bar", pu.username
        assert pu.password == None, pu.password
        assert pu.port == None, pu.port

        pu = duplicity.backend.ParsedUrl("imap://foo@bar.com@example.com/home")
        assert pu.scheme == "imap", pu.scheme
        assert pu.netloc == "foo@bar.com@example.com", pu.netloc
        assert pu.hostname == "example.com", pu.hostname
        assert pu.path == "/home", pu.path
        assert pu.username == "foo@bar.com", pu.username
        assert pu.password == None, pu.password
        assert pu.port == None, pu.port

        pu = duplicity.backend.ParsedUrl("imap://foo%40bar.com@example.com/home")
        assert pu.scheme == "imap", pu.scheme
        assert pu.netloc == "foo%40bar.com@example.com", pu.netloc
        assert pu.hostname == "example.com", pu.hostname
        assert pu.path == "/home", pu.path
        assert pu.username == "foo@bar.com", pu.username
        assert pu.password == None, pu.password
        assert pu.port == None, pu.port

    def test_errors(self):
        """Test various url errors"""
        self.assertRaises(InvalidBackendURL, duplicity.backend.ParsedUrl,
                          "ssh://foo@bar:pass@example.com:/home")
        self.assertRaises(UnsupportedBackendScheme, duplicity.backend.get_backend,
                          "foo://foo@bar:pass@example.com/home")


if __name__ == "__main__":
    unittest.main()

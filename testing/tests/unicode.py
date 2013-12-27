# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2012 Canonical Ltd
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

import sys
import unittest
from mock import patch


class UTF8Test(unittest.TestCase):

    def setUp(self):
        if 'duplicity' in sys.modules:
            del(sys.modules["duplicity"])

    @patch('gettext.translation')
    def test_module_install(self, gettext_mock):
        """Make sure we convert translations to unicode"""
        import duplicity
        gettext_mock.assert_called_once_with('duplicity', fallback=True)
        gettext_mock.return_value.install.assert_called_once_with(unicode=True)
        assert ngettext is gettext_mock.return_value.ungettext

if __name__ == "__main__":
    unittest.main()

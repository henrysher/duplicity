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
import unittest, types, sys

from duplicity.static import * #@UnusedWildImport

helper.setup()

class D:
    def foo(x, y): #@NoSelf
        return x, y
    def bar(self, x):
        return 3, x
    def _hello(self):
        return self

MakeStatic(D)


class C:
    _a = 0
    def get(cls): #@NoSelf
        return cls._a
    def inc(cls): #@NoSelf
        cls._a = cls._a + 1

MakeClass(C)


class StaticMethodsTest(unittest.TestCase):
    """Test StaticMethods module"""
    def testType(self):
        """Methods should have type StaticMethod"""
        assert type(D.foo) is types.FunctionType
        assert type(D.bar) is types.FunctionType

    def testStatic(self):
        """Methods should be callable without instance"""
        assert D.foo(1,2) == (1,2)
        assert D.bar(3,4) == (3,4)

    def testBound(self):
        """Methods should also work bound"""
        d = D()
        assert d.foo(1,2) == (1,2)
        assert d.bar(3,4) == (3,4)

    def testStatic_(self):
        """_ Methods should be untouched"""
        d = D()
        self.assertRaises(TypeError, d._hello, 4)
        assert d._hello() is d


class ClassMethodsTest(unittest.TestCase):
    def test(self):
        """Test MakeClass function"""
        assert C.get() == 0
        C.inc()
        assert C.get() == 1
        C.inc()
        assert C.get() == 2


if __name__ == "__main__":
    unittest.main()

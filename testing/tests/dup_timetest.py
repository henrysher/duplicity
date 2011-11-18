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
import sys, unittest, time, types
from copy import copy
from duplicity import globals
from duplicity import dup_time

helper.setup()

class TimeTest:
    def testConversion(self):
        """test timetostring and stringtotime"""
        dup_time.setcurtime()
        assert type(dup_time.curtime) in (types.IntType, types.LongType)
        assert type(dup_time.curtimestr) is types.StringType
        assert (dup_time.cmp(int(dup_time.curtime), dup_time.curtimestr) == 0 or
                dup_time.cmp(int(dup_time.curtime) + 1, dup_time.curtimestr) == 0)
        time.sleep(1.05)
        assert dup_time.cmp(time.time(), dup_time.curtime) == 1
        assert dup_time.cmp(dup_time.timetostring(time.time()), dup_time.curtimestr) == 1

    def testConversion_separator(self):
        """Same as testConversion, but change time Separator"""
        prev_sep = copy(globals.time_separator)
        try:
            globals.time_separator = "_"
            self.testConversion()
        finally:
            globals.time_separator = prev_sep

    def testCmp(self):
        """Test time comparisons"""
        cmp = dup_time.cmp
        assert cmp(1,2) == -1
        assert cmp(2,2) == 0
        assert cmp(5,1) == 1
        assert cmp("2001-09-01T21:49:04Z", "2001-08-01T21:49:04Z") == 1
        assert cmp("2001-09-01T04:49:04+03:23", "2001-09-01T21:49:04Z") == -1
        assert cmp("2001-09-01T12:00:00Z", "2001-09-01T04:00:00-08:00") == 0
        assert cmp("2001-09-01T12:00:00-08:00", "2001-09-01T12:00:00-07:00") == 1
        assert cmp("2001-09-01T11:00:00Z", "20010901T120000Z") == -1
        assert cmp("2001-09-01T12:00:00Z", "20010901T120000Z") == 0
        assert cmp("2001-09-01T13:00:00Z", "20010901T120000Z") == 1

    def testCmp_separator(self):
        """Like testCmp but with new separator"""
        prev_sep = copy(globals.time_separator)
        try:
            globals.time_separator = "_"
            cmp = dup_time.cmp
            assert cmp(1,2) == -1
            assert cmp(2,2) == 0
            assert cmp(5,1) == 1
            assert cmp("2001-09-01T21_49_04Z", "2001-08-01T21_49_04Z") == 1
            assert cmp("2001-09-01T04_49_04+03_23", "2001-09-01T21_49_04Z") == -1
            assert cmp("2001-09-01T12_00_00Z", "2001-09-01T04_00_00-08_00") == 0
            assert cmp("2001-09-01T12_00_00-08_00", "2001-09-01T12_00_00-07_00") == 1
        finally:
            globals.time_separator = prev_sep

    def testStringtotime(self):
        """Test converting string to time"""
        timesec = int(time.time())
        assert timesec == int(dup_time.stringtotime(dup_time.timetostring(timesec)))
        assert not dup_time.stringtotime("2001-18-83T03:03:03Z")
        assert not dup_time.stringtotime("2001-01-23L03:03:03L")
        assert not dup_time.stringtotime("2001_01_23T03:03:03Z")

    def testIntervals(self):
        """Test converting strings to intervals"""
        i2s = dup_time.intstringtoseconds
        for s in ["32", "", "d", "231I", "MM", "s", "-2h"]:
            try: i2s(s)
            except dup_time.TimeException: pass
            else: assert 0, s
        assert i2s("7D") == 7*86400
        assert i2s("232s") == 232
        assert i2s("2M") == 2*30*86400
        assert i2s("400m") == 400*60
        assert i2s("1Y") == 365*86400
        assert i2s("30h") == 30*60*60
        assert i2s("3W") == 3*7*86400

    def testIntervalsComposite(self):
        """Like above, but allow composite intervals"""
        i2s = dup_time.intstringtoseconds
        assert i2s("7D2h") == 7*86400 + 2*3600
        assert i2s("2Y3s") == 2*365*86400 + 3
        assert i2s("1M2W4D2h5m20s") == (30*86400 + 2*7*86400 + 4*86400 +
                                        2*3600 + 5*60 + 20)

    def testPrettyIntervals(self):
        """Test printable interval conversion"""
        assert dup_time.inttopretty(3600) == "1 hour"
        assert dup_time.inttopretty(7220) == "2 hours 20 seconds"
        assert dup_time.inttopretty(0) == "0 seconds"
        assert dup_time.inttopretty(353) == "5 minutes 53 seconds"
        assert dup_time.inttopretty(3661) == "1 hour 1 minute 1 second"
        assert dup_time.inttopretty(353.234234) == "5 minutes 53.23 seconds"

    def testGenericString(self):
        """Test genstrtotime, conversion of arbitrary string to time"""
        g2t = dup_time.genstrtotime
        assert g2t('now', 1000) == 1000
        assert g2t('2h3s', 10000) == 10000 - 2*3600 - 3
        assert g2t('2001-09-01T21:49:04Z') == \
               dup_time.stringtotime('2001-09-01T21:49:04Z')
        assert g2t('2002-04-26T04:22:01') == \
               dup_time.stringtotime('2002-04-26T04:22:01' + dup_time.gettzd(0))
        t = dup_time.stringtotime('2001-05-12T00:00:00' + dup_time.gettzd(0))
        assert g2t('2001-05-12') == t
        assert g2t('2001/05/12') == t
        assert g2t('5/12/2001') == t
        assert g2t('123456') == 123456

    def testGenericStringErrors(self):
        """Test genstrtotime on some bad strings"""
        g2t = dup_time.genstrtotime
        self.assertRaises(dup_time.TimeException, g2t, "hello")
        self.assertRaises(dup_time.TimeException, g2t, "")
        self.assertRaises(dup_time.TimeException, g2t, "3q")
    
    def testConvertion(self):
        t = int(time.time())
        assert dup_time.stringtotime(dup_time.timetostring(t)) == t

class TimeTest1(TimeTest, unittest.TestCase):
    
    def setUp(self):
        globals.old_filenames = False

class TimeTest2(TimeTest, unittest.TestCase):
    
    def setUp(self):
        globals.old_filenames = True

if __name__ == '__main__':
    unittest.main()

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

from duplicity.statistics import * #@UnusedWildImport
from duplicity import path

helper.setup()

class StatsObjTest(unittest.TestCase):
    """Test StatsObj class"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def set_obj(self, s):
        """Set values of s's statistics"""
        s.SourceFiles = 1
        s.SourceFileSize = 2
        s.NewFiles = 3
        s.NewFileSize = 4
        s.DeletedFiles = 5
        s.ChangedFiles = 7
        s.ChangedFileSize = 8
        s.ChangedDeltaSize = 9
        s.DeltaEntries = 10
        s.RawDeltaSize = 11
        s.TotalDestinationSizeChange = 12
        s.StartTime = 13
        s.EndTime = 14

    def test_get_stats(self):
        """Test reading and writing stat objects"""
        s = StatsObj()
        assert s.get_stat('SourceFiles') is None
        self.set_obj(s)
        assert s.get_stat('SourceFiles') == 1

        s1 = StatsDeltaProcess()
        assert s1.get_stat('SourceFiles') == 0

    def test_get_stats_string(self):
        """Test conversion of stat object into string"""
        s = StatsObj()
        stats_string = s.get_stats_string()
        assert stats_string == "", stats_string

        self.set_obj(s)
        stats_string = s.get_stats_string()
        assert stats_string == \
"""StartTime 13.00 (Wed Dec 31 18:00:13 1969)
EndTime 14.00 (Wed Dec 31 18:00:14 1969)
ElapsedTime 1.00 (1 second)
SourceFiles 1
SourceFileSize 2 (2 bytes)
NewFiles 3
NewFileSize 4 (4 bytes)
DeletedFiles 5
ChangedFiles 7
ChangedFileSize 8 (8 bytes)
ChangedDeltaSize 9 (9 bytes)
DeltaEntries 10
RawDeltaSize 11 (11 bytes)
TotalDestinationSizeChange 12 (12 bytes)
""", "'%s'" % stats_string

    def test_line_string(self):
        """Test conversion to a single line"""
        s = StatsObj()
        self.set_obj(s)
        statline = s.get_stats_line(("sample", "index", "w", "new\nline"))
        assert statline == "sample/index/w/new\\nline 1 2 3 4 5 7 8 9 10 11",\
               repr(statline)

        statline = s.get_stats_line(())
        assert statline == ". 1 2 3 4 5 7 8 9 10 11"

        statline = s.get_stats_line(("file name with spaces",))
        assert statline == ("file\\x20name\\x20with\\x20spaces " \
                            "1 2 3 4 5 7 8 9 10 11"), repr(statline)

    def test_byte_summary(self):
        """Test conversion of bytes to strings like 7.23MB"""
        s = StatsObj()
        f = s.get_byte_summary_string
        assert f(1) == "1 byte"
        assert f(234.34) == "234 bytes"
        assert f(2048) == "2.00 KB"
        assert f(3502243) == "3.34 MB"
        assert f(314992230) == "300 MB"
        assert f(36874871216) == "34.3 GB", f(36874871216)
        assert f(3775986812573450) == "3434 TB"

    def test_init_stats(self):
        """Test setting stat object from string"""
        s = StatsObj()
        s.set_stats_from_string("NewFiles 3 hello there")
        for attr in s.stat_attrs:
            if attr == 'NewFiles': assert s.get_stat(attr) == 3
            else: assert s.get_stat(attr) is None, (attr, s.__dict__[attr])

        s1 = StatsObj()
        self.set_obj(s1)
        assert not s1.stats_equal(s)

        s2 = StatsObj()
        s2.set_stats_from_string(s1.get_stats_string())
        assert s1.stats_equal(s2)

    def test_write_path(self):
        """Test reading and writing of statistics object"""
        p = path.Path("testfiles/statstest")
        if p.exists(): p.delete()
        s = StatsObj()
        self.set_obj(s)
        s.write_stats_to_path(p)

        s2 = StatsObj()
        assert not s2.stats_equal(s)
        s2.read_stats_from_path(p)
        assert s2.stats_equal(s)

    def testAverage(self):
        """Test making an average statsobj"""
        s1 = StatsObj()
        s1.StartTime = 5
        s1.EndTime = 10
        s1.ElapsedTime = 5
        s1.ChangedFiles = 2
        s1.SourceFiles = 100
        s1.NewFileSize = 4

        s2 = StatsObj()
        s2.StartTime = 25
        s2.EndTime = 35
        s2.ElapsedTime = 10
        s2.ChangedFiles = 1
        s2.SourceFiles = 50
        s2.DeletedFiles = 0

        s3 = StatsObj().set_to_average([s1, s2])
        assert s3.StartTime is s3.EndTime is None
        assert s3.ElapsedTime == 7.5
        assert s3.DeletedFiles is s3.NewFileSize is None, (s3.DeletedFiles,
                                                           s3.NewFileSize)
        assert s3.ChangedFiles == 1.5
        assert s3.SourceFiles == 75


if __name__ == "__main__":
    unittest.main()

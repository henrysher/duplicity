# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-

import config
import sys, os, unittest, cStringIO
sys.path.insert(0, "../")
from duplicity import misc, log

config.setup()

class MiscTest(unittest.TestCase):
    """Test functions/classes in misc.py"""
    def deltmp(self):
        assert not os.system("rm -rf testfiles/output")
        os.mkdir("testfiles/output")

    def test_file_volume_writer(self):
        """Test FileVolumeWriter class"""
        self.deltmp()
        s = "hello" * 10000
        assert len(s) == 50000
        infp = cStringIO.StringIO(s)
        fvw = misc.FileVolumeWriter(infp, "testfiles/output/volume")
        fvw.volume_size = 20000
        fvw.blocksize = 5000

        l = []
        for filename in fvw: l.append(filename)
        assert l == ['testfiles/output/volume.1',
                     'testfiles/output/volume.2',
                     'testfiles/output/volume.3'], l

        s2 = ""
        for filename in l:
            infp2 = open(filename, "rb")
            s2 += infp2.read()
            assert not infp2.close()

        assert s2 == s

    def test_file_volume_writer2(self):
        """Test again but one volume this time"""
        self.deltmp()
        fvw = misc.FileVolumeWriter(cStringIO.StringIO("hello, world!"),
                                    "testfiles/output/one_vol")
        assert fvw.next() == "testfiles/output/one_vol"
        self.assertRaises(StopIteration, fvw.next)

    def test_file_volume_writer3(self):
        """Test case when end of file falls exactly on volume boundary"""
        self.deltmp()
        s = "hello" * 10000
        assert len(s) == 50000
        infp = cStringIO.StringIO(s)
        fvw = misc.FileVolumeWriter(infp, "testfiles/output/volume")
        fvw.volume_size = 25000
        fvw.blocksize = 5000

        l = []
        for filename in fvw: l.append(filename)
        assert l == ['testfiles/output/volume.1',
                     'testfiles/output/volume.2']



if __name__ == "__main__":
    unittest.main()

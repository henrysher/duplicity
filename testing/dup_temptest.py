import config
import sys, os, unittest, gzip
sys.path.insert(0, "../")
from duplicity import dup_temp, file_naming

config.setup()

prefix = "testfiles/output"

class TempTest(unittest.TestCase):
    """Test various temp files methods"""
    def del_tmp(self):
        """Delete testfiles/output and recreate"""
        assert not os.system("rm -rf " + prefix)
        assert not os.system("mkdir " + prefix)

    def test_temppath(self):
        """Allocate new temppath, try open_with_delete"""
        tp = dup_temp.new_temppath()
        assert not tp.exists()
        fileobj = tp.open("wb")
        fileobj.write("hello, there")
        fileobj.close()
        tp.setdata()
        assert tp.isreg()

        fin = tp.open_with_delete("rb")
        buf = fin.read()
        assert buf == "hello, there", buf
        fin.close()
        assert not tp.exists()

    def test_tempduppath(self):
        """Allocate new tempduppath, then open_with_delete"""
        # pr indicates file is gzipped
        pr = file_naming.ParseResults("inc", manifest = 1,
                                      start_time = 1, end_time = 3,
                                      compressed = 1)

        tdp = dup_temp.new_tempduppath(pr)
        assert not tdp.exists()
        fout = tdp.filtered_open("wb")
        fout.write("hello, there")
        fout.close()
        tdp.setdata()
        assert tdp.isreg()

        fin1 = gzip.GzipFile(tdp.name, "rb")
        buf = fin1.read()
        assert buf == "hello, there", buf
        fin1.close()

        fin2 = tdp.filtered_open_with_delete("rb")
        buf2 = fin2.read()
        assert buf2 == "hello, there", buf
        fin2.close()
        assert not tdp.exists()


if __name__ == "__main__":
    unittest.main()

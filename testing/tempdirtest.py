import sys
sys.path.insert(0, "../")
import os, unittest, gzip

from duplicity import tempdir

class TempDirTest(unittest.TestCase):
	def test_all(self):
		td = tempdir.default()

		self.assert_(td.mktemp() != td.mktemp())

		dir = td.mktemp()
		os.mkdir(dir)
		os.rmdir(dir)

		fd, fname = td.mkstemp()
		os.close(fd)
		os.unlink(fname)
		td.forget(fname)

		fo, fname = td.mkstemp_file()
		fo.close() # don't forget, leave to cleanup()

		td.cleanup()        

if __name__ == "__main__":
	unittest.main()


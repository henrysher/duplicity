import config
import sys, os, unittest
sys.path.insert(0, "../")
from duplicity import log
from duplicity.path import *

config.setup()

class PathTest(unittest.TestCase):
	"""Test basic path functions"""
	def test_deltree(self):
		"""Test deleting a tree"""
		assert not os.system("rm -rf testfiles/output")
		assert not os.system("cp -a testfiles/deltree testfiles/output")
		p = Path("testfiles/output")
		assert p.isdir()
		p.deltree()
		assert not p.type, p.type

	def test_compare(self):
		"""Test directory comparisons"""
		assert not os.system("rm -rf testfiles/output")
		assert not os.system("cp -a testfiles/dir1 testfiles/output")
		assert Path("testfiles/dir1").compare_recursive(Path("testfiles/output"), 1)
		assert not Path("testfiles/dir1").compare_recursive(Path("testfiles/dir2"), 1)

	def test_quote(self):
		"""Test path quoting"""
		p = Path("hello")
		assert p.quote() == '"hello"'
		assert p.quote("\\") == '"\\\\"', p.quote("\\")
		assert p.quote("$HELLO") == '"\\$HELLO"'

	def test_unquote(self):
		"""Test path unquoting"""
		p = Path("foo") # just to provide unquote function
		def t(s):
			"""Run test on string s"""
			quoted_version = p.quote(s)
			unquoted = p.unquote(quoted_version)
			assert unquoted == s, (unquoted, s)

		t("\\")
		t("$HELLO")
		t(" aoe aoe \\ \n`")

	def test_canonical(self):
		"""Test getting canonical version of path"""
		c = Path(".").get_canonical()
		assert c == ".", c

		c = Path("//foo/bar/./").get_canonical()
		assert c == "/foo/bar", c

	def test_compare_verbose(self):
		"""Run compare_verbose on a few files"""
		vft = Path("testfiles/various_file_types")
		assert vft.compare_verbose(vft)
		reg_file = vft.append("regular_file")
		assert not vft.compare_verbose(reg_file)
		assert reg_file.compare_verbose(reg_file)
		file2 = vft.append("executable")
		assert not file2.compare_verbose(reg_file)
		assert file2.compare_verbose(file2)
		

if __name__ == "__main__":
	unittest.main()

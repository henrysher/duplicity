import sys, unittest, os
sys.path.insert(0, "../duplicity")
import backends, path, log, file_naming, dup_time, globals, gpg

log.setverbosity(7)

class UnivTest:
	"""Contains methods that help test any backend"""
	def try_basic(self, backend):
		"""Try basic operations with given backend.

		Requires backend be empty at first, and all operations are
		allowed.

		"""
		def cmp_list(l):
			"""Assert that backend.list is same as l"""
			blist = backend.list()
			blist.sort()
			l.sort()
			assert blist == l, \
				   ("Got list: %s\nWanted: %s\n" % (repr(blist), repr(l)))

		assert not os.system("rm -rf testfiles/backend_tmp")
		assert not os.system("mkdir testfiles/backend_tmp")

		regpath = path.Path("testfiles/various_file_types/regular_file")
		normal_file = "testfile"
		colonfile = ("file%swith.%scolons_-etc%s%s" %
					 ((globals.time_separator,) * 4))
		tmpregpath = path.Path("testfiles/backend_tmp/regfile")

		# Test list and put
		cmp_list([])
		backend.put(regpath, normal_file)
		cmp_list([normal_file])
		backend.put(regpath, colonfile)
		cmp_list([normal_file, colonfile])

		# Test get
		regfilebuf = regpath.open("rb").read()
		backend.get(colonfile, tmpregpath)
		backendbuf = tmpregpath.open("rb").read()
		assert backendbuf == regfilebuf
		
		# Test delete
		self.assertRaises(backends.BackendException,
						  backend.delete, ["aoeuaoeu"])
		backend.delete([colonfile, normal_file])
		cmp_list([])

	def try_fileobj_filename(self, backend, filename):
		"""Use get_fileobj_write and get_fileobj_read on filename around"""
		fout = backend.get_fileobj_write(filename)
		fout.write("hello, world!")
		fout.close()
		assert filename in backend.list()

		fin = backend.get_fileobj_read(filename)
		buf = fin.read()
		fin.close()
		assert buf == "hello, world!", buf

	def try_fileobj_ops(self, backend):
		"""Test above try_fileobj_filename with a few filenames"""
		# Must set dup_time strings because they are used by file_naming
		dup_time.setcurtime(2000)
		dup_time.setprevtime(1000)
		# Also set profile for encryption
		globals.gpg_profile = gpg.GPGProfile(passphrase = "foobar")

		filename1 = file_naming.get('full', manifest = 1, gzipped = 1)
		self.try_fileobj_filename(backend, filename1)

		filename2 = file_naming.get('new-sig', encrypted = 1)
		self.try_fileobj_filename(backend, filename2)

	def del_tmp(self):
		"""Delete and create testfiles/output"""
		assert not os.system("rm -rf testfiles/output")
		assert not os.system("mkdir testfiles/output")

class ParsedUrlTest(unittest.TestCase):
	"""Test the ParsedUrl class"""
	def test_basic(self):
		"""Test various url strings"""
		pu = backends.ParsedUrl("scp://ben@foo.bar:1234/a/b")
		assert pu.protocol == "scp", pu.protocol
		assert pu.suffix == "ben@foo.bar:1234/a/b"
		assert pu.user == "ben", pu.user
		assert pu.port == 1234, pu.port
		assert pu.host == "foo.bar", pu.host

		pu = backends.ParsedUrl("ftp://foo.bar:1234/")
		assert pu.protocol == "ftp", pu.protocol
		assert pu.suffix == "foo.bar:1234/"
		assert pu.user is None, pu.user
		assert pu.port == 1234, pu.port
		assert pu.host == "foo.bar", pu.host

		pu = backends.ParsedUrl("file:///home")
		assert pu.protocol == "file", pu.protocol
		assert pu.suffix == "/home"
		assert pu.user is None, pu.user
		assert pu.port is None, pu.port


class LocalTest(unittest.TestCase, UnivTest):
	"""Test the Local backend"""
	parsed_url = backends.ParsedUrl("file://testfiles/output")

	def test_basic(self):
		"""Test basic backend operations"""
		self.del_tmp()
		self.try_basic(backends.LocalBackend(self.parsed_url))

	def test_fileobj_ops(self):
		"""Test fileobj operations"""
		self.try_fileobj_ops(backends.LocalBackend(self.parsed_url))

class scpTest(unittest.TestCase, UnivTest):
	"""Test the SSH backend by logging into local host"""
	# Change this for your own host
	url_string = "ssh://localhost//home/ben/prog/python/" \
				 "duplicity/testing/testfiles/output"

	def test_basic(self):
		self.del_tmp()
		self.try_basic(backends.get_backend(self.url_string))
		
	def test_fileobj_ops(self):
		self.try_fileobj_ops(backends.get_backend(self.url_string))

class ftpTest(unittest.TestCase, UnivTest):
	"""Test the ftp backend"""
	# This constant should be changed for your own computer
	url_string = "ftp://Stan Ford@90-92L-imac.stanford.edu/Macintosh HD/temp"
	parsed_url = backends.ParsedUrl(url_string)
	globals.time_separator = "_"
	globals.short_filenames = 1

	def del_tmp(self):
		"""Remove all files from test directory"""
		backend = backends.ftpBackend(self.parsed_url)
		backend.delete(backend.list())
		backend.close()

	def test_basic(self):
		self.del_tmp()
		self.try_basic(backends.get_backend(self.url_string))		

	def test_fileobj_ops(self):
		self.try_fileobj_ops(backends.get_backend(self.url_string))


if __name__ == "__main__": unittest.main()


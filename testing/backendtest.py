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
			assert blist == l, \
				   ("Got list: %s\nWanted: %s\n" % (repr(blist), repr(l)))

		assert not os.system("rm -rf testfiles/backend_tmp")
		assert not os.system("mkdir testfiles/backend_tmp")

		regpath = path.Path("testfiles/various_file_types/regular_file")
		colonfile = "file:with.colons_and:some-other::chars"
		tmpregpath = path.Path("testfiles/backend_tmp/regfile")

		# Test list and put
		cmp_list([])
		backend.put(regpath, colonfile)
		cmp_list([colonfile])

		# Test get
		regfilebuf = regpath.open("rb").read()
		backend.get(colonfile, tmpregpath)
		backendbuf = tmpregpath.open("rb").read()
		assert backendbuf == regfilebuf
		
		# Test delete
		self.assertRaises(backends.BackendException,
						  backend.delete, ["aoeuaoeu"])
		backend.delete([colonfile])
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

class LocalTest(unittest.TestCase, UnivTest):
	"""Test the Local backend"""
	def test_basic(self):
		"""Test basic backend operations"""
		self.del_tmp()
		self.try_basic(backends.LocalBackend("testfiles/output"))

	def test_fileobj_ops(self):
		"""Test fileobj operations"""
		self.try_fileobj_ops(backends.LocalBackend("testfiles/output"))

class scpTest(unittest.TestCase, UnivTest):
	"""Test the SSH backend"""
	def test_basic(self):
		"""Test backends - ssh into local host"""
		self.del_tmp()
		url_string = "ssh://localhost//home/ben/prog/python/" \
					 "duplicity/testing/testfiles/output"
		self.try_basic(backends.get_backend(url_string))
		
	def test_fileobj_ops(self):
		"""Test fileobj operations"""
		url_string = "ssh://localhost//home/ben/prog/python/" \
					 "duplicity/testing/testfiles/output"
		self.try_fileobj_ops(backends.get_backend(url_string))


if __name__ == "__main__": unittest.main()


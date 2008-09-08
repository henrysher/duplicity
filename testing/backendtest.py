import config
import sys, unittest, os
sys.path.insert(0, "../")

import duplicity.backend
import duplicity.backends

from duplicity.errors import *
from duplicity import path, log, file_naming, dup_time, globals, gpg

config.setup()

class UnivTest:
	"""Contains methods that help test any backend"""
	def del_tmp(self):
		"""Remove all files from test directory"""
		config.set_environ("FTP_PASSWORD", self.password)
		backend = duplicity.backend.get_backend(self.url_string)
		backend.delete(backend.list())
		backend.close()
		"""Delete and create testfiles/output"""
		assert not os.system("rm -rf testfiles/output")
		assert not os.system("mkdir testfiles/output")

	def test_basic(self):
		"""Test basic backend operations"""
		config.set_environ("FTP_PASSWORD", self.password)
		self.del_tmp()
		self.try_basic(duplicity.backend.get_backend(self.url_string))

	def test_fileobj_ops(self):
		"""Test fileobj operations"""
		config.set_environ("FTP_PASSWORD", self.password)
		self.try_fileobj_ops(duplicity.backend.get_backend(self.url_string))

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
		colonfile = ("file%swith.%scolons_-and%s%setc" %
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
		self.assertRaises(BackendException,
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

		backend.delete ([filename])

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


class ParsedUrlTest(unittest.TestCase):
	"""Test the ParsedUrl class"""
	def test_basic(self):
		"""Test various url strings"""
		pu = duplicity.backend.ParsedUrl("scp://ben@foo.bar:1234/a/b")
		assert pu.scheme == "scp", pu.scheme
		assert pu.netloc == "ben@foo.bar:1234", pu.netloc
		assert pu.path =="/a/b", pu.path
		assert pu.username == "ben", pu.username
		assert pu.port == 1234, pu.port
		assert pu.hostname == "foo.bar", pu.hostname

		pu = duplicity.backend.ParsedUrl("ftp://foo.bar:1234/")
		assert pu.scheme == "ftp", pu.scheme
		assert pu.netloc == "foo.bar:1234", pu.netloc
		assert pu.path == "/", pu.path
		assert pu.username is None, pu.username
		assert pu.port == 1234, pu.port
		assert pu.hostname == "foo.bar", pu.hostname

		pu = duplicity.backend.ParsedUrl("file:///home")
		assert pu.scheme == "file", pu.scheme
		assert pu.netloc == "", pu.netloc
		assert pu.path == "///home", pu.path
		assert pu.username is None, pu.username
		assert pu.port is None, pu.port

		pu = duplicity.backend.ParsedUrl("ftp://foo@bar:pass@example.com:123/home")
		assert pu.scheme == "ftp", pu.scheme
		assert pu.netloc == "foo@bar:pass@example.com:123", pu.netloc
		assert pu.hostname == "example.com", pu.hostname
		assert pu.path == "/home", pu.path
		assert pu.username == "foo@bar", pu.username
		assert pu.password == "pass"
		assert pu.port == 123, pu.port


class LocalTest(unittest.TestCase, UnivTest):
	"""Test the Local backend"""
	url_string = config.file_url
	password = config.file_password


class scpTest(unittest.TestCase, UnivTest):
	"""Test the SSH backend"""
	url_string = config.ssh_url
	password = config.ssh_password


class ftpTest(unittest.TestCase, UnivTest):
	"""Test the ftp backend"""
	url_string = config.ftp_url
	password = config.ftp_password


class rsyncAbsPathTest(unittest.TestCase, UnivTest):
	"""Test the rsync abs path backend"""
	url_string = config.rsync_abspath_url
	password = config.rsync_password


class rsyncRelPathTest(unittest.TestCase, UnivTest):
	"""Test the rsync relative path backend"""
	url_string = config.rsync_relpath_url
	password = config.rsync_password


class rsyncModuleTest(unittest.TestCase, UnivTest):
	"""Test the rsync module backend"""
	url_string = config.rsync_module_url
	password = config.rsync_password


class s3ModuleTest(unittest.TestCase, UnivTest):
	"""Test the s3 module backend"""
	url_string = config.s3_url
	password = None


class webdavModuleTest(unittest.TestCase, UnivTest):
	"""Test the webdav module backend"""
	url_string = config.webdav_url
	password = config.webdav_password


class webdavsModuleTest(unittest.TestCase, UnivTest):
	"""Test the webdavs module backend"""
	url_string = config.webdavs_url
	password = config.webdavs_password


if __name__ == "__main__":
	unittest.main()

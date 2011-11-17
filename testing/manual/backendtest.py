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

import config
import sys, unittest, os
sys.path.insert(0, "../")

import duplicity.backend
try:
    import duplicity.backends.giobackend
    gio_available = True
except Exception:
    gio_available = False
from duplicity.errors import * #@UnusedWildImport
from duplicity import path, file_naming, dup_time, globals, gpg

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
        if not self.url_string:
            print "No URL for test %s...skipping... " % self.my_test_id,
            return 0
        config.set_environ("FTP_PASSWORD", self.password)
        self.del_tmp()
        self.try_basic(duplicity.backend.get_backend(self.url_string))

    def test_fileobj_ops(self):
        """Test fileobj operations"""
        if not self.url_string:
            print "No URL for test %s...skipping... " % self.my_test_id,
            return 0
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
                   ("Got list: %s  Wanted: %s\n" % (repr(blist), repr(l)))

        # Identify test that's running
        print self.my_test_id, "... ",

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


class LocalTest(unittest.TestCase, UnivTest):
    """ Test the Local backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "local"
    url_string = config.file_url
    password = config.file_password


class scpTest(unittest.TestCase, UnivTest):
    """ Test the SSH backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "ssh/scp"
    url_string = config.ssh_url
    password = config.ssh_password


class ftpTest(unittest.TestCase, UnivTest):
    """ Test the ftp backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "ftp"
    url_string = config.ftp_url
    password = config.ftp_password


class ftpsTest(unittest.TestCase, UnivTest):
    """ Test the ftp backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "ftps"
    url_string = config.ftp_url
    password = config.ftp_password


class rsyncAbsPathTest(unittest.TestCase, UnivTest):
    """ Test the rsync abs path backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "rsync_abspath"
    url_string = config.rsync_abspath_url
    password = config.rsync_password


class rsyncRelPathTest(unittest.TestCase, UnivTest):
    """ Test the rsync relative path backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "rsync_relpath"
    url_string = config.rsync_relpath_url
    password = config.rsync_password


class rsyncModuleTest(unittest.TestCase, UnivTest):
    """ Test the rsync module backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "rsync_module"
    url_string = config.rsync_module_url
    password = config.rsync_password


class s3ModuleTest(unittest.TestCase, UnivTest):
    """ Test the s3 module backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "s3/boto"
    url_string = config.s3_url
    password = None


class webdavModuleTest(unittest.TestCase, UnivTest):
    """ Test the webdav module backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "webdav"
    url_string = config.webdav_url
    password = config.webdav_password


class webdavsModuleTest(unittest.TestCase, UnivTest):
    """ Test the webdavs module backend """
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    my_test_id = "webdavs"
    url_string = config.webdavs_url
    password = config.webdavs_password


#if gio_available:
    class GIOTest(UnivTest):
        """ Generic gio module backend class """
        def setUp(self):
            duplicity.backend.force_backend(duplicity.backends.giobackend.GIOBackend)
            assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

        def tearDown(self):
            duplicity.backend.force_backend(None)
            assert not os.system("rm -rf testfiles tempdir temp2.tar")


    class gioFileModuleTest(GIOTest, unittest.TestCase):
        """ Test the gio file module backend """
        my_test_id = "gio/file"
        url_string = config.file_url
        password = config.file_password


    class gioSSHModuleTest(GIOTest, unittest.TestCase):
        """ Test the gio ssh module backend """
        my_test_id = "gio/ssh"
        url_string = config.ssh_url
        password = config.ssh_password


    class gioFTPModuleTest(GIOTest, unittest.TestCase):
        """ Test the gio ftp module backend """
        my_test_id = "gio/ftp"
        url_string = config.ftp_url
        password = config.ftp_password

if __name__ == "__main__":
    unittest.main()

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

#
# unittest for the tarfile module
#
# $Id: test_tarfile.py,v 1.11 2009/04/02 14:47:12 loafman Exp $

import helper
import sys, os, shutil, StringIO, tempfile, unittest, stat

from duplicity import tarfile

helper.setup()

SAMPLETAR = "testtar.tar"
TEMPDIR   = tempfile.mktemp()

def join(*args):
    return os.path.normpath(apply(os.path.join, args))

class BaseTest(unittest.TestCase):
    """Base test for tarfile.
    """

    def setUp(self):
        os.mkdir(TEMPDIR)
        self.tar = tarfile.open(SAMPLETAR)
        self.tar.errorlevel = 1

    def tearDown(self):
        self.tar.close()
        shutil.rmtree(TEMPDIR)

    def isroot(self):
        return hasattr(os, "geteuid") and os.geteuid() == 0

class Test_All(BaseTest):
    """Allround test.
    """
    files_in_tempdir = ["tempdir",
                        "tempdir/0length",
                        "tempdir/large",
                        "tempdir/hardlinked1",
                        "tempdir/hardlinked2",
                        "tempdir/fifo",
                        "tempdir/symlink"]

    tempdir_data = {"0length": "",
                     "large": "hello, world!" * 10000,
                     "hardlinked1": "foo",
                     "hardlinked2": "foo"}

    def test_iteration(self):
        """Test iteration through temp2.tar"""
        self.make_temptar()
        i = 0
        tf = tarfile.TarFile("none", "r", FileLogger(open("temp2.tar", "rb")))
        tf.debug = 3
        for tarinfo in tf: i += 1 #@UnusedVariable
        assert i >= 6, i

    def _test_extraction(self):
        """Test if regular files and links are extracted correctly.
        """
        for tarinfo in self.tar:
            if tarinfo.isreg() or tarinfo.islnk() or tarinfo.issym():
                self.tar.extract(tarinfo, TEMPDIR)
                name  = join(TEMPDIR, tarinfo.name)
                data1 = file(name, "rb").read()
                data2 = self.tar.extractfile(tarinfo).read()
                self.assert_(data1 == data2,
                             "%s was not extracted successfully."
                             % tarinfo.name)

                if not tarinfo.issym():
                    self.assert_(tarinfo.mtime == os.path.getmtime(name),
                                "%s's modification time was not set correctly."
                                % tarinfo.name)

            if tarinfo.isdev():
                if hasattr(os, "mkfifo") and tarinfo.isfifo():
                    self.tar.extract(tarinfo, TEMPDIR)
                    name = join(TEMPDIR, tarinfo.name)
                    self.assert_(tarinfo.mtime == os.path.getmtime(name),
                                "%s's modification time was not set correctly."
                                % tarinfo.name)

                elif hasattr(os, "mknod") and self.isroot():
                    self.tar.extract(tarinfo, TEMPDIR)
                    name = join(TEMPDIR, tarinfo.name)
                    self.assert_(tarinfo.mtime == os.path.getmtime(name),
                                "%s's modification time was not set correctly."
                                % tarinfo.name)

    def test_addition(self):
        """Test if regular files are added correctly.
           For this, we extract all regular files from our sample tar
           and add them to a new one, which we check afterwards.
        """
        files = []
        for tarinfo in self.tar:
            if tarinfo.isreg():
                self.tar.extract(tarinfo, TEMPDIR)
                files.append(tarinfo.name)

        buf = StringIO.StringIO()
        tar = tarfile.open("test.tar", "w", buf)
        for f in files:
            path = join(TEMPDIR, f)
            tarinfo = tar.gettarinfo(path)
            tarinfo.name = f
            tar.addfile(tarinfo, file(path, "rb"))
        tar.close()

        buf.seek(0)
        tar = tarfile.open("test.tar", "r", buf)
        for tarinfo in tar:
            data1 = file(join(TEMPDIR, tarinfo.name), "rb").read()
            data2 = tar.extractfile(tarinfo).read()
            self.assert_(data1 == data2)
        tar.close()

    def make_tempdir(self):
        """Make a temp directory with assorted files in it"""
        try:
            os.lstat("tempdir")
        except OSError:
            pass
        else: # assume already exists
            assert not os.system("rm -r tempdir")
        os.mkdir("tempdir")

        def write_file(name):
            """Write appropriate data into file named name in tempdir"""
            fp = open("tempdir/%s" % (name,), "wb")
            fp.write(self.tempdir_data[name])
            fp.close()

        # Make 0length file
        write_file("0length")
        os.chmod("tempdir/%s" % ("0length",), 0604)

        # Make regular file 130000 bytes in length
        write_file("large")

        # Make hard linked files
        write_file("hardlinked1")
        os.link("tempdir/hardlinked1", "tempdir/hardlinked2")

        # Make a fifo
        os.mkfifo("tempdir/fifo")

        # Make symlink
        os.symlink("foobar", "tempdir/symlink")

    def make_temptar(self):
        """Tar up tempdir, write to "temp2.tar" """
        try:
            os.lstat("temp2.tar")
        except OSError:
            pass
        else:
            assert not os.system("rm temp2.tar")

        self.make_tempdir()
        tf = tarfile.TarFile("temp2.tar", "w")
        for filename in self.files_in_tempdir:
            tf.add(filename, filename, 0)
        tf.close()

    def test_tarfile_creation(self):
        """Create directory, make tarfile, extract using gnutar, compare"""
        self.make_temptar()
        self.extract_and_compare_tarfile()

    def extract_and_compare_tarfile(self):
        os.system("rm -r tempdir")
        assert not os.system("tar -xf temp2.tar")

        def compare_data(name):
            """Assert data is what should be"""
            fp = open("tempdir/" + name, "rb")
            buf = fp.read()
            fp.close()
            assert buf == self.tempdir_data[name]

        s = os.lstat("tempdir")
        assert stat.S_ISDIR(s.st_mode)

        for key in self.tempdir_data: compare_data(key)

        # Check to make sure permissions saved
        s = os.lstat("tempdir/0length")
        assert stat.S_IMODE(s.st_mode) == 0604, stat.S_IMODE(s.st_mode)

        s = os.lstat("tempdir/fifo")
        assert stat.S_ISFIFO(s.st_mode)

        # Check to make sure hardlinked files still hardlinked
        s1 = os.lstat("tempdir/hardlinked1")
        s2 = os.lstat("tempdir/hardlinked2")
        assert s1.st_ino == s2.st_ino

        # Check symlink
        s = os.lstat("tempdir/symlink")
        assert stat.S_ISLNK(s.st_mode)


class Test_FObj(BaseTest):
    """Test for read operations via file-object.
    """

    def _test_sparse(self):
        """Test extraction of the sparse file.
        """
        BLOCK = 4096
        for tarinfo in self.tar:
            if tarinfo.issparse():
                f = self.tar.extractfile(tarinfo)
                b = 0
                block = 0
                while 1:
                    buf = f.read(BLOCK)
                    if not buf:
                        break
                    block += 1
                    self.assert_(BLOCK == len(buf))
                    if not b:
                        self.assert_("\0" * BLOCK == buf,
                                     "sparse block is broken")
                    else:
                        self.assert_("0123456789ABCDEF" * 256 == buf,
                                     "sparse block is broken")
                    b = 1 - b
                self.assert_(block == 24, "too few sparse blocks")
                f.close()

    def _test_readlines(self):
        """Test readlines() method of _FileObject.
        """
        self.tar.extract("pep.txt", TEMPDIR)
        lines1 = file(join(TEMPDIR, "pep.txt"), "r").readlines()
        lines2 = self.tar.extractfile("pep.txt").readlines()
        self.assert_(lines1 == lines2, "readline() does not work correctly")

    def _test_seek(self):
        """Test seek() method of _FileObject, incl. random reading.
        """
        self.tar.extract("pep.txt", TEMPDIR)
        data = file(join(TEMPDIR, "pep.txt"), "rb").read()

        tarinfo = self.tar.getmember("pep.txt")
        fobj = self.tar.extractfile(tarinfo)

        text = fobj.read() #@UnusedVariable
        fobj.seek(0)
        self.assert_(0 == fobj.tell(),
                     "seek() to file's start failed")
        fobj.seek(4096, 0)
        self.assert_(4096 == fobj.tell(),
                     "seek() to absolute position failed")
        fobj.seek(-2048, 1)
        self.assert_(2048 == fobj.tell(),
                     "seek() to negative relative position failed")
        fobj.seek(2048, 1)
        self.assert_(4096 == fobj.tell(),
                     "seek() to positive relative position failed")
        s = fobj.read(10)
        self.assert_(s == data[4096:4106],
                     "read() after seek failed")
        fobj.seek(0, 2)
        self.assert_(tarinfo.size == fobj.tell(),
                     "seek() to file's end failed")
        self.assert_(fobj.read() == "",
                     "read() at file's end did not return empty string")
        fobj.seek(-tarinfo.size, 2)
        self.assert_(0 == fobj.tell(),
                     "relative seek() to file's start failed")
        fobj.seek(1024)
        s1 = fobj.readlines()
        fobj.seek(1024)
        s2 = fobj.readlines()
        self.assert_(s1 == s2,
                     "readlines() after seek failed")
        fobj.close()

class FileLogger:
    """Like a file but log requests"""
    def __init__(self, infp):
        self.infp = infp
    def read(self, length):
        #print "Reading ", length
        return self.infp.read(length)
    def seek(self, position):
        #print "Seeking to ", position
        return self.infp.seek(position)
    def tell(self):
        #print "Telling"
        return self.infp.tell()
    def close(self):
        #print "Closing"
        return self.infp.close()


if __name__ == "__main__":
    unittest.main()

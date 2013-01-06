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
import sys, os, unittest, random

from duplicity import gpg
from duplicity import path

helper.setup()

default_profile = gpg.GPGProfile(passphrase = "foobar")

class GPGTest(unittest.TestCase):
    """Test GPGFile"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def deltmp(self):
        """Delete testfiles/output and recreate"""
        assert not os.system("rm -rf testfiles/output")
        assert not os.system("mkdir testfiles/output")

    def gpg_cycle(self, s, profile = None):
        """Test encryption/decryption cycle on string s"""
        self.deltmp()
        epath = path.Path("testfiles/output/encrypted_file")
        if not profile:
            profile = default_profile
        encrypted_file = gpg.GPGFile(1, epath, profile)
        encrypted_file.write(s)
        encrypted_file.close()

        epath2 = path.Path("testfiles/output/encrypted_file")
        decrypted_file = gpg.GPGFile(0, epath2, profile)
        dec_buf = decrypted_file.read()
        decrypted_file.close()

        assert s == dec_buf, (len(s), len(dec_buf))

    def test_gpg1(self):
        """Test gpg short strings"""
        self.gpg_cycle("hello, world")
        self.gpg_cycle("ansoetuh aoetnuh aoenstuh aoetnuh asoetuh saoteuh ")

    def test_gpg2(self):
        """Test gpg long strings easily compressed"""
        self.gpg_cycle(" " * 50000)
        self.gpg_cycle("aoeu" * 1000000)

    def test_gpg3(self):
        """Test on random data - must have /dev/urandom device"""
        infp = open("/dev/urandom", "rb")
        rand_buf = infp.read(120000)
        infp.close()
        self.gpg_cycle(rand_buf)

    def test_gpg_asym(self):
        """Test GPG asymmetric encryption"""
        profile = gpg.GPGProfile(passphrase = helper.sign_passphrase,
                                 recipients = [helper.encrypt_key1,
                                               helper.encrypt_key2])
        self.gpg_cycle("aoensutha aonetuh saoe", profile)

        profile2 = gpg.GPGProfile(passphrase = helper.sign_passphrase,
                                  recipients = [helper.encrypt_key1])
        self.gpg_cycle("aoeu" * 10000, profile2)

    def test_gpg_hidden_asym(self):
        """Test GPG asymmetric encryption with hidden key id"""
        profile = gpg.GPGProfile(passphrase = helper.sign_passphrase,
                                 hidden_recipients = [helper.encrypt_key1,
                                               helper.encrypt_key2])
        self.gpg_cycle("aoensutha aonetuh saoe", profile)

        profile2 = gpg.GPGProfile(passphrase = helper.sign_passphrase,
                                  hidden_recipients = [helper.encrypt_key1])
        self.gpg_cycle("aoeu" * 10000, profile2)

    def test_gpg_signing(self):
        """Test to make sure GPG reports the proper signature key"""
        self.deltmp()
        plaintext = "hello" * 50000

        signing_profile = gpg.GPGProfile(passphrase = helper.sign_passphrase,
                                         sign_key = helper.sign_key,
                                         recipients = [helper.encrypt_key1])

        epath = path.Path("testfiles/output/encrypted_file")
        encrypted_signed_file = gpg.GPGFile(1, epath, signing_profile)
        encrypted_signed_file.write(plaintext)
        encrypted_signed_file.close()

        decrypted_file = gpg.GPGFile(0, epath, signing_profile)
        assert decrypted_file.read() == plaintext
        decrypted_file.close()
        sig = decrypted_file.get_signature()
        assert sig == helper.sign_key, sig

    def test_gpg_signing_and_hidden_encryption(self):
        """Test to make sure GPG reports the proper signature key even with hidden encryption key id"""
        self.deltmp()
        plaintext = "hello" * 50000

        signing_profile = gpg.GPGProfile(passphrase = helper.sign_passphrase,
                                         sign_key = helper.sign_key,
                                         hidden_recipients = [helper.encrypt_key1])

        epath = path.Path("testfiles/output/encrypted_file")
        encrypted_signed_file = gpg.GPGFile(1, epath, signing_profile)
        encrypted_signed_file.write(plaintext)
        encrypted_signed_file.close()

        decrypted_file = gpg.GPGFile(0, epath, signing_profile)
        assert decrypted_file.read() == plaintext
        decrypted_file.close()
        sig = decrypted_file.get_signature()
        assert sig == helper.sign_key, sig

    def test_GPGWriteFile(self):
        """Test GPGWriteFile"""
        self.deltmp()
        size = 400 * 1000
        gwfh = GPGWriteFile_Helper()
        profile = gpg.GPGProfile(passphrase = "foobar")
        for i in range(10): #@UnusedVariable
            gpg.GPGWriteFile(gwfh, "testfiles/output/gpgwrite.gpg",
                             profile, size = size)
            #print os.stat("testfiles/output/gpgwrite.gpg").st_size-size
            assert size - 64 * 1024 <= os.stat("testfiles/output/gpgwrite.gpg").st_size <= size + 64 * 1024
        gwfh.set_at_end()
        gpg.GPGWriteFile(gwfh, "testfiles/output/gpgwrite.gpg",
                         profile, size = size)
        #print os.stat("testfiles/output/gpgwrite.gpg").st_size

    def test_GzipWriteFile(self):
        """Test GzipWriteFile"""
        self.deltmp()
        size = 400 * 1000
        gwfh = GPGWriteFile_Helper()
        for i in range(10): #@UnusedVariable
            gpg.GzipWriteFile(gwfh, "testfiles/output/gzwrite.gz",
                              size = size)
            #print os.stat("testfiles/output/gzwrite.gz").st_size-size
            assert size - 64 * 1024 <= os.stat("testfiles/output/gzwrite.gz").st_size <= size + 64 * 1024
        gwfh.set_at_end()
        gpg.GzipWriteFile(gwfh, "testfiles/output/gzwrite.gz", size = size)
        #print os.stat("testfiles/output/gzwrite.gz").st_size


class GPGWriteHelper2:
    def __init__(self, data): self.data = data

class GPGWriteFile_Helper:
    """Used in test_GPGWriteFile above"""
    def __init__(self):
        self.from_random_fp = open("/dev/urandom", "rb")
        self.at_end = 0

    def set_at_end(self):
        """Iterator stops when you call this"""
        self.at_end = 1

    def get_buffer(self, size):
        """Return buffer of size size, consisting of half random data"""
        s1 = size/2
        s2 = size - s1
        return "a"*s1 + self.from_random_fp.read(s2)

    def next(self):
        if self.at_end: raise StopIteration
        block_data = self.get_buffer(self.get_read_size())
        return GPGWriteHelper2(block_data)

    def get_read_size(self):
        size = 64 * 1024
        if random.randrange(2):
            return size
        else:
            return random.randrange(0, size)

    def get_footer(self):
        return "e" * random.randrange(0, 15000)


class SHATest(unittest.TestCase):
    """Test making sha signatures"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def test_sha(self):
        hash = gpg.get_hash("SHA1", path.Path("testfiles/various_file_types/regular_file"))
        assert hash == "886d722999862724e1e62d0ac51c468ee336ef8e", hash


if __name__ == "__main__":
    unittest.main()

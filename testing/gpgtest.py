from __future__ import generators
import sys
sys.path.insert(0, "../src")
import os, unittest, cStringIO, random
import gpg, path

default_profile = gpg.GPGProfile(passphrase = "foobar")

class GPGTest(unittest.TestCase):
	"""Test GPGFile"""
	def deltmp(self):
		"""Delete testfiles/output and recreate"""
		assert not os.system("rm -rf testfiles/output")
		assert not os.system("mkdir testfiles/output")

	def gpg_cycle(self, s, profile = None):
		"""Test encryption/decryption cycle on string s"""
		self.deltmp()
		epath = path.Path("testfiles/output/encrypted_file")
		if not profile: profile = default_profile
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
		profile = gpg.GPGProfile(passphrase = "foobar",
								 recipients = ["mpf@stanford.edu",
											   "duplicity_test@foo.edu"])
		self.gpg_cycle("aoensutha aonetuh saoe", profile)

		profile2 = gpg.GPGProfile(passphrase = "foobar",
								  recipients = ["duplicity_test@foo.edu"])
		self.gpg_cycle("aoeu" * 10000, profile2)

	def test_gpg_signing(self):
		"""Test to make sure GPG reports the proper signature key"""
		self.deltmp()
		plaintext = "hello" * 50000
		duplicity_keyid = "AA0E73D2"

		signing_profile = gpg.GPGProfile(passphrase = "foobar",
										 sign_key = duplicity_keyid,
										 recipients = [duplicity_keyid])

		epath = path.Path("testfiles/output/encrypted_file")
		encrypted_signed_file = gpg.GPGFile(1, epath, signing_profile)
		encrypted_signed_file.write(plaintext)
		encrypted_signed_file.close()

		decrypted_file = gpg.GPGFile(0, epath, signing_profile)
		assert decrypted_file.read() == plaintext
		decrypted_file.close()
		sig = decrypted_file.get_signature()
		assert sig == duplicity_keyid, sig

	def test_GPGWriteFile(self):
		"""Test GPGWriteFile"""
		self.deltmp()
		size = 250000
		gwfh = GPGWriteFile_Helper()
		profile = gpg.GPGProfile(passphrase = "foobar")
		for i in range(10):
			gpg.GPGWriteFile(gwfh, "testfiles/output/gpgwrite.gpg",
							 profile, size = size)
			#print os.stat("testfiles/output/gpgwrite.gpg").st_size - size
			assert size - 32 * 1024 <= os.stat("testfiles/output/gpgwrite.gpg").st_size <= size + 32 * 1024

class GPGWriteHelper2:
	def __init__(self, data): self.data = data

class GPGWriteFile_Helper:
	"""Used in test_GPGWriteFile above"""
	def __init__(self):
		self.from_random_fp = open("/dev/urandom", "rb")
		self.set_next_block()

	def set_next_block(self):
		self.next_block_length = random.randrange(0, 40000)
		block_data = self.from_random_fp.read(self.next_block_length)
		self.next_block = GPGWriteHelper2(block_data)

	def peek(self): return self.next_block

	def next(self):
		result = self.next_block
		self.set_next_block()
		return result

	def get_footer(self):
		return "e" * random.randrange(0, 15000)


class SHATest(unittest.TestCase):
	"""Test making sha signatures"""
	def test_sha(self):
		hash = gpg.get_hash("SHA1", path.Path("testfiles/various_file_types/regular_file"))
		assert hash == "886d722999862724e1e62d0ac51c468ee336ef8e", hash


if __name__ == "__main__": unittest.main()

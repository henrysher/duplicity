# Copyright 2002 Ben Escoto
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

"""duplicity's gpg interface, builds upon Frank Tobin's GnuPGInterface"""

import select, os, sys, thread, sha, md5, types, cStringIO, tempfile, re
import GnuPGInterface, misc

blocksize = 256 * 1024

class GPGError(Exception):
	"""Indicate some GPG Error"""
	pass

class GPGProfile:
	"""Just hold some GPG settings, avoid passing tons of arguments"""
	def __init__(self, passphrase = None, sign_key = None,
				 recipients = None):
		"""Set all data with initializer

		passphrase is the passphrase.  If it is None (not ""), assume
		it hasn't been set.  sign_key can be blank if no signing is
		indicated, and recipients should be a list of keys.  For all
		keys, the format should be an 8 character hex key like
		'AA0E73D2'.

		"""
		assert passphrase is None or type(passphrase) is types.StringType
		if sign_key: assert recipients # can only sign with asym encryption

		self.passphrase = passphrase
		self.sign_key = sign_key
		if recipients is not None:
			assert type(recipients) is types.ListType # must be list, not tuple
			self.recipients = recipients
		else: self.recipients = []


class GPGFile:
	"""File-like object that decrypts another file on the fly"""
	def __init__(self, encrypt, encrypt_path, profile):
		"""GPGFile initializer

		If recipients is set, use public key encryption and encrypt to
		the given keys.  Otherwise, use symmetric encryption.

		encrypt_path is the Path of the gpg encrypted file.  Right now
		only symmetric encryption/decryption is supported.

		If passphrase is false, do not set passphrase - GPG program
		should prompt for it.

		"""
		self.status_fp = None # used to find signature
		self.closed = None # set to true after file closed

		# Start GPG process - copied from GnuPGInterface docstring.
		gnupg = GnuPGInterface.GnuPG()
		gnupg.options.meta_interactive = 0
		gnupg.options.extra_args.append('--no-secmem-warning')
		gnupg.passphrase = profile.passphrase
		if profile.sign_key: gnupg.options.default_key = profile.sign_key

		if encrypt:
			if profile.recipients:
				gnupg.options.recipients = profile.recipients
				cmdlist = ['--encrypt']
				if profile.sign_key: cmdlist.append("--sign")
			else: cmdlist = ['--symmetric']
			p1 = gnupg.run(cmdlist, create_fhs=['stdin'],
						   attach_fhs={'stdout': encrypt_path.open("wb")})
			self.gpg_input = p1.handles['stdin']
		else:
			self.status_fp = tempfile.TemporaryFile()
			p1 = gnupg.run(['--decrypt'], create_fhs=['stdout'],
						   attach_fhs={'stdin': encrypt_path.open("rb"),
									   'status': self.status_fp})
			self.gpg_output = p1.handles['stdout']
		self.gpg_process = p1
		self.encrypt = encrypt

	def read(self, length = -1): return self.gpg_output.read(length)
	def write(self, buf): return self.gpg_input.write(buf)

	def close(self):
		if self.encrypt:
			self.gpg_input.close()
			if self.status_fp: self.set_signature()
			self.gpg_process.wait()
		else:
			while self.gpg_output.read(blocksize):
				pass # discard remaining output to avoid GPG error
			self.gpg_output.close()
			if self.status_fp: self.set_signature()
			self.gpg_process.wait()
		self.closed = 1

	def set_signature(self):
		"""Set self.signature to 8 character signature keyID

		This only applies to decrypted files.  If the file was not
		signed, set self.signature to None.

		"""
		self.status_fp.seek(0)
		status_buf = self.status_fp.read()
		match = re.search("^\\[GNUPG:\\] GOODSIG ([0-9A-F]*)",
						  status_buf, re.M)
		if not match: self.signature = None
		else:
			assert len(match.group(1)) >= 8
			self.signature = match.group(1)[-8:]

	def get_signature(self):
		"""Return 8 character keyID of signature, or None if none"""
		assert self.closed
		return self.signature


def GPGWriteFile(block_iter, filename, profile,
				 size = 50 * 1024 * 1024, max_footer_size = 16 * 1024):
	"""Write GPG compressed file of given size

	This function writes a gpg compressed file by reading from the
	input iter and writing to filename.  When it has read an amount
	close to the size limit, it "tops off" the incoming data with
	incompressible data, to try to hit the limit exactly.

	block_iter should have methods .next(), which returns the next
	block of data, and .peek(), which returns the next block without
	deleting it.  Also .get_footer() returns a string to write at the
	end of the input file.  The footer should have max length
	max_footer_size.

	"""
	def start_gpg(filename, passphrase):
		"""Start GPG process, return (process, to_gpg_fileobj)"""
		gnupg = GnuPGInterface.GnuPG()
		gnupg.options.meta_interactive = 0
		gnupg.options.extra_args.append('--no-secmem-warning')
		gnupg.passphrase = passphrase
		if profile.sign_key: gnupg.options.default_key = profile.sign_key

		if profile.recipients:
			gnupg.options.recipients = profile.recipients
			cmdlist = ['--encrypt']
			if profile.sign_key: cmdlist.append("--sign")
		else: cmdlist = ['--symmetric']
		p1 = gnupg.run(cmdlist, create_fhs=['stdin'],
					   attach_fhs={'stdout': open(filename, "wb")})
		return (p1, p1.handles['stdin'])

	def top_off(bytes, to_gpg_fp):
		"""Add bytes of incompressible data to to_gpg_fp

		In this case we take the incompressible data from the
		beginning of filename (it should contain enough because size
		>> largest block size).

		"""
		incompressible_fp = open(filename, "rb")
		assert misc.copyfileobj(incompressible_fp, to_gpg_fp, bytes) == bytes
		incompressible_fp.close()

	def get_current_size(): return os.stat(filename).st_size

	def close_process(gpg_process, to_gpg_fp):
		"""Close gpg process and clean up"""
		to_gpg_fp.close()
		gpg_process.wait()

	target_size = size - 18 * 1024 # fudge factor, compensate for gpg buffering
	check_size = target_size - max_footer_size
	gpg_process, to_gpg_fp = start_gpg(filename, profile.passphrase)
	while (block_iter.peek() and
		   get_current_size() + len(block_iter.peek().data) <= check_size):
		to_gpg_fp.write(block_iter.next().data)
	to_gpg_fp.write(block_iter.get_footer())
	if block_iter.peek():
		cursize = get_current_size()
		if cursize < target_size: top_off(target_size - cursize, to_gpg_fp)
	close_process(gpg_process, to_gpg_fp)


def get_hash(hash, path, hex = 1):
	"""Return hash of path

	hash should be "MD5" or "SHA1".  The output will be in hexadecimal
	form if hex is true, and in text (base64) otherwise.

	"""
	assert path.isreg()
	fp = path.open("rb")
	if hash == "SHA1": hash_obj = sha.new()
	elif hash == "MD5": hash_obj = md5.new()
	else: assert 0, "Unknown hash %s" % (hash,)

	while 1:
		buf = fp.read(blocksize)
		if not buf: break
		hash_obj.update(buf)
	assert not fp.close()
	if hex: return hash_obj.hexdigest()
	else: return hash_obj.digest()

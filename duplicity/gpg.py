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

"""
duplicity's gpg interface, builds upon Frank Tobin's GnuPGInterface
which is now patched with some code for iterative threaded execution
see duplicity's README for details
"""

import os
import sys
import types
import tempfile
import re
import gzip
import locale
import platform

from duplicity import globals
from duplicity import gpginterface
from duplicity import log
from duplicity import tempdir
from duplicity import util

try:
    from hashlib import sha1
    from hashlib import md5
except ImportError:
    from sha import new as sha1
    from md5 import new as md5

blocksize = 256 * 1024


class GPGError(Exception):
    """
    Indicate some GPG Error
    """
    pass


class GPGProfile:
    """
    Just hold some GPG settings, avoid passing tons of arguments
    """
    def __init__(self, passphrase=None, sign_key=None,
                 recipients=None, hidden_recipients=None):
        """
        Set all data with initializer

        passphrase is the passphrase.  If it is None (not ""), assume
        it hasn't been set.  sign_key can be blank if no signing is
        indicated, and recipients should be a list of keys.  For all
        keys, the format should be an hex key like 'AA0E73D2'.
        """
        assert passphrase is None or isinstance(passphrase, types.StringType)

        self.passphrase = passphrase
        self.signing_passphrase = passphrase
        self.sign_key = sign_key
        self.encrypt_secring = None
        if recipients is not None:
            assert isinstance(recipients, types.ListType)  # must be list, not tuple
            self.recipients = recipients
        else:
            self.recipients = []

        if hidden_recipients is not None:
            assert isinstance(hidden_recipients, types.ListType)  # must be list, not tuple
            self.hidden_recipients = hidden_recipients
        else:
            self.hidden_recipients = []

        self.gpg_version = self.get_gpg_version(globals.gpg_binary)

    _version_re = re.compile(r'^gpg.*\(GnuPG(?:/MacGPG2)?\) (?P<maj>[0-9]+)\.(?P<min>[0-9]+)\.(?P<bug>[0-9]+)(-.+)?$')

    def get_gpg_version(self, binary):
        gpg = gpginterface.GnuPG()
        if binary is not None:
            gpg.call = binary
        res = gpg.run(["--version"], create_fhs=["stdout"])
        line = res.handles["stdout"].readline().rstrip()
        m = self._version_re.search(line)
        if m is not None:
            return (int(m.group("maj")), int(m.group("min")), int(m.group("bug")))
        raise GPGError("failed to determine gpg version of %s from %s" % (binary, line))


class GPGFile:
    """
    File-like object that encrypts decrypts another file on the fly
    """
    def __init__(self, encrypt, encrypt_path, profile):
        """
        GPGFile initializer

        If recipients is set, use public key encryption and encrypt to
        the given keys.  Otherwise, use symmetric encryption.

        encrypt_path is the Path of the gpg encrypted file.  Right now
        only symmetric encryption/decryption is supported.

        If passphrase is false, do not set passphrase - GPG program
        should prompt for it.
        """
        self.status_fp = None  # used to find signature
        self.closed = None  # set to true after file closed
        self.logger_fp = tempfile.TemporaryFile(dir=tempdir.default().dir())
        self.stderr_fp = tempfile.TemporaryFile(dir=tempdir.default().dir())
        self.name = encrypt_path
        self.byte_count = 0

        # Start GPG process - copied from GnuPGInterface docstring.
        gnupg = gpginterface.GnuPG()
        # overrides default gpg binary 'gpg'
        if globals.gpg_binary is not None:
            gnupg.call = globals.gpg_binary
        gnupg.options.meta_interactive = 0
        gnupg.options.extra_args.append('--no-secmem-warning')

        # Support three versions of gpg present 1.x, 2.0.x, 2.1.x
        if profile.gpg_version[:1] == (1,):
            if globals.use_agent:
                # gpg1 agent use is optional
                gnupg.options.extra_args.append('--use-agent')

        elif profile.gpg_version[:2] == (2, 0):
            pass

        elif profile.gpg_version[:2] >= (2, 1):
            if not globals.use_agent:
                # This forces gpg2 to ignore the agent.
                # Necessary to enforce truly non-interactive operation.
                gnupg.options.extra_args.append('--pinentry-mode=loopback')

        else:
            raise GPGError("Unsupported GNUPG version, %s" % profile.gpg_version)

        # User supplied options added later, can override ours
        if globals.gpg_options:
            for opt in globals.gpg_options.split():
                gnupg.options.extra_args.append(opt)

        cmdlist = []
        if profile.sign_key:
            gnupg.options.default_key = profile.sign_key
            cmdlist.append("--sign")
        # encrypt: sign key needs passphrase
        # decrypt: encrypt key needs passphrase
        # special case: allow different symmetric pass with empty sign pass
        if encrypt and profile.sign_key and profile.signing_passphrase:
            passphrase = profile.signing_passphrase
        else:
            passphrase = profile.passphrase
        # in case the passphrase is not set, pass an empty one to prevent
        # TypeError: expected a character buffer object on .write()
        if passphrase is None:
            passphrase = ""

        if encrypt:
            if profile.recipients:
                gnupg.options.recipients = profile.recipients
                cmdlist.append('--encrypt')
            if profile.hidden_recipients:
                gnupg.options.hidden_recipients = profile.hidden_recipients
                cmdlist.append('--encrypt')
            if not (profile.recipients or profile.hidden_recipients):
                cmdlist.append('--symmetric')
                # use integrity protection
                gnupg.options.extra_args.append('--force-mdc')
            # Skip the passphrase if using the agent
            if globals.use_agent:
                gnupg_fhs = ['stdin', ]
            else:
                gnupg_fhs = ['stdin', 'passphrase']
            p1 = gnupg.run(cmdlist, create_fhs=gnupg_fhs,
                           attach_fhs={'stdout': encrypt_path.open("wb"),
                                       'stderr': self.stderr_fp,
                                       'logger': self.logger_fp})
            if not globals.use_agent:
                p1.handles['passphrase'].write(passphrase)
                p1.handles['passphrase'].close()
            self.gpg_input = p1.handles['stdin']
        else:
            if (profile.recipients or profile.hidden_recipients) and profile.encrypt_secring:
                cmdlist.append('--secret-keyring')
                cmdlist.append(profile.encrypt_secring)
            self.status_fp = tempfile.TemporaryFile(dir=tempdir.default().dir())
            # Skip the passphrase if using the agent
            if globals.use_agent:
                gnupg_fhs = ['stdout', ]
            else:
                gnupg_fhs = ['stdout', 'passphrase']
            p1 = gnupg.run(['--decrypt'], create_fhs=gnupg_fhs,
                           attach_fhs={'stdin': encrypt_path.open("rb"),
                                       'status': self.status_fp,
                                       'stderr': self.stderr_fp,
                                       'logger': self.logger_fp})
            if not(globals.use_agent):
                p1.handles['passphrase'].write(passphrase)
                p1.handles['passphrase'].close()
            self.gpg_output = p1.handles['stdout']
        self.gpg_process = p1
        self.encrypt = encrypt

    def read(self, length=-1):
        try:
            res = self.gpg_output.read(length)
            if res is not None:
                self.byte_count += len(res)
        except Exception:
            self.gpg_failed()
        return res

    def write(self, buf):
        try:
            res = self.gpg_input.write(buf)
            if res is not None:
                self.byte_count += len(res)
        except Exception:
            self.gpg_failed()
        return res

    def tell(self):
        return self.byte_count

    def seek(self, offset):
        assert not self.encrypt
        assert offset >= self.byte_count, "%d < %d" % (offset, self.byte_count)
        if offset > self.byte_count:
            self.read(offset - self.byte_count)

    def gpg_failed(self):
        msg = u"GPG Failed, see log below:\n"
        msg += u"===== Begin GnuPG log =====\n"
        for fp in (self.logger_fp, self.stderr_fp):
            fp.seek(0)
            for line in fp:
                try:
                    msg += unicode(line.strip(), locale.getpreferredencoding(), 'replace') + u"\n"
                except Exception as e:
                    msg += line.strip() + u"\n"
        msg += u"===== End GnuPG log =====\n"
        if not (msg.find(u"invalid packet (ctb=14)") > -1):
            raise GPGError(msg)
        else:
            return ""

    def close(self):
        if self.encrypt:
            try:
                self.gpg_input.close()
            except Exception:
                self.gpg_failed()
            if self.status_fp:
                self.set_signature()
            try:
                self.gpg_process.wait()
            except Exception:
                self.gpg_failed()
        else:
            res = 1
            while res:
                # discard remaining output to avoid GPG error
                try:
                    res = self.gpg_output.read(blocksize)
                except Exception:
                    self.gpg_failed()
            try:
                self.gpg_output.close()
            except Exception:
                self.gpg_failed()
            if self.status_fp:
                self.set_signature()
            try:
                self.gpg_process.wait()
            except Exception:
                self.gpg_failed()
        self.logger_fp.close()
        self.stderr_fp.close()
        self.closed = 1

    def set_signature(self):
        """
        Set self.signature to signature keyID

        This only applies to decrypted files.  If the file was not
        signed, set self.signature to None.
        """
        self.status_fp.seek(0)
        status_buf = self.status_fp.read()
        match = re.search("^\\[GNUPG:\\] GOODSIG ([0-9A-F]*)",
                          status_buf, re.M)
        if not match:
            self.signature = None
        else:
            assert len(match.group(1)) >= 8
            self.signature = match.group(1)

    def get_signature(self):
        """
        Return  keyID of signature, or None if none
        """
        assert self.closed
        return self.signature


def GPGWriteFile(block_iter, filename, profile,
                 size=200 * 1024 * 1024,
                 max_footer_size=16 * 1024):
    """
    Write GPG compressed file of given size

    This function writes a gpg compressed file by reading from the
    input iter and writing to filename.  When it has read an amount
    close to the size limit, it "tops off" the incoming data with
    incompressible data, to try to hit the limit exactly.

    block_iter should have methods .next(size), which returns the next
    block of data, which should be at most size bytes long.  Also
    .get_footer() returns a string to write at the end of the input
    file.  The footer should have max length max_footer_size.

    Because gpg uses compression, we don't assume that putting
    bytes_in bytes into gpg will result in bytes_out = bytes_in out.
    However, do assume that bytes_out <= bytes_in approximately.

    Returns true if succeeded in writing until end of block_iter.
    """

    # workaround for circular module imports
    from duplicity import path

    def top_off(bytes, file):
        """
        Add bytes of incompressible data to to_gpg_fp

        In this case we take the incompressible data from the
        beginning of filename (it should contain enough because size
        >> largest block size).
        """
        incompressible_fp = open(filename, "rb")
        assert util.copyfileobj(incompressible_fp, file.gpg_input, bytes) == bytes
        incompressible_fp.close()

    def get_current_size():
        return os.stat(filename).st_size

    target_size = size - 50 * 1024  # fudge factor, compensate for gpg buffering
    data_size = target_size - max_footer_size
    file = GPGFile(True, path.Path(filename), profile)
    at_end_of_blockiter = 0
    try:
        while True:
            bytes_to_go = data_size - get_current_size()
            if bytes_to_go < block_iter.get_read_size():
                break
            try:
                data = block_iter.next().data
            except StopIteration:
                at_end_of_blockiter = 1
                break
            file.write(data)

        file.write(block_iter.get_footer())
        if not at_end_of_blockiter:
            # don't pad last volume
            cursize = get_current_size()
            if cursize < target_size:
                top_off(target_size - cursize, file)
        file.close()
        return at_end_of_blockiter
    except Exception:
        # ensure that GPG processing terminates
        file.close()
        raise


def GzipWriteFile(block_iter, filename, size=200 * 1024 * 1024, gzipped=True):
    """
    Write gzipped compressed file of given size

    This is like the earlier GPGWriteFile except it writes a gzipped
    file instead of a gpg'd file.  This function is somewhat out of
    place, because it doesn't deal with GPG at all, but it is very
    similar to GPGWriteFile so they might as well be defined together.

    The input requirements on block_iter and the output is the same as
    GPGWriteFile (returns true if wrote until end of block_iter).
    """
    class FileCounted:
        """
        Wrapper around file object that counts number of bytes written
        """
        def __init__(self, fileobj):
            self.fileobj = fileobj
            self.byte_count = 0

        def write(self, buf):
            result = self.fileobj.write(buf)
            self.byte_count += len(buf)
            return result

        def close(self):
            return self.fileobj.close()

    file_counted = FileCounted(open(filename, "wb"))

    # if gzipped wrap with GzipFile else plain file out
    if gzipped:
        outfile = gzip.GzipFile(None, "wb", 6, file_counted)
    else:
        outfile = file_counted
    at_end_of_blockiter = 0
    while True:
        bytes_to_go = size - file_counted.byte_count
        if bytes_to_go < block_iter.get_read_size():
            break
        try:
            new_block = block_iter.next()
        except StopIteration:
            at_end_of_blockiter = 1
            break
        outfile.write(new_block.data)

    assert not outfile.close() and not file_counted.close()
    return at_end_of_blockiter


def PlainWriteFile(block_iter, filename, size=200 * 1024 * 1024, gzipped=False):
    """
    Write plain uncompressed file of given size

    This is like the earlier GPGWriteFile except it writes a gzipped
    file instead of a gpg'd file.  This function is somewhat out of
    place, because it doesn't deal with GPG at all, but it is very
    similar to GPGWriteFile so they might as well be defined together.

    The input requirements on block_iter and the output is the same as
    GPGWriteFile (returns true if wrote until end of block_iter).
    """
    return GzipWriteFile(block_iter, filename, size, gzipped)


def get_hash(hash, path, hex=1):
    """
    Return hash of path

    hash should be "MD5" or "SHA1".  The output will be in hexadecimal
    form if hex is true, and in text (base64) otherwise.
    """
    # assert path.isreg()
    fp = path.open("rb")
    if hash == "SHA1":
        hash_obj = sha1()
    elif hash == "MD5":
        hash_obj = md5()
    else:
        assert 0, "Unknown hash %s" % (hash,)

    while 1:
        buf = fp.read(blocksize)
        if not buf:
            break
        hash_obj.update(buf)
    assert not fp.close()
    if hex:
        return hash_obj.hexdigest()
    else:
        return hash_obj.digest()

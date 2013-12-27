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

"""Manage temporary files"""

import os, sys

from duplicity import log
from duplicity import util
from duplicity import path
from duplicity import file_naming
from duplicity import tempdir
from duplicity import globals
from duplicity import gpg


def new_temppath():
    """
    Return a new TempPath
    """
    filename = tempdir.default().mktemp()
    return TempPath(filename)


class TempPath(path.Path):
    """
    Path object used as a temporary file
    """
    def delete(self):
        """
        Forget and delete
        """
        path.Path.delete(self)
        tempdir.default().forget(self.name)

    def open_with_delete(self, mode):
        """
        Returns a fileobj.  When that is closed, delete file
        """
        fh = FileobjHooked(path.Path.open(self, mode))
        fh.addhook(self.delete)
        return fh


def get_fileobj_duppath(dirpath, partname, permname, remname, overwrite=False):
    """
    Return a file object open for writing, will write to filename

    Data will be processed and written to a temporary file.  When the
    return fileobject is closed, rename to final position.  filename
    must be a recognizable duplicity data file.
    """
    if not globals.restart:
        td = tempdir.TemporaryDirectory(dirpath.name)
        tdpname = td.mktemp()
        tdp = TempDupPath(tdpname, parseresults = file_naming.parse(partname))
        fh = FileobjHooked(tdp.filtered_open("wb"), tdp = tdp, dirpath = dirpath,
                           partname = partname, permname = permname, remname = remname)
    else:
        dp = path.DupPath(dirpath.name, index = (partname,))
        mode = "ab"
        if overwrite:
            mode = "wb"
        fh = FileobjHooked(dp.filtered_open(mode), tdp = None, dirpath = dirpath,
                           partname = partname, permname = permname, remname = remname)

    def rename_and_forget():
        tdp.rename(dirpath.append(partname))
        td.forget(tdpname)

    if not globals.restart:
        fh.addhook(rename_and_forget)

    return fh


def new_tempduppath(parseresults):
    """
    Return a new TempDupPath, using settings from parseresults
    """
    filename = tempdir.default().mktemp()
    return TempDupPath(filename, parseresults = parseresults)


class TempDupPath(path.DupPath):
    """
    Like TempPath, but build around DupPath
    """
    def delete(self):
        """
        Forget and delete
        """
        path.DupPath.delete(self)
        tempdir.default().forget(self.name)

    def filtered_open_with_delete(self, mode):
        """
        Returns a filtered fileobj.  When that is closed, delete file
        """
        fh = FileobjHooked(path.DupPath.filtered_open(self, mode))
        fh.addhook(self.delete)
        return fh

    def open_with_delete(self, mode = "rb"):
        """
        Returns a fileobj.  When that is closed, delete file
        """
        assert mode == "rb" # Why write a file and then close it immediately?
        fh = FileobjHooked(path.DupPath.open(self, mode))
        fh.addhook(self.delete)
        return fh


class FileobjHooked:
    """
    Simulate a file, but add hook on close
    """
    def __init__(self, fileobj, tdp = None, dirpath = None,
                 partname = None, permname = None, remname = None):
        """
        Initializer.  fileobj is the file object to simulate
        """
        self.fileobj = fileobj      # the actual file object
        self.closed = False         # True if closed
        self.hooklist = []          # filled later with thunks to run on close
        self.tdp = tdp              # TempDupPath object
        self.dirpath = dirpath      # path to directory
        self.partname = partname    # partial filename
        self.permname = permname    # permanent filename
        self.remname = remname      # remote filename

    def write(self, buf):
        """
        Write fileobj, return result of write()
        """
        return self.fileobj.write(buf)

    def flush(self):
        """
        Flush fileobj and force sync.
        """
        self.fileobj.flush()
        os.fsync(self.fileobj.fileno())

    def to_partial(self):
        """
        We have achieved the first checkpoint, make file visible and permanent.
        """
        assert not globals.restart
        self.tdp.rename(self.dirpath.append(self.partname))
        self.fileobj.flush()
        del self.hooklist[0]

    def to_remote(self):
        """
        We have written the last checkpoint, now encrypt or compress
        and send a copy of it to the remote for final storage.
        """
        pr = file_naming.parse(self.remname)
        src = self.dirpath.append(self.partname)
        tgt = self.dirpath.append(self.remname)
        src_iter = SrcIter(src)
        if pr.compressed:
            gpg.GzipWriteFile(src_iter, tgt.name, size = sys.maxint)
        elif pr.encrypted:
            gpg.GPGWriteFile(src_iter, tgt.name, globals.gpg_profile, size = sys.maxint)
        else:
            os.system("cp -p \"%s\" \"%s\"" % (src.name, tgt.name))
        globals.backend.move(tgt) #@UndefinedVariable

    def to_final(self):
        """
        We are finished, rename to final, gzip if needed.
        """
        src = self.dirpath.append(self.partname)
        tgt = self.dirpath.append(self.permname)
        src_iter = SrcIter(src)
        pr = file_naming.parse(self.permname)
        if pr.compressed:
            gpg.GzipWriteFile(src_iter, tgt.name, size = sys.maxint)
            os.unlink(src.name)
        else:
            os.rename(src.name, tgt.name)

    def read(self, length = -1):
        """
        Read fileobj, return result of read()
        """
        return self.fileobj.read(length)

    def tell(self):
        """
        Returns current location of fileobj
        """
        return self.fileobj.tell()

    def seek(self, offset):
        """
        Seeks to a location of fileobj
        """
        return self.fileobj.seek(offset)

    def close(self):
        """
        Close fileobj, running hooks right afterwards
        """
        assert not self.fileobj.close()
        for hook in self.hooklist:
            hook()

    def addhook(self, hook):
        """
        Add hook (function taking no arguments) to run upon closing
        """
        self.hooklist.append(hook)


    def get_name(self):
        """
        Return the name of the file
        """
        return self.fileobj.name

    name = property(get_name)


class Block:
    """
    Data block to return from SrcIter
    """
    def __init__(self, data):
        self.data = data

class SrcIter:
    """
    Iterate over source and return Block of data.
    """
    def __init__(self, src):
        self.src = src
        self.fp = src.open("rb")
    def next(self):
        try:
            res = Block(self.fp.read(self.get_read_size()))
        except Exception:
            log.FatalError(_("Failed to read %s: %s") %
                           (util.ufn(self.src.name), sys.exc_info()),
                           log.ErrorCode.generic)
        if not res.data:
            self.fp.close()
            raise StopIteration
        return res
    def get_read_size(self):
        return 128 * 1024
    def get_footer(self):
        return ""

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
Functions for producing signatures and deltas of directories

Note that the main processes of this module have two parts.  In the
first, the signature or delta is constructed of a ROPath iterator.  In
the second, the ROPath iterator is put into tar block form.
"""

from future_builtins import map

import cStringIO
import types
import math
from duplicity import statistics
from duplicity import util
from duplicity import globals
from duplicity.path import *  # @UnusedWildImport
from duplicity.lazy import *  # @UnusedWildImport
from duplicity import progress

# A StatsObj will be written to this from DirDelta and DirDelta_WriteSig.
stats = None
tracker = None


class DiffDirException(Exception):
    pass


def DirSig(path_iter):
    """
    Alias for SigTarBlockIter below
    """
    return SigTarBlockIter(path_iter)


def DirFull(path_iter):
    """
    Return a tarblock full backup of items in path_iter

    A full backup is just a diff starting from nothing (it may be less
    elegant than using a standard tar file, but we can be sure that it
    will be easy to split up the tar and make the volumes the same
    sizes).
    """
    return DirDelta(path_iter, cStringIO.StringIO(""))


def DirFull_WriteSig(path_iter, sig_outfp):
    """
    Return full backup like above, but also write signature to sig_outfp
    """
    return DirDelta_WriteSig(path_iter, cStringIO.StringIO(""), sig_outfp)


def DirDelta(path_iter, dirsig_fileobj_list):
    """
    Produce tarblock diff given dirsig_fileobj_list and pathiter

    dirsig_fileobj_list should either be a tar fileobj or a list of
    those, sorted so the most recent is last.
    """
    global stats
    stats = statistics.StatsDeltaProcess()
    if isinstance(dirsig_fileobj_list, types.ListType):
        sig_iter = combine_path_iters([sigtar2path_iter(x) for x
                                       in dirsig_fileobj_list])
    else:
        sig_iter = sigtar2path_iter(dirsig_fileobj_list)
    delta_iter = get_delta_iter(path_iter, sig_iter)
    if globals.dry_run or (globals.progress and not progress.tracker.has_collected_evidence()):
        return DummyBlockIter(delta_iter)
    else:
        return DeltaTarBlockIter(delta_iter)


def delta_iter_error_handler(exc, new_path, sig_path, sig_tar=None):
    """
    Called by get_delta_iter, report error in getting delta
    """
    if new_path:
        index_string = new_path.get_relative_path()
    elif sig_path:
        index_string = sig_path.get_relative_path()
    else:
        assert 0, "Both new and sig are None for some reason"
    log.Warn(_("Error %s getting delta for %s") % (str(exc), util.ufn(index_string)))
    return None


def get_delta_path(new_path, sig_path, sigTarFile=None):
    """
    Return new delta_path which, when read, writes sig to sig_fileobj,
    if sigTarFile is not None
    """
    assert new_path
    if sigTarFile:
        ti = new_path.get_tarinfo()
        index = new_path.index
    delta_path = new_path.get_ropath()
    log.Debug(_("Getting delta of %s and %s") % (new_path, sig_path))

    def callback(sig_string):
        """
        Callback activated when FileWithSignature read to end
        """
        ti.size = len(sig_string)
        ti.name = "signature/" + "/".join(index)
        sigTarFile.addfile(ti, cStringIO.StringIO(sig_string))

    if new_path.isreg() and sig_path and sig_path.isreg() and sig_path.difftype == "signature":
        delta_path.difftype = "diff"
        old_sigfp = sig_path.open("rb")
        newfp = FileWithReadCounter(new_path.open("rb"))
        if sigTarFile:
            newfp = FileWithSignature(newfp, callback,
                                      new_path.getsize())
        delta_path.setfileobj(librsync.DeltaFile(old_sigfp, newfp))
    else:
        delta_path.difftype = "snapshot"
        if sigTarFile:
            ti.name = "snapshot/" + "/".join(index)
        if not new_path.isreg():
            if sigTarFile:
                sigTarFile.addfile(ti)
            if stats:
                stats.SourceFileSize += delta_path.getsize()
        else:
            newfp = FileWithReadCounter(new_path.open("rb"))
            if sigTarFile:
                newfp = FileWithSignature(newfp, callback,
                                          new_path.getsize())
            delta_path.setfileobj(newfp)
    new_path.copy_attribs(delta_path)
    delta_path.stat.st_size = new_path.stat.st_size
    return delta_path


def log_delta_path(delta_path, new_path=None, stats=None):
    """
    Look at delta path and log delta.  Add stats if new_path is set
    """
    if delta_path.difftype == "snapshot":
        if new_path and stats:
            stats.add_new_file(new_path)
        log.Info(_("A %s") %
                 (util.ufn(delta_path.get_relative_path())),
                 log.InfoCode.diff_file_new,
                 util.escape(delta_path.get_relative_path()))
    else:
        if new_path and stats:
            stats.add_changed_file(new_path)
        log.Info(_("M %s") %
                 (util.ufn(delta_path.get_relative_path())),
                 log.InfoCode.diff_file_changed,
                 util.escape(delta_path.get_relative_path()))


def get_delta_iter(new_iter, sig_iter, sig_fileobj=None):
    """
    Generate delta iter from new Path iter and sig Path iter.

    For each delta path of regular file type, path.difftype with be
    set to "snapshot", "diff".  sig_iter will probably iterate ROPaths
    instead of Paths.

    If sig_fileobj is not None, will also write signatures to sig_fileobj.
    """
    collated = collate2iters(new_iter, sig_iter)
    if sig_fileobj:
        sigTarFile = util.make_tarfile("w", sig_fileobj)
    else:
        sigTarFile = None
    for new_path, sig_path in collated:
        log.Debug(_("Comparing %s and %s") % (new_path and util.uindex(new_path.index),
                                              sig_path and util.uindex(sig_path.index)))
        if not new_path or not new_path.type:
            # File doesn't exist (but ignore attempts to delete base dir;
            # old versions of duplicity could have written out the sigtar in
            # such a way as to fool us; LP: #929067)
            if sig_path and sig_path.exists() and sig_path.index != ():
                # but signature says it did
                log.Info(_("D %s") %
                         (util.ufn(sig_path.get_relative_path())),
                         log.InfoCode.diff_file_deleted,
                         util.escape(sig_path.get_relative_path()))
                if sigTarFile:
                    ti = ROPath(sig_path.index).get_tarinfo()
                    ti.name = "deleted/" + "/".join(sig_path.index)
                    sigTarFile.addfile(ti)
                stats.add_deleted_file(sig_path)
                yield ROPath(sig_path.index)
        elif not sig_path or new_path != sig_path:
            # Must calculate new signature and create delta
            delta_path = robust.check_common_error(delta_iter_error_handler,
                                                   get_delta_path,
                                                   (new_path, sig_path, sigTarFile))
            if delta_path:
                # log and collect stats
                log_delta_path(delta_path, new_path, stats)
                yield delta_path
            else:
                # if not, an error must have occurred
                stats.Errors += 1
        else:
            stats.add_unchanged_file(new_path)
    stats.close()
    if sigTarFile:
        sigTarFile.close()


def sigtar2path_iter(sigtarobj):
    """
    Convert signature tar file object open for reading into path iter
    """
    tf = util.make_tarfile("r", sigtarobj)
    tf.debug = 1
    for tarinfo in tf:
        tiname = util.get_tarinfo_name(tarinfo)
        for prefix in ["signature/", "snapshot/", "deleted/"]:
            if tiname.startswith(prefix):
                # strip prefix and '/' from name and set it to difftype
                name, difftype = tiname[len(prefix):], prefix[:-1]
                break
        else:
            raise DiffDirException("Bad tarinfo name %s" % (tiname,))

        index = tuple(name.split("/"))
        if not index[-1]:
            index = index[:-1]  # deal with trailing /, ""

        ropath = ROPath(index)
        ropath.difftype = difftype
        if difftype == "signature" or difftype == "snapshot":
            ropath.init_from_tarinfo(tarinfo)
            if ropath.isreg():
                ropath.setfileobj(tf.extractfile(tarinfo))
        yield ropath
    sigtarobj.close()


def collate2iters(riter1, riter2):
    """
    Collate two iterators.

    The elements yielded by each iterator must be have an index
    variable, and this function returns pairs (elem1, elem2), (elem1,
    None), or (None, elem2) two elements in a pair will have the same
    index, and earlier indicies are yielded later than later indicies.
    """
    relem1, relem2 = None, None
    while 1:
        if not relem1:
            try:
                relem1 = riter1.next()
            except StopIteration:
                if relem2:
                    yield (None, relem2)
                for relem2 in riter2:
                    yield (None, relem2)
                break
            index1 = relem1.index
        if not relem2:
            try:
                relem2 = riter2.next()
            except StopIteration:
                if relem1:
                    yield (relem1, None)
                for relem1 in riter1:
                    yield (relem1, None)
                break
            index2 = relem2.index

        if index1 < index2:
            yield (relem1, None)
            relem1 = None
        elif index1 == index2:
            yield (relem1, relem2)
            relem1, relem2 = None, None
        else:
            # index2 is less
            yield (None, relem2)
            relem2 = None


def combine_path_iters(path_iter_list):
    """
    Produce new iterator by combining the iterators in path_iter_list

    This new iter will iterate every path that is in path_iter_list in
    order of increasing index.  If multiple iterators in
    path_iter_list yield paths with the same index, combine_path_iters
    will discard all paths but the one yielded by the last path_iter.

    This is used to combine signature iters, as the output will be a
    full up-to-date signature iter.
    """
    path_iter_list = path_iter_list[:]  # copy before destructive reverse
    path_iter_list.reverse()

    def get_triple(iter_index):
        """
        Represent the next element as a triple, to help sorting
        """
        try:
            path = path_iter_list[iter_index].next()
        except StopIteration:
            return None
        return (path.index, iter_index, path)

    def refresh_triple_list(triple_list):
        """
        Update all elements with path_index same as first element
        """
        path_index = triple_list[0][0]
        iter_index = 0
        while iter_index < len(triple_list):
            old_triple = triple_list[iter_index]
            if old_triple[0] == path_index:
                new_triple = get_triple(old_triple[1])
                if new_triple:
                    triple_list[iter_index] = new_triple
                    iter_index += 1
                else:
                    del triple_list[iter_index]
            else:
                break  # assumed triple_list sorted, so can exit now

    triple_list = [x for x in map(get_triple, range(len(path_iter_list))) if x]
    while triple_list:
        triple_list.sort()
        yield triple_list[0][2]
        refresh_triple_list(triple_list)


def DirDelta_WriteSig(path_iter, sig_infp_list, newsig_outfp):
    """
    Like DirDelta but also write signature into sig_fileobj

    Like DirDelta, sig_infp_list can be a tar fileobj or a sorted list
    of those.  A signature will only be written to newsig_outfp if it
    is different from (the combined) sig_infp_list.
    """
    global stats
    stats = statistics.StatsDeltaProcess()
    if isinstance(sig_infp_list, types.ListType):
        sig_path_iter = get_combined_path_iter(sig_infp_list)
    else:
        sig_path_iter = sigtar2path_iter(sig_infp_list)
    delta_iter = get_delta_iter(path_iter, sig_path_iter, newsig_outfp)
    if globals.dry_run or (globals.progress and not progress.tracker.has_collected_evidence()):
        return DummyBlockIter(delta_iter)
    else:
        return DeltaTarBlockIter(delta_iter)


def get_combined_path_iter(sig_infp_list):
    """
    Return path iter combining signatures in list of open sig files
    """
    return combine_path_iters([sigtar2path_iter(x) for x in sig_infp_list])


class FileWithReadCounter:
    """
    File-like object which also computes amount read as it is read
    """
    def __init__(self, infile):
        """FileWithReadCounter initializer"""
        self.infile = infile

    def read(self, length=-1):
        try:
            buf = self.infile.read(length)
        except IOError as ex:
            buf = ""
            log.Warn(_("Error %s getting delta for %s") % (str(ex), util.ufn(self.infile.name)))
        if stats:
            stats.SourceFileSize += len(buf)
        return buf

    def close(self):
        return self.infile.close()


class FileWithSignature:
    """
    File-like object which also computes signature as it is read
    """
    blocksize = 32 * 1024

    def __init__(self, infile, callback, filelen, *extra_args):
        """
        FileTee initializer

        The object will act like infile, but whenever it is read it
        add infile's data to a SigGenerator object.  When the file has
        been read to the end the callback will be called with the
        calculated signature, and any extra_args if given.

        filelen is used to calculate the block size of the signature.
        """
        self.infile, self.callback = infile, callback
        self.sig_gen = librsync.SigGenerator(get_block_size(filelen))
        self.activated_callback = None
        self.extra_args = extra_args

    def read(self, length=-1):
        buf = self.infile.read(length)
        self.sig_gen.update(buf)
        return buf

    def close(self):
        # Make sure all of infile read
        if not self.activated_callback:
            while self.read(self.blocksize):
                pass
            self.activated_callback = 1
            self.callback(self.sig_gen.getsig(), *self.extra_args)
        return self.infile.close()


class TarBlock:
    """
    Contain information to add next file to tar
    """
    def __init__(self, index, data):
        """
        TarBlock initializer - just store data
        """
        self.index = index
        self.data = data


class TarBlockIter:
    """
    A bit like an iterator, yield tar blocks given input iterator

    Unlike an iterator, however, control over the maximum size of a
    tarblock is available by passing an argument to next().  Also the
    get_footer() is available.
    """
    def __init__(self, input_iter):
        """
        TarBlockIter initializer
        """
        self.input_iter = input_iter
        self.offset = 0  # total length of data read
        self.process_waiting = False  # process_continued has more blocks
        self.process_next_vol_number = None  # next volume number to write in multivol
        self.previous_index = None  # holds index of last block returned
        self.previous_block = None  # holds block of last block returned
        self.remember_next = False  # see remember_next_index()
        self.remember_value = None  # holds index of next block
        self.remember_block = None  # holds block of next block
        self.queued_data = None  # data to return in next next() call

    def tarinfo2tarblock(self, index, tarinfo, file_data=""):
        """
        Make tarblock out of tarinfo and file data
        """
        tarinfo.size = len(file_data)
        headers = tarinfo.tobuf(errors='replace')
        blocks, remainder = divmod(tarinfo.size, tarfile.BLOCKSIZE)  # @UnusedVariable
        if remainder > 0:
            filler_data = "\0" * (tarfile.BLOCKSIZE - remainder)
        else:
            filler_data = ""
        return TarBlock(index, "%s%s%s" % (headers, file_data, filler_data))

    def process(self, val):
        """
        Turn next value of input_iter into a TarBlock
        """
        assert not self.process_waiting
        XXX  # Override in subclass @UndefinedVariable

    def process_continued(self):
        """
        Get more tarblocks

        If processing val above would produce more than one TarBlock,
        get the rest of them by calling process_continue.
        """
        assert self.process_waiting
        XXX  # Override in subclass @UndefinedVariable

    def next(self):
        """
        Return next block and update offset
        """
        if self.queued_data is not None:
            result = self.queued_data
            self.queued_data = None
            # Keep rest of metadata as is (like previous_index)
            return result

        if self.process_waiting:
            result = self.process_continued()
        else:
            # Below a StopIteration exception will just be passed upwards
            result = self.process(self.input_iter.next())
        block_number = self.process_next_vol_number
        self.offset += len(result.data)
        self.previous_index = result.index
        self.previous_block = block_number
        if self.remember_next:
            self.remember_value = result.index
            self.remember_block = block_number
            self.remember_next = False
        return result

    def get_read_size(self):
        # read size must always be the same, because if we are restarting a
        # backup volume where the previous volume ended in a data block, we
        # have to be able to assume it's length in order to continue reading
        # the file from the right place.
        return 64 * 1024

    def get_previous_index(self):
        """
        Return index of last tarblock, or None if no previous index
        """
        return self.previous_index, self.previous_block

    def queue_index_data(self, data):
        """
        Next time next() is called, we will return data instead of processing
        """
        self.queued_data = data

    def remember_next_index(self):
        """
        When called, remember the index of the next block iterated
        """
        self.remember_next = True
        self.remember_value = None
        self.remember_block = None

    def recall_index(self):
        """
        Retrieve index remembered with remember_next_index
        """
        return self.remember_value, self.remember_block

    def get_footer(self):
        """
        Return closing string for tarfile, reset offset
        """
        blocks, remainder = divmod(self.offset, tarfile.RECORDSIZE)  # @UnusedVariable
        self.offset = 0
        return '\0' * (tarfile.RECORDSIZE - remainder)  # remainder can be 0

    def __iter__(self):
        return self


class DummyBlockIter(TarBlockIter):
    """
    TarBlockIter that does no file reading
    """
    def process(self, delta_ropath):
        """
        Get a fake tarblock from delta_ropath
        """
        ti = delta_ropath.get_tarinfo()
        index = delta_ropath.index

        # Return blocks of deleted files or fileless snapshots
        if not delta_ropath.type or not delta_ropath.fileobj:
            return self.tarinfo2tarblock(index, ti)

        if stats:
            # Since we don't read the source files, we can't analyze them.
            # Best we can do is count them raw.
            stats.SourceFiles += 1
            stats.SourceFileSize += delta_ropath.getsize()
            log.Progress(None, stats.SourceFileSize)
        return self.tarinfo2tarblock(index, ti)


class SigTarBlockIter(TarBlockIter):
    """
    TarBlockIter that yields blocks of a signature tar from path_iter
    """
    def process(self, path):
        """
        Return associated signature TarBlock from path
        """
        ti = path.get_tarinfo()
        if path.isreg():
            sfp = librsync.SigFile(path.open("rb"),
                                   get_block_size(path.getsize()))
            sigbuf = sfp.read()
            sfp.close()
            ti.name = "signature/" + "/".join(path.index)
            return self.tarinfo2tarblock(path.index, ti, sigbuf)
        else:
            ti.name = "snapshot/" + "/".join(path.index)
            return self.tarinfo2tarblock(path.index, ti)


class DeltaTarBlockIter(TarBlockIter):
    """
    TarBlockIter that yields parts of a deltatar file

    Unlike SigTarBlockIter, the argument to __init__ is a
    delta_path_iter, so the delta information has already been
    calculated.
    """
    def process(self, delta_ropath):
        """
        Get a tarblock from delta_ropath
        """
        def add_prefix(tarinfo, prefix):
            """Add prefix to the name of a tarinfo file"""
            if tarinfo.name == ".":
                tarinfo.name = prefix + "/"
            else:
                tarinfo.name = "%s/%s" % (prefix, tarinfo.name)

        ti = delta_ropath.get_tarinfo()
        index = delta_ropath.index

        # Return blocks of deleted files or fileless snapshots
        if not delta_ropath.type or not delta_ropath.fileobj:
            if not delta_ropath.type:
                add_prefix(ti, "deleted")
            else:
                assert delta_ropath.difftype == "snapshot"
                add_prefix(ti, "snapshot")
            return self.tarinfo2tarblock(index, ti)

        # Now handle single volume block case
        fp = delta_ropath.open("rb")
        data, last_block = self.get_data_block(fp)
        if stats:
            stats.RawDeltaSize += len(data)
        if last_block:
            if delta_ropath.difftype == "snapshot":
                add_prefix(ti, "snapshot")
            elif delta_ropath.difftype == "diff":
                add_prefix(ti, "diff")
            else:
                assert 0, "Unknown difftype"
            return self.tarinfo2tarblock(index, ti, data)

        # Finally, do multivol snapshot or diff case
        full_name = "multivol_%s/%s" % (delta_ropath.difftype, ti.name)
        ti.name = full_name + "/1"
        self.process_prefix = full_name
        self.process_fp = fp
        self.process_ropath = delta_ropath
        self.process_waiting = 1
        self.process_next_vol_number = 2
        return self.tarinfo2tarblock(index, ti, data)

    def get_data_block(self, fp):
        """
        Return pair (next data block, boolean last data block)
        """
        read_size = self.get_read_size()
        buf = fp.read(read_size)
        if len(buf) < read_size:
            if fp.close():
                raise DiffDirException("Error closing file")
            return (buf, True)
        else:
            return (buf, False)

    def process_continued(self):
        """
        Return next volume in multivol diff or snapshot
        """
        assert self.process_waiting
        ropath = self.process_ropath
        ti, index = ropath.get_tarinfo(), ropath.index
        ti.name = "%s/%d" % (self.process_prefix, self.process_next_vol_number)
        data, last_block = self.get_data_block(self.process_fp)
        if stats:
            stats.RawDeltaSize += len(data)
        if last_block:
            self.process_prefix = None
            self.process_fp = None
            self.process_ropath = None
            self.process_waiting = None
            self.process_next_vol_number = None
        else:
            self.process_next_vol_number += 1
        return self.tarinfo2tarblock(index, ti, data)


def write_block_iter(block_iter, out_obj):
    """
    Write block_iter to filename, path, or file object
    """
    if isinstance(out_obj, Path):
        fp = open(out_obj.name, "wb")
    elif isinstance(out_obj, types.StringType):
        fp = open(out_obj, "wb")
    else:
        fp = out_obj
    for block in block_iter:
        fp.write(block.data)
    fp.write(block_iter.get_footer())
    assert not fp.close()
    if isinstance(out_obj, Path):
        out_obj.setdata()


def get_block_size(file_len):
    """
    Return a reasonable block size to use on files of length file_len

    If the block size is too big, deltas will be bigger than is
    necessary.  If the block size is too small, making deltas and
    patching can take a really long time.
    """
    if file_len < 1024000:
        return 512  # set minimum of 512 bytes
    else:
        # Split file into about 2000 pieces, rounding to 512
        file_blocksize = int((file_len / (2000 * 512)) * 512)
        return min(file_blocksize, globals.max_blocksize)

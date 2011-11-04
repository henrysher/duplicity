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
import os, sys, unittest

from duplicity.path import * #@UnusedWildImport
from duplicity import diffdir
from duplicity import selection
from duplicity import util
from duplicity import tarfile #@Reimport

helper.setup()

class DDTest(unittest.TestCase):
    """Test functions in diffdir.py"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def copyfileobj(self, infp, outfp):
        """Copy in fileobj to out, closing afterwards"""
        blocksize = 32 * 1024
        while 1:
            buf = infp.read(blocksize)
            if not buf: break
            outfp.write(buf)
        assert not infp.close()
        assert not outfp.close()

    def deltmp(self):
        """Delete temporary directories"""
        assert not os.system("rm -rf testfiles/output")
        os.mkdir("testfiles/output")

    def testsig(self):
        """Test producing tar signature of various file types"""
        self.deltmp()
        select = selection.Select(Path("testfiles/various_file_types"))
        select.set_iter()
        sigtar = diffdir.SigTarBlockIter(select)
        diffdir.write_block_iter(sigtar, "testfiles/output/sigtar")

        i = 0
        for tarinfo in tarfile.TarFile("testfiles/output/sigtar", "r"): #@UnusedVariable
            i += 1
        assert i >= 5, "There should be at least 5 files in sigtar"

    def empty_diff_schema(self, dirname):
        """Given directory name, make sure can tell when nothing changes"""
        self.deltmp()
        select = selection.Select(Path(dirname))
        select.set_iter()
        sigtar = diffdir.SigTarBlockIter(select)
        diffdir.write_block_iter(sigtar, "testfiles/output/sigtar")

        sigtar_fp = open("testfiles/output/sigtar")
        select2 = selection.Select(Path(dirname))
        select2.set_iter()
        diffdir.write_block_iter(diffdir.DirDelta(select2, sigtar_fp),
                                 "testfiles/output/difftar")

        size = os.stat("testfiles/output/difftar").st_size
        assert size == 0 or size == 10240, size # 10240 is size of one record
        if size != 0:
            fin = open("testfiles/output/difftar", "rb")
            diff_buf = fin.read()
            assert not fin.close()
            assert diff_buf == '\0'*10240

    def test_empty_diff(self):
        """Test producing a diff against same sig; should be len 0"""
        self.empty_diff_schema("testfiles/various_file_types")
        return

        self.deltmp()
        select = selection.Select(Path("testfiles/various_file_types"))
        select.set_iter()
        sigtar = diffdir.SigTarBlockIter(select)
        diffdir.write_block_iter(sigtar, "testfiles/output/sigtar")

        sigtar_fp = open("testfiles/output/sigtar")
        select2 = selection.Select(Path("testfiles/various_file_types"))
        select2.set_iter()
        diffdir.write_block_iter(diffdir.DirDelta(select2, sigtar_fp),
                                 "testfiles/output/difftar")

        size = os.stat("testfiles/output/difftar").st_size #@UnusedVariable

    def test_empty_diff2(self):
        """Test producing diff against directories of special files"""
        self.empty_diff_schema("testfiles/special_cases/neg_mtime")
        self.empty_diff_schema("testfiles/special_cases/no_uname")

    def test_diff(self):
        """Test making a diff"""
        self.deltmp()
        sel1 = selection.Select(Path("testfiles/dir1"))
        diffdir.write_block_iter(diffdir.SigTarBlockIter(sel1.set_iter()),
                                 "testfiles/output/dir1.sigtar")

        sigtar_fp = open("testfiles/output/dir1.sigtar", "rb")
        sel2 = selection.Select(Path("testfiles/dir2"))
        delta_tar = diffdir.DirDelta(sel2.set_iter(), sigtar_fp)
        diffdir.write_block_iter(delta_tar,
                                 "testfiles/output/dir1dir2.difftar")

        changed_files = ["diff/changeable_permission",
                         "diff/regular_file",
                         "snapshot/symbolic_link/",
                         "deleted/deleted_file",
                         "snapshot/directory_to_file",
                         "snapshot/file_to_directory/"]
        for tarinfo in tarfile.TarFile("testfiles/output/dir1dir2.difftar",
                                       "r"):
            tiname = util.get_tarinfo_name(tarinfo)
            if tiname in changed_files:
                changed_files.remove(tiname)
        assert not changed_files, ("Following files not found:\n"
                                   + "\n".join(changed_files))

    def test_diff2(self):
        """Another diff test - this one involves multivol support"""
        self.deltmp()
        sel1 = selection.Select(Path("testfiles/dir2"))
        diffdir.write_block_iter(diffdir.SigTarBlockIter(sel1.set_iter()),
                                 "testfiles/output/dir2.sigtar")

        sigtar_fp = open("testfiles/output/dir2.sigtar", "rb")
        sel2 = selection.Select(Path("testfiles/dir3"))
        delta_tar = diffdir.DirDelta(sel2.set_iter(), sigtar_fp)
        diffdir.write_block_iter(delta_tar,
                                 "testfiles/output/dir2dir3.difftar")

        buffer = ""
        tf = tarfile.TarFile("testfiles/output/dir2dir3.difftar", "r")
        for tarinfo in tf:
            if tarinfo.name.startswith("multivol_diff/"):
                buffer += tf.extractfile(tarinfo).read()
        assert 3000000 < len(buffer) < 4000000
        fout = open("testfiles/output/largefile.delta", "wb")
        fout.write(buffer)
        fout.close()
        assert not os.system("rdiff patch testfiles/dir2/largefile "
                             "testfiles/output/largefile.delta "
                             "testfiles/output/largefile.patched")
        dir3large = open("testfiles/dir3/largefile", "rb").read()
        patchedlarge = open("testfiles/output/largefile.patched", "rb").read()
        assert dir3large == patchedlarge

    def test_dirdelta_write_sig(self):
        """Test simultaneous delta and sig generation

        Generate signatures and deltas of dirs1, 2, 3, 4 and compare
        those produced by DirDelta_WriteSig and other methods.

        """
        self.deltmp()
        deltadir1 = Path("testfiles/output/dir.deltatar1") #@UnusedVariable
        deltadir2 = Path("testfiles/output/dir.deltatar2") #@UnusedVariable
        cur_full_sigs = Path("testfiles/output/fullsig.dir1")

        cur_dir = Path("testfiles/dir1")
        get_sel = lambda cur_dir: selection.Select(cur_dir).set_iter()
        diffdir.write_block_iter(diffdir.SigTarBlockIter(get_sel(cur_dir)),
                                 cur_full_sigs)

        sigstack = [cur_full_sigs]
        for dirname in ['dir2', 'dir3', 'dir4']:
            #print "Processing ", dirname
            old_dir = cur_dir #@UnusedVariable
            cur_dir = Path("testfiles/" + dirname)

            old_full_sigs = cur_full_sigs
            cur_full_sigs = Path("testfiles/output/fullsig." + dirname)

            delta1 = Path("testfiles/output/delta1." + dirname)
            delta2 = Path("testfiles/output/delta2." + dirname)
            incsig = Path("testfiles/output/incsig." + dirname)

            # Write old-style delta to deltadir1
            diffdir.write_block_iter(diffdir.DirDelta(get_sel(cur_dir),
                                               old_full_sigs.open("rb")),
                                     delta1)

            # Write new signature and delta to deltadir2 and sigdir2, compare
            block_iter = diffdir.DirDelta_WriteSig(get_sel(cur_dir),
                           map(lambda p: p.open("rb"), sigstack),
                                                   incsig.open("wb"))
            sigstack.append(incsig)
            diffdir.write_block_iter(block_iter, delta2)

            #print delta1.name, delta2.name
            compare_tar(delta1.open("rb"), delta2.open("rb"))
            assert not os.system("cmp %s %s" % (delta1.name, delta2.name))

            # Write old-style signature to cur_full_sigs
            diffdir.write_block_iter(diffdir.SigTarBlockIter(get_sel(cur_dir)),
                                     cur_full_sigs)

    def test_combine_path_iters(self):
        """Test diffdir.combine_path_iters"""
        class Dummy:
            def __init__(self, index, other = None):
                self.index = index
                self.other = other
            def __repr__(self): return "(%s %s)" % (self.index, self.other)

        def get_iter1():
            yield Dummy(())
            yield Dummy((1,))
            yield Dummy((1, 5), 2)

        def get_iter2():
            yield Dummy((), 2)
            yield Dummy((1,5))
            yield Dummy((2,))

        def get_iter3():
            yield Dummy((), 3)
            yield Dummy((2,), 1)

        result = diffdir.combine_path_iters([get_iter1(),
                                             get_iter2(),
                                             get_iter3()])
        elem1 = result.next()
        assert elem1.index == () and elem1.other == 3, elem1
        elem2 = result.next()
        assert elem2.index == (1,) and elem2.other is None, elem2
        elem3 = result.next()
        assert elem3.index == (1,5) and elem3.other is None
        elem4 = result.next()
        assert elem4.index == (2,) and elem4.other == 1
        try: elem5 = result.next()
        except StopIteration: pass
        else: assert 0, elem5


def compare_tar(tarfile1, tarfile2):
    """Compare two tarfiles"""
    tf1 = tarfile.TarFile("none", "r", tarfile1)
    tf2 = tarfile.TarFile("none", "r", tarfile2)
    tf2_iter = iter(tf2)

    for ti1 in tf1:
        try: ti2 = tf2_iter.next()
        except StopIteration:
            assert 0, ("Premature end to second tarfile, "
                       "ti1.name = %s" % ti1.name)
        #print "Comparing ", ti1.name, ti2.name
        assert tarinfo_eq(ti1, ti2), "%s %s" % (ti1.name, ti2.name)
        if ti1.size != 0:
            fp1 = tf1.extractfile(ti1)
            buf1 = fp1.read()
            fp1.close()
            fp2 = tf2.extractfile(ti2)
            buf2 = fp2.read()
            fp2.close()
            assert buf1 == buf2
    try: ti2 = tf2_iter.next()
    except StopIteration: pass
    else: assert 0, ("Premature end to first tarfile, "
                     "ti2.name = %s" % ti2.name)

    tarfile1.close()
    tarfile2.close()

def tarinfo_eq(ti1, ti2):
    if ti1.name != ti2.name:
        print "Name:", ti1.name, ti2.name
        return 0
    if ti1.size != ti2.size:
        print "Size:", ti1.size, ti2.size
        return 0
    if ti1.mtime != ti2.mtime:
        print "Mtime:", ti1.mtime, ti2.mtime
        return 0
    if ti1.mode != ti2.mode:
        print "Mode:", ti1.mode, ti2.mode
        return 0
    if ti1.type != ti2.type:
        print "Type:", ti1.type, ti2.type
        return 0
    if ti1.issym() or ti1.islnk():
        if ti1.linkname != ti2.linkname:
            print "Linkname:", ti1.linkname, ti2.linkname
            return 0
    if ti1.uid != ti2.uid or ti1.gid != ti2.gid:
        print "IDs:", ti1.uid, ti2.uid, ti1.gid, ti2.gid
        return 0
    if ti1.uname != ti2.uname or ti1.gname != ti2.gname:
        print "Owner names:", ti1.uname, ti2.uname, ti1.gname, ti2.gname
        return 0
    return 1

if __name__ == "__main__":
    unittest.main()

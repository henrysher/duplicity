# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-

import config
import sys, os, unittest
sys.path.insert(0, "../")
from duplicity import diffdir, patchdir, selection
from duplicity.path import *

config.setup()

class RootTest(unittest.TestCase):
    """Test doing operations that only root can"""
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

    def total_sequence(self, filelist):
        """Test signatures, diffing, and patching on directory list"""
        assert len(filelist) >= 2
        self.deltmp()
        assert not os.system("cp -a %s testfiles/output/sequence" %
                             (filelist[0],))
        seq_path = Path("testfiles/output/sequence")
        sig = Path("testfiles/output/sig.tar")
        diff = Path("testfiles/output/diff.tar")
        for dirname in filelist[1:]:
            new_path = Path(dirname)
            diffdir.write_block_iter(
                diffdir.DirSig(selection.Select(seq_path).set_iter()), sig)

            diffdir.write_block_iter(
                diffdir.DirDelta(selection.Select(new_path).set_iter(),
                                 sig.open("rb")),
                diff)

            patchdir.Patch(seq_path, diff.open("rb"))

            assert seq_path.compare_recursive(new_path, 1)

    def test_basic_cycle(self):
        """Test cycle on dir with devices, changing uid/gid, etc."""
        self.total_sequence(['testfiles/root1', 'testfiles/root2'])

def runtests(): unittest.main()

if __name__ == "__main__":
    unittest.main()

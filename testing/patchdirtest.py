from __future__ import generators
import sys
sys.path.insert(0, "../src")
import os, unittest
import diffdir, patchdir, log, selection, tarfile
from path import *

log.setverbosity(3)
		

class PatchingTest(unittest.TestCase):
	"""Test patching"""
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

	def test_total(self):
		"""Test cycle on dirx"""
		self.total_sequence(['testfiles/dir1',
							 'testfiles/dir2',
							 'testfiles/dir3'])

	def get_sel(self, path):
		"""Get selection iter over the given directory"""
		return selection.Select(path).set_iter()

	def total_sequence(self, filelist):
		"""Test signatures, diffing, and patching on directory list"""
		assert len(filelist) >= 2
		self.deltmp()
		sig = Path("testfiles/output/sig.tar")
		diff = Path("testfiles/output/diff.tar")
		seq_path = Path("testfiles/output/sequence")		
		new_path, old_path = None, None # set below in for loop

		# Write initial full backup to diff.tar
		for dirname in filelist:
			old_path, new_path = new_path, Path(dirname)
			if old_path:
				sigblock = diffdir.DirSig(self.get_sel(seq_path))
				diffdir.write_block_iter(sigblock, sig)
				deltablock = diffdir.DirDelta(self.get_sel(new_path),
											  sig.open("rb"))
			else: deltablock = diffdir.DirFull(self.get_sel(new_path))
			diffdir.write_block_iter(deltablock, diff)

			patchdir.Patch(seq_path, diff.open("rb"))
			#print "#########", seq_path, new_path
			assert seq_path.compare_recursive(new_path, 1)

	def test_root(self):
		"""Test changing uid/gid, devices"""
		self.deltmp()
		os.system("cp -a testfiles/root1 testfiles/output/sequence")
		seq_path = Path("testfiles/output/sequence")
		new_path = Path("testfiles/root2")
		sig = Path("testfiles/output/sig.tar")
		diff = Path("testfiles/output/diff.tar")

		diffdir.write_block_iter(diffdir.DirSig(self.get_sel(seq_path)), sig)
		deltablock = diffdir.DirDelta(self.get_sel(new_path), sig.open("rb"))
		diffdir.write_block_iter(deltablock, diff)

		patchdir.Patch(seq_path, diff.open("rb"))

		# since we are not running as root, don't even both comparing,
		# just make sure file5 exists and file4 doesn't.
		file5 = seq_path.append("file5")
		assert file5.isreg()
		file4 = seq_path.append("file4")
		assert file4.type is None

	def test_root2(self):
		"""Again test files we don't have access to, this time Tar_WriteSig"""
		self.deltmp()
		sig_path = Path("testfiles/output/sig.sigtar")
		tar_path = Path("testfiles/output/tar.tar")
		basis_path = Path("testfiles/root1")

		deltablock = diffdir.DirFull_WriteSig(self.get_sel(basis_path),
											  sig_path.open("wb"))
		diffdir.write_block_iter(deltablock, tar_path)
		
	def test_block_tar(self):
		"""Test building block tar from a number of files"""
		def get_fileobjs():
			"""Return iterator yielding open fileobjs of tar files"""
			for i in range(1, 4):
				p = Path("testfiles/blocktartest/test%d.tar" % i)
				fp = p.open("rb")
				yield fp
				fp.close()

		tf = patchdir.TarFile_FromFileobjs(get_fileobjs())
		namelist = []
		for tarinfo in tf: namelist.append(tarinfo.name)
		for i in range(1, 6):
			assert ("tmp/%d" % i) in namelist, namelist
		

if __name__ == "__main__": unittest.main()

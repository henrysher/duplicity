import sys, random, unittest
sys.path.insert(0, "../src")
import collections, backends, path, gpg, globals

filename_list1 = ["duplicity-full.2002-08-17T16:17:01-07:00.manifest.gpg",
				  "duplicity-full.2002-08-17T16:17:01-07:00.vol1.difftar.gpg",
				  "duplicity-full.2002-08-17T16:17:01-07:00.vol2.difftar.gpg",
				  "duplicity-full.2002-08-17T16:17:01-07:00.vol3.difftar.gpg",
				  "duplicity-full.2002-08-17T16:17:01-07:00.vol4.difftar.gpg",
				  "duplicity-full.2002-08-17T16:17:01-07:00.vol5.difftar.gpg",
				  "duplicity-full.2002-08-17T16:17:01-07:00.vol6.difftar.gpg",
				  "duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.manifest.gpg",
				  "duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.vol1.difftar.gpg",
				  "Extra stuff to be ignored"]

remote_sigchain_filename_list = ["duplicity-full-signatures.2002-08-17T16:17:01-07:00.sigtar.gpg",
								 "duplicity-new-signatures.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.sigtar.gpg",
								 "duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.gpg"]

local_sigchain_filename_list =  ["duplicity-full-signatures.2002-08-17T16:17:01-07:00.sigtar.gz",
								 "duplicity-new-signatures.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.sigtar.gz",
								 "duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.gz"]


col_test_dir = path.Path("testfiles/collectionstest")
archive_dir = col_test_dir.append("archive_dir")
archive_dir_backend = backends.get_backend("file://testfiles/collectionstest"
										   "/archive_dir")

dummy_backend = None
real_backend = backends.LocalBackend(col_test_dir.append("remote_dir").name)


class CollectionTest(unittest.TestCase):
	"""Test collections"""
	def set_gpg_profile(self):
		"""Set gpg profile to standard "foobar" sym"""
		globals.gpg_profile = gpg.GPGProfile(passphrase = "foobar")

	def test_backup_chains(self):
		"""Test basic backup chain construction"""
		random.shuffle(filename_list1)
		cs = collections.CollectionsStatus(dummy_backend, archive_dir)
		chains, orphaned, incomplete = cs.get_backup_chains(filename_list1)
		if len(chains) != 1 or len(orphaned) != 0:
			print chains
			print orphaned
			assert 0

		chain = chains[0]
		assert chain.end_time == 1029654270L
		assert chain.fullset.time == 1029626221L

	def test_collections_status(self):
		"""Test CollectionStatus object's set_values()"""
		def check_cs(cs):
			"""Check values of collections status"""
			assert cs.values_set

			assert cs.matched_chain_pair
			assert cs.matched_chain_pair[0].end_time == 1029826800L
			assert len(cs.all_backup_chains) == 1, cs.all_backup_chains

		cs1 = collections.CollectionsStatus(real_backend).set_values()
		check_cs(cs1)
		assert not cs1.matched_chain_pair[0].islocal()

		cs2 = collections.CollectionsStatus(real_backend, archive_dir).set_values()
		check_cs(cs2)
		assert cs2.matched_chain_pair[0].islocal()

	def test_sig_chain(self):
		"""Test a single signature chain"""
		chain = collections.SignatureChain(1, archive_dir)
		for filename in local_sigchain_filename_list:
			assert chain.add_filename(filename)
		assert not chain.add_filename("duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.gpg")

	def test_sig_chains(self):
		"""Test making signature chains from filename list"""
		cs = collections.CollectionsStatus(dummy_backend, archive_dir)
		chains, orphaned_paths = cs.get_signature_chains(local = 1)
		self.sig_chains_helper(chains, orphaned_paths)

	def test_sig_chains2(self):
		"""Test making signature chains from filename list on backend"""
		cs = collections.CollectionsStatus(archive_dir_backend)
		chains, orphaned_paths = cs.get_signature_chains(local = None)
		self.sig_chains_helper(chains, orphaned_paths)

	def sig_chains_helper(self, chains, orphaned_paths):
		"""Test chains and orphaned_paths values for two above tests"""
		if orphaned_paths:
			for op in orphaned_paths: print op
			assert 0
		assert len(chains) == 1, chains
		assert chains[0].end_time == 1029826800L

	def sigchain_fileobj_get(self, local):
		"""Return chain, local if local is true with filenames added"""
		if local:
			chain = collections.SignatureChain(1, archive_dir)
			for filename in local_sigchain_filename_list:
				assert chain.add_filename(filename)
		else:
			chain = collections.SignatureChain(None, real_backend)
			for filename in remote_sigchain_filename_list:
				assert chain.add_filename(filename)
		return chain

	def sigchain_fileobj_testlist(self, chain):
		"""Make sure the list of file objects in chain has right contents

		The contents of the testfiles/collectiontest/remote_dir have
		to be coordinated with this test.

		"""
		fileobjlist = chain.get_fileobjs()
		assert len(fileobjlist) == 3
		def test_fileobj(i, s):
			buf = fileobjlist[i].read()
			fileobjlist[i].close()
			assert buf == s, (buf, s)
		test_fileobj(0, "Hello, world!")
		test_fileobj(1, "hello 1")
		test_fileobj(2, "Hello 2")

	def test_sigchain_fileobj(self):
		"""Test getting signature chain fileobjs from archive_dir"""
		self.set_gpg_profile()
		self.sigchain_fileobj_testlist(self.sigchain_fileobj_get(1))
		self.sigchain_fileobj_testlist(self.sigchain_fileobj_get(None))		

		

if __name__ == "__main__": unittest.main()

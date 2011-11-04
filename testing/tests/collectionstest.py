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
import os, sys, random, unittest

from duplicity import collections
from duplicity import backend
from duplicity import path
from duplicity import gpg
from duplicity import globals
from duplicity import dup_time

helper.setup()

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

# A filename list with some incomplete volumes, an older full volume,
# and a complete chain.
filename_list2 = ["duplicity-full.2001-01-01T16:17:01-07:00.manifest.gpg",
                  "duplicity-full.2001-01-01T16:17:01-07:00.vol1.difftar.gpg",
                  "duplicity-full.2002-08-17T16:17:01-07:00.manifest.gpg",
                  "duplicity-full.2002-08-17T16:17:01-07:00.vol1.difftar.gpg",
                  "duplicity-full.2002-08-17T16:17:01-07:00.vol2.difftar.gpg",
                  "duplicity-full.2002-08-17T16:17:01-07:00.vol3.difftar.gpg",
                  "duplicity-full.2002-08-17T16:17:01-07:00.vol4.difftar.gpg",
                  "duplicity-full.2002-08-17T16:17:01-07:00.vol5.difftar.gpg",
                  "duplicity-full.2002-08-17T16:17:01-07:00.vol6.difftar.gpg",
                  "duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.manifest.gpg",
                  "duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.vol1.difftar.gpg",
                  "The following are extraneous duplicity files",
                  "duplicity-new-signatures.2001-08-17T02:05:13-05:00.to.2002-08-17T05:05:14-05:00.sigtar.gpg",
                  "duplicity-full.2002-08-15T01:01:01-07:00.vol1.difftar.gpg",
                  "duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.manifest.gpg",
                  "duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.vol1.difftar.gpg",
                  "Extra stuff to be ignored"]

assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")

col_test_dir = path.Path("testfiles/collectionstest")
archive_dir = col_test_dir.append("archive_dir")
globals.archive_dir = archive_dir
archive_dir_backend = backend.get_backend("file://testfiles/collectionstest"
                                           "/archive_dir")

dummy_backend = None
real_backend = backend.get_backend("file://%s/%s" %
                                   (col_test_dir.name, "remote_dir"))
output_dir = path.Path("testfiles/output") # used as a temp directory
output_dir_backend = backend.get_backend("file://testfiles/output")


class CollectionTest(unittest.TestCase):
    """Test collections"""
    def setUp(self):
        assert not os.system("tar xzf testfiles.tar.gz > /dev/null 2>&1")
        assert not os.system("mkdir testfiles/output")

    def tearDown(self):
        assert not os.system("rm -rf testfiles tempdir temp2.tar")

    def del_tmp(self):
        """Reset the testfiles/output directory"""
        output_dir.deltree()
        output_dir.mkdir()

    def set_gpg_profile(self):
        """Set gpg profile to standard "foobar" sym"""
        globals.gpg_profile = gpg.GPGProfile(passphrase = "foobar")

    def test_backup_chains(self):
        """Test basic backup chain construction"""
        random.shuffle(filename_list1)
        cs = collections.CollectionsStatus(dummy_backend, archive_dir)
        chains, orphaned, incomplete = cs.get_backup_chains(filename_list1) #@UnusedVariable
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

        cs = collections.CollectionsStatus(real_backend, archive_dir).set_values()
        check_cs(cs)
        assert cs.matched_chain_pair[0].islocal()

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
        cs = collections.CollectionsStatus(archive_dir_backend, archive_dir)
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

    def get_filelist2_cs(self):
        """Return set CollectionsStatus object from filelist 2"""
        # Set up testfiles/output with files from filename_list2
        self.del_tmp()
        for filename in filename_list2:
            p = output_dir.append(filename)
            p.touch()

        cs = collections.CollectionsStatus(output_dir_backend, archive_dir)
        cs.set_values()
        return cs

    def test_get_extraneous(self):
        """Test the listing of extraneous files"""
        cs = self.get_filelist2_cs()
        assert len(cs.orphaned_backup_sets) == 1, cs.orphaned_backup_sets
        assert len(cs.local_orphaned_sig_names) == 0, cs.local_orphaned_sig_names
        assert len(cs.remote_orphaned_sig_names) == 1, cs.remote_orphaned_sig_names
        assert len(cs.incomplete_backup_sets) == 1, cs.incomplete_backup_sets

        right_list = ["duplicity-new-signatures.2001-08-17T02:05:13-05:00.to.2002-08-17T05:05:14-05:00.sigtar.gpg",
                      "duplicity-full.2002-08-15T01:01:01-07:00.vol1.difftar.gpg",
                      "duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.manifest.gpg",
                      "duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.vol1.difftar.gpg"]
        local_received_list, remote_received_list = cs.get_extraneous(False) #@UnusedVariable
        errors = []
        for filename in remote_received_list:
            if filename not in right_list:
                errors.append("### Got bad extraneous filename " + filename)
            else: right_list.remove(filename)
        for filename in right_list:
            errors.append("### Didn't receive extraneous filename " + filename)
        assert not errors, "\n"+"\n".join(errors)

    def test_get_olderthan(self):
        """Test getting list of files older than a certain time"""
        cs = self.get_filelist2_cs()
        oldsets = cs.get_older_than(
            dup_time.genstrtotime("2002-05-01T16:17:01-07:00"))
        oldset_times = map(lambda s: s.get_time(), oldsets)
        right_times = map(dup_time.genstrtotime, ['2001-01-01T16:17:01-07:00'])
        assert oldset_times == right_times, \
               [oldset_times, right_times]

        oldsets_required = cs.get_older_than_required(
            dup_time.genstrtotime("2002-08-17T20:00:00-07:00"))
        oldset_times = map(lambda s: s.get_time(), oldsets_required)
        right_times_required = map(dup_time.genstrtotime,
                                   ['2002-08-17T16:17:01-07:00'])
        assert oldset_times == right_times_required, \
               [oldset_times, right_times_required]


if __name__ == "__main__":
    unittest.main()

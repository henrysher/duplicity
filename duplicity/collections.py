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

"""Classes and functions on collections of backup volumes"""

import gzip, types
import log, file_naming, path, dup_time, globals, manifest

class CollectionsError(Exception): pass

class BackupSet:
	"""Backup set - the backup information produced by one session"""
	def __init__(self, backend):
		"""Initialize new backup set, only backend is required at first"""
		self.backend = backend
		self.info_set = None
		self.volume_name_dict = {} # dict from volume number to filename
		self.remote_manifest_name = None
		self.local_manifest_path = None
		self.time = None # will be set if is full backup set
		self.start_time, self.end_time = None, None # will be set if inc

	def is_complete(self):
		"""Assume complete if found manifest file"""
		return self.remote_manifest_name

	def add_filename(self, filename):
		"""Add a filename to given set.  Return true if it fits.

		The filename will match the given set if it has the right
		times and is of the right type.  The information will be set
		from the first filename given.

		"""
		pr = file_naming.parse(filename)
		if not pr or not (pr.type == "full" or pr.type == "inc"): return None

		if not self.info_set: self.set_info(pr)
		else:
			if pr.type != self.type: return None
			if pr.time != self.time: return None
			if (pr.start_time != self.start_time or
				pr.end_time != self.end_time): return None

		if pr.manifest: self.set_manifest(filename)
		else:
			assert pr.volume_number is not None
			assert not self.volume_name_dict.has_key(pr.volume_number), \
				   (self.volume_name_dict, filename)
			self.volume_name_dict[pr.volume_number] = filename
		return 1

	def set_info(self, pr):
		"""Set BackupSet information from ParseResults object"""
		assert not self.info_set
		self.type = pr.type
		self.time = pr.time
		self.start_time, self.end_time = pr.start_time, pr.end_time
		self.time = pr.time
		self.info_set = 1

	def set_manifest(self, remote_filename):
		"""Add local and remote manifest filenames to backup set"""
		assert not self.remote_manifest_name, (self.remote_manifest_name,
											   remote_filename)
		self.remote_manifest_name = remote_filename

		if not globals.archive_dir: return
		for local_filename in globals.archive_dir.listdir():
			pr = file_naming.parse(local_filename)
			if (pr and pr.manifest and pr.type == self.type and
				pr.time == self.time and pr.start_time == self.start_time
				and pr.end_time == self.end_time):
				self.local_manifest_path = \
							  globals.archive_dir.append(local_filename)
				break

	def delete(self):
		"""Remove all files in set"""
		self.backend.delete(self.remote_manfest_name)
		for filename in self.volume_name_dict: self.backend.delete(filename)

	def __str__(self):
		"""For now just list files in set"""
		filelist = []
		if self.remote_manifest_name:
			filelist.append(self.remote_manifest_name)
		filelist.extend(self.volume_name_dict.values())
		return "\n".join(filelist)

	def get_timestr(self):
		"""Return time string suitable for log statements"""
		return dup_time.timetopretty(self.time or self.end_time)

	def check_manifests(self):
		"""Make sure remote manifest is equal to local one"""
		if not self.remote_manifest_name and not self.local_manifest_path:
			log.FatalError("Fatal Error: "
						   "No manifests found for most recent backup")
		assert self.remote_manifest_name, "if only one, should be remote"
		remote_manifest = self.get_remote_manifest()
		if self.local_manifest_path:
			local_manifest = self.get_local_manifest()
			if remote_manifest != local_manifest:
				log.FatalError(
"""Fatal Error: Remote manifest does not match local one.  Either the
remote backup set or the local archive directory has been corrupted.""")

		remote_manifest.check_dirinfo()

	def get_local_manifest(self):
		"""Return manifest object by reading local manifest file"""
		assert self.local_manifest_path
		manifest_buffer = self.local_manifest_path.get_data()
		return manifest.Manifest().from_string(manifest_buffer)

	def get_remote_manifest(self):
		"""Return manifest by reading remote manifest on backend"""
		assert self.remote_manifest_name
		manifest_buffer = self.backend.get_data(self.remote_manifest_name)
		return manifest.Manifest().from_string(manifest_buffer)

	def get_manifest(self):
		"""Return manifest object, showing preference for local copy"""
		if self.local_manifest_path: return self.get_local_manifest()
		else: return self.get_remote_manifest()


class BackupChain:
	"""BackupChain - a number of linked BackupSets

	A BackupChain always starts with a full backup set and continues
	with incremental ones.

	"""
	def __init__(self, backend):
		"""Initialize new chain, only backend is required at first"""
		self.backend = backend
		self.fullset = None
		self.incset_list = [] # sorted list of BackupSets
		self.start_time, self.end_time = None, None

	def set_full(self, fullset):
		"""Add full backup set"""
		assert not self.fullset and isinstance(fullset, BackupSet)
		self.fullset = fullset
		assert fullset.time
		self.start_time, self.end_time = fullset.time, fullset.time

	def add_inc(self, incset):
		"""Add incset to self.  Return None if incset does not match"""
		if self.end_time == incset.start_time:
			self.incset_list.append(incset)
			self.end_time = incset.end_time
			assert self.end_time
			return 1
		else: return None

	def delete(self):
		"""Delete all sets in chain, in reverse order"""
		for i in range(len(self.incset_list)-1, -1, -1):
			self.incset_list[i].delete()

	def get_sets_at_time(self, time):
		"""Return a list of sets in chain earlier or equal to time"""
		older_incsets = filter(lambda s: s.end_time <= time, self.incset_list)
		return [self.fullset] + older_incsets

	def get_last(self):
		"""Return last BackupSet in chain"""
		if self.incset_list: return self.incset_list[-1]
		else: return self.fullset


class SignatureChain:
	"""A number of linked signatures

	Analog to BackupChain - start with a full-sig, and continue with
	new-sigs.

	"""
	def __init__(self, local, location):
		"""Return new SignatureChain.

		local should be true iff the signature chain resides in
		globals.archive_dir and false if the chain is in
		globals.backend.

		"""
		if local: self.archive_dir, self.backend = location, None
		else: self.archive_dir, self.backend = None, location
		self.fullsig = None # filename of full signature
		self.inclist = [] # list of filenames of incremental signatures
		self.start_time, self.end_time = None, None

	def check_times(self, time_list):
		"""Check to make sure times are in whole seconds"""
		for time in time_list:
			if type(time) not in (types.LongType, types.IntType):
				assert 0, "Time %s in %s wrong type" % (time, time_list)

	def islocal(self):
		"""Return true if represents a signature chain in archive_dir"""
		return self.archive_dir

	def add_filename(self, filename, pr = None):
		"""Add new sig filename to current chain.  Return true if fits"""
		if not pr: pr = file_naming.parse(filename)
		if not pr: return None

		if self.fullsig:
			if pr.type != "new-sig": return None
			if pr.start_time != self.end_time: return None
			self.inclist.append(filename)
			self.check_times([pr.end_time])
			self.end_time = pr.end_time
			return 1
		else:
			if pr.type != "full-sig": return None
			self.fullsig = filename
			self.check_times([pr.time, pr.time])
			self.start_time, self.end_time = pr.time, pr.time
			return 1
		
	def get_fileobjs(self):
		"""Return ordered list of signature fileobjs opened for reading"""
		assert self.fullsig
		if self.archive_dir: # local
			def filename_to_fileobj(filename):
				"""Open filename in archive_dir, return filtered fileobj"""
				sig_dp = path.DupPath(self.archive_dir.name, (filename,))
				return sig_dp.filtered_open("rb")
		else: filename_to_fileobj = self.backend.get_fileobj_read
		return map(filename_to_fileobj, [self.fullsig] + self.inclist)

	def delete(self):
		"""Remove all files in signature set"""
		# Try to delete in opposite order, so something useful even if aborted
		if self.archive_dir:
			for i in range(len(self.inclist)-1, -1, -1):
				self.inclist[i].delete()
			self.fullsig.delete()
		else:
			assert self.backend
			inclist_copy = self.inclist[:]
			inclist_copy.reverse()
			inclist_copy.append(self.fullsig)
			self.backend.delete(inclist_copy)


class CollectionsStatus:
	"""Hold information about available chains and sets"""
	def __init__(self, backend, archive_dir = None):
		"""Make new object.  Does not set values"""
		self.backend, self.archive_dir = backend, archive_dir

		# Will hold (signature chain, backup chain) pair of active
		# (most recent) chains
		self.matched_chain_pair = None

		# These should be sorted by end_time
		self.all_backup_chains = None
		self.other_backup_chains = None
		self.other_sig_chains = None

		# Other misc paths and sets which shouldn't be there
		self.orphaned_sig_names = None
		self.orphaned_backup_sets = None
		self.incomplete_backup_sets = None

		# True if set_values() below has run
		self.values_set = None

	def __str__(self):
		"""Return string version, for testing purposes"""
		l = ["Backend: %s" % (self.backend,),
			 "Archive dir: %s" % (self.archive_dir,),
			 "Matched pair: %s" % (self.matched_chain_pair,),
			 "All backup chains: %s" % (self.all_backup_chains,),
			 "Other backup chains: %s" % (self.other_backup_chains,),
			 "Other sig chains: %s" % (self.other_sig_chains,),
			 "Orphaned sig names: %s" % (self.orphaned_sig_names,),
			 "Orphaned backup sets: %s" % (self.orphaned_backup_sets,),
			 "Incomplete backup sets: %s" % (self.incomplete_backup_sets,)]
		return "\n".join(l)

	def set_values(self, sig_chain_warning = 1):
		"""Set values from archive_dir and backend.

		if archive_dir is None, omit any local chains.  Returs self
		for convenience.  If sig_chain_warning is set to None, do not
		warn about unnecessary sig chains.  This is because there may
		naturally be some unecessary ones after a full backup.

		"""
		self.values_set = 1
		backend_filename_list = self.backend.list()

		backup_chains, self.orphaned_backup_sets, self.incomplete_backup_set=\
					   self.get_backup_chains(backend_filename_list)
		backup_chains = self.get_sorted_chains(backup_chains)
		self.all_backup_chains = backup_chains

		if self.archive_dir:
			local_sig_chains, local_orphaned_sig_names = \
							  self.get_signature_chains(local = 1)
		else: local_sig_chains, local_orphaned_sig_names = [], []
		remote_sig_chains, remote_orphaned_sig_names = \
						   self.get_signature_chains(0, backend_filename_list)
		self.orphaned_sig_names = (local_orphaned_sig_names +
								   remote_orphaned_sig_names)
		self.set_matched_chain_pair(local_sig_chains + remote_sig_chains,
									backup_chains)
		self.warn(sig_chain_warning)
		return self

	def set_matched_chain_pair(self, sig_chains, backup_chains):
		"""Set self.matched_chain_pair and self.other_sig/backup_chains

		The latest matched_chain_pair will be set.  If there are both
		remote and local signature chains capable of matching the
		latest backup chain, use the local sig chain (it does not need
		to be downloaded).

		"""
		if sig_chains and backup_chains:
			latest_backup_chain = backup_chains[-1]
			sig_chains = self.get_sorted_chains(sig_chains)
			for i in range(len(sig_chains)-1, -1, -1):
				if sig_chains[i].end_time == latest_backup_chain.end_time:
					self.matched_chain_pair = (sig_chains[i],
											   backup_chains[-1])
					del sig_chains[i]
					break
			
		self.other_sig_chains = sig_chains
		self.other_backup_chains = backup_chains

	def warn(self, sig_chain_warning):
		"""Log various error messages if find incomplete/orphaned files"""
		assert self.values_set
		if self.orphaned_sig_names:
			log.Log("Warning, found the following orphaned signature files:\n"
					+ "\n".join(self.orphaned_sig_names), 2)
		if self.other_sig_chains and sig_chain_warning:
			if self.matched_chain_pair:
				log.Log("Warning, found unnecessary signature chain(s)", 2)
			else: log.FatalError("Found signatures but no corresponding "
								 "backup files")

		if self.incomplete_backup_sets:
			log.Log("Warning, found incomplete backup sets, probably left "
					"from aborted session", 2)
		if self.orphaned_backup_sets:
			log.Log("Warning, found the following orphaned backup files:\n"
					+ "\n".join(map(lambda x: str(x), orphaned_sets)), 2)

	def get_backup_chains(self, filename_list):
		"""Split given filename_list into chains

		Return value will be pair (list of chains, list of sets, list
		of incomplete sets), where the list of sets will comprise sets
		not fitting into any chain, and the incomplete sets are sets
		missing files.

		"""
		# First put filenames in set form
		sets = []
		def add_to_sets(filename):
			"""Try adding filename to existing sets, or make new one"""
			for set in sets:
				if set.add_filename(filename): break
			else:
				new_set = BackupSet(self.backend)
				if new_set.add_filename(filename): sets.append(new_set)
				else: log.Log("Ignoring file '%s'" % filename, 9)
		map(add_to_sets, filename_list)
		sets, incomplete_sets = self.get_sorted_sets(sets)

		chains, orphaned_sets = [], []
		def add_to_chains(set):
			"""Try adding set to existing chains, or make new one"""
			if set.type == "full":
				new_chain = BackupChain(self.backend)
				new_chain.set_full(set)
				chains.append(new_chain)
			else:
				assert set.type == "inc"
				for chain in chains:
					if chain.add_inc(set): break
				else: orphaned_sets.append(set)
		map(add_to_chains, sets)
		return (chains, orphaned_sets, incomplete_sets)

	def get_sorted_sets(self, set_list):
		"""Sort set list by end time, return (sorted list, incomplete)"""
		time_set_pairs, incomplete_sets = [], []
		for set in set_list:
			if not set.is_complete: incomplete_sets.append(set)
			elif set.type == "full": time_set_pairs.append((set.time, set))
			else: time_set_pairs.append((set.end_time, set))
		time_set_pairs.sort()
		return (map(lambda p: p[1], time_set_pairs), incomplete_sets)

	def get_signature_chains(self, local, filelist = None):
		"""Find chains in archive_dir (if local is true) or backend

		Use filelist if given, otherwise regenerate.  Return value is
		pair (list of chains, list of signature paths not in any
		chains).

		"""
		def get_filelist():
			if filelist is not None: return filelist
			elif local: return self.archive_dir.listdir()
			else: return self.backend.list()

		def get_new_sigchain():
			"""Return new empty signature chain"""
			if local: return SignatureChain(1, self.archive_dir)
			else: return SignatureChain(None, self.backend)

		# Build initial chains from full sig filenames
		chains, new_sig_filenames = [], []
		for filename in get_filelist():
			pr = file_naming.parse(filename)
			if pr:
				if pr.type == "full-sig":
					new_chain = get_new_sigchain()
					assert new_chain.add_filename(filename, pr)
					chains.append(new_chain)
				elif pr.type == "new-sig": new_sig_filenames.append(filename)

		# Try adding new signatures to existing chains
		orphaned_filenames = []
		new_sig_filenames.sort()
		for sig_filename in new_sig_filenames:
			for chain in chains:
				if chain.add_filename(sig_filename): break
			else: orphaned_filenames.append(sig_filename)
		return (chains, orphaned_filenames)

	def get_sorted_chains(self, chain_list):
		"""Return chains sorted by end_time.  If tie, local goes last"""
		# Build dictionary from end_times to lists of corresponding chains
		endtime_chain_dict = {}
		for chain in chain_list:
			if endtime_chain_dict.has_key(chain.end_time):
				endtime_chain_dict[chain.end_time].append(chain)
			else: endtime_chain_dict[chain.end_time] = [chain]
		
		# Use dictionary to build final sorted list
		sorted_end_times = endtime_chain_dict.keys()
		sorted_end_times.sort()
		sorted_chain_list = []
		for end_time in sorted_end_times:
			chain_list = endtime_chain_dict[end_time]
			if len(chain_list) == 1: sorted_chain_list.append(chain_list[0])
			else:
				assert len(chain_list) == 2
				if chain_list[0].backend: # is remote, goes first
					assert chain_list[1].archive_dir # other is local
					sorted_chain_list.append(chain_list[0])
					sorted_chain_list.append(chain_list[1])
				else: # is local, goes second
					assert chain_list[1].backend # other is remote
					sorted_chain_list.append(chain_list[1])
					sorted_chain_list.append(chain_list[0])

		return sorted_chain_list

	def get_backup_chain_at_time(self, time):
		"""Return backup chain covering specified time

		Tries to find the backup chain covering the given time.  If
		there is none, return the earliest chain before, and failing
		that, the earliest chain.

		"""
		if not self.all_backup_chains:
			raise CollectionsError("No backup chains found")

		covering_chains = filter(lambda c: c.start_time <= time <= c.end_time,
								 self.all_backup_chains)
		if len(covering_chains) > 1:
			raise CollectionsError("Two chains cover the given time")
		elif len(covering_chains) == 1: return covering_chains[0]

		old_chains = filter(lambda c: c.end_time < time,
							self.all_backup_chains)
		if old_chains: return old_chains[-1]
		else: return self.all_backup_chains[0] # no chains are old enough

	def cleanup_signatures(self):
		"""Delete unnecessary older signatures"""
		map(SignatureChain.delete, self.other_sig_chains)

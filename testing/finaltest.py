import sys, os, unittest
sys.path.insert(0, "../duplicity")
import path, backends

# This can be changed to select the URL to use
backend_url = "file://testfiles/output"
#backend_url = "ftp://Stan Ford@90-92L-imac.stanford.edu/Macintosh HD/temp"
#backend_url = "scp://localhost//home/ben/prog/python/duplicity/testing/testfiles/output"

# Extra arguments to be passed to duplicity
other_args = []
#other_args = ["--short-filenames"]
#other_args = ["--ssh-command 'ssh -v'", "--scp-command 'scp -C'"]

# If this is set to true, after each backup, verify contents
verify = 1

class FinalTest(unittest.TestCase):
	"""Test backup/restore using duplicity binary"""
	def run_duplicity(self, arglist, options = [], current_time = None):
		"""Run duplicity binary with given arguments and options"""
		cmd_list = ["../duplicity-bin"]
		cmd_list.extend(options + ["-v3", "--allow-source-mismatch"])
		if current_time: cmd_list.append("--current-time %s" % (current_time,))
		if other_args: cmd_list.extend(other_args)
		cmd_list.extend(arglist)
		cmdline = " ".join(cmd_list)
		print "Running '%s'." % cmdline
		if not os.environ.has_key('PASSPHRASE'):
			os.environ['PASSPHRASE'] = 'foobar'
		assert not os.system(cmdline)

	def backup(self, type, input_dir, options = [], current_time = None):
		"""Run duplicity backup to default directory"""
		options = options[:]
		if type == "full": options.append('--full')
		args = [input_dir, "'%s'" % backend_url]
		self.run_duplicity(args, options, current_time)

	def restore(self, file_to_restore = None, time = None, options = [],
				current_time = None):
		options = options[:] # just nip any mutability problems in bud
		assert not os.system("rm -rf testfiles/restore_out")
		args = ["'%s'" % backend_url, "testfiles/restore_out"]
		if file_to_restore:
			options.extend(['--file-to-restore', file_to_restore])
		if time: options.extend(['--restore-time', str(time)])
		self.run_duplicity(args, options, current_time)

	def verify(self, dirname, file_to_verify = None, time = None, options = [],
			   current_time = None):
		options = options[:]
		args = ["--verify", "'%s'" % backend_url, dirname]
		if file_to_verify:
			options.extend(['--file-to-restore', file_to_verify])
		if time: options.extend(['--restore-time', str(time)])
		self.run_duplicity(args, options, current_time)

	def deltmp(self):
		"""Delete temporary directories"""
		assert not os.system("rm -rf testfiles/output "
							 "testfiles/restore_out testfiles/tmp_archive")
		assert not os.system("mkdir testfiles/output testfiles/tmp_archive")
		backend = backends.get_backend(backend_url)
		bl = backend.list()
		if bl: backend.delete(backend.list())
		backend.close()

	def runtest(self, dirlist, backup_options = [], restore_options = []):
		"""Run backup/restore test on directories in dirlist"""
		assert len(dirlist) >= 1
		self.deltmp()

		# Back up directories to local backend
		current_time = 100000
		self.backup("full", dirlist[0], current_time = current_time,
					options = backup_options)
		for new_dir in dirlist[1:]:
			current_time += 100000
			self.backup("inc", new_dir, current_time = current_time,
						options = backup_options)

		# Restore each and compare them
		for i in range(len(dirlist)):
			dirname = dirlist[i]
			current_time = 100000*(i + 1)
			self.restore(time = current_time, options = restore_options)
			self.check_same(dirname, "testfiles/restore_out")
			if verify:
				self.verify(dirname,
							time = current_time, options = restore_options)

	def check_same(self, filename1, filename2):
		"""Verify two filenames are the same"""
		path1, path2 = path.Path(filename1), path.Path(filename2)
		assert path1.compare_recursive(path2, verbose = 1)

	def test_basic_cycle(self, backup_options = [], restore_options = []):
		"""Run backup/restore test on basic directories"""
		self.runtest(["testfiles/dir1", "testfiles/dir2",
					  "testfiles/dir3",
					  "testfiles/various_file_types/regular_file",
					  "testfiles/empty_dir"],
					 backup_options = backup_options,
					 restore_options = restore_options)

		# Test restoring various sub files
		for filename, time, dir in [('symbolic_link', 99999, 'dir1'),
									('directory_to_file', 100100, 'dir1'),
									('directory_to_file', 200100, 'dir2'),
									('largefile', 300000, 'dir3')]:
			self.restore(filename, time, options = restore_options)
			self.check_same('testfiles/%s/%s' % (dir, filename),
							'testfiles/restore_out')
			if verify:
				self.verify('testfiles/%s/%s' % (dir, filename),
							file_to_verify = filename, time = time,
							options = restore_options)

	def test_asym_cycle(self):
		"""Like test_basic_cycle but use asymmetric encryption and signing"""
		backup_options = ["--encrypt-key AA0E73D2", "--sign-key AA0E73D2"]
		restore_options = ['--sign-key AA0E73D2']
		self.test_basic_cycle(backup_options = backup_options,
							  restore_options = restore_options)

	def test_archive_dir(self):
		"""Like test_basic_cycle, but use a local archive dir"""
		options = ["--archive-dir testfiles/tmp_archive"]
		self.test_basic_cycle(backup_options = options,
							  restore_options = options)

	def test_single_regfile(self):
		"""Test backing and restoring up a single regular file"""
		self.runtest(["testfiles/various_file_types/regular_file"])


if __name__ == "__main__": unittest.main()

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

"""Parse command line, check for consistency, and set globals"""

import getopt, re, sys
import backends, globals, log, path, selection, gpg, dup_time

select_opts = [] # Will hold all the selection options
select_files = [] # Will hold file objects when filelist given
full_backup = None # Will be set to true if -f or --full option given
list_current = None # Will be set to true if --list-current option given
collection_status = None # Will be set to true if --collection-status given
cleanup = None # Set to true if --cleanup option given
verify = None # Set to true if --verify option given

def parse_cmdline_options(arglist):
	"""Parse argument list"""
	global select_opts, select_files, full_backup
	global list_current, collection_status, cleanup, remove_time, verify
	def sel_fl(filename):
		"""Helper function for including/excluding filelists below"""
		try: return open(filename, "r")
		except IOError: log.FatalError("Error opening file %s" % filename)

	try: optlist, args = getopt.getopt(arglist, "firt:v:V",
		 ["allow-source-mismatch", "archive-dir=", "cleanup",
		  "current-time=", "collection-status", "encrypt-key=",
		  "exclude=", "exclude-device-files", "exclude-filelist=",
		  "exclude-globbing-filelist=", "exclude-filelist-stdin",
		  "exclude-other-filesystems", "exclude-regexp=",
		  "file-to-restore=", "force", "full", "incremental",
		  "include=", "include-filelist=", "include-filelist-stdin",
		  "include-globbing-filelist=", "include-regexp=",
		  "list-current-files", "no-encryption",
		  "no-print-statistics", "null-separator",
		  "remove-older-than=", "restore-dir=", "restore-time=",
		  "scp-command=", "short-filenames", "sign-key=",
		  "ssh-command=", "verbosity=", "verify", "version"])
	except getopt.error, e:
		command_line_error("%s" % (str(e),))

	for opt, arg in optlist:
		if opt == "--allow-source-mismatch": globals.allow_source_mismatch = 1
		elif opt == "--archive-dir": set_archive_dir(arg)
		elif opt == "--cleanup": cleanup = 1
		elif opt == "--collection-status": collection_status = 1
		elif opt == "--current-time":
			dup_time.setcurtime(get_int(arg, "current-time"))
		elif opt == "--encrypt-key":
			globals.gpg_profile.recipients.append(arg)
		elif (opt == "--exclude" or opt == "--exclude-regexp" or
			opt == "--include" or opt == "--include-regexp"):
			select_opts.append((opt, arg))
		elif (opt == "--exclude-device-files" or
			  opt == "--exclude-other-filesystems"):
			select_opts.append((opt, None))
		elif (opt == "--exclude-filelist" or opt == "--include-filelist" or
			  opt == "--exclude-globbing-filelist" or
			  opt == "--include-globbing-filelist"):
			select_opts.append((opt, arg))
			select_files.append(sel_fl(arg))
		elif opt == "--exclude-filelist-stdin":
			select_opts.append(("--exclude-filelist", "standard input"))
			select_files.append(sys.stdin)
		elif opt == "-f" or opt == "--full": full_backup = 1
		elif opt == "--force": globals.force = 1
		elif opt == "--include-filelist-stdin":
			select_opts.append(("--include-filelist", "standard input"))
			select_files.append(sys.stdin)
		elif opt == "-i" or opt == "--incremental": globals.incremental = 1
		elif opt == "--list-current-files": list_current = 1
		elif opt == "--no-encryption": globals.encryption = 0
		elif opt == "--no-print-statistics": globals.print_statistics = 0
		elif opt == "--null-separator": globals.null_separator = 1
		elif opt == "-r" or opt == "--file-to-restore":
			globals.restore_dir = arg
		elif opt == "--remove-older-than":
			globals.remove_time = dup_time.genstrtotime(arg)
		elif opt == "-t" or opt == "--restore-time":
			globals.restore_time = dup_time.genstrtotime(arg)
		elif opt == "--scp-command": backends.scp_command = arg
		elif opt == "--short-filenames": globals.short_filenames = 1
		elif opt == "--sign-key": set_sign_key(arg)
		elif opt == "--ssh-command": backends.ssh_command = arg
		elif opt == "-V" or opt == "--version":
			print "duplicity", str(globals.version)
			sys.exit(0)
		elif opt == "-v" or opt == "--verbosity": log.setverbosity(int(arg))
		elif opt == "--verify": verify = 1
		else: command_line_error("Unknown option %s" % opt)

	return args

def command_line_error(message):
	"""Indicate a command line error and exit"""
	sys.stderr.write("Command line error: %s\n" % (message,))
	sys.stderr.write("See the duplicity manual page for instructions\n")
	sys.exit(1)

def get_int(int_string, description):
	"""Require that int_string be an integer, return int value"""
	try: return int(int_string)
	except ValueError: log.FatalError("Received '%s' for %s, need integer" %
									  (int_string, description))

def set_archive_dir(dirstring):
	"""Check archive dir and set global"""
	archive_dir = path.Path(dirstring)
	if not archive_dir.isdir():
		log.FatalError("Specified archive directory '%s' does not exist "
					   " or is not a directory" % (archive_dir.name,))
	globals.archive_dir = archive_dir

def set_sign_key(sign_key):
	"""Set globals.sign_key assuming proper key given"""
	if not len(sign_key) == 8 or not re.search("^[0-9A-F]*$", sign_key):
		log.FatalError("Sign key should be an 8 character hex string, like "
					   "'AA0E73D2'.\nReceived '%s' instead." % (sign_key,))
	globals.gpg_profile.sign_key = sign_key

def set_selection():
	"""Return selection iter starting at filename with arguments applied"""
	global select_opts, select_files
	sel = selection.Select(globals.local_path)
	sel.ParseArgs(select_opts, select_files)
	globals.select = sel.set_iter()

def set_backend(arg1, arg2):
	"""Figure out which arg is url, set backend

	Return value is pair (path_first, path) where is_first is true iff
	path made from arg1.

	"""
	backend1, backend2 = backends.get_backend(arg1), backends.get_backend(arg2)
	if not backend1 and not backend2:
		log.FatalError(
"""One of the arguments must be an URL.  Examples of URL strings are
"scp://user@host.net:1234/path" and "file:///usr/local".  See the man
page for more information.""")
	if backend1 and backend2:
		command_line_error("Two URLs specified.  "
						   "One argument should be a path.")
	if backend1:
		globals.backend = backend1
		return (None, arg2)
	elif backend2:
		globals.backend = backend2
		return (1, arg1)

def process_local_dir(action, local_pathname):
	"""Check local directory, set globals.local_path"""
	local_path = path.Path(path.Path(local_pathname).get_canonical())
	if action == "restore":
		if local_path.exists() and not local_path.isemptydir():
			log.FatalError("Restore destination directory %s already "
						   "exists.\nWill not overwrite." % (local_pathname,))
	elif action == "verify":
		if not local_path.exists():
			log.FatalError("Verify directory %s does not exist" %
						   (local_path.name,))
	else:
		assert action == "full" or action == "inc"
		if not local_path.exists():
			log.FatalError("Backup source directory %s does not exist."
						   % (local_path.name,))
	
	globals.local_path = local_path

def check_consistency(action):
	"""Final consistency check, see if something wrong with command line"""
	global full_backup, select_opts, list_current
	def assert_only_one(arglist):
		"""Raises error if two or more of the elements of arglist are true"""
		n = 0
		for m in arglist:
			if m: n+=1
		assert n <= 1, "Invalid syntax, two conflicting modes specified"
	if action in ["list-current", "collection-status",
				  "cleanup", "remove-old"]:
		assert_only_one([list_current, collection_status, cleanup,
						 globals.remove_time is not None])
	elif action == "restore" or action == "verify":
		if full_backup:
			command_line_error("--full option cannot be used when "
							   "restoring or verifying")
		elif globals.incremental:
			command_line_error("--incremental option cannot be used when "
							   "restoring or verifying")
		if select_opts and action == "restore":
			command_line_error("Selection options --exclude/--include\n"
							   "currently work only when backing up, "
							   "not restoring.")
	else:
		assert action == "inc" or action == "full"
		if verify: command_line_error("--verify option cannot be used "
									  "when backing up")
		if globals.restore_dir:
			log.FatalError("--restore-dir option incompatible with %s backup"
						   % (action,))

def ProcessCommandLine(cmdline_list):
	"""Process command line, set globals, return action

	action will be "list-current", "collection-status", "cleanup",
	"remove-old", "restore", "verify", "full", or "inc".

	"""
	globals.gpg_profile = gpg.GPGProfile()

	args = parse_cmdline_options(cmdline_list)
	if len(args) < 1: command_line_error("Too few arguments")
	elif len(args) == 1:
		if list_current: action = "list-current"
		elif collection_status: action = "collection-status"
		elif cleanup: action = "cleanup"
		elif globals.remove_time is not None: action = "remove-old"
		else: command_line_error("Too few arguments")
		globals.backend = backends.get_backend(args[0])
		if not globals.backend: log.FatalError("""Bad URL '%s'.
Examples of URL strings are "scp://user@host.net:1234/path" and
"file:///usr/local".  See the man page for more information.""" % (args[0],))
	elif len(args) == 2: # Figure out whether backup or restore
		backup, local_pathname = set_backend(args[0], args[1])
		if backup:
			if full_backup: action = "full"
			else: action = "inc"
		else:
			if verify: action = "verify"
			else: action = "restore"

		process_local_dir(action, local_pathname)
		if action in ['full', 'inc', 'verify']: set_selection()
	elif len(args) > 2: command_line_error("Too many arguments")

	check_consistency(action)
	log.Log("Main action: " + action, 7)
	return action

# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, Inc., 675 Mass Ave, Cambridge MA
# 02139, USA; either version 2 of the License, or (at your option) any
# later version; incorporated herein by reference.

"""Parse command line, check for consistency, and set globals"""

import getopt, re, sys
import backends, globals, log, path, selection, gpg, dup_time

select_opts = [] # Will hold all the selection options
full_backup = None # Will be set to true if -f or --full option given

def parse_cmdline_options(arglist):
	"""Parse argument list"""
	global select_opts, full_backup
	try: optlist, args = getopt.getopt(arglist, "firt:v:V",
		 ["allow-source-mismatch", "archive-dir=", "current-time=",
		  "encrypt-key=", "exclude=", "exclude-device-files",
		  "exclude-filelist=", "exclude-filelist-stdin",
		  "exclude-other-filesystems", "exclude-regexp=",
		  "file-to-restore=", "full", "incremental", "include=",
		  "include-filelist=", "include-filelist-stdin",
		  "include-regexp=", "null-separator", "restore-dir=",
		  "restore-time=", "sign-key=", "verbosity="])
	except getopt.error, e:
		command_line_error("%s" % (str(e),))

	for opt, arg in optlist:
		if opt == "--allow-source-mismatch": globals.allow_source_mismatch = 1
		elif opt == "--archive-dir": set_archive_dir(arg)
		elif opt == "--current-time":
			globals.current_time = get_int(arg, "current-time")
		elif opt == "--encrypt-key":
			globals.gpg_profile.recipients.append(arg)
		elif (opt == "--exclude" or opt == "--exclude-regexp" or
			opt == "--include" or opt == "--include-regexp"):
			select_opts.append((opt, arg))
		elif (opt == "--exclude-device-files" or
			  opt == "--exclude-other-filesystems"):
			select_opts.append((opt, None))
		elif opt == "--exclude-filelist" or opt == "--include-filelist":
			select_opts.append((opt, (arg, open(arg, "rb"))))
		elif (opt == "--exclude-filelist-stdin" or
			  opt == "--include-filelist-stdin"):
			select_opts.append((opt, ("stdin", sys.stdin)))
		elif opt == "-f" or opt == "--full": full_backup = 1
		elif opt == "-i" or opt == "--incremental": globals.incremental = 1
		elif opt == "-r" or opt == "--file-to-restore":
			globals.restore_dir = arg
		elif opt == "-t" or opt == "--restore-time":
			globals.restore_time = dup_time.genstrtotime(arg)
		elif opt == "--sign-key": set_sign_key(arg)
		elif opt == "-V":
			print "duplicity version", str(globals.version)
			sys.exit(0)
		elif opt == "-v" or opt == "--verbosity": log.setverbosity(int(arg))
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

def get_action(args):
	"""Figure out the main action from the arguments"""

	if len(args) < 3: command_line_error("Too few arguments")
	command = args[0]
	if command != "restore" and len(args) < 4:
		command_line_error("Too few arguments")
	if len(args) > 4: command_line_error("Too many arguments")

	if command == "inc" or command == "increment": command = "inc"
	return command, args[1:]

def set_selection():
	"""Return selection iter starting at filename with arguments applied"""
	global select_opts
	sel = selection.Select(globals.local_path)
	sel.ParseArgs(select_opts)
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
	else:
		assert action == "full" or action == "inc"
		if not local_path.exists():
			log.FatalError("Backup source directory %s does not exist."
						   % (local_path.name,))
	globals.local_path = local_path

def check_consistency(action):
	"""Final consistency check, see if something wrong with command line"""
	global full_backup, select_opts
	if action == "restore":
		if full_backup:
			command_line_error("--full option cannot be used when restoring")
		elif globals.incremental:
			command_line_error("--incremental option cannot be used when "
							   "restoring")
		elif select_opts:
			command_line_error("Selection options --exclude/--include\n"
							   "currently work only when backing up, "
							   "not restoring.")
	else:
		assert action == "inc" or action == "full"
		if globals.restore_dir:
			log.FatalError("--restore-dir option incompatible with %s backup"
						   % (action,))

def ProcessCommandLine(cmdline_list):
	"""Process command line, set globals, return action

	action will be "restore", "full", or "inc".

	"""
	global full_backup
	globals.gpg_profile = gpg.GPGProfile()

	args = parse_cmdline_options(cmdline_list)
	if len(args) < 2: command_line_error("Too few arguments")
	elif len(args) > 2: command_line_error("Too many arguments")

	backup, local_pathname = set_backend(args[0], args[1])
	if backup:
		if full_backup: action = "full"
		else: action = "inc"
	else: action = "restore"

	process_local_dir(action, local_pathname)
	if backup: set_selection()
	check_consistency(action)
	return action

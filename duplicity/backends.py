# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, Inc., 675 Mass Ave, Cambridge MA
# 02139, USA; either version 2 of the License, or (at your option) any
# later version; incorporated herein by reference.

"""Provides functions and classes for getting/sending files to destination"""

import os
import log, path, dup_temp, file_naming

class BackendException(Exception): pass

def get_backend(url_string):
	"""Return Backend object from url string, or None if not a url string

	url strings are like
	scp://foobar:password@hostname.net:124/usr/local.  If a protocol
	is unsupported a fatal error will be raised.

	"""
	global protocol_class_dict
	def bad_url(message = None):
		if message:
			err_string = "Bad URL string '%s': %s" % (url_string, message)
		else: err_string = "Bad URL string '%s'" % url_string
		log.FatalError(err_string)

	colon_position = url_string.find(":")
	if colon_position < 1: return None
	protocol = url_string[:colon_position]
	if url_string[colon_position+1:colon_position+3] != '//': return None
	remaining_string = url_string[colon_position+3:]
	
	try: backend, separate_host = protocol_class_dict[protocol]
	except KeyError: bad_url("Unknown protocol '%s'" % protocol)
	assert not separate_host, "This part isn't done yet"

	return backend(remaining_string)


class Backend:
	"""Represent a connection to the destination device/computer

	Classes that subclass this should implement the put, get, list,
	and delete methods.

	"""
	def init(self, some_arguments): pass

	def put(self, source_path, remote_filename = None):
		"""Transfer source_path (Path object) to remote_filename (string)

		If remote_filename is None, get the filename from the last
		path component of pathname.

		"""
		if not remote_filename: remote_filename = source_path.get_filename()
		pass

	def get(self, remote_filename, local_path):
		"""Retrieve remote_filename and place in local_path"""
		pass
	
	def list(self):
		"""Return list of filenames (strings) present in backend"""
		pass

	def delete(self, filename_list):
		"""Delete each filename in filename_list, in order if possible"""
		pass

	def run_command(self, commandline):
		"""Run given commandline with logging and error detection"""
		log.Log("Running '%s'" % commandline, 4)
		if os.system(commandline):
			raise BackendException("Error running '%s'" % commandline)

	def popen(self, commandline):
		"""Run command and return stdout results"""
		log.Log("Reading results of '%s'" % commandline, 4)
		fout = os.popen(commandline)
		results = fout.read()
		if fout.close():
			raise BackendException("Error running '%s'" % commandline)
		return results

	def get_fileobj_read(self, filename, parseresults = None):
		"""Return fileobject opened for reading of filename on backend

		The file will be downloaded first into a temp file.  When the
		returned fileobj is closed, the temp file will be deleted.

		"""
		if not parseresults:
			parseresults = file_naming.parse(filename)
			assert parseresults, "Filename not correctly parsed"
		tdp = dup_temp.new_tempduppath(parseresults)
		self.get(filename, tdp)
		tdp.setdata()
		return tdp.filtered_open_with_delete("rb")

	def get_fileobj_write(self, filename, parseresults = None):
		"""Return fileobj opened for writing, write to backend on close

		The file will be encoded as specified in parseresults (or as
		read from the filename), and stored in a temp file until it
		can be copied over and deleted.

		"""
		if not parseresults:
			parseresults = file_naming.parse(filename)
			assert parseresults, "Filename not correctly parsed"
		tdp = dup_temp.new_tempduppath(parseresults)

		def close_file_hook():
			"""This is called when returned fileobj is closed"""
			self.put(tdp, filename)
			tdp.delete()

		fh = dup_temp.FileobjHooked(tdp.filtered_open("wb"))
		fh.addhook(close_file_hook)
		return fh

	def get_data(self, filename, parseresults = None):
		"""Retrieve a file from backend, process it, return contents"""
		fin = self.get_fileobj_read(filename, parseresults)
		buf = fin.read()
		assert not fin.close()
		return buf

	def put_data(self, buffer, filename, parseresults = None):
		"""Put buffer into filename on backend after processing"""
		fout = self.get_fileobj_write(filename, parseresults)
		fout.write(buffer)
		assert not fout.close()


class LocalBackend(Backend):
	"""Use this backend when saving to local disk

	Urls look like file://testfiles/output.  Relative to root can be
	gotten with extra slash (file:///usr/local).

	"""
	def __init__(self, directory_name):
		self.remote_pathdir = path.Path(directory_name)

	def put(self, source_path, remote_filename = None, rename = None):
		"""If rename is set, try that first, copying if doesn't work"""
		if not remote_filename: remote_filename = source_path.get_filename()
		target_path = self.remote_pathdir.append(remote_filename)
		log.Log("Writing %s" % target_path.name, 6)
		if rename:
			try: source_path.rename(target_path)
			except OSError: pass
			else: return
		target_path.writefileobj(source_path.open("rb"))

	def get(self, filename, local_path):
		"""Get file and put in local_path (Path object)"""
		source_path = self.remote_pathdir.append(filename)
		local_path.writefileobj(source_path.open("rb"))

	def list(self):
		"""List files in that directory"""
		return self.remote_pathdir.listdir()

	def delete(self, filename_list):
		"""Delete all files in filename list"""
		try:
			for filename in filename_list:
				self.remote_pathdir.append(filename).delete()
		except OSError, e: raise BackendException(str(e))


class scpBackend(Backend):
	"""This backend copies files using scp.  List not supported"""
	def __init__(self, url_string):
		"""scpBackend initializer

		Here url_string is something like
		username@host.net/file/whatever, which is produced after the 
		'scp://' of a url is stripped.

		"""
		comps = url_string.split("/")
		self.host_string = comps[0] # of form user@hostname
		self.remote_dir = "/".join(comps[1:]) # can be empty string
		if self.remote_dir: self.remote_prefix = self.remote_dir + "/"
		else: self.remote_prefix = ""

	def put(self, source_path, remote_filename = None):
		"""Use scp to copy source_dir/filename to remote computer"""
		if not remote_filename: remote_filename = source_path.get_filename()
		commandline = "scp %s %s:%s%s" % \
					  (source_path.name, self.host_string,
					   self.remote_prefix, remote_filename)
		self.run_command(commandline)

	def get(self, remote_filename, local_path):
		"""Use scp to get a remote file"""
		commandline = "scp %s:%s%s %s" % \
					  (self.host_string, self.remote_prefix,
					   remote_filename, local_path.name)
		self.run_command(commandline)
		local_path.setdata()
		if not local_path.exists():
			raise BackendException("File %s not found" % local_path.name)
		
	def list(self):
		"""List files available for scp

		Note that this command can get confused when dealing with
		files with newlines in them, as the embedded newlines cannot
		be distinguished from the file boundaries.

		"""
		commandline = "ssh %s ls %s" % (self.host_string, self.remote_dir)
		return filter(lambda x: x, self.popen(commandline).split("\n"))

	def delete(self, filename_list):
		"""Runs ssh rm to delete files.  Files must not require quoting"""
		pathlist = map(lambda fn: self.remote_prefix + fn, filename_list)
		commandline = "ssh %s rm %s" % \
					  (self.host_string, " ".join(pathlist))
		self.run_command(commandline)


class sftpBackend(Backend):
	"""This backend uses sftp to perform file operations"""
	pass # Do this later


# Dictionary relating protocol strings to tuples (backend_object,
# separate_host).  If separate_host is true, get_backend() above will
# parse the url further to try to extract a hostname, protocol, etc.
protocol_class_dict = {"scp": (scpBackend, 0),
					   "ssh": (scpBackend, 0),
					   "file": (LocalBackend, 0)}

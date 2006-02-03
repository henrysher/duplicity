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

"""Provides functions and classes for getting/sending files to destination"""

import os, types, ftplib, tempfile
import log, path, dup_temp, file_naming

class BackendException(Exception): pass
class ParsingException(Exception): pass

def get_backend(url_string):
	"""Return Backend object from url string, or None if not a url string

	url strings are like
	scp://foobar:password@hostname.net:124/usr/local.  If a protocol
	is unsupported a fatal error will be raised.

	"""
	global protocol_class_dict
	try: pu = ParsedUrl(url_string)
	except ParsingException: return None

	try: backend_class = protocol_class_dict[pu.protocol]
	except KeyError: log.FatalError("Unknown protocol '%s'" % (pu.protocol,))
	return backend_class(pu)

class ParsedUrl:
	"""Contains information gleaned from a generic url"""
	protocol = None # set to string like "ftp" indicating protocol
	suffix = None # Set to everything after protocol://

	server = None # First part of suffix (part before '/')
	path = None # Second part of suffix (part after '/')

	host = None # Set to host, if can be extracted
	user = None # Set to user, as in ftp://user@host/whatever
	port = None # Set to port, like scp://host:port/foo

	def __init__(self, url_string):
		"""Create ParsedUrl object, process url_string"""
		self.url_string = url_string
		self.set_protocol_suffix()
		self.set_server_path()
		self.set_host_user_port()

	def bad_url(self, message = None):
		"""Report a bad url, using message if given"""
		if message:
			err_string = "Bad URL string '%s': %s" % (self.url_string, message)
		else: err_string = "Bad URL string '%s'" % (self.url_string,)
		raise ParsingException(err_string)

	def set_protocol_suffix(self):
		"""Parse self.url_string, setting self.protocol and self.suffix"""
		colon_position = self.url_string.find(":")
		if colon_position < 1: self.bad_url("No colon (:) found")
		self.protocol = self.url_string[:colon_position]
		if self.url_string[colon_position+1:colon_position+3] != '//':
			self.bad_url("first colon not followed by '//'")
		self.suffix = self.url_string[colon_position+3:]

	def set_server_path(self):
		"""Set self.server and self.path from self.suffix"""
		comps = self.suffix.split('/')
		assert len(comps) > 0
		self.server = comps[0]
		if len(comps) > 1:
			self.path = '/'.join(comps[1:])

	def set_host_user_port(self):
		"""Set self.host, self.user, and self.port from self.server"""
		if not self.server: return

		# Extract port
		port_comps = self.server.split(":")
		if len(port_comps) >= 2:
			try: self.port = int(port_comps[-1])
			except ValueError: user_host = self.server
			else: user_host = ":".join(port_comps[:-1])
		else: user_host = self.server

		# Set user and host
		user_comps = user_host.split("@")
		if len(user_comps) >= 2:
			self.user = user_comps[0]
			self.host = "@".join(user_comps[1:])
		else: self.host = user_host


class Backend:
	"""Represent a connection to the destination device/computer

	Classes that subclass this should implement the put, get, list,
	and delete methods.

	"""
	def init(self, parsed_url): pass

	def put(self, source_path, remote_filename = None):
		"""Transfer source_path (Path object) to remote_filename (string)

		If remote_filename is None, get the filename from the last
		path component of pathname.

		"""
		if not remote_filename: remote_filename = source_path.get_filename()
		pass

	def get(self, remote_filename, local_path):
		"""Retrieve remote_filename and place in local_path"""
		local_path.setdata()
		pass
	
	def list(self):
		"""Return list of filenames (strings) present in backend"""
		pass

	def delete(self, filename_list):
		"""Delete each filename in filename_list, in order if possible"""
		pass

	def run_command(self, commandline):
		"""Run given commandline with logging and error detection"""
		log.Log("Running '%s'" % commandline, 5)
		if os.system(commandline):
			raise BackendException("Error running '%s'" % commandline)

	def popen(self, commandline):
		"""Run command and return stdout results"""
		log.Log("Reading results of '%s'" % commandline, 5)
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

	def get_fileobj_write(self, filename, parseresults = None,
						  sizelist = None):
		"""Return fileobj opened for writing, write to backend on close

		The file will be encoded as specified in parseresults (or as
		read from the filename), and stored in a temp file until it
		can be copied over and deleted.

		If sizelist is not None, it should be set to an empty list.
		The number of bytes will be inserted into the list.

		"""
		if not parseresults:
			parseresults = file_naming.parse(filename)
			assert parseresults, "Filename %s not correctly parsed" % filename
		tdp = dup_temp.new_tempduppath(parseresults)

		def close_file_hook():
			"""This is called when returned fileobj is closed"""
			self.put(tdp, filename)
			if sizelist is not None:
				tdp.setdata()
				sizelist.append(tdp.getsize())
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

	def close(self):
		"""This is called when a connection is no longer needed"""
		pass


class LocalBackend(Backend):
	"""Use this backend when saving to local disk

	Urls look like file://testfiles/output.  Relative to root can be
	gotten with extra slash (file:///usr/local).

	"""
	def __init__(self, parsed_url):
		self.remote_pathdir = path.Path(parsed_url.suffix)

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
		assert type(filename_list) is not types.StringType
		try:
			for filename in filename_list:
				self.remote_pathdir.append(filename).delete()
		except OSError, e: raise BackendException(str(e))


# The following can be redefined to use different shell commands from
# ssh or scp or to add more arguments.  However, the replacements must
# have the same syntax.  Also these strings will be executed by the
# shell, so shouldn't have strange characters in them.
ssh_command = "ssh"
scp_command = "scp"
sftp_command = "sftp"

class scpBackend(Backend):
	"""This backend copies files using scp.  List not supported"""
	def __init__(self, parsed_url):
		"""scpBackend initializer"""
		self.host_string = parsed_url.server # of form user@hostname:port
		self.remote_dir = parsed_url.path # can be empty string
		if self.remote_dir: self.remote_prefix = self.remote_dir + "/"
		else: self.remote_prefix = ""

	def put(self, source_path, remote_filename = None):
		"""Use scp to copy source_dir/filename to remote computer"""
		if not remote_filename: remote_filename = source_path.get_filename()
		commandline = "%s %s %s:%s%s" % \
					  (scp_command, source_path.name, self.host_string,
					   self.remote_prefix, remote_filename)
		self.run_command(commandline)

	def get(self, remote_filename, local_path):
		"""Use scp to get a remote file"""
		commandline = "%s %s:%s%s %s" % \
					  (scp_command, self.host_string, self.remote_prefix,
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
		commandline = ("echo -e 'cd %s\nls -1' | %s -b - %s" %
					   (self.remote_dir, sftp_command, self.host_string))
		l = self.popen(commandline).split('\n')[2:] # omit sftp prompts
		return filter(lambda x: x, l)

	def delete(self, filename_list):
		"""Runs ssh rm to delete files.  Files must not require quoting"""
		assert len(filename_list) > 0
		pathlist = map(lambda fn: self.remote_prefix + fn, filename_list)
		del_prefix = "echo 'rm "
		del_postfix = ("' | %s -b - %s 1>/dev/null" %
					   (sftp_command, self.host_string))
		for fn in filename_list:
			commandline = del_prefix + self.remote_prefix + fn + del_postfix
			self.run_command(commandline)


class sftpBackend(Backend):
	"""This backend uses sftp to perform file operations"""
	pass # Do this later


class ftpBackend(Backend):
	"""Connect to remote store using File Transfer Protocol"""
	def __init__(self, parsed_url):
		"""Create a new ftp backend object, log in to host"""
		self.ftp = ftplib.FTP()
		if parsed_url.port is None: self.error_wrap('connect', parsed_url.host)
		else: self.error_wrap('connect', parsed_url.host, parsed_url.port)

		if parsed_url.user is not None:
			self.error_wrap('login', parsed_url.user, self.get_password())
		else: self.error_wrap('login')
		self.ftp.cwd(parsed_url.path)

	def error_wrap(self, command, *args):
		"""Run self.ftp.command(*args), but raise BackendException on error"""
		try: return ftplib.FTP.__dict__[command](self.ftp, *args)
		except ftplib.all_errors, e: raise BackendException(e)

	def get_password(self):
		"""Get ftp password using environment if possible"""
		try: return os.environ['FTP_PASSWORD']
		except KeyError:
			log.Log("FTP_PASSWORD not set, using empty ftp password", 3)
			return ''

	def put(self, source_path, remote_filename = None):
		"""Transfer source_path to remote_filename"""
		if not remote_filename: remote_filename = source_path.get_filename()
		source_file = source_path.open("rb")
		log.Log("Saving %s on FTP server" % (remote_filename,), 5)
		self.error_wrap('storbinary', "STOR "+remote_filename, source_file)
		assert not source_file.close()

	def get(self, remote_filename, local_path):
		"""Get remote filename, saving it to local_path"""
		target_file = local_path.open("wb")
		log.Log("Retrieving %s from FTP server" % (remote_filename,), 5)
		self.error_wrap('retrbinary', "RETR "+remote_filename,
						target_file.write)
		assert not target_file.close()
		local_path.setdata()

	def list(self):
		"""List files in directory"""
		log.Log("Listing files on FTP server", 5)
		# Some ftp servers raise error 450 if the directory is empty
		try: return self.error_wrap('nlst')
		except BackendException, e:
			if "450" in str(e): return []
			raise

	def delete(self, filename_list):
		"""Delete files in filename_list"""
		for filename in filename_list:
			log.Log("Deleting %s from FTP server" % (filename,), 5)
			self.error_wrap('delete', filename)

	def close(self):
		"""Shut down connection"""
		self.error_wrap('quit')


class rsyncBackend(Backend):
	"""Connect to remote store using rsync

	rsync backend contributed by Sebastian Wilhelmi <seppi@seppi.de>

	"""
	def __init__(self, parsed_url):
		"""rsyncBackend initializer"""
		self.url_string = parsed_url.url_string
		if self.url_string[-1] != '/':
			self.url_string += '/'

	def put(self, source_path, remote_filename = None):
		"""Use rsync to copy source_dir/filename to remote computer"""
		if not remote_filename: remote_filename = source_path.get_filename()
		remote_path = os.path.join (self.url_string, remote_filename)
		commandline = "rsync %s %s" % (source_path.name, remote_path)
		self.run_command(commandline)

	def get(self, remote_filename, local_path):
		"""Use rsync to get a remote file"""
		remote_path = os.path.join (self.url_string, remote_filename)
		commandline = "rsync %s %s" % (remote_path, local_path.name)
		self.run_command(commandline)
		local_path.setdata()
		if not local_path.exists():
			raise BackendException("File %s not found" % local_path.name)
		
	def list(self):
		"""List files"""
		def split (str):
			line = str.split ()
			if len (line) > 4 and line[4] != '.':
				return line[4]
			else:
				return None
		commandline = "rsync %s" % self.url_string
		return filter (lambda x: x, map (split, self.popen(commandline).split('\n')))

	def delete(self, filename_list):
		"""Delete files."""
		delete_list = filename_list
		dont_delete_list = []
		for file in self.list ():
			if file in delete_list:
				delete_list.remove (file)
			else:
				dont_delete_list.append (file)
		if len (delete_list) > 0:
			raise BackendException("Files %s not found" % str (delete_list))

		dir = tempfile.mktemp ()
		exclude_name = tempfile.mktemp ()
		exclude = open (exclude_name, 'w')
		to_delete = [exclude_name]
		os.mkdir (dir)
		for file in dont_delete_list:
				path = os.path.join (dir, file)
				to_delete.append (path)
				f = open (path, 'w')
				f.close ()
				print >>exclude, file
		exclude.close ()
		commandline = ("rsync --recursive --delete --exclude-from=%s %s/ %s" %
			       (exclude_name, dir, self.url_string))
		self.run_command(commandline)
		for file in to_delete:
			os.unlink (file)
		os.rmdir (dir)
		
# Dictionary relating protocol strings to backend_object classes.
protocol_class_dict = {"scp": scpBackend,
					   "ssh": scpBackend,
					   "file": LocalBackend,
					   "ftp": ftpBackend,
					   "rsync": rsyncBackend}


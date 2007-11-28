# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
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

"""Manage temporary files"""

import os
import tempfile
import log, path, file_naming

tempfile_names = []

def register_filename(filename):
	"""Add filename to tempfile list"""
	assert not filename in tempfile_names
	tempfile_names.append(filename)

def unregister_filename(filename):
	"""Remove filename from tempfile list"""
	try: index = tempfile_names.index(filename)
	except ValueError: log.Log("Warning, %s is not a registered tempfile" %
							   filename)
	else: del tempfile_names[index]

def cleanup():
	"""Delete all existing tempfiles"""
	for filename in tempfile_names:
		log.Warn("%s still in tempfile list, deleting" % (filename,))
		p = path.Path(filename)
		if p.exists(): p.delete()

def new_temppath():
	"""Return a new TempPath"""
	fd, filename = tempfile.mkstemp("","duplicity.")
	os.close(fd)
	register_filename(filename)
	return TempPath(filename)

class TempPath(path.Path):
	"""Path object used as a temporary file"""
	def delete(self):
		"""Unregister and delete"""
		path.Path.delete(self)
		unregister_filename(self.name)

	def open_with_delete(self, mode):
		"""Returns a fileobj.  When that is closed, delete file"""
		fh = FileobjHooked(path.Path.open(self, mode))
		fh.addhook(self.delete)
		return fh

def get_fileobj_duppath(dirpath, filename):
	"""Return a file object open for writing, will write to filename

	Data will be processed and written to a temporary file.  When the
	return fileobject is closed, rename to final position.  filename
	must be a recognizable duplicity data file.

	"""
	oldtempdir = tempfile.tempdir
	tempfile.tempdir = dirpath.name
	tdp = new_tempduppath(file_naming.parse(filename))
	tempfile.tempdir = oldtempdir
	fh = FileobjHooked(tdp.filtered_open("wb"))
	fh.addhook(lambda: tdp.rename(dirpath.append(filename)))
	return fh

def new_tempduppath(parseresults):
	"""Return a new TempDupPath, using settings from parseresults"""
	fd, filename = tempfile.mkstemp("","duplicity.")
	os.close(fd)
	register_filename(filename)
	return TempDupPath(filename, parseresults = parseresults)

class TempDupPath(path.DupPath):
	"""Like TempPath, but build around DupPath"""
	def delete(self):
		"""Unregister and delete"""
		path.DupPath.delete(self)
		unregister_filename(self.name)

	def filtered_open_with_delete(self, mode):
		"""Returns a filtered fileobj.  When that is closed, delete file"""
		fh = FileobjHooked(path.DupPath.filtered_open(self, mode))
		fh.addhook(self.delete)
		return fh

	def open_with_delete(self, mode = "rb"):
		"""Returns a fileobj.  When that is closed, delete file"""
		assert mode == "rb" # Why write a file and then close it immediately?
		fh = FileobjHooked(path.DupPath.open(self, mode))
		fh.addhook(self.delete)
		return fh

class FileobjHooked:
	"""Simulate a file, but add hook on close"""
	def __init__(self, fileobj):
		"""Initializer.  fileobj is the file object to simulate"""
		self.fileobj = fileobj
		self.closed = None
		self.hooklist = [] # fill later with thunks to run on close
		# self.second by MDR.  Will be filled by addfilehandle -- poor mans tee
		self.second = None

	def write(self, buf):
		if self.second: self.second.write(buf) # by MDR.  actual tee
		return self.fileobj.write(buf)
	
	def read(self, length = -1): return self.fileobj.read(length)

	def close(self):
		"""Close fileobj, running hooks right afterwards"""
		assert not self.fileobj.close()
		if self.second: assert not self.second.close()
		for hook in self.hooklist: hook()

	def addhook(self, hook):
		"""Add hook (function taking no arguments) to run upon closing"""
		self.hooklist.append(hook)

	def addfilehandle(self, fh): # by MDR
		"""Add a second filehandle for listening to the input
		
		This only works properly for two write handles"""
		assert not self.second
		self.second = fh

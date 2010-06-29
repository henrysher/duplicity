# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2010 Tomaz Muraus <kami@k5-storitve.net>
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

import os
import re
import time
import hmac
import hashlib
import urllib
import urllib2

import duplicity.backend
from duplicity import log
from duplicity.errors import *

MAX_RETRIES = 5
SLEEP_TIME = 2

class SpiderOakBackend(duplicity.backend.Backend):
	"""
	Backend for storing files using DIY Archival Data Storage API.
	https://spideroak.com/diy/
	
	To use the backend you must set the following environment variables:
	
	SPIDEROAK_KEY_ID - your API key id
	SPIDEROAK_KEY - your API key
	
	and the destination URL must be in the following format:
	
	spideroak+https://<your username>.diy.spideroak.com
	"""

	def __init__(self, parsed_url):
		duplicity.backend.Backend.__init__(self, parsed_url)
		
		url = parsed_url.geturl()
		if url.find('diy.spideroak.com') == -1:
			raise BackendException('Invalid URL. URL must be in format: '
						'spideroak+https://<username>.diy.spideroak.com')
		if not os.environ.has_key('SPIDEROAK_KEY_ID'):
			raise BackendException('SPIDEROAK_KEY_ID environment variable'
								   'is not set.')
			
		if not os.environ.has_key('SPIDEROAK_KEY'):
			raise BackendException('SPIDEROAK_KEY environment variable'
								   'is not set.')
		
		url = url.replace(parsed_url.scheme + '://', '')
		username, path = url.rsplit('.diy.spideroak.com')
		
		if path:
			path = path[:-1] if path[-1] == '/' else path
		else:
			path = ''
		
		self.retry_count = {}
		self.conn_data = {
						'url': 'https://%s.diy.spideroak.com' % (username),
						'username': username,
						'path': path,
						'key_id': os.environ.get('SPIDEROAK_KEY_ID'),
						'key': os.environ.get('SPIDEROAK_KEY'),
		}
			
	def get(self, filename, local_path):
		"""Get file and put in local_path (Path object)"""
		try:
			request = self.__make_request('GET', filename)
			
			try:
				file = open(local_path.name, 'wb')
				
				while 1:
					chunk = request.read(4096)
					if not chunk:
						break
					file.write(chunk)
				local_path.setdata()
			finally:
				file.close()
		except urllib2.HTTPError, e:
			if self.__retry_command('get', filename, local_path) is False:
				log.FatalError('Downloading file %s failed (code: %d)' %
							(filename, e.code), log.ErrorCode.connection_failed)

		log.Debug('Downloaded file: %s' % (filename))
	
	def list(self):
		""" List files in that directory """
		key = self.conn_data['path']

		try:
			files = self.__make_request('GET', '?action=listmatch').read()
		except urllib2.HTTPError, e:
			if self.__retry_command('list') is False:
				log.FatalError('Listing files failed (code: %d)' % (e.code),
							   log.ErrorCode.connection_failed)
			
		files = files[1:-1]
		files = [urllib.unquote(file) for file \
									  in re.findall(r"'(.*?)'", files)]
		
		if key:
			# SpiderOak API always returns the full path to the file, so strip
			# the leading path (if specified)
			key = key[1:] + '/'
			files = [file.replace(key, '') for file in files]

		log.Debug('Listed files')
	
		return files
	
	def put(self, source_path, remote_filename = None, rename = None):
		""" Transfer source_path to remote_filename """
		if not remote_filename:
			remote_filename = source_path.get_filename()

		log.Debug('Uploading file: %s' % (source_path.name))
		
		try:
			file = open(source_path.name, 'rb')
			content = file.read()
			self.__make_request('POST', resource = remote_filename, data = content)
		except IOError, e:
			log.FatalError('Uploading file %s failed' % (source_path.name), 
						   log.ErrorCode.generic)
		except urllib2.HTTPError, e:
			if self.__retry_command('put', source_path, remote_filename, rename) is False:
				log.FatalError('Uploading file %s failed (code: %d)' %
						(source_path.name, e.code), log.ErrorCode.connection_failed)
		finally:
			file.close()
	
	def delete(self, filename_list):
		""" Delete all files in filename list """
		for filename in filename_list:
			
			try:
				self.__make_request('POST', filename, '?action=delete', data = '')
				log.Debug('Deleted file: %s' % (filename))
			except urllib2.HTTPError, e:
				if self.__retry_command('delete', filename_list) is False:
					log.FatalError('Deleting file %s failed (code: %d)' %
								  (filename, e.code), log.ErrorCode.connection_failed)
				
	def __retry_command(self, method, *args):
		""" Retry failed command and increase the number of attempts. """
		retry_count = self.retry_count.get(method, 0)
		
		if not retry_count < MAX_RETRIES:
			return False

		log.Debug('Retrying command %s (args = %s) [attempt: %d]' %
				 (method, ', ' . join([str(arg) for arg in args]), retry_count + 1))
		
		try:
			self.retry_count[method] += 1
		except KeyError:
			self.retry_count[method] = 1
		
		time.sleep(SLEEP_TIME)
		getattr(self, method)(*args)
			
	def __delete_all(self):
		""" Delete all the files on the specified path. """
		files = self.list()
		self.delete(files)
	
	def __make_request(self, method = 'GET', resource = '', action = '', data = None):
		signature, timestamp = self.__authenticate(self.conn_data['key'], \
								self.conn_data['username'], method)
		url = '%s/data%s/%s%s' % (self.conn_data['url'], self.conn_data['path'], \
								 resource, action)
		headers = {
					'Authorization': 'DIYAPI %s:%s' % (self.conn_data['key_id'], signature),
					'X-DIYAPI-Timestamp': '%s' % (timestamp)
		}

		request = urllib2.Request(url, data = data, headers = headers)
		request = urllib2.urlopen(request)
		
		return request
	
	def __authenticate(self, key_id, username, method = 'GET'):
		timestamp = int(time.time())
		signature = self.__make_signature(timestamp, key_id, username, method)
		
		return (signature, timestamp)
	
	def __make_signature(self, timestamp, key, username, method):
		string_to_sign = '\n'.join((username, method, str(timestamp)))
		
		return hmac.new(key, string_to_sign, hashlib.sha256).hexdigest()
	
duplicity.backend.register_backend('spideroak+https', SpiderOakBackend)
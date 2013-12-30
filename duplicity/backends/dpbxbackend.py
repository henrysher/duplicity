# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2013 jno <jno@pisem.net>
#
# Version: 0.3
#
# 0. You can make me happy with https://www.dropbox.com/referrals/NTE2ODA0Mzg5
# 1. Most of the code was taken from cli_client.py. The ftpsbackend.py was used as a template
# 2. DPBX & dpbx are used because the use of the actual name is prohibited
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
import os.path
import urllib
import re
import locale, sys

import traceback, StringIO
from exceptions import Exception

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import *
from duplicity import tempdir
from duplicity.backend import retry_fatal


# This application key is registered in my name (jno at pisem dot net).
# You can register your own developer account with Dropbox and
# register a new application for yourself, obtaining the new
# APP_KEY and APP_SECRET.
# Note 1: you must not store your credentials "as is" in the code.
#         The values must be "processed" at least.
#         This is a must for "production" keys.
# Note 2: the name of the application defines the name of the
#         subfolder in the "Apps" folder.
# http://www.dropbox.com/developers/apps is the place to get the key.

APP_KEY = 'bc6toosmbn7bk6t'
APP_SECRET = 'ojx8n8jf4c5ttr1'

# Limit file access to Apps/Duplicity (the name of the application).
ACCESS_TYPE = 'app_folder'
# This file will store cached value of oAuth token
_TOKEN_CACHE_FILE = os.path.expanduser("~/.dropbox.token_store.txt")

def log_exception(e):
  log.Error('Exception [%s]:'%(e,))
  f = StringIO.StringIO()
  traceback.print_exc(file=f)
  f.seek(0)
  for s in f.readlines():
    log.Error('| '+s.rstrip())
  f.close()

def command(login_required=True):
    """a decorator for handling authentication and exceptions"""
    def decorate(f):
        def wrapper(self, *args):
            if login_required and not self.sess.is_linked():
              log.FatalError("dpbx Cannot login: check your credentials",log.ErrorCode.dpbx_nologin)
              return

            try:
                return f(self, *args)
            except TypeError, e:
                log_exception(e)
                log.FatalError('dpbx type error "%s"' % (e,), log.ErrorCode.backend_code_error)
            except rest.ErrorResponse, e:
                msg = e.user_error_msg or str(e)
                log.Error('dpbx error: %s' % (msg,), log.ErrorCode.backend_command_error)
                raise e
            except Exception, e:
                log_exception(e)
                log.Error('dpbx code error "%s"' % (e,), log.ErrorCode.backend_code_error)
                raise e

        wrapper.__doc__ = f.__doc__
        return wrapper
    return decorate

class DPBXBackend(duplicity.backend.Backend):
    """Connect to remote store using Dr*pB*x service"""
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        from dropbox import client, rest, session

        class StoredSession(session.DropboxSession):
            """a wrapper around DropboxSession that stores a token to a file on disk"""
            TOKEN_FILE = _TOKEN_CACHE_FILE
        
            def load_creds(self):
                try:
                    f = open(self.TOKEN_FILE)
                    stored_creds = f.read()
                    f.close()
                    self.set_token(*stored_creds.split('|'))
                    log.Info( "[loaded access token]" )
                except IOError:
                    pass # don't worry if it's not there
        
            def write_creds(self, token):
                open(self.TOKEN_FILE, 'w').close() # create/reset file
                os.chmod(self.TOKEN_FILE,0600)     # set it -rw------ (NOOP in Windows?)
                # now write the content
                f = open(self.TOKEN_FILE, 'w')
                f.write("|".join([token.key, token.secret]))
                f.close()
        
            def delete_creds(self):
                os.unlink(self.TOKEN_FILE)
        
            def link(self):
                if not sys.stdout.isatty() or not sys.stdin.isatty() :
                  log.FatalError('dpbx error: cannot interact, but need human attention', log.ErrorCode.backend_command_error)
                request_token = self.obtain_request_token()
                url = self.build_authorize_url(request_token)
                print
                print '-'*72
                print "url:", url
                print "Please authorize in the browser. After you're done, press enter."
                raw_input()
        
                self.obtain_access_token(request_token)
                self.write_creds(self.token)
        
            def unlink(self):
                self.delete_creds()
                session.DropboxSession.unlink(self)

        self.sess = StoredSession(etacsufbo(APP_KEY)
                    , etacsufbo(APP_SECRET)
                    , access_type=ACCESS_TYPE)
                    # , locale='en')
        self.api_client = client.DropboxClient(self.sess)
        self.sess.load_creds()

        self.login()

    def login(self):
        if not self.sess.is_linked():
          try: # to login to the box
            self.sess.link()
          except rest.ErrorResponse, e:
            log.FatalError('dpbx Error: %s\n' % str(e), log.ErrorCode.dpbx_nologin)
          if not self.sess.is_linked(): # stil not logged in
            log.FatalError("dpbx Cannot login: check your credentials",log.ErrorCode.dpbx_nologin)

    @retry_fatal
    @command()
    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        if not remote_filename:
            remote_filename = source_path.get_filename()

        remote_dir  = urllib.unquote(self.parsed_url.path.lstrip('/'))
        remote_path = os.path.join(remote_dir, remote_filename).rstrip()

        from_file = open(source_path.name, "rb")

        resp = self.api_client.put_file(remote_path, from_file)
        log.Debug( 'dpbx,put(%s,%s): %s'%(source_path.name, remote_path, resp))

    @retry_fatal
    @command()
    def get(self, remote_filename, local_path):
        """Get remote filename, saving it to local_path"""
        remote_path = os.path.join(urllib.unquote(self.parsed_url.path), remote_filename).rstrip()

        to_file = open( local_path.name, 'wb' )
        f, metadata = self.api_client.get_file_and_metadata(remote_path)
        log.Debug('dpbx.get(%s,%s): %s'%(remote_path,local_path.name,metadata))
        # print 'Metadata:', metadata
        to_file.write(f.read())
        f.close()
        to_file.close()

        local_path.setdata()

    @retry_fatal
    @command()
    def _list(self,none=None):
        """List files in directory"""
        # Do a long listing to avoid connection reset
        remote_dir = urllib.unquote(self.parsed_url.path.lstrip('/')).rstrip()
        resp = self.api_client.metadata(remote_dir)
        log.Debug('dpbx.list(%s): %s'%(remote_dir,resp))
        l = []
        if 'contents' in resp:
            encoding = locale.getdefaultlocale()[1]
            if encoding is None:
                encoding = 'LATIN1'
            for f in resp['contents']:
                name = os.path.basename(f['path'])
                l.append(name.encode(encoding))
        return l

    @retry_fatal
    @command()
    def delete(self, filename_list):
        """Delete files in filename_list"""
        if not filename_list :
          log.Debug('dpbx.delete(): no op')
          return
        remote_dir = urllib.unquote(self.parsed_url.path.lstrip('/')).rstrip()
        for filename in filename_list:
          remote_name = os.path.join( remote_dir, filename )
          resp = self.api_client.file_delete( remote_name )
          log.Debug('dpbx.delete(%s): %s'%(remote_name,resp))

    @command()
    def close(self):
      """close backend session? no! just "flush" the data"""
      info = self.api_client.account_info()
      log.Debug('dpbx.close():')
      for k in info :
        log.Debug(':: %s=[%s]'%(k,info[k]))
      entries = []
      more = True
      cursor = None
      while more :
        info = self.api_client.delta(cursor)
        if info.get('reset',False) :
          log.Debug("delta returned True value for \"reset\", no matter")
        cursor = info.get('cursor',None)
        more   = info.get('more',False)
        entr   = info.get('entries',[])
        entries += entr
      for path,meta in entries:
        mm = meta and 'ok' or 'DELETE'
        log.Info(':: :: [%s] %s'%(path,mm))
        if meta :
          for k in meta :
            log.Debug(':: :: :: %s=[%s]'%(k,meta[k]))

    def _mkdir(self, path):
        """create a new directory"""
        resp = self.api_client.file_create_folder(path)
        log.Debug('dpbx._mkdir(%s): %s'%(path,resp))

def etacsufbo(s):
  return ''.join(reduce(lambda x,y:(x and len(x[-1])==1)and(x.append(y+
          x.pop(-1))and x or x)or(x+[y]),s,[]))

duplicity.backend.register_backend("dpbx", DPBXBackend)

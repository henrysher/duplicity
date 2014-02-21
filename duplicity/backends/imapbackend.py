# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2008 Ian Barton <ian@manor-farm.org>
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

import imaplib
import re
import os
import time
import socket
import StringIO
import rfc822
import getpass
import email

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport


class ImapBackend(duplicity.backend.Backend):
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        log.Debug("I'm %s (scheme %s) connecting to %s as %s" %
                  (self.__class__.__name__, parsed_url.scheme, parsed_url.hostname, parsed_url.username))

        #  Store url for reconnection on error
        self._url = parsed_url

        #  Set the username
        if ( parsed_url.username is None ):
            username = raw_input('Enter account userid: ')
        else:
            username = parsed_url.username

        #  Set the password
        if ( not parsed_url.password ):
            if os.environ.has_key('IMAP_PASSWORD'):
                password = os.environ.get('IMAP_PASSWORD')
            else:
                password = getpass.getpass("Enter account password: ")
        else:
            password = parsed_url.password

        self._username = username
        self._password = password
        self._resetConnection()

    def _resetConnection(self):
        parsed_url = self._url
        try:
            imap_server = os.environ['IMAP_SERVER']
        except KeyError:
            imap_server = parsed_url.hostname

        #  Try to close the connection cleanly
        try:
            self._conn.close()
        except Exception:
            pass

        if (parsed_url.scheme == "imap"):
            cl = imaplib.IMAP4
            self._conn = cl(imap_server, 143)
        elif (parsed_url.scheme == "imaps"):
            cl = imaplib.IMAP4_SSL
            self._conn = cl(imap_server, 993)

        log.Debug("Type of imap class: %s" % (cl.__name__))
        self.remote_dir = re.sub(r'^/', r'', parsed_url.path, 1)

        #  Login
        if (not(globals.imap_full_address)):
            self._conn.login(self._username, self._password)
            self._conn.select(globals.imap_mailbox)
            log.Info("IMAP connected")
        else:
            self._conn.login(self._username + "@" + parsed_url.hostname, self._password)
            self._conn.select(globals.imap_mailbox)
            log.Info("IMAP connected")


    def _prepareBody(self,f,rname):
        mp = email.MIMEMultipart.MIMEMultipart()

        # I am going to use the remote_dir as the From address so that
        # multiple archives can be stored in an IMAP account and can be
        # accessed separately
        mp["From"]=self.remote_dir
        mp["Subject"]=rname

        a = email.MIMEBase.MIMEBase("application","binary")
        a.set_payload(f.read())

        email.Encoders.encode_base64(a)

        mp.attach(a)

        return mp.as_string()

    def put(self, source_path, remote_filename = None):
        if not remote_filename:
            remote_filename = source_path.get_filename()
        f=source_path.open("rb")
        allowedTimeout = globals.timeout
        if (allowedTimeout == 0):
            # Allow a total timeout of 1 day
            allowedTimeout = 2880
        while allowedTimeout > 0:
            try:
                self._conn.select(remote_filename)
                body=self._prepareBody(f,remote_filename)
                # If we don't select the IMAP folder before
                # append, the message goes into the INBOX.
                self._conn.select(globals.imap_mailbox)
                self._conn.append(globals.imap_mailbox, None, None, body)
                break
            except (imaplib.IMAP4.abort, socket.error, socket.sslerror):
                allowedTimeout -= 1
                log.Info("Error saving '%s', retrying in 30s " % remote_filename)
                time.sleep(30)
                while allowedTimeout > 0:
                    try:
                        self._resetConnection()
                        break
                    except (imaplib.IMAP4.abort, socket.error, socket.sslerror):
                        allowedTimeout -= 1
                        log.Info("Error reconnecting, retrying in 30s ")
                        time.sleep(30)

        log.Info("IMAP mail with '%s' subject stored" % remote_filename)

    def get(self, remote_filename, local_path):
        allowedTimeout = globals.timeout
        if (allowedTimeout == 0):
            # Allow a total timeout of 1 day
            allowedTimeout = 2880
        while allowedTimeout > 0:
            try:
                self._conn.select(globals.imap_mailbox)
                (result,list) = self._conn.search(None, 'Subject', remote_filename)
                if result != "OK":
                    raise Exception(list[0])

                #check if there is any result
                if list[0] == '':
                    raise Exception("no mail with subject %s")

                (result,list) = self._conn.fetch(list[0],"(RFC822)")

                if result != "OK":
                    raise Exception(list[0])
                rawbody=list[0][1]

                p = email.Parser.Parser()

                m = p.parsestr(rawbody)

                mp = m.get_payload(0)

                body = mp.get_payload(decode=True)
                break
            except (imaplib.IMAP4.abort, socket.error, socket.sslerror):
                allowedTimeout -= 1
                log.Info("Error loading '%s', retrying in 30s " % remote_filename)
                time.sleep(30)
                while allowedTimeout > 0:
                    try:
                        self._resetConnection()
                        break
                    except (imaplib.IMAP4.abort, socket.error, socket.sslerror):
                        allowedTimeout -= 1
                        log.Info("Error reconnecting, retrying in 30s ")
                        time.sleep(30)

        tfile = local_path.open("wb")
        tfile.write(body)
        local_path.setdata()
        log.Info("IMAP mail with '%s' subject fetched" % remote_filename)

    def _list(self):
        ret = []
        (result,list) = self._conn.select(globals.imap_mailbox)
        if result != "OK":
            raise BackendException(list[0])

        # Going to find all the archives which have remote_dir in the From
        # address

        # Search returns an error if you haven't selected an IMAP folder.
        (result,list) = self._conn.search(None, 'FROM', self.remote_dir)
        if result!="OK":
            raise Exception(list[0])
        if list[0]=='':
            return ret
        nums=list[0].split(" ")
        set="%s:%s"%(nums[0],nums[-1])
        (result,list) = self._conn.fetch(set,"(BODY[HEADER])")
        if result!="OK":
            raise Exception(list[0])

        for msg in list:
            if (len(msg)==1):continue
            io = StringIO.StringIO(msg[1])
            m = rfc822.Message(io)
            subj = m.getheader("subject")
            header_from = m.getheader("from")

            # Catch messages with empty headers which cause an exception.
            if (not (header_from == None)):
                if (re.compile("^" + self.remote_dir + "$").match(header_from)):
                    ret.append(subj)
                    log.Info("IMAP LIST: %s %s" % (subj,header_from))
        return ret

    def _imapf(self,fun,*args):
        (ret,list)=fun(*args)
        if ret != "OK":
            raise Exception(list[0])
        return list

    def _delete_single_mail(self,i):
        self._imapf(self._conn.store,i,"+FLAGS",'\\DELETED')

    def _expunge(self):
        list=self._imapf(self._conn.expunge)

    def delete(self, filename_list):
        assert len(filename_list) > 0
        for filename in filename_list:
            list = self._imapf(self._conn.search,None,"(SUBJECT %s)"%filename)
            list = list[0].split()
            if len(list)==0 or list[0]=="":raise Exception("no such mail with subject '%s'"%filename)
            self._delete_single_mail(list[0])
            log.Notice("marked %s to be deleted" % filename)
        self._expunge()
        log.Notice("IMAP expunged %s files" % len(list))

    def close(self):
        self._conn.select(globals.imap_mailbox)
        self._conn.close()
        self._conn.logout()

duplicity.backend.register_backend("imap", ImapBackend);
duplicity.backend.register_backend("imaps", ImapBackend);


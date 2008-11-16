# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-

import imaplib
import base64
import re
import os
import StringIO
import rfc822
import getpass
import email.Encoders
import email.MIMEBase
import email.MIMEMultipart
import email.Parser
import duplicity.backend
import duplicity.globals as globals
import duplicity.log as log
from duplicity.errors import *

#  An option which can be changed by a command line argument
#  Just in case other languages want something other than
#  "[Gmail]/All Mail".  Another option is "Inbox" but things may
#  get archived and we want to make sure that we see all the 
#  possible archive files.
gmail_mailbox = "[Gmail]/All Mail"

class GmailImapBackend(duplicity.backend.Backend):
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        
        if( parsed_url.scheme == "gmail" ):
            cl = imaplib.IMAP4_SSL
            self._conn = cl('imap.gmail.com', 993)
        else:
            cl = imaplib.IMAP4
            self._conn = cl('imap.gmail.com', 143)


        log.Log("type of IMAP class=%s, I'm %s (scheme %s) connecting to %s as %s" %
                (cl.__name__,self.__class__.__name__, parsed_url.scheme, parsed_url.hostname, parsed_url.get_username()), 9)

        self.remote_dir = re.sub(r'^/', r'', parsed_url.path, 1)

        #  Set the username
        if ( parsed_url.get_username() is None ):
            username = raw_input('Enter GMAIL account userid: ')
        else:
            username = parsed_url.get_username()
       
        #  Set the password
        if ( not parsed_url.get_password() ):
            password = getpass.getpass("Enter GMAIL account password: ")
        else:
            password = parsed_url.get_password()

        #  Login 
        self._conn.login(username, password)
        self._conn.select(gmail_mailbox)
        log.Log("IMAP connected",5)
        
    def _prepareBody(self,f,rname):
        mp = email.MIMEMultipart.MIMEMultipart()

        # I am going to use the remote_dir as the From address so that 
        # multiple archives can be stored in a GMail account and can be
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
        self._conn.select(remote_filename)
        body=self._prepareBody(f,remote_filename)
        self._conn.append(gmail_mailbox,None,None,body)
        log.Log("IMAP mail with '%s' subject stored"%remote_filename,5)

    def get(self, remote_filename, local_path):
        self._conn.select(gmail_mailbox)

        (result,list) = self._conn.search(None,"(HEADER Subject %s)"%remote_filename)
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

        tfile = local_path.open("wb")
        tfile.write(body)
        local_path.setdata()
        log.Log("IMAP mail with '%s' subject fetched"%remote_filename,5)

    def list(self):
        ret = []
        self._conn.select(gmail_mailbox)

        # Going to find all the archives which have remote_dir in the From 
        # address
        (result,list) = self._conn.search(None,"(From %s)" % self.remote_dir)
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
            subj = m.getheaders("subject")[0]
            header_from = m.getheaders("from")[0]
            if (re.compile("^" + self.remote_dir + "$").match(header_from)):
                ret.append(subj)
                log.Log("IMAP LIST: %s %s" % (subj,header_from), 6)
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
            list = self._imapf(self._conn.search,None,"(HEADER Subject %s)"%filename)
            list = list[0].split()
            if len(list)==0 or list[0]=="":raise Exception("no such mail with subject '%s'"%filename)
            self._delete_single_mail(list[0])
            log.Log("marked %s to be deleted" % filename, 4)
        self._expunge()
        log.Log("IMAP expunged %s files" % len(list), 3)

    def close(self):
        self._conn.select(gmail_mailbox)
        self._conn.close()
        self._conn.logout()

duplicity.backend.register_backend("gmail", GmailImapBackend);

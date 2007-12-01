# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# duplicity is free software; you can redistribute it and/or modify
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
Provides a backend for IMAP/s/gmail protocols.

Written by maho@pagema.net
"""

import imaplib
import base64
import re
import os
import StringIO
import rfc822
import log

from  backends import Backend


class ImapBackend(Backend):
    def __init__(self, parsed_url):
        Backend.__init__(self, parsed_url)
        
        cl = self.getIMAPClass()
       
        log.Log("type of IMAP class=%s, I'm %s connecting to %s"%(cl.__name__,self.__class__.__name__,
									self.parsed_url.host),9)
        self._conn=cl(self.parsed_url.host)
	log.Log("connected",8)
        (us,pa) = parsed_url.user.split(":");
        self._conn.login(us, pa)
	log.Log("logged in as %s"%us,8)
        self._conn.select(parsed_url.path)
        log.Log("IMAP connected",5)
        
    def getIMAPClass(self):
        return imaplib.IMAP4

    def _prepareBody(self,f,rname):
        ret="Subject: %s\n\n"%rname
        body=f.read(-1);
        body=base64.b64encode(body)
        
        fr=0
        le=75
        while(True):
            line=body[fr:fr+le]
            if line=='':break
            ret=ret+line
            fr=fr+75

        return ret

    def put(self, source_path, remote_filename = None):
        if not remote_filename: remote_filename = source_path.get_filename()

        f=source_path.open("rb")
        
        body=self._prepareBody(f,remote_filename)
        
        self._conn.append(self.parsed_url.path,None,None,body)
        log.Log("IMAP mail with '%s' subject stored"%remote_filename,5)

    def get(self, remote_filename, local_path):
        
        (result,list) = self._conn.search(None,"(HEADER Subject %s)"%remote_filename)
        if result != "OK": raise Exception(list[0])
        
        #check if there is any result
        if list[0] == '': raise Exception("no mail with subject %s")
        
        (result,list) = self._conn.fetch(list[0],"(RFC822)")
        
        if result != "OK": raise Exception(list[0])
        rawbody=list[0][1]
        #strip subject
        m = re.compile("^Subject[^\r\n]*[\r\n]*")
        b64body=m.sub("",rawbody);
        
        tfile = local_path.open("wb")
        tfile.write(base64.b64decode(b64body))
        local_path.setdata()
        log.Log("IMAP mail with '%s' subject fetched"%remote_filename,5)

    def list(self):
        ret = []
        (result,list) = self._conn.search(None,"(ALL)")
        if result!="OK":raise Exception(list[0])
        if list[0]=='': return ret
        nums=list[0].split(" ")
        set="%s:%s"%(nums[0],nums[-1])
        (result,list) = self._conn.fetch(set,"(BODY[HEADER])")
        if result!="OK":raise Exception(list[0])

        for msg in list:
            if (len(msg)==1):continue
            io = StringIO.StringIO(msg[1])
            m = rfc822.Message(io)
            subj = m.getheaders("subject")[0]
            ret.append(subj)
            log.Log("IMAP LIST: %s"%subj,6)
        return ret
            
    def _imapf(self,fun,*args):
        (ret,list)=fun(*args)
        if ret != "OK": raise Exception(list[0])
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
            if list[0]=="":raise Exception("no such mail with subject '%s'"%filename)
            self._delete_single_mail(list[0])
            log.Log("marked %s to be deleted"%filename,4)
        self._expunge()
        log.Log("IMAP expunged %s files"%len(list),3)


class ImapsBackend(ImapBackend):
    def __init__(self,parsed_url):
        log.Log("IMAPS backend launched",7)
        ImapBackend.__init__(self,parsed_url)
	
    def getIMAPClass(self):
        return imaplib.IMAP4_SSL


class Gmail(ImapsBackend):
    def _delete_single_mail(self,i):
        self._imapf(self._conn.copy,i,'[Gmail]/Trash')


    def _expunge(self):
        ImapsBackend._expunge(self)
        list=self._imapf(self._conn.select,"[Gmail]/Trash")
        num=list[0]
        list=self._imapf(self._conn.store,"1:%s"%num,"+FLAGS","\\DELETED")
        log.Log("expunged %s mails from [Gmail]/Trash"%len(list),5)

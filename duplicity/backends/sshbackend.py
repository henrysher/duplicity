# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2011 Alexander Zangerl <az@snafu.priv.at>
#
# $Id: sshbackend.py,v 1.2 2011/12/31 04:44:12 az Exp $
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

import re
import string
import os
import errno
import sys
import getpass

# debian squeeze's paramiko is a bit old, so we silence randompool depreciation warning
# note also: passphrased private keys work with squeeze's paramiko only if done with DES, not AES
import warnings
warnings.simplefilter("ignore")
import paramiko
warnings.resetwarnings()

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import *

read_blocksize=65635            # for doing scp retrievals, where we need to read ourselves

class SftpBackend(duplicity.backend.Backend):
    """This backend accesses files using the sftp protocol, or scp when the --use-scp option is given.
    It does not need any local client programs, but an ssh server and the sftp program must be installed on the remote
    side (or with --use-scp, the programs scp, ls, mkdir, rm and a POSIX-compliant shell).

    Authentication keys are requested from an ssh agent if present, then ~/.ssh/id_rsa/dsa are tried.
    If -oIdentityFile=path is present in --ssh-options, then that file is also tried.
    The passphrase for any of these keys is taken from the URI or FTP_PASSWORD.
    If none of the above are available, password authentication is attempted (using the URI or FTP_PASSWORD).

    Missing directories on the remote side will be created.

    If --use-scp is active then all operations on the remote side require passing arguments through a shell,
    which introduces unavoidable quoting issues: directory and file names that contain single quotes will not work.
    This problem does not exist with sftp.
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        # host string could be [user@]hostname
        if parsed_url.username:
            username=parsed_url.username
        else:
            username=getpass.getuser()

        if parsed_url.path:
            # remove first leading '/'
            self.remote_dir = re.sub(r'^/', r'', parsed_url.path, 1)
        else:
            self.remote_dir = '.'


        # set up password
        if globals.ssh_askpass:
            password = self.get_password()
        else:
            if parsed_url.password:
                password = parsed_url.password
            else:
                password = None
        self.client = paramiko.SSHClient()
        # load known_hosts files
        # paramiko is very picky wrt format and bails out on any problem...
        try:
            if os.path.isfile("/etc/ssh/ssh_known_hosts"):
                self.client.load_system_host_keys("/etc/ssh/ssh_known_hosts")
        except Exception, e:
            raise BackendException("could not load /etc/ssh/ssh_known_hosts, maybe corrupt?")
        try:
            self.client.load_system_host_keys()
        except Exception, e:
            raise BackendException("could not load ~/.ssh/known_hosts, maybe corrupt?")

        # alternative ssh private key?
        keyfilename=None
        m=re.search("-oidentityfile=(\S+)",globals.ssh_options,re.I)
        if (m!=None):
            keyfilename=m.group(1)

        if parsed_url.port:
            portnumber=parsed_url.port
        else:
            portnumber=22
        try:
            self.client.connect(hostname=parsed_url.hostname, port=portnumber,
                                username=username, password=password,
                                allow_agent=True, look_for_keys=True,
                                key_filename=keyfilename)
        except Exception, e:
            raise BackendException("ssh connection to %s:%d failed: %s" % (parsed_url.hostname,portnumber,e))
        self.client.get_transport().set_keepalive((int)(globals.timeout / 2))

        # scp or sftp?
        if (globals.use_scp):
            # sanity-check the directory name
            if (re.search("'",self.remote_dir)):
                raise BackendException("cannot handle directory names with single quotes with --use-scp!")

            # make directory if needed
            self.runremote("test -d '%s' || mkdir -p '%s'" % (self.remote_dir,self.remote_dir),False,"scp mkdir ")
        else:
            try:
                self.sftp=self.client.open_sftp()
            except Exception, e:
                raise BackendException("sftp negotiation failed: %s" % e)


            # move to the appropriate directory, possibly after creating it and its parents
            dirs = self.remote_dir.split(os.sep)
            if len(dirs) > 0:
                if not dirs[0]:
                    dirs = dirs[1:]
                    dirs[0]= '/' + dirs[0]
                for d in dirs:
                    if (d == ''):
                        continue
                    try:
                        attrs=self.sftp.stat(d)
                    except IOError, e:
                        if e.errno == errno.ENOENT:
                            try:
                                self.sftp.mkdir(d)
                            except Exception, e:
                                raise BackendException("sftp mkdir %s failed: %s" % (self.sftp.normalize(".")+"/"+d,e))
                        else:
                            raise BackendException("sftp stat %s failed: %s" % (self.sftp.normalize(".")+"/"+d,e))
                    try:
                        self.sftp.chdir(d)
                    except Exception, e:
                        raise BackendException("sftp chdir to %s failed: %s" % (self.sftp.normalize(".")+"/"+d,e))

    def put(self, source_path, remote_filename = None):
        """transfers a single file to the remote side.
        In scp mode unavoidable quoting issues will make this fail if the remote directory or file name
        contain single quotes."""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        if (globals.use_scp):
            f=file(source_path.name,'rb')
            try:
                chan=self.client.get_transport().open_session()
                chan.settimeout(globals.timeout)
                chan.exec_command("scp -t '%s'" % self.remote_dir) # scp in sink mode uses the arg as base directory
            except Exception, e:
                raise BackendException("scp execution failed: %s" % e)
            # scp protocol: one 0x0 after startup, one after the Create meta, one after saving
            # if there's a problem: 0x1 or 0x02 and some error text
            response=chan.recv(1)
            if (response!="\0"):
                raise BackendException("scp remote error: %s" % chan.recv(-1))
            fstat=os.stat(source_path.name)
            chan.send('C%s %d %s\n' %(oct(fstat.st_mode)[-4:], fstat.st_size, remote_filename))
            response=chan.recv(1)
            if (response!="\0"):
                raise BackendException("scp remote error: %s" % chan.recv(-1))
            chan.sendall(f.read()+'\0')
            f.close()
            response=chan.recv(1)
            if (response!="\0"):
                raise BackendException("scp remote error: %s" % chan.recv(-1))
            chan.close()
        else:
            try:
                self.sftp.put(source_path.name,remote_filename)
            except Exception, e:
                raise BackendException("sftp put of %s (as %s) failed: %s" % (source_path.name,remote_filename,e))


    def get(self, remote_filename, local_path):
        """retrieves a single file from the remote side.
        In scp mode unavoidable quoting issues will make this fail if the remote directory or file names
        contain single quotes."""
        if (globals.use_scp):
            try:
                chan=self.client.get_transport().open_session()
                chan.settimeout(globals.timeout)
                chan.exec_command("scp -f '%s/%s'" % (self.remote_dir,remote_filename))
            except Exception, e:
                raise BackendException("scp execution failed: %s" % e)

            chan.send('\0')     # overall ready indicator
            msg=chan.recv(-1)
            m=re.match(r"C([0-7]{4})\s+(\d+)\s+(\S.*)$",msg)
            if (m==None or m.group(3)!=remote_filename):
                raise BackendException("scp get %s failed: incorrect response '%s'" % (remote_filename,msg))
            chan.recv(1)        # dispose of the newline trailing the C message

            size=int(m.group(2))
            togo=size
            f=file(local_path.name,'wb')
            chan.send('\0')     # ready for data
            try:
                while togo>0:
                    if togo>read_blocksize:
                        blocksize = read_blocksize
                    else:
                        blocksize = togo
                    buff=chan.recv(blocksize)
                    f.write(buff)
                    togo-=len(buff)
            except Exception, e:
                raise BackendException("scp get %s failed: %s" % (remote_filename,e))

            msg=chan.recv(1)    # check the final status
            if msg!='\0':
                raise BackendException("scp get %s failed: %s" % (remote_filename,chan.recv(-1)))
            f.close()
            chan.send('\0')     # send final done indicator
            chan.close()
        else:
            try:
                self.sftp.get(remote_filename,local_path.name)
            except Exception, e:
                raise BackendException("sftp get of %s (to %s) failed: %s" % (remote_filename,local_path.name,e))
        local_path.setdata()

    def list(self):
        """lists the contents of the one-and-only duplicity dir on the remote side.
        In scp mode unavoidable quoting issues will make this fail if the directory name
        contains single quotes."""
        if (globals.use_scp):
            output=self.runremote("ls -1 '%s'" % self.remote_dir,False,"scp dir listing ")
            return output.splitlines()
        else:
            try:
                return self.sftp.listdir()
            except Exception, e:
                raise BackendException("sftp listing of %s failed: %s" % (self.sftp.getcwd(),e))

    def delete(self, filename_list):
        """deletes all files in the list on the remote side. In scp mode unavoidable quoting issues
        will cause failures if filenames containing single quotes are encountered."""
        for fn in filename_list:
            if (globals.use_scp):
                self.runremote("rm '%s/%s'" % (self.remote_dir,fn),False,"scp rm ")
            else:
                try:
                    self.sftp.remove(fn)
                except Exception, e:
                    raise BackendException("sftp rm %s failed: %s" % (fn,e))

    def runremote(self,cmd,ignoreexitcode=False,errorprefix=""):
        """small convenience function that opens a shell channel, runs remote command and returns
        stdout of command. throws an exception if exit code!=0 and not ignored"""
        try:
            chan=self.client.get_transport().open_session()
            chan.settimeout(globals.timeout)
            chan.exec_command(cmd)
        except Exception, e:
            raise BackendException("%sexecution failed: %s" % (errorprefix,e))
        output=chan.recv(-1)
        res=chan.recv_exit_status()
        if (res!=0 and not ignoreexitcode):
            raise BackendException("%sfailed(%d): %s" % (errorprefix,res,chan.recv_stderr(4096)))
        return output

duplicity.backend.register_backend("sftp", SftpBackend)
duplicity.backend.register_backend("scp", SftpBackend)
duplicity.backend.register_backend("ssh", SftpBackend)

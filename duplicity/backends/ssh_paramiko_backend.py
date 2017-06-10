# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2011 Alexander Zangerl <az@snafu.priv.at>
# Copyright 2012 edso (ssh_config added)
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
import logging
from binascii import hexlify

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import BackendException

read_blocksize = 65635  # for doing scp retrievals, where we need to read ourselves


class SSHParamikoBackend(duplicity.backend.Backend):
    """This backend accesses files using the sftp or scp protocols.
    It does not need any local client programs, but an ssh server and the sftp
    program must be installed on the remote side (or with scp, the programs
    scp, ls, mkdir, rm and a POSIX-compliant shell).

    Authentication keys are requested from an ssh agent if present, then
    ~/.ssh/id_rsa/dsa are tried. If -oIdentityFile=path is present in
    --ssh-options, then that file is also tried. The passphrase for any of
    these keys is taken from the URI or FTP_PASSWORD. If none of the above are
    available, password authentication is attempted (using the URI or
    FTP_PASSWORD).

    Missing directories on the remote side will be created.

    If scp is active then all operations on the remote side require passing
    arguments through a shell, which introduces unavoidable quoting issues:
    directory and file names that contain single quotes will not work.
    This problem does not exist with sftp.
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        self.retry_delay = 10

        if parsed_url.path:
            # remove first leading '/'
            self.remote_dir = re.sub(r'^/', r'', parsed_url.path, 1)
        else:
            self.remote_dir = '.'

        # lazily import paramiko when we need it
        # debian squeeze's paramiko is a bit old, so we silence randompool
        # depreciation warning note also: passphrased private keys work with
        # squeeze's paramiko only if done with DES, not AES
        import warnings
        warnings.simplefilter("ignore")
        import paramiko
        warnings.resetwarnings()

        class AgreedAddPolicy (paramiko.AutoAddPolicy):
            """
            Policy for showing a yes/no prompt and adding the hostname and new
            host key to the known host file accordingly.

            This class simply extends the AutoAddPolicy class with a yes/no
            prompt.
            """
            def missing_host_key(self, client, hostname, key):
                fp = hexlify(key.get_fingerprint())
                fingerprint = ':'.join(a + b for a, b in zip(fp[::2], fp[1::2]))
                question = """The authenticity of host '%s' can't be established.
%s key fingerprint is %s.
Are you sure you want to continue connecting (yes/no)? """ % (hostname,
                                                              key.get_name().upper(),
                                                              fingerprint)
                while True:
                    sys.stdout.write(question)
                    choice = raw_input().lower()
                    if choice in ['yes', 'y']:
                        paramiko.AutoAddPolicy.missing_host_key(self, client,
                                                                hostname, key)
                        return
                    elif choice in ['no', 'n']:
                        raise AuthenticityException(hostname)
                    else:
                        question = "Please type 'yes' or 'no': "

        class AuthenticityException (paramiko.SSHException):
            def __init__(self, hostname):
                paramiko.SSHException.__init__(self,
                                               'Host key verification for server %s failed.' %
                                               hostname)

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(AgreedAddPolicy())

        # paramiko uses logging with the normal python severity levels,
        # but duplicity uses both custom levels and inverted logic...*sigh*
        self.client.set_log_channel("sshbackend")
        ours = paramiko.util.get_logger("sshbackend")
        dest = logging.StreamHandler(sys.stderr)
        dest.setFormatter(logging.Formatter('ssh: %(message)s'))
        ours.addHandler(dest)

        # ..and the duplicity levels are neither linear,
        # nor are the names compatible with python logging,
        # eg. 'NOTICE'...WAAAAAH!
        plevel = logging.getLogger("duplicity").getEffectiveLevel()
        if plevel <= 1:
            wanted = logging.DEBUG
        elif plevel <= 5:
            wanted = logging.INFO
        elif plevel <= 7:
            wanted = logging.WARNING
        elif plevel <= 9:
            wanted = logging.ERROR
        else:
            wanted = logging.CRITICAL
        ours.setLevel(wanted)

        # load known_hosts files
        # paramiko is very picky wrt format and bails out on any problem...
        try:
            if os.path.isfile("/etc/ssh/ssh_known_hosts"):
                self.client.load_system_host_keys("/etc/ssh/ssh_known_hosts")
        except Exception as e:
            raise BackendException("could not load /etc/ssh/ssh_known_hosts, "
                                   "maybe corrupt?")
        try:
            # use load_host_keys() to signal it's writable to paramiko
            # load if file exists or add filename to create it if needed
            file = os.path.expanduser('~/.ssh/known_hosts')
            if os.path.isfile(file):
                self.client.load_host_keys(file)
            else:
                self.client._host_keys_filename = file
        except Exception as e:
            raise BackendException("could not load ~/.ssh/known_hosts, "
                                   "maybe corrupt?")

        """ the next block reorganizes all host parameters into a
        dictionary like SSHConfig does. this dictionary 'self.config'
        becomes the authorative source for these values from here on.
        rationale is that it is easiest to deal wrt overwriting multiple
        values from ssh_config file. (ede 03/2012)
        """
        self.config = {'hostname': parsed_url.hostname}
        # get system host config entries
        self.config.update(self.gethostconfig('/etc/ssh/ssh_config',
                                              parsed_url.hostname))
        # update with user's config file
        self.config.update(self.gethostconfig('~/.ssh/config',
                                              parsed_url.hostname))
        # update with url values
        # username from url
        if parsed_url.username:
            self.config.update({'user': parsed_url.username})
        # username from input
        if 'user' not in self.config:
            self.config.update({'user': getpass.getuser()})
        # port from url
        if parsed_url.port:
            self.config.update({'port': parsed_url.port})
        # ensure there is deafult 22 or an int value
        if 'port' in self.config:
            self.config.update({'port': int(self.config['port'])})
        else:
            self.config.update({'port': 22})
        # parse ssh options for alternative ssh private key, identity file
        m = re.search("^(?:.+\s+)?(?:-oIdentityFile=|-i\s+)(([\"'])([^\\2]+)\\2|[\S]+).*",
                      globals.ssh_options)
        if (m is not None):
            keyfilename = m.group(3) if m.group(3) else m.group(1)
            self.config['identityfile'] = keyfilename
        # ensure ~ is expanded and identity exists in dictionary
        if 'identityfile' in self.config:
            if not isinstance(self.config['identityfile'], list):
                # Paramiko 1.9.0 and earlier do not support multiple
                # identity files when parsing config files and always
                # return a string; later versions always return a list,
                # even if there is only one file given.
                #
                # All recent versions seem to support *using* multiple
                # identity files, though, so to make things easier, we
                # simply always use a list.
                self.config['identityfile'] = [self.config['identityfile']]

            self.config['identityfile'] = [
                os.path.expanduser(i) for i in self.config['identityfile']]
        else:
            self.config['identityfile'] = None

        # get password, enable prompt if askpass is set
        self.use_getpass = globals.ssh_askpass
        # set url values for beautiful login prompt
        parsed_url.username = self.config['user']
        parsed_url.hostname = self.config['hostname']
        password = self.get_password()

        try:
            self.client.connect(hostname=self.config['hostname'],
                                port=self.config['port'],
                                username=self.config['user'],
                                password=password,
                                allow_agent=True,
                                look_for_keys=True,
                                key_filename=self.config['identityfile'])
        except Exception as e:
            raise BackendException("ssh connection to %s@%s:%d failed: %s" % (
                self.config['user'],
                self.config['hostname'],
                self.config['port'], e))
        self.client.get_transport().set_keepalive((int)(globals.timeout / 2))

        self.scheme = duplicity.backend.strip_prefix(parsed_url.scheme,
                                                     'paramiko')
        self.use_scp = (self.scheme == 'scp')

        # scp or sftp?
        if (self.use_scp):
            # sanity-check the directory name
            if (re.search("'", self.remote_dir)):
                raise BackendException("cannot handle directory names with single quotes with scp")

            # make directory if needed
            self.runremote("mkdir -p '%s'" % (self.remote_dir,), False, "scp mkdir ")
        else:
            try:
                self.sftp = self.client.open_sftp()
            except Exception as e:
                raise BackendException("sftp negotiation failed: %s" % e)

            # move to the appropriate directory, possibly after creating it and its parents
            dirs = self.remote_dir.split(os.sep)
            if len(dirs) > 0:
                if not dirs[0]:
                    dirs = dirs[1:]
                    dirs[0] = '/' + dirs[0]
                for d in dirs:
                    if (d == ''):
                        continue
                    try:
                        attrs = self.sftp.stat(d)
                    except IOError as e:
                        if e.errno == errno.ENOENT:
                            try:
                                self.sftp.mkdir(d)
                            except Exception as e:
                                raise BackendException("sftp mkdir %s failed: %s" %
                                                       (self.sftp.normalize(".") + "/" + d, e))
                        else:
                            raise BackendException("sftp stat %s failed: %s" %
                                                   (self.sftp.normalize(".") + "/" + d, e))
                    try:
                        self.sftp.chdir(d)
                    except Exception as e:
                        raise BackendException("sftp chdir to %s failed: %s" %
                                               (self.sftp.normalize(".") + "/" + d, e))

    def _put(self, source_path, remote_filename):
        if self.use_scp:
            f = file(source_path.name, 'rb')
            try:
                chan = self.client.get_transport().open_session()
                chan.settimeout(globals.timeout)
                # scp in sink mode uses the arg as base directory
                chan.exec_command("scp -t '%s'" % self.remote_dir)
            except Exception as e:
                raise BackendException("scp execution failed: %s" % e)
            # scp protocol: one 0x0 after startup, one after the Create meta,
            # one after saving if there's a problem: 0x1 or 0x02 and some error
            # text
            response = chan.recv(1)
            if (response != "\0"):
                raise BackendException("scp remote error: %s" % chan.recv(-1))
            fstat = os.stat(source_path.name)
            chan.send('C%s %d %s\n' % (oct(fstat.st_mode)[-4:], fstat.st_size,
                                       remote_filename))
            response = chan.recv(1)
            if (response != "\0"):
                raise BackendException("scp remote error: %s" % chan.recv(-1))
            chan.sendall(f.read() + '\0')
            f.close()
            response = chan.recv(1)
            if (response != "\0"):
                raise BackendException("scp remote error: %s" % chan.recv(-1))
            chan.close()
        else:
            self.sftp.put(source_path.name, remote_filename)

    def _get(self, remote_filename, local_path):
        if self.use_scp:
            try:
                chan = self.client.get_transport().open_session()
                chan.settimeout(globals.timeout)
                chan.exec_command("scp -f '%s/%s'" % (self.remote_dir,
                                                      remote_filename))
            except Exception as e:
                raise BackendException("scp execution failed: %s" % e)

            chan.send('\0')  # overall ready indicator
            msg = chan.recv(-1)
            m = re.match(r"C([0-7]{4})\s+(\d+)\s+(\S.*)$", msg)
            if (m is None or m.group(3) != remote_filename):
                raise BackendException("scp get %s failed: incorrect response '%s'" %
                                       (remote_filename, msg))
            chan.recv(1)  # dispose of the newline trailing the C message

            size = int(m.group(2))
            togo = size
            f = file(local_path.name, 'wb')
            chan.send('\0')  # ready for data
            try:
                while togo > 0:
                    if togo > read_blocksize:
                        blocksize = read_blocksize
                    else:
                        blocksize = togo
                    buff = chan.recv(blocksize)
                    f.write(buff)
                    togo -= len(buff)
            except Exception as e:
                raise BackendException("scp get %s failed: %s" % (remote_filename, e))

            msg = chan.recv(1)  # check the final status
            if msg != '\0':
                raise BackendException("scp get %s failed: %s" % (remote_filename,
                                                                  chan.recv(-1)))
            f.close()
            chan.send('\0')  # send final done indicator
            chan.close()
        else:
            self.sftp.get(remote_filename, local_path.name)

    def _list(self):
        # In scp mode unavoidable quoting issues will make this fail if the
        # directory name contains single quotes.
        if self.use_scp:
            output = self.runremote("ls -1 '%s'" % self.remote_dir, False,
                                    "scp dir listing ")
            return output.splitlines()
        else:
            return self.sftp.listdir()

    def _delete(self, filename):
        # In scp mode unavoidable quoting issues will cause failures if
        # filenames containing single quotes are encountered.
        if self.use_scp:
            self.runremote("rm '%s/%s'" % (self.remote_dir, filename), False,
                           "scp rm ")
        else:
            self.sftp.remove(filename)

    def runremote(self, cmd, ignoreexitcode=False, errorprefix=""):
        """small convenience function that opens a shell channel, runs remote
        command and returns stdout of command. throws an exception if exit
        code!=0 and not ignored"""
        try:
            ch_in, ch_out, ch_err = self.client.exec_command(cmd, -1, globals.timeout)
            output = ch_out.read(-1)
            return output
        except Exception as e:
            if not ignoreexitcode:
                raise BackendException("%sfailed: %s \n %s" % (
                    errorprefix, ch_err.read(-1), e))

    def gethostconfig(self, file, host):
        import paramiko

        file = os.path.expanduser(file)
        if not os.path.isfile(file):
            return {}

        sshconfig = paramiko.SSHConfig()
        try:
            sshconfig.parse(open(file))
        except Exception as e:
            raise BackendException("could not load '%s', maybe corrupt?" % (file))

        return sshconfig.lookup(host)


duplicity.backend.register_backend("sftp", SSHParamikoBackend)
duplicity.backend.register_backend("scp", SSHParamikoBackend)
duplicity.backend.register_backend("paramiko+sftp", SSHParamikoBackend)
duplicity.backend.register_backend("paramiko+scp", SSHParamikoBackend)
duplicity.backend.uses_netloc.extend(['sftp', 'scp', 'paramiko+sftp', 'paramiko+scp'])

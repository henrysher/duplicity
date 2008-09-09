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

# The following can be redefined to use different shell commands from
# ssh or scp or to add more arguments.  However, the replacements must
# have the same syntax.  Also these strings will be executed by the
# shell, so shouldn't have strange characters in them.

import re
import string
import time

import duplicity.backend
import duplicity.globals as globals
import duplicity.log as log
from duplicity.errors import *

scp_command = "scp"
sftp_command = "sftp"

# default to batch mode using public-key encryption
ssh_askpass = False

# user added ssh options
ssh_options = ""

class SSHBackend(duplicity.backend.Backend):
    """This backend copies files using scp.  List not supported"""
    def __init__(self, parsed_url):
        """scpBackend initializer"""
        duplicity.backend.Backend.__init__(self, parsed_url)
        try:
            import pexpect
            self.pexpect = pexpect
        except ImportError:
            self.pexpect = None

        if not (self.pexpect and
                hasattr(self.pexpect, '__version__') and
                self.pexpect.__version__ >= '2.1'):
            log.FatalError("This backend requires the pexpect module version 2.1 or later."
                           "You can get pexpect from http://pexpect.sourceforge.net or "
                           "python-pexpect from your distro's repository.")

        # host string of form [user@]hostname
        if parsed_url.username:
            self.host_string = parsed_url.username + "@" + parsed_url.hostname
        else:
            self.host_string = parsed_url.hostname
        # make sure remote_dir is always valid
        if parsed_url.path:
            # remove leading '/'
            self.remote_dir = re.sub(r'^/', r'', parsed_url.path, 1)
        else:
            self.remote_dir = '.'
        self.remote_prefix = self.remote_dir + '/'
        # maybe use different ssh port
        if parsed_url.port:
            self.ssh_options = ssh_options + " -oPort=%s" % parsed_url.port
        else:
            self.ssh_options = ssh_options
        # set up password
        if ssh_askpass:
            self.password = self.get_password()
        else:
            self.password = ''

    def run_scp_command(self, commandline):
        """ Run an scp command, responding to password prompts """
        for n in range(1, globals.num_retries+1):
            log.Log("Running '%s' (attempt #%d)" % (commandline, n), 5)
            child = self.pexpect.spawn(commandline, timeout = globals.timeout)
            cmdloc = 0
            if ssh_askpass:
                state = "authorizing"
            else:
                state = "copying"
            while 1:
                if state == "authorizing":
                    match = child.expect([self.pexpect.EOF,
                                          self.pexpect.TIMEOUT,
                                          "(?i)password:",
                                          "(?i)permission denied",
                                          "authenticity"],
                                         timeout = globals.timeout)
                    log.Log("State = %s, Before = '%s'" % (state, child.before.strip()), 9)
                    if match == 0:
                        log.Log("Failed to authenticate", 5)
                        break
                    elif match == 1:
                        log.Log("Timeout waiting to authenticate", 5)
                        break
                    elif match == 2:
                        child.sendline(self.password)
                        state = "copying"
                    elif match == 3:
                        log.Log("Invalid SSH password", 1)
                        break
                    elif match == 4:
                        log.Log("Remote host authentication failed (missing known_hosts entry?)", 1)
                        break
                elif state == "copying":
                    match = child.expect([self.pexpect.EOF,
                                          self.pexpect.TIMEOUT,
                                          "stalled",
                                          "authenticity",
                                          "ETA"],
                                         timeout = globals.timeout)
                    log.Log("State = %s, Before = '%s'" % (state, child.before.strip()), 9)
                    if match == 0:
                        break
                    elif match == 1:
                        log.Log("Timeout waiting for response", 5)
                        break
                    elif match == 2:
                        state = "stalled"
                    elif match == 3:
                        log.Log("Remote host authentication failed (missing known_hosts entry?)", 1)
                        break
                elif state == "stalled":
                    match = child.expect([self.pexpect.EOF,
                                          self.pexpect.TIMEOUT,
                                          "ETA"],
                                         timeout = globals.timeout)
                    log.Log("State = %s, Before = '%s'" % (state, child.before.strip()), 9)
                    if match == 0:
                        break
                    elif match == 1:
                        log.Log("Stalled for too long, aborted copy", 5)
                        break
                    elif match == 2:
                        state = "copying"
            child.close(force = True)
            if child.exitstatus == 0:
                return
            log.Log("Running '%s' failed (attempt #%d)" % (commandline, n), 1)
            time.sleep(30)
        log.Log("Giving up trying to execute '%s' after %d attempts" % (commandline, globals.num_retries), 1)
        raise BackendException("Error running '%s'" % commandline)

    def run_sftp_command(self, commandline, commands):
        """ Run an sftp command, responding to password prompts, passing commands from list """
        for n in range(1, globals.num_retries+1):
            log.Log("Running '%s' (attempt #%d)" % (commandline, n), 5)
            child = self.pexpect.spawn(commandline, timeout = globals.timeout)
            cmdloc = 0
            while 1:
                match = child.expect([self.pexpect.EOF,
                                      self.pexpect.TIMEOUT,
                                      "sftp>",
                                      "(?i)password:",
                                      "(?i)permission denied",
                                      "authenticity",
                                      "(?i)no such file or directory"])
                log.Log("State = sftp, Before = '%s'" % (child.before.strip()), 9)
                if match == 0:
                    break
                elif match == 1:
                    log.Log("Timeout waiting for response", 5)
                    break
                if match == 2:
                    if cmdloc < len(commands):
                        command = commands[cmdloc]
                        log.Log("sftp command: '%s'" % (command,), 5)
                        child.sendline(command)
                        cmdloc += 1
                    else:
                        command = 'quit'
                        child.sendline(command)
                        res = child.before
                elif match == 3:
                    child.sendline(self.password)
                elif match == 4:
                    log.Log("Invalid SSH password", 1)
                    break
                elif match == 5:
                    log.Log("Host key authenticity could not be verified (missing known_hosts entry?)", 1)
                    break
                elif match == 6:
                    log.Log("Remote file or directory '%s' does not exist" % self.remote_dir, 1)
                    break
            child.close(force = True)
            if child.exitstatus == 0:
                return res
            log.Log("Running '%s' failed (attempt #%d)" % (commandline, n), 1)
            time.sleep(30)
        log.Log("Giving up trying to execute '%s' after %d attempts" % (commandline, globals.num_retries), 1)
        raise BackendException("Error running '%s'" % commandline)

    def put(self, source_path, remote_filename = None):
        """Use scp to copy source_dir/filename to remote computer"""
        if not remote_filename: remote_filename = source_path.get_filename()
        commandline = "%s %s %s %s:%s%s" % \
            (scp_command, self.ssh_options, source_path.name, self.host_string,
             self.remote_prefix, remote_filename)
        self.run_scp_command(commandline)

    def get(self, remote_filename, local_path):
        """Use scp to get a remote file"""
        commandline = "%s %s %s:%s%s %s" % \
            (scp_command, self.ssh_options, self.host_string, self.remote_prefix,
             remote_filename, local_path.name)
        self.run_scp_command(commandline)
        local_path.setdata()
        if not local_path.exists():
            raise BackendException("File %s not found locally after get "
                                   "from backend" % local_path.name)

    def list(self):
        """
        List files available for scp

        Note that this command can get confused when dealing with
        files with newlines in them, as the embedded newlines cannot
        be distinguished from the file boundaries.
        """
        commands = ["mkdir %s" % (self.remote_dir,),
                    "cd %s" % (self.remote_dir,),
                    "ls -1"]
        commandline = ("%s %s %s" % (sftp_command,
                                     self.ssh_options,
                                     self.host_string))

        l = self.run_sftp_command(commandline, commands).split('\n')[1:]

        return filter(lambda x: x, map(string.strip, l))

    def delete(self, filename_list):
        """
        Runs sftp rm to delete files.  Files must not require quoting.
        """
        commands = ["cd %s" % (self.remote_dir,)]
        for fn in filename_list:
            commands.append("rm %s" % fn)
        commandline = ("%s %s %s" % (sftp_command, self.ssh_options, self.host_string))
        self.run_sftp_command(commandline, commands)

duplicity.backend.register_backend("ssh", SSHBackend)
duplicity.backend.register_backend("scp", SSHBackend)

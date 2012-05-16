# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2012 edso
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

from duplicity import globals, log

def warn_option(option, optionvar):
    if optionvar:
        log.Warn(_("Warning: Option %s is supported by ssh pexpect backend only and will be ignored.") % option)

if (globals.ssh_backend and
    globals.ssh_backend.lower().strip() == 'pexpect'):
    import _ssh_pexpect
else:
    # take user by the hand to prevent typo driven bug reports
    if globals.ssh_backend.lower().strip() != 'paramiko':
        log.Warn(_("Warning: Selected ssh backend '%s' is neither 'paramiko nor 'pexpect'. Will use default paramiko instead.") % globals.ssh_backend)
    warn_option("--scp-command", globals.scp_command)
    warn_option("--sftp-command", globals.sftp_command)
    import _ssh_paramiko

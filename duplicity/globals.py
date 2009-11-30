# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
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

"""Store global configuration information"""

import socket, sys, os

# The current version of duplicity
version = "$version"

# The name of the current host, or None if it cannot be set
hostname = socket.getfqdn()

# The main local path.  For backing up the is the path to be backed
# up.  For restoring, this is the destination of the restored files.
local_path = None

# The backend representing the remote side
backend = None

# If set, the Select object which iterates paths in the local
# source directory.
select = None

# Set to GPGProfile that will be used to compress/uncompress encrypted
# files.  Replaces encryption_keys, sign_key, and passphrase settings.
gpg_profile = None

# If set, abort if cannot do an incremental backup.  Otherwise if
# signatures not found, default to full.
incremental = None

# If set, signifies time in seconds before which backup files should
# be deleted.
remove_time = None

# If set, signifies the number of backups chains to keep when perfroming
# a --remove-all-but-n-full.
keep_chains = None

# Working directory for the tempfile module. Defaults to /tmp on most systems.
temproot = None

# Protocol for webdav
webdav_proto = 'http'

# will be a Restart object if restarting
restart = None

# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2013 J.P. Krauss <jkrauss@asymworks.com>
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

import duplicity.backend
from duplicity import log
from duplicity import util
from duplicity.errors import BackendException
from ._cf_pyrax import PyraxBackend


class HubicBackend(PyraxBackend):
    """
    Backend for Hubic using Pyrax
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        try:
            import pyrax
        except ImportError as e:
            raise BackendException("""\
Hubic backend requires the pyrax library available from Rackspace.
Exception: %s""" % str(e))

        # Inform Pyrax that we're talking to Hubic
        pyrax.set_setting("identity_type", "duplicity.backends.pyrax_identity.hubic.HubicIdentity")

        CREDENTIALS_FILE = os.path.expanduser("~/.hubic_credentials")
        if os.path.exists(CREDENTIALS_FILE):
            try:
                pyrax.set_credential_file(CREDENTIALS_FILE)
            except Exception as e:
                log.FatalError("Connection failed, please check your credentials: %s %s"
                               % (e.__class__.__name__, util.uexc(e)),
                               log.ErrorCode.connection_failed)

        else:
            raise BackendException("No ~/.hubic_credentials file found.")

        container = parsed_url.path.lstrip('/')

        self.client_exc = pyrax.exceptions.ClientException
        self.nso_exc = pyrax.exceptions.NoSuchObject
        self.container = pyrax.cloudfiles.create_container(container)

duplicity.backend.register_backend("cf+hubic", HubicBackend)

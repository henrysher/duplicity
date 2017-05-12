# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2017 Nils Tekampe <nils@tekampe.org>
#
# This file is part of duplicity.
# It is the Dockerfile of a simple ftp server that is used for backend testing 
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

FROM stilliard/pure-ftpd 

# Install some tools for convenience
RUN apt-get update \
    && apt-get install -y \
            nano \
            mc \
    && rm -rf /var/lib/apt/lists/*

# Creating a ftp user account for testing testuser:testuser
COPY pureftpd.passwd /etc/pure-ftpd/passwd/pureftpd.passwd 

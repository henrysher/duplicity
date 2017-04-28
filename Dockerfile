# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2017 Nils Tekampe <nils@tekampe.org>
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

FROM ubuntu:16.04

#Setting a working directory for everything else
WORKDIR /duplicity

# Installing some pre-requisites and some
# packages needed for testing duplicity
RUN apt-get update && apt-get install -y \
            build-essential \
            bzr \
            intltool \
            lftp \
            libffi-dev \
            librsync-dev \
            libssl-dev \
            openssl \
            par2 \
            python-dev \
            rdiff \
    && rm -rf /var/lib/apt/lists/*

# Need to make gpg2 the default gpg
RUN mv /usr/bin/gpg /usr/bin/gpg1 && ln -s /usr/bin/gpg2 /usr/bin/gpg

# Installing pip
RUN curl https://bootstrap.pypa.io/get-pip.py | python

# Installing requirements for pip
RUN pip install --requirement requirements.txt

# Branch the duplicity repo for testing
RUN bzr branch --use-existing-dir lp:duplicity /duplicity

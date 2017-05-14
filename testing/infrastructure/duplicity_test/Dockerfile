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

# Installing some pre-requisites and some
# packages needed for testing duplicity
RUN apt-get update \
    && apt-get install -y \
            build-essential \
            bzr \
            intltool \
            lftp \
            librsync-dev \
            libffi-dev \
            libssl-dev \
            openssl \
            par2 \
            python-dev \
            rdiff \
            tzdata

# The following packages are not necessary for testing but make life easier or support debugging
RUN apt-get install -y \
            nano \
            mc \
            iputils-ping \
            net-tools \
            ftp \
    && rm -rf /var/lib/apt/lists/*

# Need to make gpg2 the default gpg
RUN mv /usr/bin/gpg /usr/bin/gpg1 && ln -s /usr/bin/gpg2 /usr/bin/gpg

# Installing pip
RUN curl https://bootstrap.pypa.io/get-pip.py | python

# Installing requirements for pip
COPY requirements.txt /tmp
RUN pip install --requirement /tmp/requirements.txt

# Delete root's password so we can do 'su -'
RUN passwd --delete root

# Install test user and swap to it
RUN groupadd test && useradd -m -g test test
USER test

# Setting a working directory to home
WORKDIR /home/test

# Copy a SSH key to the users folder that is used for some test cases
USER root
COPY ./id_rsa /home/test/.ssh/
COPY ./id_rsa.pub /home/test/.ssh/
RUN chown -R test:test /home/test/.ssh
RUN chmod 400 /home/test/.ssh/id_rsa
USER test 

# Branch the duplicity repo for testing
RUN bzr branch lp:duplicity duplicity

# Set final workdir to duplicity
WORKDIR duplicity

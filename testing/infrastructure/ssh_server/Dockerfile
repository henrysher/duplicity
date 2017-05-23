# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2017 Nils Tekampe <nils@tekampe.org>
# Thanks to Aleksandar Diklic "https://github.com/rastasheep"
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
#
FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y \
            mc \
            nano \
            openssh-server\
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd

RUN echo 'root:root' |chpasswd

RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri "s/UsePAM yes/#UsePAM yes/g" /etc/ssh/sshd_config
RUN sed -ri "s/#Port 22/Port 2222/g" /etc/ssh/sshd_config
RUN echo "Match User userWithOnlyKeyAccess" >> /etc/ssh/sshd_config
RUN echo "     PasswordAuthentication no" >> /etc/ssh/sshd_config

RUN useradd -ms /bin/bash userWithKeyAccess
RUN useradd -ms /bin/bash userWithPasswordAccess
RUN useradd -ms /bin/bash userWithOnlyKeyAccess

USER userWithKeyAccess
WORKDIR /home/userWithKeyAccess
COPY ./id_rsa.pub /home/userWithKeyAccess/.ssh/authorized_keys

USER userWithOnlyKeyAccess
WORKDIR /home/userWithOnlyKeyAccess
COPY ./id_rsa.pub /home/userWithOnlyKeyAccess/.ssh/authorized_keys

USER userWithPasswordAccess
WORKDIR /home/userWithPasswordAccess

USER root

RUN echo 'userWithKeyAccess:userWithKeyAccess' |chpasswd
RUN echo 'userWithPasswordAccess:userWithPasswordAccess' |chpasswd

RUN chown -R userWithKeyAccess:userWithKeyAccess /home/userWithKeyAccess/.ssh
RUN chown -R userWithOnlyKeyAccess:userWithOnlyKeyAccess /home/userWithOnlyKeyAccess/.ssh/

RUN ["service", "ssh", "restart"]

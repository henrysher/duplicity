#!/bin/bash
#
# Copyright 2017 Nils Tekampe <nils@tekampe.org>
#
# This file is part of duplicity.
# This script sets up a test network for the tests of dupclicity
# This script takes the assumption that the containers for the testinfrastructure do deither run
# or they are removed. It is not intended to have stopped containers.
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


# Check whether a specific docker network for testing is already exisitng. If not, create it.
docker network inspect testnetwork &> /dev/null

if [ $? -ne 0 ]; then
    echo "docker testnetwork not found. Creating network."
    docker network create --subnet=10.10.10.0/24 testnetwork
fi


# Remove all running instances of the test system and also remove the containers. This ensure
# that the test infrastructure is frehshly started.
docker rm $(docker stop $(docker ps -a -q --filter name=ftpd_server --format="{{.ID}}"))
docker rm $(docker stop $(docker ps -a -q --filter name=duplicity_test --format="{{.ID}}"))


# Start the containers. Docker run will automatically download the image if necessary
docker run -d --net testnetwork --ip 10.10.10.3 --name ftpd_server -p 21:21 -p 30000-30009:30000-30009 -e "PUBLICHOST=localhost" dernils/duplicity_testinfrastructure_ftp
docker run --name duplicity_test --net testnetwork --ip 10.10.10.2 -it  dernils/duplicitytest:latest

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

# Define the subnet and the name of the testnetwork that should be used for testing
SUBNET=10.20.0.0/24
SUBNET_BASE=10.20.0
TESTNETWORK=testnetwork
IP_DUPLICITY_SSH=${SUBNET_BASE}.4
IP_DUPLICITY_FTP=${SUBNET_BASE}.3
IP_DUPLICITY_TEST=${SUBNET_BASE}.2

# Remove all running instances of the test system and also remove the containers. This ensures
# that the test infrastructure is frehshly started.
# We kill only containers nameed beginning with "duplicity_test_" to ensure that we do not
# accidentially touch other containers

echo "Removing any running instances of duplicity_test_*"
docker rm -f $(docker ps  -a -q --filter name=duplicity_test_) &> /dev/null

echo "(Re)create docker testnetwork."
docker network rm ${TESTNETWORK} &> /dev/null
docker network create --subnet=${SUBNET} ${TESTNETWORK}

# Start the containers. Docker run will automatically download the image if necessary
# Hand over the parameters for testing to the main docker container

echo "Starting duplicity_test_ftp..."
docker run -d --net ${TESTNETWORK} --ip ${IP_DUPLICITY_FTP} --name duplicity_test_ftp \
    -p 21:21 -p 30000-30009:30000-30009 -t firstprime/duplicity_ftp

echo "Starting duplicity_test_ssh..."
docker run -d --net ${TESTNETWORK} --ip ${IP_DUPLICITY_SSH} --name duplicity_test_ssh \
    -p 2222:22 -t firstprime/duplicity_ssh:latest

echo "Starting duplicity_test_main..."
docker run --net ${TESTNETWORK} --ip ${IP_DUPLICITY_TEST} --name duplicity_test_main \
    -e DUPLICITY_TESTNETWORK=${TESTNETWORK} -e DUPLICITY_SUBNET=${SUBNET} -e "PUBLICHOST=localhost" \
    -e DUPLICITY_IP_SSH_SERVER=${IP_DUPLICITY_SSH} -e DUPLICITY_IP_FTP_SERVER=${IP_DUPLICITY_FTP} \
    -it firstprime/duplicity_test:latest

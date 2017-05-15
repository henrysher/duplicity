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
subnet=10.10.10.0/24
testnetwork=testnetwork
ip_ssh_server=10.10.10.4
ip_ftp_server=10.10.10.3
ip_duplicity_test=10.10.10.2

# Check whether a specific docker network for testing is already exisitng. If not, create it.
docker network inspect $testnetwork &> /dev/null

if [ $? -ne 0 ]; then
    echo "docker testnetwork not found. Creating network."
    docker network create --subnet=$subnet $testnetwork
fi

# Remove all running instances of the test system and also remove the containers. This ensure
# that the test infrastructure is frehshly started.
# We are using UUIDs as part of the names of the docker container to ensure that we do not accidentially touch other containers
docker rm -f $(docker stop $(docker ps  -a -q --filter name=d70c0e18-37d5-11e7-a919-92ebcb67fe33-ftpd_server --format="{{.ID}}"))
docker rm -f $(docker stop $(docker ps  -a -q --filter name=ee681ee4-37d5-11e7-a919-92ebcb67fe33-duplicity_ssh_server --format="{{.ID}}"))
docker rm -f $(docker stop $(docker ps  -a -q --filter name=f3c09128-37d5-11e7-a919-92ebcb67fe33-duplicity_test --format="{{.ID}}"))


# Start the containers. Docker run will automatically download the image if necessary
# Hand over the parameters for testing to the main docker container 
docker run -d --net $testnetwork --ip $ip_ftp_server --name d70c0e18-37d5-11e7-a919-92ebcb67fe33-ftpd_server -p 21:21 -p 30000-30009:30000-30009  dernils/duplicity_testinfrastructure_ftp
docker run -d --net $testnetwork --ip $ip_ssh_server --name ee681ee4-37d5-11e7-a919-92ebcb67fe33-duplicity_ssh_server  -p 22:22 dernils/duplicity_testinfrastructure_ssh:latest 
docker run --name f3c09128-37d5-11e7-a919-92ebcb67fe33-duplicity_test --net $testnetwork --ip $ip_duplicity_test -e DUPLICITY_TESTNETWORK=$testnetwork -e DUPLICITY_SUBNET=$subnet -e "PUBLICHOST=localhost" -e DUPLICITY_IP_SSH_SERVER=$ip_ssh_server -e DUPLICITY_IP_FTP_SERVER=$ip_ftp_server -it  dernils/duplicitytest:latest

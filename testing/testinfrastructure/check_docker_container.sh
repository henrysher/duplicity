#!/bin/bash

# Author: Erik Kristensen
# Email: erik@erikkristensen.com
# License: MIT
# Nagios Usage: check_nrpe!check_docker_container!_container_id_
# Usage: ./check_docker_container.sh _container_id_
#
# Depending on your docker configuration, root might be required. If your nrpe user has rights
# to talk to the docker daemon, then root is not required. This is why root privileges are not
# checked.
#
# The script checks if a container is running.
#   OK - running
#   WARNING - restarting
#   CRITICAL - stopped
#   UNKNOWN - does not exist
#
# CHANGELOG - March 20, 2017
#  - Removes Ghost State Check, Checks for Restarting State, Properly finds the Networking IP addresses
#  - Returns unknown (exit code 3) if docker binary is missing, unable to talk to the daemon, or if container id is missing

CONTAINER=$1

if [ "x${CONTAINER}" == "x" ]; then
  echo "UNKNOWN - Container ID or Friendly Name Required"
  exit 3
fi

if [ "x$(which docker)" == "x" ]; then
  echo "UNKNOWN - Missing docker binary"
  exit 3
fi

docker info > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "UNKNOWN - Unable to talk to the docker daemon"
  exit 3
fi

RUNNING=$(docker inspect --format="{{.State.Running}}" $CONTAINER 2> /dev/null)

if [ $? -eq 1 ]; then
  echo "UNKNOWN - $CONTAINER does not exist."
  exit 2
fi

if [ "$RUNNING" == "false" ]; then
  echo "CRITICAL - $CONTAINER is not running."
  exit 1
fi

RESTARTING=$(docker inspect --format="{{.State.Restarting}}" $CONTAINER)

if [ "$RESTARTING" == "true" ]; then
  echo "WARNING - $CONTAINER state is restarting."
  exit 3
fi

STARTED=$(docker inspect --format="{{.State.StartedAt}}" $CONTAINER)
NETWORK=$(docker inspect --format="{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" $CONTAINER)

echo "OK - $CONTAINER is running. IP: $NETWORK, StartedAt: $STARTED"
exit 0
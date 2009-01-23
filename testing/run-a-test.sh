#!/bin/bash

SUDO=sudo

cd `dirname $0`
pwd

if [ ! -e $1 ]; then
    echo "No test named $1"
    exit 1
fi

cd ../duplicity
./compilec.py
cd -

${SUDO} tar xzf testfiles.tar.gz

for v in 2.3 2.4 2.5 2.6; do
    if [ -e /usr/bin/python$v ]; then
        echo "Running tests for python$v"
        echo "========== Running $1 =========="
        ${SUDO} python$v -u $1 2>&1 | grep -v "unsafe ownership"
    fi
done

${SUDO} rm -rf testfiles tempdir temp2.tar

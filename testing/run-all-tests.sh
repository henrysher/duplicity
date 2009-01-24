#!/bin/bash

SUDO=sudo

cd `dirname $0`
pwd

cd ../duplicity
./compilec.py
cd -

${SUDO} tar xzf testfiles.tar.gz

for v in 2.3 2.4 2.5 2.6; do
    if [ -e /usr/bin/python$v ]; then
        LOG=run-all-tests-$v.log
        rm -f $LOG
        echo "Running tests for python$v" | tee -a $LOG
        for t in `cat alltests`; do
            echo "========== Running $t ==========" | tee -a $LOG
            ${SUDO} python$v -u $t -v 2>&1 | grep -v "unsafe ownership" | tee -a $LOG
            echo | tee -a  $LOG
            echo | tee -a  $LOG
        done
    fi
done

${SUDO} rm -rf testfiles tempdir temp2.tar

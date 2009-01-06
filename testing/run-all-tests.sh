#!/bin/bash

alltests=" \
    backendtest.py \
    collectionstest.py \
    diffdirtest.py \
    dup_temptest.py \
    dup_timetest.py \
    file_namingtest.py \
    gpgtest.py \
    gpgtest2.py \
    GnuPGInterfacetest.py \
    lazytest.py \
    logtest.py \
    manifesttest.py \
    misctest.py \
    patchdirtest.py \
    pathtest.py \
    rdiffdirtest.py \
    roottest.py \
    selectiontest.py \
    statictest.py \
    statisticstest.py \
    tempdirtest.py \
    test_tarfile.py \
    finaltest.py \
"

SUDO=sudo

cd `dirname $0`
pwd

${SUDO} tar xzf testfiles.tar.gz

for v in 2.3 2.4 2.5 2.6; do
    if [ -e /usr/bin/python$v ]; then
        LOG=run-all-tests-$v.log
        rm -f $LOG
        echo "Running tests for python$v"
        echo "Running tests for python$v" >> $LOG
        for t in ${alltests}; do
            echo "========== Running $t =========="
            echo "========== Running $t ==========" >> $LOG
            ${SUDO} python$v -u $t 2>&1 | grep -v "unsafe ownership" >> $LOG
            echo >> $LOG
            echo >> $LOG
        done
    fi
done

${SUDO} rm -rf testfiles tempdir temp2.tar

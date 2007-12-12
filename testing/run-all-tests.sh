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


cd `dirname $0`
pwd

sudo tar xzf testfiles.tar.gz

for t in ${alltests}; do
    echo "========== Running $t =========="
    sudo python -u $t 2>&1 | grep -v "unsafe ownership"
    echo
    echo
done

sudo rm -rf testfiles tempdir

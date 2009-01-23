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

cd ../duplicity
./compilec.py
cd -

${SUDO} tar xzf testfiles.tar.gz

ARGS='-u -m trace --count --file=counts --ignore-dir=/usr/lib/python2.5'

${SUDO} rm -rf counts coverage
touch counts
mkdir coverage
for t in ${alltests}; do
    CMD="${SUDO} python ${ARGS} $t"
    echo "========== Running ${CMD} =========="
    ${CMD} 2>&1 | grep -v "unsafe ownership"
done

${SUDO} rm -rf testfiles tempdir temp2.tar

# Gen the coverage maps by file
python -m trace --report --missing --file=counts --coverdir=coverage

# This bit of renaming exposes the oddly named .cover files,
# at least on my system under Python 2.5.  If you're missing
# files, just do an 'ls -la coverage' and they appear.
cd coverage
rename 's/\.\.\.//g' ...*
rename 's/.home.ken.workspace.duplicity-src.//g' .home*
cd -

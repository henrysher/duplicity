#!/bin/bash

SUDO=sudo

cd `dirname $0`
pwd

cd ../duplicity
./compilec.py
cd -

${SUDO} tar xzf testfiles.tar.gz

ARGS=`python <<EOF
import sys
print "python -u -m trace --count --file=counts "
for p in sys.path:
    print "--ignore-dir=%s " % (p)
EOF`

${SUDO} rm -rf counts coverage
touch counts
mkdir coverage
for t in `cat alltests`; do
    CMD="${SUDO} ${ARGS} $t -v"
    echo "========== Running $t =========="
    ${CMD} 2>&1 | grep -v "unsafe ownership"
done

${SUDO} rm -rf testfiles tempdir temp2.tar

# Gen the coverage maps by file
python -m trace --report --missing --file=counts --coverdir=coverage

# This bit of renaming exposes the oddly named .cover files,
# at least on my system under Python 2.5.  If you're missing
# files, just do an 'ls -la coverage'.
cd coverage
rename 's/\.\.\.//g' ...*
rename 's/.home.ken.workspace.duplicity-src.//g' .home*
cd -

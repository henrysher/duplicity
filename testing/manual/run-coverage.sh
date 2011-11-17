#!/bin/bash
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
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

SUDO=sudo

cd `dirname $0`
pwd

cd ../duplicity
./compilec.py
cd -

#${SUDO} tar xzf testfiles.tar.gz

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

#${SUDO} rm -rf testfiles tempdir temp2.tar

# Gen the coverage maps by file
python -m trace --report --missing --file=counts --coverdir=coverage

# This bit of renaming exposes the oddly named .cover files,
# at least on my system under Python 2.5.  If you're missing
# files, just do an 'ls -la coverage'.
cd coverage
rename 's/\.\.\.//g' ...*
rename 's/.home.ken.workspace.duplicity-src.//g' .home*
cd -

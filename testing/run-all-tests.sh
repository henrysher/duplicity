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

# Check permissions
if [ "`id -ur`" != '0' ]; then
    echo 'Error: you must be root.'
    exit 1
fi

# run against all supported python versions
for v in 2.4 2.5 2.6 2.7; do
    if [ ! -e /usr/bin/python$v ]; then
        echo "python$v not found on system"
        continue
    fi

    # Go to directory housing this script
    cd `dirname $0`

    echo "========== Compiling librsync for python$v =========="
    pushd ../duplicity
    python$v ./compilec.py
    popd

    for t in `ls manual`; do
        echo "========== Running $t for python$v =========="
        pushd .
        python$v -u manual/$t -v 2>&1 | grep -v "unsafe ownership"
        popd
        echo "========== Finished $t for python$v =========="
        echo
        echo
    done
done

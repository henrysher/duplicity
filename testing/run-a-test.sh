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

# Go to directory housing this script
cd `dirname $0`

# skip if test does not exist
if [ ! -e $1 ]; then
    echo "No test named $1"
    exit 1
fi

# run against all supported python versions
for v in 2.4 2.5 2.6 2.7; do
    if [ ! -e /usr/bin/python$v ]; then
        echo "python$v not found on system"
        continue
    fi

    echo "========== Compiling librsync for python$v =========="
    pushd ../duplicity
    python$v ./compilec.py
    popd

    echo "========== Running $1 for python$v =========="
    pushd .
    if ! env TZ=US/Central LANG= PYTHONPATH=.. python$v -u $1 -v 2>&1; then
      echo "Test failed"
      exit 1
    fi
    popd
    echo "========== Finished $1 for python$v =========="
    echo
    echo
done

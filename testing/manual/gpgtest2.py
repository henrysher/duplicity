# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
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

import config
import os
import thread

from duplicity import GnuPGInterface

config.setup()

def main():
    gnupg = GnuPGInterface.GnuPG()
    gnupg.options.meta_interactive = 0
    gnupg.passphrase = "foobar"

    p1 = gnupg.run(['--symmetric'], create_fhs=['stdin', 'stdout'])

    if os.fork() == 0: # child
        p1.handles['stdin'].write("hello, world!")
        p1.handles['stdin'].close()
        os._exit(0)
    else: # parent
        p1.handles['stdin'].close()
        s = p1.handles['stdout'].read() #@UnusedVariable
        p1.handles['stdout'].close()
        p1.wait()


def main2():
    a = range(500000)
    thread.start_new_thread(tmp, (a,))
    tmp(a)

def tmp(a):
    for i in range(10): #@UnusedVariable
        for i in a: pass #@UnusedVariable


main2()

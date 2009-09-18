# -*- coding: utf-8 -*-
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2009 Plamen K. Kosseff <p.kosseff@gmail.com>
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

import os

par2_exeutable = None

def which (filename):
    result = None
    if not os.environ.has_key('PATH') or os.environ['PATH'] == '':
        p = os.defpath
    else:
        p = os.environ['PATH']

    pathlist = p.split(os.pathsep)

    for path in pathlist:
        f = os.path.join(path, filename)
        fexe = os.path.join(path, filename + ".exe")
        fbat = os.path.join(path, filename + ".bat")
        fcmd = os.path.join(path, filename + ".cmd")
        fcom = os.path.join(path, filename + ".com")
        if os.access(f, os.X_OK):
            result = f
        elif os.access(fexe, os.X_OK):
            result = fexe
        elif os.access(fbat, os.X_OK):
            result = fbat
        elif os.access(fcmd, os.X_OK):
            result = fcmd
        elif os.access(fcom, os.X_OK):
            result = fcom
    return result


def is_par2_supported():
    global par2_exeutable
    path = which("par2");
    if path:
        par2_exeutable = path
    return par2_exeutable <> None and par2_exeutable != ""


def create(par2_name, filename):
    global par2_exeutable
    if not par2_exeutable or par2_exeutable == "":
        is_par2_supported();
    if par2_exeutable and par2_exeutable != "":
        os.system("%s c -q -q -r20 -n1 %s %s" % (par2_exeutable, par2_name, filename))
        if not par2_name.endswith(".par2"):
            os.rename(par2_name + ".par2", par2_name)
        par2_filename = os.path.basename(par2_name).partition(".par2")[0]
        path = os.path.abspath(os.path.dirname(par2_name))
        flist = filter(lambda item : item.endswith(".par2") and item.startswith(par2_filename), os.listdir(path))
        for i in flist:
            yield path, str(i)

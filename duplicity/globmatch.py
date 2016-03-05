# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2014 Aaron Whitehouse <aaron@whitehouse.kiwi.nz>
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

import re


class GlobbingError(Exception):
    """Something has gone wrong when parsing a glob string"""
    pass


class FilePrefixError(GlobbingError):
    """Signals that a specified file doesn't start with correct prefix"""
    pass


def glob_get_prefix_regexs(glob_str):
    """Return list of regexps equivalent to prefixes of glob_str"""
    # Internal. Used by glob_get_normal_sf.
    glob_parts = glob_str.split("/")
    if "" in glob_parts[1:-1]:
        # "" OK if comes first or last, as in /foo/
        raise GlobbingError("Consecutive '/'s found in globbing string "
                            + glob_str)

    prefixes = ["/".join(glob_parts[:i + 1]) for i in range(len(glob_parts))]
    # we must make exception for root "/", only dir to end in slash
    if prefixes[0] == "":
        prefixes[0] = "/"
    return map(glob_to_regex, prefixes)


def glob_to_regex(pat):
    """Returned regular expression equivalent to shell glob pat

    Currently only the ?, *, [], and ** expressions are supported.
    Ranges like [a-z] are also currently unsupported.  There is no
    way to quote these special characters.

    This function taken with minor modifications from efnmatch.py
    by Donovan Baarda.

    """
    # Internal. Used by glob_get_normal_sf, glob_get_prefix_res and unit tests.
    i, n, res = 0, len(pat), ''
    while i < n:
        c, s = pat[i], pat[i:i + 2]
        i = i + 1
        if s == '**':
            res = res + '.*'
            i = i + 1
        elif c == '*':
            res = res + '[^/]*'
        elif c == '?':
            res = res + '[^/]'
        elif c == '[':
            j = i
            if j < n and pat[j] in '!^':
                j = j + 1
            if j < n and pat[j] == ']':
                j = j + 1
            while j < n and pat[j] != ']':
                j = j + 1
            if j >= n:
                res = res + '\\['  # interpret the [ literally
            else:
                # Deal with inside of [..]
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] in '!^':
                    stuff = '^' + stuff[1:]
                res = res + '[' + stuff + ']'
        else:
            res = res + re.escape(c)
    return res

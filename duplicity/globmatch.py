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


def _glob_get_prefix_regexs(glob_str):
    """Return list of regexps equivalent to prefixes of glob_str"""
    # Internal. Used by glob_get_normal_sf.
    glob_parts = glob_str.split("/")
    if "" in glob_parts[1:-1]:
        # "" OK if comes first or last, as in /foo/
        raise GlobbingError("Consecutive '/'s found in globbing string " +
                            glob_str)

    prefixes = ["/".join(glob_parts[:i + 1]) for i in range(len(glob_parts))]
    # we must make exception for root "/", only dir to end in slash
    if prefixes[0] == "":
        prefixes[0] = "/"
    return list(map(glob_to_regex, prefixes))


def path_matches_glob_fn(glob_str, include, ignore_case=False):
    """Return a function test_fn(path) which
    tests whether path matches glob, as per the Unix shell rules, taking as
    arguments a path, a glob string and include (0 indicating that the glob
    string is an exclude glob and 1 indicating that it is an include glob,
    returning:
    0 - if the file should be excluded
    1 - if the file should be included
    2 - if the folder should be scanned for any included/excluded files
    None - if the selection function has nothing to say about the file
    """
    glob_ends_w_slash = False

    if glob_str != "/" and glob_str[-1] == "/":
        glob_ends_w_slash = True
        # Remove trailing / from directory name (unless that is the entire
        # string)
        glob_str = glob_str[:-1]

    flags = 0
    if ignore_case:
        flags = re.IGNORECASE

    re_comp = lambda r: re.compile(r, re.S | flags)

    # matches what glob matches and any files in directory
    # Resulting regular expression is:
    # ^ string must be at the beginning of path
    # string translated into regex
    # ($|/) nothing must follow except for the end of the string, newline or /
    # Note that the "/" at the end of the regex means that it will match
    # if the glob matches a parent folders of path
    glob_comp_re = re_comp("^%s($|/)" % glob_to_regex(glob_str))

    if glob_ends_w_slash:
        # Creates a version of glob_comp_re that does not match folder contents
        # This can be used later to check that an exact match is actually a
        # folder, rather than a file.
        glob_comp_re_exact = re_comp("^%s($)" % glob_to_regex(glob_str))

    if glob_str.find("**") != -1:
        # glob_str has a ** in it
        glob_str = glob_str[:glob_str.find("**") + 2]  # truncate after **

    # Below regex is translates to:
    # ^ string must be at the beginning of path
    # the regexs corresponding to the parent directories of glob_str
    # $ nothing must follow except for the end of the string or newline
    scan_comp_re = re_comp("^(%s)$" %
                           "|".join(_glob_get_prefix_regexs(glob_str)))

    def test_fn(path):
        if glob_comp_re.match(path.name):
            # Path matches glob, or is contained within a matching folder
            if not glob_ends_w_slash:
                return include
            else:
                # Glob ended with a /, so we need to check any exact match was
                # a folder
                if glob_comp_re_exact.match(path.name):
                    # Not an included file/folder, so must be a folder to match
                    if path.isdir():
                        # Is a directory, so all is well
                        return include
                    else:
                        # Exact match and not a folder
                        return None
                else:
                    # An included file/folder, so normal approach is fine
                    return include

        elif include == 1 and scan_comp_re.match(path.name):
            return 2
        else:
            return None

    return test_fn


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

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

"""Produce and parse the names of duplicity's backup files"""

import re
from duplicity import dup_time
from duplicity import globals

full_vol_re = None
full_vol_re_short = None
full_manifest_re = None
full_manifest_re_short = None
inc_vol_re = None
inc_vol_re_short = None
inc_manifest_re = None
inc_manifest_re_short = None
full_sig_re = None
full_sig_re_short = None
new_sig_re = None
new_sig_re_short = None

def prepare_regex():
    global full_vol_re
    global full_vol_re_short
    global full_manifest_re
    global full_manifest_re_short
    global inc_vol_re
    global inc_vol_re_short
    global inc_manifest_re
    global inc_manifest_re_short
    global full_sig_re
    global full_sig_re_short
    global new_sig_re
    global new_sig_re_short

    if full_vol_re:
        return

    full_vol_re = re.compile("^" + globals.file_prefix + "duplicity-full"
                         "\\.(?P<time>.*?)"
                         "\\.vol(?P<num>[0-9]+)"
                         "\\.difftar"
                         "(?P<partial>(\\.part))?"
                         "($|\\.)")

    full_vol_re_short = re.compile("^" + globals.file_prefix + "df"
                               "\\.(?P<time>[0-9a-z]+?)"
                               "\\.(?P<num>[0-9a-z]+)"
                               "\\.dt"
                               "(?P<partial>(\\.p))?"
                               "($|\\.)")

    full_manifest_re = re.compile("^" + globals.file_prefix + "duplicity-full"
                              "\\.(?P<time>.*?)"
                              "\\.manifest"
                              "(?P<partial>(\\.part))?"
                              "($|\\.)")

    full_manifest_re_short = re.compile("^" + globals.file_prefix + "df"
                                    "\\.(?P<time>[0-9a-z]+?)"
                                    "\\.m"
                                    "(?P<partial>(\\.p))?"
                                    "($|\\.)")

    inc_vol_re = re.compile("^" + globals.file_prefix + "duplicity-inc"
                        "\\.(?P<start_time>.*?)"
                        "\\.to\\.(?P<end_time>.*?)"
                        "\\.vol(?P<num>[0-9]+)"
                        "\\.difftar"
                        "($|\\.)")

    inc_vol_re_short = re.compile("^" + globals.file_prefix + "di"
                              "\\.(?P<start_time>[0-9a-z]+?)"
                              "\\.(?P<end_time>[0-9a-z]+?)"
                              "\\.(?P<num>[0-9a-z]+)"
                              "\\.dt"
                              "($|\\.)")

    inc_manifest_re = re.compile("^" + globals.file_prefix + "duplicity-inc"
                             "\\.(?P<start_time>.*?)"
                             "\\.to"
                             "\\.(?P<end_time>.*?)"
                             "\\.manifest"
                             "(?P<partial>(\\.part))?"
                             "(\\.|$)")

    inc_manifest_re_short = re.compile("^" + globals.file_prefix + "di"
                                   "\\.(?P<start_time>[0-9a-z]+?)"
                                   "\\.(?P<end_time>[0-9a-z]+?)"
                                   "\\.m"
                                   "(?P<partial>(\\.p))?"
                                   "(\\.|$)")

    full_sig_re = re.compile("^" + globals.file_prefix + "duplicity-full-signatures"
                         "\\.(?P<time>.*?)"
                         "\\.sigtar"
                         "(?P<partial>(\\.part))?"
                         "(\\.|$)")

    full_sig_re_short = re.compile("^" + globals.file_prefix + "dfs"
                               "\\.(?P<time>[0-9a-z]+?)"
                               "\\.st"
                               "(?P<partial>(\\.p))?"
                               "(\\.|$)")

    new_sig_re = re.compile("^" + globals.file_prefix + "duplicity-new-signatures"
                        "\\.(?P<start_time>.*?)"
                        "\\.to"
                        "\\.(?P<end_time>.*?)"
                        "\\.sigtar"
                        "(?P<partial>(\\.part))?"
                        "(\\.|$)")

    new_sig_re_short = re.compile("^" + globals.file_prefix + "dns"
                              "\\.(?P<start_time>[0-9a-z]+?)"
                              "\\.(?P<end_time>[0-9a-z]+?)"
                              "\\.st"
                              "(?P<partial>(\\.p))?"
                              "(\\.|$)")


def to_base36(n):
    """
    Return string representation of n in base 36 (use 0-9 and a-z)
    """
    div, mod = divmod(n, 36)
    if mod <= 9:
        last_digit = str(mod)
    else:
        last_digit = chr(ord('a') + mod - 10)
    if n == mod:
        return last_digit
    else:
        return to_base36(div)+last_digit


def from_base36(s):
    """
    Convert string s in base 36 to long int
    """
    total = 0L
    for i in range(len(s)):
        total *= 36
        digit_ord = ord(s[i])
        if ord('0') <= digit_ord <= ord('9'):
            total += digit_ord - ord('0')
        elif ord('a') <= digit_ord <= ord('z'):
            total += digit_ord - ord('a') + 10
        else:
            assert 0, "Digit %s in %s not in proper range" % (s[i], s)
    return total


def get_suffix(encrypted, gzipped):
    """
    Return appropriate suffix depending on status of
    encryption, compression, and short_filenames.
    """
    if encrypted:
        gzipped = False
    if encrypted:
        if globals.short_filenames:
            suffix = '.g'
        else:
            suffix = ".gpg"
    elif gzipped:
        if globals.short_filenames:
            suffix = ".z"
        else:
            suffix = '.gz'
    else:
        suffix = ""
    return suffix


def get(type, volume_number = None, manifest = False,
        encrypted = False, gzipped = False, partial = False):
    """
    Return duplicity filename of specified type

    type can be "full", "inc", "full-sig", or "new-sig". volume_number
    can be given with the full and inc types.  If manifest is true the
    filename is of a full or inc manifest file.
    """
    assert dup_time.curtimestr
    if encrypted:
        gzipped = False
    suffix = get_suffix(encrypted, gzipped)
    part_string = ""
    if globals.short_filenames:
        if partial:
            part_string = ".p"
    else:
        if partial:
            part_string = ".part"

    if type == "full-sig" or type == "new-sig":
        assert not volume_number and not manifest
        assert not (volume_number and part_string)
        if type == "full-sig":
            if globals.short_filenames:
                return ("dfs.%s.st%s%s" %
                        (to_base36(dup_time.curtime), part_string, suffix))
            else:
                return ("duplicity-full-signatures.%s.sigtar%s%s" %
                        (dup_time.curtimestr, part_string, suffix))
        elif type == "new-sig":
            if globals.short_filenames:
                return ("dns.%s.%s.st%s%s" %
                        (to_base36(dup_time.prevtime), to_base36(dup_time.curtime),
                         part_string, suffix))
            else:
                return ("duplicity-new-signatures.%s.to.%s.sigtar%s%s" %
                        (dup_time.prevtimestr, dup_time.curtimestr,
                         part_string, suffix))
    else:
        assert volume_number or manifest
        assert not (volume_number and manifest)
        if volume_number:
            if globals.short_filenames:
                vol_string = "%s.dt" % to_base36(volume_number)
            else:
                vol_string = "vol%d.difftar" % volume_number
        else:
            if globals.short_filenames:
                vol_string = "m"
            else:
                vol_string = "manifest"
        if type == "full":
            if globals.short_filenames:
                return ("df.%s.%s%s%s" % (to_base36(dup_time.curtime),
                                          vol_string, part_string, suffix))
            else:
                return ("duplicity-full.%s.%s%s%s" % (dup_time.curtimestr,
                                                      vol_string, part_string, suffix))
        elif type == "inc":
            if globals.short_filenames:
                return ("di.%s.%s.%s%s%s" % (to_base36(dup_time.prevtime),
                                             to_base36(dup_time.curtime),
                                             vol_string, part_string, suffix))
            else:
                return ("duplicity-inc.%s.to.%s.%s%s%s" % (dup_time.prevtimestr,
                                                           dup_time.curtimestr,
                                                           vol_string, part_string, suffix))
        else:
            assert 0


def parse(filename):
    """
    Parse duplicity filename, return None or ParseResults object
    """
    filename = filename.lower()
    def str2time(timestr, short):
        """
        Return time in seconds if string can be converted, None otherwise
        """
        if short:
            t = from_base36(timestr)
        else:
            try:
                t = dup_time.genstrtotime(timestr.upper())
            except dup_time.TimeException:
                return None
        return t

    def get_vol_num(s, short):
        """
        Return volume number from volume number string
        """
        if short:
            return from_base36(s)
        else:
            return int(s)

    def check_full():
        """
        Return ParseResults if file is from full backup, None otherwise
        """
        prepare_regex()
        short = True
        m1 = full_vol_re_short.search(filename)
        m2 = full_manifest_re_short.search(filename)
        if not m1 and not m2 and not globals.short_filenames:
            short = False
            m1 = full_vol_re.search(filename)
            m2 = full_manifest_re.search(filename)
        if m1 or m2:
            t = str2time((m1 or m2).group("time"), short)
            if t:
                if m1:
                    return ParseResults("full", time = t,
                                        volume_number = get_vol_num(m1.group("num"), short))
                else:
                    return ParseResults("full", time = t, manifest = True,
                                        partial = (m2.group("partial") != None))
        return None

    def check_inc():
        """
        Return ParseResults if file is from inc backup, None otherwise
        """
        prepare_regex()
        short = True
        m1 = inc_vol_re_short.search(filename)
        m2 = inc_manifest_re_short.search(filename)
        if not m1 and not m2 and not globals.short_filenames:
            short = False
            m1 = inc_vol_re.search(filename)
            m2 = inc_manifest_re.search(filename)
        if m1 or m2:
            t1 = str2time((m1 or m2).group("start_time"), short)
            t2 = str2time((m1 or m2).group("end_time"), short)
            if t1 and t2:
                if m1:
                    return ParseResults("inc", start_time = t1,
                                        end_time = t2, volume_number = get_vol_num(m1.group("num"), short))
                else:
                    return ParseResults("inc", start_time = t1, end_time = t2, manifest = 1,
                                        partial = (m2.group("partial") != None))
        return None

    def check_sig():
        """
        Return ParseResults if file is a signature, None otherwise
        """
        prepare_regex()
        short = True
        m = full_sig_re_short.search(filename)
        if not m and not globals.short_filenames:
            short = False
            m = full_sig_re.search(filename)
        if m:
            t = str2time(m.group("time"), short)
            if t:
                return ParseResults("full-sig", time = t,
                                    partial = (m.group("partial") != None))
            else:
                return None

        short = True
        m = new_sig_re_short.search(filename)
        if not m and not globals.short_filenames:
            short = False
            m = new_sig_re.search(filename)
        if m:
            t1 = str2time(m.group("start_time"), short)
            t2 = str2time(m.group("end_time"), short)
            if t1 and t2:
                return ParseResults("new-sig", start_time = t1, end_time = t2,
                                    partial = (m.group("partial") != None))
        return None

    def set_encryption_or_compression(pr):
        """
        Set encryption and compression flags in ParseResults pr
        """
        if (filename.endswith('.z') or
            not globals.short_filenames and filename.endswith('gz')):
            pr.compressed = 1
        else:
            pr.compressed = None

        if (filename.endswith('.g') or
            not globals.short_filenames and filename.endswith('.gpg')):
            pr.encrypted = 1
        else:
            pr.encrypted = None

    pr = check_full()
    if not pr:
        pr = check_inc()
        if not pr:
            pr = check_sig()
            if not pr:
                return None
    set_encryption_or_compression(pr)
    return pr


class ParseResults:
    """
    Hold information taken from a duplicity filename
    """
    def __init__(self, type, manifest = None, volume_number = None,
                 time = None, start_time = None, end_time = None,
                 encrypted = None, compressed = None, partial = False):

        assert type in ["full-sig", "new-sig", "inc", "full"]

        self.type = type
        if type == "inc" or type == "full":
            assert manifest or volume_number
        if type == "inc" or type == "new-sig":
            assert start_time and end_time
        else:
            assert time

        self.manifest = manifest
        self.volume_number = volume_number
        self.time = time
        self.start_time, self.end_time = start_time, end_time

        self.compressed = compressed # true if gzip compressed
        self.encrypted = encrypted # true if gpg encrypted

        self.partial = partial

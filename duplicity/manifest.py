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

"""Create and edit manifest for session contents"""

import re

from duplicity import log
from duplicity import globals
from duplicity import util

class ManifestError(Exception):
    """
    Exception raised when problem with manifest
    """
    pass


class Manifest:
    """
    List of volumes and information about each one
    """
    def __init__(self, fh = None):
        """
        Create blank Manifest

        @param fh: fileobj for manifest
        @type fh: DupPath

        @rtype: Manifest
        @return: manifest
        """
        self.hostname = None
        self.local_dirname = None
        self.volume_info_dict = {} # dictionary vol numbers -> vol infos
        self.fh = fh

    def set_dirinfo(self):
        """
        Set information about directory from globals,
        and write to manifest file.

        @rtype: Manifest
        @return: manifest
        """
        self.hostname = globals.hostname
        self.local_dirname = globals.local_path.name #@UndefinedVariable
        if self.fh:
            if self.hostname:
                self.fh.write("Hostname %s\n" % self.hostname)
            if self.local_dirname:
                self.fh.write("Localdir %s\n" % Quote(self.local_dirname))
        return self

    def check_dirinfo(self):
        """
        Return None if dirinfo is the same, otherwise error message

        Does not raise an error message if hostname or local_dirname
        are not available.

        @rtype: string
        @return: None or error message
        """
        if globals.allow_source_mismatch:
            return

        if self.hostname and self.hostname != globals.hostname:
            errmsg = _("Fatal Error: Backup source host has changed.\n"
                       "Current hostname: %s\n"
                       "Previous hostname: %s") % (globals.hostname, self.hostname)
            code = log.ErrorCode.hostname_mismatch
            code_extra = "%s %s" % (util.escape(globals.hostname), util.escape(self.hostname))

        elif (self.local_dirname and self.local_dirname != globals.local_path.name): #@UndefinedVariable
            errmsg = _("Fatal Error: Backup source directory has changed.\n"
                       "Current directory: %s\n"
                       "Previous directory: %s") % (globals.local_path.name, self.local_dirname) #@UndefinedVariable
            code = log.ErrorCode.source_dir_mismatch
            code_extra = "%s %s" % (util.escape(globals.local_path.name), util.escape(self.local_dirname)) #@UndefinedVariable
        else:
            return

        log.FatalError(errmsg + "\n\n" +
                       _("Aborting because you may have accidentally tried to "
                         "backup two different data sets to the same remote "
                         "location, or using the same archive directory.  If "
                         "this is not a mistake, use the "
                         "--allow-source-mismatch switch to avoid seeing this "
                         "message"), code, code_extra)

    def add_volume_info(self, vi):
        """
        Add volume info vi to manifest and write to manifest

        @param vi: volume info to add
        @type vi: VolumeInfo

        @return: void
        """
        vol_num = vi.volume_number
        self.volume_info_dict[vol_num] = vi
        if self.fh:
            self.fh.write(vi.to_string() + "\n")

    def del_volume_info(self, vol_num):
        """
        Remove volume vol_num from the manifest

        @param vol_num: volume number to delete
        @type vi: int

        @return: void
        """
        try:
            del self.volume_info_dict[vol_num]
        except Exception:
            raise ManifestError("Volume %d not present in manifest" % (vol_num,))

    def to_string(self):
        """
        Return string version of self (just concatenate vi strings)

        @rtype: string
        @return: self in string form
        """
        result = ""
        if self.hostname:
            result += "Hostname %s\n" % self.hostname
        if self.local_dirname:
            result += "Localdir %s\n" % Quote(self.local_dirname)

        vol_num_list = self.volume_info_dict.keys()
        vol_num_list.sort()
        def vol_num_to_string(vol_num):
            return self.volume_info_dict[vol_num].to_string()
        result = "%s%s\n" % (result,
                             "\n".join(map(vol_num_to_string, vol_num_list)))
        return result

    __str__ = to_string

    def from_string(self, s):
        """
        Initialize self from string s, return self
        """
        def get_field(fieldname):
            """
            Return the value of a field by parsing s, or None if no field
            """
            m = re.search("(^|\\n)%s\\s(.*?)\n" % fieldname, s, re.I)
            if not m:
                return None
            else:
                return Unquote(m.group(2))
        self.hostname = get_field("hostname")
        self.local_dirname = get_field("localdir")

        next_vi_string_regexp = re.compile("(^|\\n)(volume\\s.*?)"
                                           "(\\nvolume\\s|$)", re.I | re.S)
        starting_s_index = 0
        highest_vol = 0
        latest_vol = 0
        while 1:
            match = next_vi_string_regexp.search(s[starting_s_index:])
            if not match:
                break
            vi = VolumeInfo().from_string(match.group(2))
            self.add_volume_info(vi)
            highest_vol = max(highest_vol, vi.volume_number)
            latest_vol = vi.volume_number
            starting_s_index += match.end(2)
        # If we restarted after losing some remote volumes, the highest volume
        # seen may be higher than the last volume recorded.  That is, the
        # manifest could contain "vol1, vol2, vol3, vol2."  If so, we don't
        # want to keep vol3's info.
        for i in range(latest_vol + 1, highest_vol + 1):
            self.del_volume_info(i)
        return self

    def __eq__(self, other):
        """
        Two manifests are equal if they contain the same volume infos
        """
        vi_list1 = self.volume_info_dict.keys()
        vi_list1.sort()
        vi_list2 = other.volume_info_dict.keys()
        vi_list2.sort()

        if vi_list1 != vi_list2:
            log.Notice(_("Manifests not equal because different volume numbers"))
            return False

        for i in range(len(vi_list1)):
            if not vi_list1[i] == vi_list2[i]:
                log.Notice(_("Manifests not equal because volume lists differ"))
                return False

        if (self.hostname != other.hostname or
            self.local_dirname != other.local_dirname):
            log.Notice(_("Manifests not equal because hosts or directories differ"))
            return False

        return True

    def __ne__(self, other):
        """
        Defines !=.  Not doing this always leads to annoying bugs...
        """
        return not self.__eq__(other)

    def write_to_path(self, path):
        """
        Write string version of manifest to given path
        """
        assert not path.exists()
        fout = path.open("wb")
        fout.write(self.to_string())
        assert not fout.close()
        path.setdata()

    def get_containing_volumes(self, index_prefix):
        """
        Return list of volume numbers that may contain index_prefix
        """
        return filter(lambda vol_num:
                      self.volume_info_dict[vol_num].contains(index_prefix),
                      self.volume_info_dict.keys())


class VolumeInfoError(Exception):
    """
    Raised when there is a problem initializing a VolumeInfo from string
    """
    pass


class VolumeInfo:
    """
    Information about a single volume
    """
    def __init__(self):
        """VolumeInfo initializer"""
        self.volume_number = None
        self.start_index = None
        self.start_block = None
        self.end_index = None
        self.end_block = None
        self.hashes = {}

    def set_info(self, vol_number,
                 start_index, start_block,
                 end_index, end_block):
        """
        Set essential VolumeInfo information, return self

        Call with starting and ending paths stored in the volume.  If
        a multivol diff gets split between volumes, count it as being
        part of both volumes.
        """
        self.volume_number = vol_number
        self.start_index = start_index
        self.start_block = start_block
        self.end_index = end_index
        self.end_block = end_block

        return self

    def set_hash(self, hash_name, data):
        """
        Set the value of hash hash_name (e.g. "MD5") to data
        """
        self.hashes[hash_name] = data

    def get_best_hash(self):
        """
        Return pair (hash_type, hash_data)

        SHA1 is the best hash, and MD5 is the second best hash.  None
        is returned if no hash is available.
        """
        if not self.hashes:
            return None
        try:
            return ("SHA1", self.hashes['SHA1'])
        except KeyError:
            pass
        try:
            return ("MD5", self.hashes['MD5'])
        except KeyError:
            pass
        return self.hashes.items()[0]

    def to_string(self):
        """
        Return nicely formatted string reporting all information
        """
        def index_to_string(index):
            """Return printable version of index without any whitespace"""
            if index:
                s = "/".join(index)
                return Quote(s)
            else:
                return "."

        slist = ["Volume %d:" % self.volume_number]
        whitespace = "    "
        slist.append("%sStartingPath   %s %s" %
                     (whitespace, index_to_string(self.start_index), (self.start_block or " ")))
        slist.append("%sEndingPath     %s %s" %
                     (whitespace, index_to_string(self.end_index), (self.end_block or " ")))
        for key in self.hashes:
            slist.append("%sHash %s %s" %
                         (whitespace, key, self.hashes[key]))
        return "\n".join(slist)

    __str__ = to_string

    def from_string(self, s):
        """
        Initialize self from string s as created by to_string
        """
        def string_to_index(s):
            """
            Return tuple index from string
            """
            s = Unquote(s)
            if s == ".":
                return ()
            return tuple(s.split("/"))

        linelist = s.strip().split("\n")

        # Set volume number
        m = re.search("^Volume ([0-9]+):", linelist[0], re.I)
        if not m:
            raise VolumeInfoError("Bad first line '%s'" % (linelist[0],))
        self.volume_number = int(m.group(1))

        # Set other fields
        for line in linelist[1:]:
            if not line:
                continue
            line_split = line.strip().split()
            field_name = line_split[0].lower()
            other_fields = line_split[1:]
            if field_name == "Volume":
                log.Warn(_("Warning, found extra Volume identifier"))
                break
            elif field_name == "startingpath":
                self.start_index = string_to_index(other_fields[0])
                if len(other_fields) > 1:
                    self.start_block = int(other_fields[1])
                else:
                    self.start_block = None
            elif field_name == "endingpath":
                self.end_index = string_to_index(other_fields[0])
                if len(other_fields) > 1:
                    self.end_block = int(other_fields[1])
                else:
                    self.end_block = None
            elif field_name == "hash":
                self.set_hash(other_fields[0], other_fields[1])

        if self.start_index is None or self.end_index is None:
            raise VolumeInfoError("Start or end index not set")
        return self

    def __eq__(self, other):
        """
        Used in test suite
        """
        if not isinstance(other, VolumeInfo):
            log.Notice(_("Other is not VolumeInfo"))
            return None
        if self.volume_number != other.volume_number:
            log.Notice(_("Volume numbers don't match"))
            return None
        if self.start_index != other.start_index:
            log.Notice(_("start_indicies don't match"))
            return None
        if self.end_index != other.end_index:
            log.Notice(_("end_index don't match"))
            return None
        hash_list1 = self.hashes.items()
        hash_list1.sort()
        hash_list2 = other.hashes.items()
        hash_list2.sort()
        if hash_list1 != hash_list2:
            log.Notice(_("Hashes don't match"))
            return None
        return 1

    def __ne__(self, other):
        """
        Defines !=
        """
        return not self.__eq__(other)

    def contains(self, index_prefix, recursive = 1):
        """
        Return true if volume might contain index

        If recursive is true, then return true if any index starting
        with index_prefix could be contained.  Otherwise, just check
        if index_prefix itself is between starting and ending
        indicies.
        """
        if recursive:
            return (self.start_index[:len(index_prefix)] <=
                    index_prefix <= self.end_index)
        else:
            return self.start_index <= index_prefix <= self.end_index


nonnormal_char_re = re.compile("(\\s|[\\\\\"'])")
def Quote(s):
    """
    Return quoted version of s safe to put in a manifest or volume info
    """
    if not nonnormal_char_re.search(s):
        return s # no quoting necessary
    slist = []
    for char in s:
        if nonnormal_char_re.search(char):
            slist.append("\\x%02x" % ord(char))
        else:
            slist.append(char)
    return '"%s"' % "".join(slist)


def Unquote(quoted_string):
    """
    Return original string from quoted_string produced by above
    """
    if not quoted_string[0] == '"' or quoted_string[0] == "'":
        return quoted_string
    assert quoted_string[0] == quoted_string[-1]
    return_list = []
    i = 1 # skip initial char
    while i < len(quoted_string)-1:
        char = quoted_string[i]
        if char == "\\":
            # quoted section
            assert quoted_string[i+1] == "x"
            return_list.append(chr(int(quoted_string[i+2:i+4], 16)))
            i += 4
        else:
            return_list.append(char)
            i += 1
    return "".join(return_list)

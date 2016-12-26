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

from future_builtins import filter, map

import os  # @UnusedImport
import stat  # @UnusedImport
import sys
import re

from duplicity.path import *  # @UnusedWildImport
from duplicity import log  # @Reimport
from duplicity import globals  # @Reimport
from duplicity import diffdir
from duplicity import util  # @Reimport
from duplicity.globmatch import GlobbingError, FilePrefixError, \
    path_matches_glob_fn

"""Iterate exactly the requested files in a directory

Parses includes and excludes to yield correct files.  More
documentation on what this code does can be found on the man page.

"""


class SelectError(Exception):
    """Some error dealing with the Select class"""
    pass


class Select:
    """Iterate appropriate Paths in given directory

    This class acts as an iterator on account of its next() method.
    Basically, it just goes through all the files in a directory in
    order (depth-first) and subjects each file to a bunch of tests
    (selection functions) in order.  The first test that includes or
    excludes the file means that the file gets included (iterated) or
    excluded.  The default is include, so with no tests we would just
    iterate all the files in the directory in order.

    The one complication to this is that sometimes we don't know
    whether or not to include a directory until we examine its
    contents.  For instance, if we want to include all the **.py
    files.  If /home/ben/foo.py exists, we should also include /home
    and /home/ben, but if these directories contain no **.py files,
    they shouldn't be included.  For this reason, a test may not
    include or exclude a directory, but merely "scan" it.  If later a
    file in the directory gets included, so does the directory.

    As mentioned above, each test takes the form of a selection
    function.  The selection function takes a path, and returns:

    None - means the test has nothing to say about the related file
    0 - the file is excluded by the test
    1 - the file is included
    2 - the test says the file (must be directory) should be scanned

    Also, a selection function f has a variable f.exclude which should
    be true iff f could potentially exclude some file.  This is used
    to signal an error if the last function only includes, which would
    be redundant and presumably isn't what the user intends.

    """
    # This re should not match normal filenames, but usually just globs
    glob_re = re.compile("(.*[*?[]|ignorecase\\:)", re.I | re.S)

    def __init__(self, path):
        """Initializer, called with Path of root directory"""
        assert isinstance(path, Path), str(path)
        self.selection_functions = []
        self.rootpath = path
        self.prefix = self.rootpath.name

    def set_iter(self):
        """Initialize generator, prepare to iterate."""
        # Externally-accessed method
        self.rootpath.setdata()  # this may have changed since Select init
        self.iter = self.Iterate(self.rootpath)
        self.next = self.iter.next
        self.__iter__ = lambda: self
        return self

    def Iterate(self, path):
        """Return iterator yielding paths in path

        This function looks a bit more complicated than it needs to be
        because it avoids extra recursion (and no extra function calls
        for non-directory files) while still doing the "directory
        scanning" bit.

        """
        # Only called by set_iter. Internal.
        def error_handler(exc, path, filename):
            fullpath = os.path.join(path.name, filename)
            try:
                mode = os.stat(fullpath)[stat.ST_MODE]
                if stat.S_ISSOCK(mode):
                    log.Info(_("Skipping socket %s") % util.ufn(fullpath),
                             log.InfoCode.skipping_socket,
                             util.escape(fullpath))
                else:
                    log.Warn(_("Error initializing file %s") % util.ufn(fullpath),
                             log.WarningCode.cannot_iterate,
                             util.escape(fullpath))
            except OSError:
                log.Warn(_("Error accessing possibly locked file %s") % util.ufn(fullpath),
                         log.WarningCode.cannot_stat, util.escape(fullpath))
            return None

        def diryield(path):
            """Generate relevant files in directory path

            Returns (path, num) where num == 0 means path should be
            generated normally, num == 1 means the path is a directory
            and should be included iff something inside is included.

            """
            # Only called by Iterate. Internal.
            # todo: get around circular dependency issue by importing here
            from duplicity import robust  # @Reimport
            for filename in robust.listpath(path):
                new_path = robust.check_common_error(
                    error_handler, Path.append, (path, filename))
                if new_path:
                    s = self.Select(new_path)
                    if (new_path.type in ["reg", "dir"] and
                        not os.access(new_path.name, os.R_OK)) and \
                            (s == 1 or s == 2):
                        # Path is a file or folder that cannot be read, but
                        # should be included or scanned.
                        log.Warn(_("Error accessing possibly locked file %s") %
                                 util.ufn(new_path.name),
                                 log.WarningCode.cannot_read,
                                 util.escape(new_path.name))
                        if diffdir.stats:
                            diffdir.stats.Errors += 1
                    elif s == 1:
                        # Should be included
                        yield (new_path, 0)
                    elif s == 2 and new_path.isdir():
                        # Is a directory that should be scanned
                        yield (new_path, 1)

        if not path.type:
            # base doesn't exist
            log.Warn(_("Warning: base %s doesn't exist, continuing") %
                     util.ufn(path.name))
            return
        log.Debug(_("Selecting %s") % util.ufn(path.name))
        yield path
        if not path.isdir():
            return
        diryield_stack = [diryield(path)]
        delayed_path_stack = []

        while diryield_stack:
            try:
                subpath, val = diryield_stack[-1].next()
            except StopIteration:
                diryield_stack.pop()
                if delayed_path_stack:
                    delayed_path_stack.pop()
                continue
            if val == 0:
                if delayed_path_stack:
                    for delayed_path in delayed_path_stack:
                        log.Log(_("Selecting %s") % util.ufn(delayed_path.name), 6)
                        yield delayed_path
                    del delayed_path_stack[:]
                log.Debug(_("Selecting %s") % util.ufn(subpath.name))
                yield subpath
                if subpath.isdir():
                    diryield_stack.append(diryield(subpath))
            elif val == 1:
                delayed_path_stack.append(subpath)
                diryield_stack.append(diryield(subpath))

    def Select(self, path):
        """Run through the selection functions and return dominant val 0/1/2"""
        # Only used by diryield and tests. Internal.
        log.Debug("Selection: examining path %s" % util.ufn(path.name))
        if not self.selection_functions:
            log.Debug("Selection:     + no selection functions found. Including")
            return 1
        scan_pending = False
        for sf in self.selection_functions:
            result = sf(path)
            log.Debug("Selection:     result: %4s from function: %s" %
                      (str(result), sf.name))
            if result is 2:
                # Selection function says that the path should be scanned for matching files, but keep going
                # through the selection functions looking for a real match (0 or 1).
                scan_pending = True
            elif result == 0 or result == 1:
                # A real match found, no need to try other functions.
                break

        if scan_pending and result != 1:
            # A selection function returned 2 and either no real match was
            # found or the highest-priority match was 0
            result = 2
        if result is None:
            result = 1

        if result == 0:
            log.Debug("Selection:     - excluding file")
        elif result == 1:
            log.Debug("Selection:     + including file")
        else:
            assert result == 2
            log.Debug("Selection:     ? scanning directory for matches")

        return result

    def ParseArgs(self, argtuples, filelists):
        """Create selection functions based on list of tuples

        The tuples are created when the initial commandline arguments
        are read.  They have the form (option string, additional
        argument) except for the filelist tuples, which should be
        (option-string, (additional argument, filelist_fp)).

        """
        # Called by commandline.py set_selection. External.
        filelists_index = 0
        try:
            for opt, arg in argtuples:
                if opt == "--exclude":
                    self.add_selection_func(self.glob_get_sf(arg, 0))
                elif opt == "--exclude-if-present":
                    self.add_selection_func(self.present_get_sf(arg, 0))
                elif opt == "--exclude-device-files":
                    self.add_selection_func(self.devfiles_get_sf())
                elif (opt == "--exclude-filelist") or (opt == "--exclude-globbing-filelist"):
                    # --exclude-globbing-filelist is now deprecated, as all filelists are globbing
                    # but keep this here for the short term for backwards-compatibility
                    for sf in self.filelist_globbing_get_sfs(filelists[filelists_index], 0, arg):
                        self.add_selection_func(sf)
                    filelists_index += 1
                elif opt == "--exclude-other-filesystems":
                    self.add_selection_func(self.other_filesystems_get_sf(0))
                elif opt == "--exclude-regexp":
                    self.add_selection_func(self.regexp_get_sf(arg, 0))
                elif opt == "--exclude-older-than":
                    self.add_selection_func(self.exclude_older_get_sf(arg))
                elif opt == "--include":
                    self.add_selection_func(self.glob_get_sf(arg, 1))
                elif (opt == "--include-filelist") or (opt == "--include-globbing-filelist"):
                    # --include-globbing-filelist is now deprecated, as all filelists are globbing
                    # but keep this here for the short term for backwards-compatibility
                    for sf in self.filelist_globbing_get_sfs(filelists[filelists_index], 1, arg):
                        self.add_selection_func(sf)
                    filelists_index += 1
                elif opt == "--include-regexp":
                    self.add_selection_func(self.regexp_get_sf(arg, 1))
                else:
                    assert 0, "Bad selection option %s" % opt
        except SelectError as e:
            self.parse_catch_error(e)
        assert filelists_index == len(filelists)
        self.parse_last_excludes()

    def parse_catch_error(self, exc):
        """Deal with selection error exc"""
        # Internal, used by ParseArgs.
        if isinstance(exc, FilePrefixError):
            log.FatalError(_("""\
Fatal Error: The file specification
    %s
cannot match any files in the base directory
    %s
Useful file specifications begin with the base directory or some
pattern (such as '**') which matches the base directory.""") %
                           (exc, util.ufn(self.prefix)), log.ErrorCode.file_prefix_error)
        elif isinstance(exc, GlobbingError):
            log.FatalError(_("Fatal Error while processing expression\n"
                             "%s") % exc, log.ErrorCode.globbing_error)
        else:
            raise  # pylint: disable=misplaced-bare-raise

    def parse_last_excludes(self):
        """Exit with error if last selection function isn't an exclude"""
        # Internal. Used by ParseArgs.
        if (self.selection_functions and
                not self.selection_functions[-1].exclude):
            log.FatalError(_("""\
Last selection expression:
    %s
only specifies that files be included.  Because the default is to
include all files, the expression is redundant.  Exiting because this
probably isn't what you meant.""") %
                           (self.selection_functions[-1].name,),
                           log.ErrorCode.redundant_inclusion)

    def add_selection_func(self, sel_func, add_to_start=None):
        """Add another selection function at the end or beginning"""
        # Internal. Used by ParseArgs.
        if add_to_start:
            self.selection_functions.insert(0, sel_func)
        else:
            self.selection_functions.append(sel_func)

    def filelist_sanitise_line(self, line, include_default):
        """
        Sanitises lines of both normal and globbing filelists, returning (line, include) and line=None if blank/comment

        The aim is to parse filelists in a consistent way, prior to the interpretation of globbing statements.
        The function removes whitespace, comment lines and processes modifiers (leading +/-) and quotes.
        """
        # Internal. Used by filelist_globbing_get_sfs

        line = line.strip()
        if not line:  # skip blanks
            return None, include_default
        if line[0] == "#":  # skip full-line comments
            return None, include_default

        include = include_default
        if line[:2] == "+ ":
            # Check for "+ " or "- " syntax
            include = 1
            line = line[2:]
        elif line[:2] == "- ":
            include = 0
            line = line[2:]

        if (line[:1] == "'" and line[-1:] == "'") or (line[:1] == '"' and line[-1:] == '"'):
            line = line[1:-1]

        return line, include

    def filelist_globbing_get_sfs(self, filelist_fp, inc_default, list_name):
        """Return list of selection functions by reading fileobj

        filelist_fp should be an open file object
        inc_default is true iff this is an include list
        list_name is just the name of the list, used for logging
        See the man page on --[include/exclude]-globbing-filelist

        """
        # Internal. Used by ParseArgs.
        log.Notice(_("Reading globbing filelist %s") % list_name)
        separator = globals.null_separator and "\0" or "\n"
        filelist_fp.seek(0)
        for line in filelist_fp.read().split(separator):
            line, include = self.filelist_sanitise_line(line, inc_default)
            if not line:
                # Skip blanks and comment lines
                continue
            yield self.glob_get_sf(line, include)

    def other_filesystems_get_sf(self, include):
        """Return selection function matching files on other filesystems"""
        # Internal. Used by ParseArgs and unit tests.
        assert include == 0 or include == 1
        root_devloc = self.rootpath.getdevloc()

        def sel_func(path):
            if path.exists() and path.getdevloc() != root_devloc:
                return include
            else:
                return None

        sel_func.exclude = not include
        sel_func.name = "Match other filesystems"
        return sel_func

    def regexp_get_sf(self, regexp_string, include):
        """Return selection function given by regexp_string"""
        # Internal. Used by ParseArgs and unit tests.
        assert include == 0 or include == 1
        try:
            regexp = re.compile(regexp_string)
        except Exception:
            log.Warn(_("Error compiling regular expression %s") % regexp_string)
            raise

        def sel_func(path):
            if regexp.search(path.name):
                return include
            else:
                return None

        sel_func.exclude = not include
        sel_func.name = "Regular expression: %s" % regexp_string
        return sel_func

    def devfiles_get_sf(self):
        """Return a selection function to exclude all dev files"""
        # Internal. Used by ParseArgs.
        if self.selection_functions:
            log.Warn(_("Warning: exclude-device-files is not the first "
                       "selector.\nThis may not be what you intended"))

        def sel_func(path):
            if path.isdev():
                return 0
            else:
                return None

        sel_func.exclude = 1
        sel_func.name = "Exclude device files"
        return sel_func

    def glob_get_sf(self, glob_str, include):
        """Return selection function given by glob string"""
        # Internal. Used by ParseArgs, filelist_globbing_get_sfs and unit tests.
        assert include == 0 or include == 1
        if glob_str == "**":
            sel_func = lambda path: include
        elif not self.glob_re.match(glob_str):
            # normal file
            sel_func = self.glob_get_filename_sf(glob_str, include)
        else:
            sel_func = self.glob_get_normal_sf(glob_str, include)

        sel_func.exclude = not include
        sel_func.name = "Command-line %s glob: %s" % \
                        (include and "include" or "exclude", glob_str)
        return sel_func

    def present_get_sf(self, filename, include):
        """Return selection function given by existence of a file in a directory"""
        # Internal. Used by ParseArgs.
        assert include == 0 or include == 1

        def exclude_sel_func(path):
            # do not follow symbolic links when checking for file existence!
            if path.isdir():
                # First check path is read accessible
                if not (os.access(path.name, os.R_OK)):
                    # Path is not read accessible
                    # ToDo: Ideally this error would only show if the folder
                    # was ultimately included by the full set of selection
                    # functions. Currently this will give an error for any
                    # locked directory within the folder being backed up.
                    log.Warn(_(
                        "Error accessing possibly locked file %s") % util.ufn(
                        path.name),
                        log.WarningCode.cannot_read, util.escape(path.name))
                    if diffdir.stats:
                        diffdir.stats.Errors += 1
                elif path.append(filename).exists():
                    return 0
                else:
                    return None

        if include == 0:
            sel_func = exclude_sel_func
        else:
            log.FatalError(u"--include-if-present not implemented (would it make sense?).",
                           log.ErrorCode.not_implemented)

        sel_func.exclude = not include
        sel_func.name = "Command-line %s filename: %s" % \
                        (include and "include-if-present" or "exclude-if-present", filename)
        return sel_func

    def glob_get_filename_sf(self, filename, include):
        """Get a selection function given a normal filename

        Some of the parsing is better explained in
        filelist_parse_line.  The reason this is split from normal
        globbing is things are a lot less complicated if no special
        globbing characters are used.

        """
        # Internal. Used by glob_get_sf and unit tests.
        # ToDo: Make all globbing/non-globbing use same code path
        # This distinction has bitten us too many times with bugs in one or
        # the other.
        match_only_dirs = False

        if filename != "/" and filename[-1] == "/":
            match_only_dirs = True
            # Remove trailing / from directory name (unless that is the entire
            # string)
            filename = filename[:-1]

        if not filename.startswith(self.prefix):
            raise FilePrefixError(filename)
        index = tuple(filter(lambda x: x,
                             filename[len(self.prefix):].split("/")))
        return self.glob_get_tuple_sf(index, include, match_only_dirs)

    def glob_get_tuple_sf(self, tuple, include, match_only_dirs=False):
        """Return selection function based on tuple"""
        # Internal. Used by glob_get_filename_sf.

        def include_sel_func(path):
            if len(tuple) == len(path.index) and match_only_dirs and not path.isdir():
                # If we are assessing the actual directory (rather than the
                # contents of the directory) and the glob ended with a /,
                # only match directories
                return None
            elif (path.index == tuple[:len(path.index)] or
                    path.index[:len(tuple)] == tuple):
                return 1  # /foo/bar implicitly matches /foo, vice-versa
            else:
                return None

        def exclude_sel_func(path):
            if match_only_dirs and not path.isdir():
                # If the glob ended with a /, only match directories
                return None
            elif path.index[:len(tuple)] == tuple:
                return 0  # /foo excludes /foo/bar, not vice-versa
            else:
                return None

        if include == 1:
            sel_func = include_sel_func
        elif include == 0:
            sel_func = exclude_sel_func
        sel_func.exclude = not include
        sel_func.name = "Tuple select %s" % (tuple,)
        return sel_func

    def glob_get_normal_sf(self, glob_str, include):
        """Return selection function based on glob_str

        The basic idea is to turn glob_str into a regular expression,
        and just use the normal regular expression.  There is a
        complication because the selection function should return '2'
        (scan) for directories which may contain a file which matches
        the glob_str.  So we break up the glob string into parts, and
        any file which matches an initial sequence of glob parts gets
        scanned.

        Thanks to Donovan Baarda who provided some code which did some
        things similar to this.

        """
        # Internal. Used by glob_get_sf and unit tests.

        ignore_case = False

        if glob_str.lower().startswith("ignorecase:"):
            # Glob string starts with ignorecase, so remove that from the
            # string and change it to lowercase.
            glob_str = glob_str[len("ignorecase:"):].lower()
            ignore_case = True

        # Check to make sure prefix is ok
        if not path_matches_glob_fn(glob_str, include=1)(self.rootpath):
            raise FilePrefixError(glob_str)

        return path_matches_glob_fn(glob_str, include, ignore_case)

    def exclude_older_get_sf(self, date):
        """Return selection function based on files older than modification date """
        # Internal. Used by ParseArgs.

        def sel_func(path):
            if not path.isreg():
                return None
            try:
                if os.path.getmtime(path.name) < date:
                    return 0
            except OSError as e:
                pass  # this is probably only on a race condition of file being deleted
            return None

        sel_func.exclude = True
        sel_func.name = "Select older than %s" % (date,)
        return sel_func

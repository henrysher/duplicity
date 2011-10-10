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

"""Parse command line, check for consistency, and set globals"""

from copy import copy
import optparse
import os
import re
import sys
import socket

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from duplicity import backend
from duplicity import dup_time
from duplicity import globals
from duplicity import gpg
from duplicity import log
from duplicity import path
from duplicity import selection


select_opts = []            # Will hold all the selection options
select_files = []           # Will hold file objects when filelist given

full_backup = None          # Will be set to true if full command given
list_current = None         # Will be set to true if list-current command given
collection_status = None    # Will be set to true if collection-status command given
cleanup = None              # Set to true if cleanup command given
verify = None               # Set to true if verify command given

commands = ["cleanup",
            "collection-status",
            "full",
            "incremental",
            "list-current-files",
            "remove-older-than",
            "remove-all-but-n-full",
            "remove-all-inc-of-but-n-full",
            "restore",
            "verify",
            ]

def old_fn_deprecation(opt):
    print >>sys.stderr, _("Warning: Option %s is pending deprecation "
                          "and will be removed in a future release.\n"
                          "Use of default filenames is strongly suggested.") % opt


def expand_fn(filename):
    return os.path.expanduser(os.path.expandvars(filename))


def expand_archive_dir(archdir, backname):
    """
    Return expanded version of archdir joined with backname.
    """
    assert globals.backup_name is not None, \
        "expand_archive_dir() called prior to globals.backup_name being set"

    return expand_fn(os.path.join(archdir, backname))


def generate_default_backup_name(backend_url):
    """
    @param backend_url: URL to backend.
    @returns A default backup name (string).
    """
    # For default, we hash args to obtain a reasonably safe default.
    # We could be smarter and resolve things like relative paths, but
    # this should actually be a pretty good compromise. Normally only
    # the destination will matter since you typically only restart
    # backups of the same thing to a given destination. The inclusion
    # of the source however, does protect against most changes of
    # source directory (for whatever reason, such as
    # /path/to/different/snapshot). If the user happens to have a case
    # where relative paths are used yet the relative path is the same
    # (but duplicity is run from a different directory or similar),
    # then it is simply up to the user to set --archive-dir properly.
    burlhash = md5()
    burlhash.update(backend_url)
    return burlhash.hexdigest()

def check_file(option, opt, value):
    return expand_fn(value)

def check_time(option, opt, value):
    try:
        return dup_time.genstrtotime(value)
    except dup_time.TimeException, e:
        raise optparse.OptionValueError(str(e))

def check_verbosity(option, opt, value):
    fail = False

    value = value.lower()
    if value in ['e', 'error']:
        verb = log.ERROR
    elif value in ['w', 'warning']:
        verb = log.WARNING
    elif value in ['n', 'notice']:
        verb = log.NOTICE
    elif value in ['i', 'info']:
        verb = log.INFO
    elif value in ['d', 'debug']:
        verb = log.DEBUG
    else:
        try:
            verb = int(value)
            if verb < 0 or verb > 9:
                fail = True
        except ValueError:
            fail = True

    if fail:
        # TRANSL: In this portion of the usage instructions, "[ewnid]" indicates which
        # characters are permitted (e, w, n, i, or d); the brackets imply their own
        # meaning in regex; i.e., only one of the characters is allowed in an instance.
        raise optparse.OptionValueError("Verbosity must be one of: digit [0-9], character [ewnid], "
                                        "or word ['error', 'warning', 'notice', 'info', 'debug']. "
                                        "The default is 4 (Notice).  It is strongly recommended "
                                        "that verbosity level is set at 2 (Warning) or higher.")

    return verb

class DupOption(optparse.Option):
    TYPES = optparse.Option.TYPES + ("file", "time", "verbosity",)
    TYPE_CHECKER = copy(optparse.Option.TYPE_CHECKER)
    TYPE_CHECKER["file"] = check_file
    TYPE_CHECKER["time"] = check_time
    TYPE_CHECKER["verbosity"] = check_verbosity

    ACTIONS = optparse.Option.ACTIONS + ("extend",)
    STORE_ACTIONS = optparse.Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = optparse.Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = optparse.Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            if not value:
                return
            if hasattr(values, dest) and getattr(values, dest):
                setattr(values, dest, getattr(values, dest) + ' ' + value)
            else:
                setattr(values, dest, value)
        else:
            optparse.Option.take_action(
                self, action, dest, opt, value, values, parser)

""" 
Fix:
    File "/usr/lib/pythonX.X/optparse.py", line XXXX, in print_help
    file.write(self.format_help().encode(encoding, "replace"))
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xXX in position XXXX:
See:
    http://bugs.python.org/issue2931
    http://mail.python.org/pipermail/python-dev/2006-May/065458.html
"""
class OPHelpFix(optparse.OptionParser):
    def _get_encoding(self, file):
        """
        try to get the encoding or switch to UTF-8
        which is default encoding in python3 and most recent unixes
        """
        encoding = getattr(file, "encoding", "UTF-8")
        return encoding

    def print_help(self, file=None):
        """
        overwrite method with proper utf-8 decoding
        """
        if file is None:
            file = sys.stdout
        encoding = self._get_encoding(file)
        file.write(self.format_help().decode('utf-8').encode(encoding, "replace"))

def parse_cmdline_options(arglist):
    """Parse argument list"""
    global select_opts, select_files, full_backup
    global list_current, collection_status, cleanup, remove_time, verify

    def use_gio(*args):
        try:
            import duplicity.backends.giobackend
            backend.force_backend(duplicity.backends.giobackend.GIOBackend)
        except ImportError:
            log.FatalError(_("Unable to load gio module"), log.ErrorCode.gio_not_available)

    def set_log_fd(fd):
        if fd < 1:
            raise optparse.OptionValueError("log-fd must be greater than zero.")
        log.add_fd(fd)

    def set_time_sep(sep, opt):
        if sep == '-':
            raise optparse.OptionValueError("Dash ('-') not valid for time-separator.")
        globals.time_separator = sep
        old_fn_deprecation(opt)

    def add_selection(o, s, v, p):
        select_opts.append((s, v))

    def add_filelist(o, s, v, p):
        filename = v
        select_opts.append((s, filename))
        try:
            select_files.append(open(filename, "r"))
        except IOError:
            log.FatalError(_("Error opening file %s") % filename,
                           log.ErrorCode.cant_open_filelist)

    def print_ver(o, s, v, p):
        print "duplicity %s" % (globals.version)
        sys.exit(0)

    def add_rename(o, s, v, p):
        globals.rename[os.path.normcase(os.path.normpath(v[0]))] = v[1]

    parser = OPHelpFix( option_class=DupOption, usage=usage() )

    # If this is true, only warn and don't raise fatal error when backup
    # source directory doesn't match previous backup source directory.
    parser.add_option("--allow-source-mismatch", action="store_true")

    # Set to the path of the archive directory (the directory which
    # contains the signatures and manifests of the relevent backup
    # collection), and for checkpoint state between volumes.
    # TRANSL: Used in usage help to represent a Unix-style path name. Example:
    # --archive-dir <path>
    parser.add_option("--archive-dir", type="file", metavar=_("path"))

    # Asynchronous put/get concurrency limit
    # (default of 0 disables asynchronicity).
    parser.add_option("--asynchronous-upload", action="store_const", const=1,
                      dest="async_concurrency")

    # config dir for future use
    parser.add_option("--config-dir", type="file", metavar=_("path"),
                      help=optparse.SUPPRESS_HELP)

    # for testing -- set current time
    parser.add_option("--current-time", type="int",
                      dest="current_time", help=optparse.SUPPRESS_HELP)

    # Don't actually do anything, but still report what would be done
    parser.add_option("--dry-run", action="store_true")

    # TRANSL: Used in usage help to represent an ID for a GnuPG key. Example:
    # --encrypt-key <gpg_key_id>
    parser.add_option("--encrypt-key", type="string", metavar=_("gpg-key-id"),
                      dest="", action="callback",
                      callback=lambda o, s, v, p: globals.gpg_profile.recipients.append(v)) #@UndefinedVariable

    # secret keyring in which the private encrypt key can be found
    parser.add_option("--encrypt-secret-keyring", type="string", metavar=_("path"))
    
    parser.add_option("--encrypt-sign-key", type="string", metavar=_("gpg-key-id"),
                      dest="", action="callback",
                      callback=lambda o, s, v, p: ( globals.gpg_profile.recipients.append(v), set_sign_key(v)) )

    # TRANSL: Used in usage help to represent a "glob" style pattern for
    # matching one or more files, as described in the documentation.
    # Example:
    # --exclude <shell_pattern>
    parser.add_option("--exclude", action="callback", metavar=_("shell_pattern"),
                      dest="", type="string", callback=add_selection)

    parser.add_option("--exclude-device-files", action="callback",
                      dest="", callback=add_selection)

    parser.add_option("--exclude-filelist", type="file", metavar=_("filename"),
                      dest="", action="callback", callback=add_filelist)

    parser.add_option("--exclude-filelist-stdin", action="callback", dest="",
                      callback=lambda o, s, v, p: (select_opts.append(("--exclude-filelist", "standard input")),
                                                   select_files.append(sys.stdin)))

    parser.add_option("--exclude-globbing-filelist", type="file", metavar=_("filename"),
                      dest="", action="callback", callback=add_filelist)

    # TRANSL: Used in usage help to represent the name of a file. Example:
    # --log-file <filename>
    parser.add_option("--exclude-if-present", metavar=_("filename"), dest="",
                      type="file", action="callback", callback=add_selection)

    parser.add_option("--exclude-other-filesystems", action="callback",
                      dest="", callback=add_selection)

    # TRANSL: Used in usage help to represent a regular expression (regexp).
    parser.add_option("--exclude-regexp", metavar=_("regular_expression"),
                      dest="", type="string", action="callback", callback=add_selection)

    # Whether we should be particularly aggressive when cleaning up
    parser.add_option("--extra-clean", action="store_true")

    # used in testing only - raises exception after volume
    parser.add_option("--fail-on-volume", type="int",
                      help=optparse.SUPPRESS_HELP)

    # used in testing only - skips upload for a given volume
    parser.add_option("--skip-volume", type="int",
                      help=optparse.SUPPRESS_HELP)

    # If set, restore only the subdirectory or file specified, not the
    # whole root.
    # TRANSL: Used in usage help to represent a Unix-style path name. Example:
    # --archive-dir <path>
    parser.add_option("--file-to-restore", "-r", action="callback", type="file",
                      metavar=_("path"), dest="restore_dir",
                      callback=lambda o, s, v, p: setattr(p.values, "restore_dir", v.rstrip('/')))

    # Used to confirm certain destructive operations like deleting old files.
    parser.add_option("--force", action="store_true")

    # FTP data connection type
    parser.add_option("--ftp-passive", action="store_const", const="passive", dest="ftp_connection")
    parser.add_option("--ftp-regular", action="store_const", const="regular", dest="ftp_connection")

    # If set, forces a full backup if the last full backup is older than
    # the time specified
    parser.add_option("--full-if-older-than", type="time", dest="full_force_time", metavar=_("time"))

    parser.add_option("--gio", action="callback", callback=use_gio)

    parser.add_option("--gpg-options", action="extend", metavar=_("options"))

    # ignore (some) errors during operations; supposed to make it more
    # likely that you are able to restore data under problematic
    # circumstances. the default should absolutely always be False unless
    # you know what you are doing.
    parser.add_option("--ignore-errors", action="callback",
                      dest="ignore_errors",
                      callback=lambda o, s, v, p: (log.Warn(
                          _("Running in 'ignore errors' mode due to %s; please "
                            "re-consider if this was not intended") % s),
                          setattr(p.values, "ignore errors", True)))

    # Whether to use the full email address as the user name when
    # logging into an imap server. If false just the user name
    # part of the email address is used.
    parser.add_option("--imap-full-address", action="store_true",
                      help=optparse.SUPPRESS_HELP)

    # Name of the imap folder where we want to store backups.
    # Can be changed with a command line argument.
    # TRANSL: Used in usage help to represent an imap mailbox
    parser.add_option("--imap-mailbox", metavar=_("imap_mailbox"))

    parser.add_option("--include", action="callback", metavar=_("shell_pattern"),
                      dest="", type="string", callback=add_selection)
    parser.add_option("--include-filelist", type="file", metavar=_("filename"),
                      dest="", action="callback", callback=add_filelist)
    parser.add_option("--include-filelist-stdin", action="callback", dest="",
                      callback=lambda o, s, v, p: (select_opts.append(("--include-filelist", "standard input")),
                                                   select_files.append(sys.stdin)))
    parser.add_option("--include-globbing-filelist", type="file", metavar=_("filename"),
                      dest="", action="callback", callback=add_filelist)
    parser.add_option("--include-regexp", metavar=_("regular_expression"), dest="",
                      type="string", action="callback", callback=add_selection)

    parser.add_option("--log-fd", type="int", metavar=_("file_descriptor"),
                      dest="", action="callback",
                      callback=lambda o, s, v, p: set_log_fd(v))

    # TRANSL: Used in usage help to represent the name of a file. Example:
    # --log-file <filename>
    parser.add_option("--log-file", type="file", metavar=_("filename"),
                      dest="", action="callback",
                      callback=lambda o, s, v, p: log.add_file(v))

    # TRANSL: Used in usage help (noun)
    parser.add_option("--name", dest="backup_name", metavar=_("backup name"))

    # If set to false, then do not encrypt files on remote system
    parser.add_option("--no-encryption", action="store_false", dest="encryption")

    # If set, print the statistics after every backup session
    parser.add_option("--no-print-statistics", action="store_false", dest="print_statistics")

    # If true, filelists and directory statistics will be split on
    # nulls instead of newlines.
    parser.add_option("--null-separator", action="store_true")

    # number of retries on network operations
    # TRANSL: Used in usage help to represent a desired number of
    # something. Example:
    # --num-retries <number>
    parser.add_option("--num-retries", type="int", metavar=_("number"))

    # File owner uid keeps number from tar file. Like same option in GNU tar.
    parser.add_option("--numeric-owner", action="store_true")

    # Whether the old filename format is in effect.
    parser.add_option("--old-filenames", action="callback",
                      dest="old_filenames",
                      callback=lambda o, s, v, p: (setattr(p.values, o.dest, True),
                                                   old_fn_deprecation(s)))

    # option to trigger Pydev debugger
    parser.add_option("--pydevd", action="store_true")

    # option to rename files during restore
    parser.add_option("--rename", type="file", action="callback", nargs=2,
                      callback=add_rename)

    # Restores will try to bring back the state as of the following time.
    # If it is None, default to current time.
    # TRANSL: Used in usage help to represent a time spec for a previous
    # point in time, as described in the documentation. Example:
    # duplicity remove-older-than time [options] target_url
    parser.add_option("--restore-time", "--time", "-t", type="time", metavar=_("time"))

    # Whether to create European buckets (sorry, hard-coded to only
    # support european for now).
    parser.add_option("--s3-european-buckets", action="store_true")

    # Whether to use S3 Reduced Redudancy Storage
    parser.add_option("--s3-use-rrs", action="store_true")

    # Whether to use "new-style" subdomain addressing for S3 buckets. Such
    # use is not backwards-compatible with upper-case buckets, or buckets
    # that are otherwise not expressable in a valid hostname.
    parser.add_option("--s3-use-new-style", action="store_true")

    # Whether to use plain HTTP (without SSL) to send data to S3
    # See <https://bugs.launchpad.net/duplicity/+bug/433970>.
    parser.add_option("--s3-unencrypted-connection", action="store_true")

    # Chunk size used for S3 multipart uploads.The number of parallel uploads to
    # S3 be given by chunk size / volume size. Use this to maximize the use of
    # your bandwidth. Defaults to 25MB
    parser.add_option("--s3-multipart-chunk-size", type="int", action="callback", metavar=_("number"),
                      callback=lambda o, s, v, p: setattr(p.values, "s3_multipart_chunk_size", v*1024*1024))

    # scp command to use
    # TRANSL: noun
    parser.add_option("--scp-command", metavar=_("command"))

    # sftp command to use
    # TRANSL: noun
    parser.add_option("--sftp-command", metavar=_("command"))

    # If set, use short (< 30 char) filenames for all the remote files.
    parser.add_option("--short-filenames", action="callback",
                      dest="short_filenames",
                      callback=lambda o, s, v, p: (setattr(p.values, o.dest, True),
                                                   old_fn_deprecation(s)))

    # TRANSL: Used in usage help to represent an ID for a GnuPG key. Example:
    # --encrypt-key <gpg_key_id>
    parser.add_option("--sign-key", type="string", metavar=_("gpg-key-id"),
                      dest="", action="callback",
                      callback=lambda o, s, v, p: set_sign_key(v))

    # default to batch mode using public-key encryption
    parser.add_option("--ssh-askpass", action="store_true")

    # user added ssh options
    parser.add_option("--ssh-options", action="extend", metavar=_("options"))

    # Working directory for the tempfile module. Defaults to /tmp on most systems.
    parser.add_option("--tempdir", dest="temproot", type="file", metavar=_("path"))

    # network timeout value
    # TRANSL: Used in usage help. Example:
    # --timeout <seconds>
    parser.add_option("--timeout", type="int", metavar=_("seconds"))

    # Character used like the ":" in time strings like
    # 2002-08-06T04:22:00-07:00.  The colon isn't good for filenames on
    # windows machines.
    # TRANSL: abbreviation for "character" (noun)
    parser.add_option("--time-separator", type="string", metavar=_("char"),
                      action="callback",
                      callback=lambda o, s, v, p: set_time_sep(v, s))

    # Whether to specify --use-agent in GnuPG options
    parser.add_option("--use-agent", action="store_true")

    parser.add_option("--use-scp", action="store_true")

    parser.add_option("--verbosity", "-v", type="verbosity", metavar="[0-9]",
                      dest="", action="callback",
                      callback=lambda o, s, v, p: log.setverbosity(v))

    parser.add_option("-V", "--version", action="callback", callback=print_ver)

    # volume size
    # TRANSL: Used in usage help to represent a desired number of
    # something. Example:
    # --num-retries <number>
    parser.add_option("--volsize", type="int", action="callback", metavar=_("number"),
                      callback=lambda o, s, v, p: setattr(p.values, "volsize", v*1024*1024))

    (options, args) = parser.parse_args()

    # Copy all arguments and their values to the globals module.  Don't copy
    # attributes that are 'hidden' (start with an underscore) or whose name is
    # the empty string (used for arguments that don't directly store a value
    # by using dest="")
    for f in filter(lambda x: x and not x.startswith("_"), dir(options)):
        v = getattr(options, f)
        # Only set if v is not None because None is the default for all the
        # variables.  If user didn't set it, we'll use defaults in globals.py
        if v is not None:
            setattr(globals, f, v)

    socket.setdefaulttimeout(globals.timeout)

    # expect no cmd and two positional args
    cmd = ""
    num_expect = 2

    # process first arg as command
    if args:
        cmd = args.pop(0)
        possible = [c for c in commands if c.startswith(cmd)]
        # no unique match, that's an error
        if len(possible) > 1:
            command_line_error("command '%s' not unique, could be %s" % (cmd, possible))
        # only one match, that's a keeper
        elif len(possible) == 1:
            cmd = possible[0]
        # no matches, assume no cmd
        elif not possible:
            args.insert(0, cmd)

    if cmd == "cleanup":
        cleanup = True
        num_expect = 1
    elif cmd == "collection-status":
        collection_status = True
        num_expect = 1
    elif cmd == "full":
        full_backup = True
        num_expect = 2
    elif cmd == "incremental":
        globals.incremental = True
        num_expect = 2
    elif cmd == "list-current-files":
        list_current = True
        num_expect = 1
    elif cmd == "remove-older-than":
        try:
            arg = args.pop(0)
        except Exception:
            command_line_error("Missing time string for remove-older-than")
        globals.remove_time = dup_time.genstrtotime(arg)
        num_expect = 1
    elif cmd == "remove-all-but-n-full" or cmd == "remove-all-inc-of-but-n-full":
        if cmd == "remove-all-but-n-full" :
            globals.remove_all_but_n_full_mode = True
        if cmd == "remove-all-inc-of-but-n-full" :
            globals.remove_all_inc_of_but_n_full_mode = True
        try:
            arg = args.pop(0)
        except Exception:
            command_line_error("Missing count for " + cmd)
        globals.keep_chains = int(arg)
        if not globals.keep_chains > 0:
            command_line_error(cmd + " count must be > 0")
        num_expect = 1
    elif cmd == "verify":
        verify = True

    if len(args) != num_expect:
        command_line_error("Expected %d args, got %d" % (num_expect, len(args)))

    # expand pathname args, but not URL
    for loc in range(len(args)):
        if not '://' in args[loc]:
            args[loc] = expand_fn(args[loc])

    # Note that ProcessCommandLine depends on us verifying the arg
    # count here; do not remove without fixing it. We must make the
    # checks here in order to make enough sense of args to identify
    # the backend URL/lpath for args_to_path_backend().
    if len(args) < 1:
        command_line_error("Too few arguments")
    elif len(args) == 1:
        backend_url = args[0]
    elif len(args) == 2:
        lpath, backend_url = args_to_path_backend(args[0], args[1]) #@UnusedVariable
    else:
        command_line_error("Too many arguments")

    if globals.backup_name is None:
        globals.backup_name = generate_default_backup_name(backend_url)

    # set and expand archive dir
    set_archive_dir(expand_archive_dir(globals.archive_dir,
                                       globals.backup_name))

    log.Info(_("Using archive dir: %s") % (globals.archive_dir.name,))
    log.Info(_("Using backup name: %s") % (globals.backup_name,))

    return args


def command_line_error(message):
    """Indicate a command line error and exit"""
    log.FatalError(_("Command line error: %s") % (message,) + "\n" +
                   _("Enter 'duplicity --help' for help screen."),
                   log.ErrorCode.command_line)


def usage():
    """Returns terse usage info. The code is broken down into pieces for ease of
    translation maintenance. Any comments that look extraneous or redundant should
    be assumed to be for the benefit of translators, since they can get each string
    (paired with its preceding comment, if any) independently of the others."""

    dict = {
        # TRANSL: Used in usage help to represent a Unix-style path name. Example:
        # rsync://user[:password]@other_host[:port]//absolute_path
        'absolute_path'  : _("absolute_path"),

        # TRANSL: Used in usage help. Example:
        # tahoe://alias/some_dir
        'alias'          : _("alias"),

        # TRANSL: Used in help to represent a "bucket name" for Amazon Web
        # Services' Simple Storage Service (S3). Example:
        # s3://other.host/bucket_name[/prefix]
        'bucket_name'    : _("bucket_name"),

        # TRANSL: abbreviation for "character" (noun)
        'char'           : _("char"),

        # TRANSL: noun
        'command'        : _("command"),

        # TRANSL: Used in usage help to represent the name of a container in
        # Amazon Web Services' Cloudfront. Example:
        # cf+http://container_name
        'container_name' : _("container_name"),

        # TRANSL: noun
        'count'          : _("count"),

        # TRANSL: Used in usage help to represent the name of a file directory
        'directory'      : _("directory"),

        # TRANSL: Used in usage help to represent the name of a file. Example:
        # --log-file <filename>
        'filename'       : _("filename"),

        # TRANSL: Used in usage help to represent an ID for a GnuPG key. Example:
        # --encrypt-key <gpg_key_id>
        'gpg_key_id'     : _("gpg-key-id"),

        # TRANSL: Used in usage help, e.g. to represent the name of a code
        # module. Example:
        # rsync://user[:password]@other.host[:port]::/module/some_dir
        'module'         : _("module"),

        # TRANSL: Used in usage help to represent a desired number of
        # something. Example:
        # --num-retries <number>
        'number'         : _("number"),

        # TRANSL: Used in usage help. (Should be consistent with the "Options:"
        # header.) Example:
        # duplicity [full|incremental] [options] source_dir target_url
        'options'        : _("options"),

        # TRANSL: Used in usage help to represent an internet hostname. Example:
        # ftp://user[:password]@other.host[:port]/some_dir
        'other_host'     : _("other.host"),

        # TRANSL: Used in usage help. Example:
        # ftp://user[:password]@other.host[:port]/some_dir
        'password'       : _("password"),

        # TRANSL: Used in usage help to represent a Unix-style path name. Example:
        # --archive-dir <path>
        'path'           : _("path"),

        # TRANSL: Used in usage help to represent a TCP port number. Example:
        # ftp://user[:password]@other.host[:port]/some_dir
        'port'           : _("port"),

        # TRANSL: Used in usage help. This represents a string to be used as a
        # prefix to names for backup files created by Duplicity. Example:
        # s3://other.host/bucket_name[/prefix]
        'prefix'         : _("prefix"),

        # TRANSL: Used in usage help to represent a Unix-style path name. Example:
        # rsync://user[:password]@other.host[:port]/relative_path
        'relative_path'  : _("relative_path"),

        # TRANSL: Used in usage help. Example:
        # --timeout <seconds>
        'seconds'        : _("seconds"),

        # TRANSL: Used in usage help to represent a "glob" style pattern for
        # matching one or more files, as described in the documentation.
        # Example:
        # --exclude <shell_pattern>
        'shell_pattern'  : _("shell_pattern"),

        # TRANSL: Used in usage help to represent the name of a single file
        # directory or a Unix-style path to a directory. Example:
        # file:///some_dir
        'some_dir'       : _("some_dir"),

        # TRANSL: Used in usage help to represent the name of a single file
        # directory or a Unix-style path to a directory where files will be
        # coming FROM. Example:
        # duplicity [full|incremental] [options] source_dir target_url
        'source_dir'     : _("source_dir"),

        # TRANSL: Used in usage help to represent a URL files will be coming
        # FROM. Example:
        # duplicity [restore] [options] source_url target_dir
        'source_url'     : _("source_url"),

        # TRANSL: Used in usage help to represent the name of a single file
        # directory or a Unix-style path to a directory. where files will be
        # going TO. Example:
        # duplicity [restore] [options] source_url target_dir
        'target_dir'     : _("target_dir"),

        # TRANSL: Used in usage help to represent a URL files will be going TO.
        # Example:
        # duplicity [full|incremental] [options] source_dir target_url
        'target_url'     : _("target_url"),

        # TRANSL: Used in usage help to represent a time spec for a previous
        # point in time, as described in the documentation. Example:
        # duplicity remove-older-than time [options] target_url
        'time'           : _("time"),

        # TRANSL: Used in usage help to represent a user name (i.e. login).
        # Example:
        # ftp://user[:password]@other.host[:port]/some_dir
        'user'           : _("user") }

    # TRANSL: Header in usage help
    msg = """
  duplicity [full|incremental] [%(options)s] %(source_dir)s %(target_url)s
  duplicity [restore] [%(options)s] %(source_url)s %(target_dir)s
  duplicity verify [%(options)s] %(source_url)s %(target_dir)s
  duplicity collection-status [%(options)s] %(target_url)s
  duplicity list-current-files [%(options)s] %(target_url)s
  duplicity cleanup [%(options)s] %(target_url)s
  duplicity remove-older-than %(time)s [%(options)s] %(target_url)s
  duplicity remove-all-but-n-full %(count)s [%(options)s] %(target_url)s
  duplicity remove-all-inc-of-but-n-full %(count)s [%(options)s] %(target_url)s

""" % dict

    # TRANSL: Header in usage help
    msg = msg + _("Backends and their URL formats:") + """
  cf+http://%(container_name)s
  file:///%(some_dir)s
  ftp://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]/%(some_dir)s
  ftps://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]/%(some_dir)s
  hsi://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]/%(some_dir)s
  imap://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]/%(some_dir)s
  rsync://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]::/%(module)s/%(some_dir)s
  rsync://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]/%(relative_path)s
  rsync://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]//%(absolute_path)s
  s3://%(other_host)s/%(bucket_name)s[/%(prefix)s]
  s3+http://%(bucket_name)s[/%(prefix)s]
  scp://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]/%(some_dir)s
  ssh://%(user)s[:%(password)s]@%(other_host)s[:%(port)s]/%(some_dir)s
  tahoe://%(alias)s/%(directory)s
  webdav://%(user)s[:%(password)s]@%(other_host)s/%(some_dir)s
  webdavs://%(user)s[:%(password)s]@%(other_host)s/%(some_dir)s
  gdocs://%(user)s[:%(password)s]@%(other_host)s/%(some_dir)s

""" % dict

    # TRANSL: Header in usage help
    msg = msg + _("Commands:") + """
  cleanup <%(target_url)s>
  collection-status <%(target_url)s>
  full <%(source_dir)s> <%(target_url)s>
  incr <%(source_dir)s> <%(target_url)s>
  list-current-files <%(target_url)s>
  restore <%(target_url)s> <%(source_dir)s>
  remove-older-than <%(time)s> <%(target_url)s>
  remove-all-but-n-full <%(count)s> <%(target_url)s>
  remove-all-inc-of-but-n-full <%(count)s> <%(target_url)s>
  verify <%(target_url)s> <%(source_dir)s>""" % dict

    return msg


def set_archive_dir(dirstring):
    """Check archive dir and set global"""
    if not os.path.exists(dirstring):
        try:
            os.makedirs(dirstring)
        except Exception:
            pass
    archive_dir = path.Path(dirstring)
    if not archive_dir.isdir():
        log.FatalError(_("Specified archive directory '%s' does not exist, "
                         "or is not a directory") % (archive_dir.name,),
                       log.ErrorCode.bad_archive_dir)
    globals.archive_dir = archive_dir


def set_sign_key(sign_key):
    """Set globals.sign_key assuming proper key given"""
    if not len(sign_key) == 8 or not re.search("^[0-9A-F]*$", sign_key):
        log.FatalError(_("Sign key should be an 8 character hex string, like "
                         "'AA0E73D2'.\nReceived '%s' instead.") % (sign_key,),
                       log.ErrorCode.bad_sign_key)
    globals.gpg_profile.sign_key = sign_key


def set_selection():
    """Return selection iter starting at filename with arguments applied"""
    global select_opts, select_files
    sel = selection.Select(globals.local_path)
    sel.ParseArgs(select_opts, select_files)
    globals.select = sel.set_iter()

def args_to_path_backend(arg1, arg2):
    """
    Given exactly two arguments, arg1 and arg2, figure out which one
    is the backend URL and which one is a local path, and return
    (local, backend).
    """
    arg1_is_backend, arg2_is_backend = backend.is_backend_url(arg1), backend.is_backend_url(arg2)

    if not arg1_is_backend and not arg2_is_backend:
        command_line_error(
"""One of the arguments must be an URL.  Examples of URL strings are
"scp://user@host.net:1234/path" and "file:///usr/local".  See the man
page for more information.""")
    if arg1_is_backend and arg2_is_backend:
        command_line_error("Two URLs specified.  "
                           "One argument should be a path.")
    if arg1_is_backend:
        return (arg2, arg1)
    elif arg2_is_backend:
        return (arg1, arg2)
    else:
        raise AssertionError('should not be reached')

def set_backend(arg1, arg2):
    """Figure out which arg is url, set backend

    Return value is pair (path_first, path) where is_first is true iff
    path made from arg1.

    """
    path, bend = args_to_path_backend(arg1, arg2)

    globals.backend = backend.get_backend(bend)

    if path == arg2:
        return (None, arg2) # False?
    else:
        return (1, arg1) # True?


def process_local_dir(action, local_pathname):
    """Check local directory, set globals.local_path"""
    local_path = path.Path(path.Path(local_pathname).get_canonical())
    if action == "restore":
        if (local_path.exists() and not local_path.isemptydir()) and not globals.force:
            log.FatalError(_("Restore destination directory %s already "
                             "exists.\nWill not overwrite.") % (local_pathname,),
                           log.ErrorCode.restore_dir_exists)
    elif action == "verify":
        if not local_path.exists():
            log.FatalError(_("Verify directory %s does not exist") %
                           (local_path.name,),
                           log.ErrorCode.verify_dir_doesnt_exist)
    else:
        assert action == "full" or action == "inc"
        if not local_path.exists():
            log.FatalError(_("Backup source directory %s does not exist.")
                           % (local_path.name,),
                           log.ErrorCode.backup_dir_doesnt_exist)

    globals.local_path = local_path


def check_consistency(action):
    """Final consistency check, see if something wrong with command line"""
    global full_backup, select_opts, list_current
    def assert_only_one(arglist):
        """Raises error if two or more of the elements of arglist are true"""
        n = 0
        for m in arglist:
            if m:
                n+=1
        assert n <= 1, "Invalid syntax, two conflicting modes specified"
    if action in ["list-current", "collection-status",
                  "cleanup", "remove-old", "remove-all-but-n-full", "remove-all-inc-of-but-n-full"]:
        assert_only_one([list_current, collection_status, cleanup,
                         globals.remove_time is not None])
    elif action == "restore" or action == "verify":
        if full_backup:
            command_line_error("--full option cannot be used when "
                               "restoring or verifying")
        elif globals.incremental:
            command_line_error("--incremental option cannot be used when "
                               "restoring or verifying")
        if select_opts and action == "restore":
            log.Warn( _("Command line warning: %s") % _("Selection options --exclude/--include\n"
                                                        "currently work only when backing up,"
                                                        "not restoring.") )
    else:
        assert action == "inc" or action == "full"
        if verify:
            command_line_error("--verify option cannot be used "
                                      "when backing up")
        if globals.restore_dir:
            command_line_error("restore option incompatible with %s backup"
                               % (action,))


def ProcessCommandLine(cmdline_list):
    """Process command line, set globals, return action

    action will be "list-current", "collection-status", "cleanup",
    "remove-old", "restore", "verify", "full", or "inc".

    """
    globals.gpg_profile = gpg.GPGProfile()

    args = parse_cmdline_options(cmdline_list)

    # we can now try to import all the backends
    backend.import_backends()

    # parse_cmdline_options already verified that we got exactly 1 or 2
    # non-options arguments
    assert len(args) >= 1 and len(args) <= 2, "arg count should have been checked already"

    if len(args) == 1:
        if list_current:
            action = "list-current"
        elif collection_status:
            action = "collection-status"
        elif cleanup:
            action = "cleanup"
        elif globals.remove_time is not None:
            action = "remove-old"
        elif globals.remove_all_but_n_full_mode:
            action = "remove-all-but-n-full"
        elif globals.remove_all_inc_of_but_n_full_mode:
            action = "remove-all-inc-of-but-n-full"
        else:
            command_line_error("Too few arguments")
        globals.backend = backend.get_backend(args[0])
        if not globals.backend:
            log.FatalError(_("""Bad URL '%s'.
Examples of URL strings are "scp://user@host.net:1234/path" and
"file:///usr/local".  See the man page for more information.""") % (args[0],),
                                               log.ErrorCode.bad_url)
    elif len(args) == 2:
        # Figure out whether backup or restore
        backup, local_pathname = set_backend(args[0], args[1])
        if backup:
            if full_backup:
                action = "full"
            else:
                action = "inc"
        else:
            if verify:
                action = "verify"
            else:
                action = "restore"

        process_local_dir(action, local_pathname)
        if action in ['full', 'inc', 'verify']:
            set_selection()
    elif len(args) > 2:
        raise AssertionError("this code should not be reachable")

    check_consistency(action)
    log.Info(_("Main action: ") + action)
    return action

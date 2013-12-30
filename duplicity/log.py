# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2008 Michael Terry <mike@mterry.name>
# Copyright 2011 Canonical Ltd
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

"""Log various messages depending on verbosity level"""

import os
import sys
import logging
import datetime

MIN = 0
ERROR = 0
WARNING = 2
NOTICE = 3
INFO = 5
DEBUG = 9
MAX = 9

_logger = None

def DupToLoggerLevel(verb):
    """Convert duplicity level to the logging module's system, where higher is
       more severe"""
    return MAX - verb + 1

def LoggerToDupLevel(verb):
    """Convert logging module level to duplicity's system, where lowere is
       more severe"""
    return DupToLoggerLevel(verb)

def LevelName(level):
    level = LoggerToDupLevel(level)
    if   level >= 9: return "DEBUG"
    elif level >= 5: return "INFO"
    elif level >= 3: return "NOTICE"
    elif level >= 1: return "WARNING"
    else:            return "ERROR"

def Log(s, verb_level, code=1, extra=None, force_print=False):
    """Write s to stderr if verbosity level low enough"""
    global _logger
    # controlLine is a terrible hack until duplicity depends on Python 2.5
    # and its logging 'extra' keyword that allows a custom record dictionary.
    if extra:
        _logger.controlLine = '%d %s' % (code, extra)
    else:
        _logger.controlLine = '%d' % (code)
    if not s:
        s = '' # If None is passed, standard logging would render it as 'None'

    if force_print:
        initial_level = _logger.getEffectiveLevel()
        _logger.setLevel(DupToLoggerLevel(MAX))

    # If all the backends kindly gave us unicode, we could enable this next
    # assert line.  As it is, we'll attempt to convert s to unicode if we
    # are handed bytes.  One day we should update the backends.
    #assert isinstance(s, unicode)
    if not isinstance(s, unicode):
        s = s.decode("utf8", "replace")

    _logger.log(DupToLoggerLevel(verb_level), s)
    _logger.controlLine = None

    if force_print:
        _logger.setLevel(initial_level)

def Debug(s):
    """Shortcut used for debug message (verbosity 9)."""
    Log(s, DEBUG)

class InfoCode:
    """Enumeration class to hold info code values.
       These values should never change, as frontends rely upon them.
       Don't use 0 or negative numbers."""
    generic = 1
    progress = 2
    collection_status = 3
    diff_file_new = 4
    diff_file_changed = 5
    diff_file_deleted = 6
    patch_file_writing = 7
    patch_file_patching = 8
    #file_list = 9 # 9 isn't used anymore.  It corresponds to an older syntax for listing files
    file_list = 10
    synchronous_upload_begin = 11
    asynchronous_upload_begin = 12
    synchronous_upload_done = 13
    asynchronous_upload_done = 14
    skipping_socket = 15
    upload_progress = 16

def Info(s, code=InfoCode.generic, extra=None):
    """Shortcut used for info messages (verbosity 5)."""
    Log(s, INFO, code, extra)

def Progress(s, current, total=None):
    """Shortcut used for progress messages (verbosity 5)."""
    if total:
        controlLine = '%d %d' % (current, total)
    else:
        controlLine = '%d' % current
    Log(s, INFO, InfoCode.progress, controlLine)

def _ElapsedSecs2Str(secs):
    tdelta = datetime.timedelta(seconds=secs)
    hours,rem = divmod(tdelta.seconds, 3600)
    minutes,seconds = divmod(rem, 60)
    fmt = ""
    if tdelta.days > 0:
        fmt = "%dd," % (tdelta.days)
    fmt = "%s%02d:%02d:%02d" % (fmt, hours, minutes, seconds)
    return fmt

def _RemainingSecs2Str(secs):
    tdelta = datetime.timedelta(seconds=secs)
    hours,rem = divmod(tdelta.seconds, 3600)
    minutes,seconds = divmod(rem, 60)
    fmt = ""
    if tdelta.days > 0:
        fmt = "%dd" % (tdelta.days)
        if hours > 0:
            fmt = "%s %dh" % (fmt, hours)
        if minutes > 0:
            fmt = "%s %dmin" % (fmt, minutes)
    elif hours > 0:
        fmt = "%dh" % hours
        if minutes > 0:
            fmt = "%s %dmin" % (fmt, minutes)
    elif minutes > 5:
        fmt = "%dmin" % minutes
    elif minutes > 0:
        fmt = "%dmin" % minutes
        if seconds >= 30:
            fmt = "%s 30sec" % fmt
    elif seconds > 45:
        fmt = "< 1min"
    elif seconds > 30:
        fmt = "< 45sec"
    elif seconds > 15:
        fmt = "< 30sec"
    else:
        fmt = "%dsec" % seconds
    return fmt

def TransferProgress(progress, eta, changed_bytes, elapsed, speed, stalled):
    """Shortcut used for upload progress messages (verbosity 5)."""
    dots = int(0.4 * progress) # int(40.0 * progress / 100.0) -- for 40 chars
    data_amount = float(changed_bytes) / 1024.0
    data_scale = "KB"
    if data_amount > 1000.0:
        data_amount /= 1024.0
        data_scale = "MB"
    if data_amount > 1000.0:
        data_amount /= 1024.0
        data_scale = "GB"
    if stalled:
        eta_str = "Stalled!" 
        speed_amount = 0
        speed_scale = "B"
    else:
        eta_str = _RemainingSecs2Str(eta)
        speed_amount = float(speed) / 1024.0
        speed_scale = "KB"
        if speed_amount > 1000.0:
            speed_amount /= 1024.0
            speed_scale = "MB"
        if speed_amount > 1000.0:
            speed_amount /= 1024.0
            speed_scale = "GB"
    s = "%.1f%s %s [%.1f%s/s] [%s>%s] %d%% ETA %s" % (data_amount, data_scale,
                                                            _ElapsedSecs2Str(elapsed), 
                                                            speed_amount, speed_scale, 
                                                            '='*dots, ' '*(40-dots), 
                                                            progress, 
                                                            eta_str
                                                          )

    controlLine = "%d %d %d %d %d %d" % (changed_bytes, elapsed, progress, eta, speed, stalled)
    Log(s, NOTICE, InfoCode.upload_progress, controlLine)

def PrintCollectionStatus(col_stats, force_print=False):
    """Prints a collection status to the log"""
    Log(unicode(col_stats), 8, InfoCode.collection_status,
        '\n' + '\n'.join(col_stats.to_log_info()), force_print)

def Notice(s):
    """Shortcut used for notice messages (verbosity 3, the default)."""
    Log(s, NOTICE)

class WarningCode:
    """Enumeration class to hold warning code values.
       These values should never change, as frontends rely upon them.
       Don't use 0 or negative numbers."""
    generic = 1
    orphaned_sig = 2
    unnecessary_sig = 3
    unmatched_sig = 4
    incomplete_backup = 5
    orphaned_backup = 6
    ftp_ncftp_v320 = 7 # moved from error
    cannot_iterate = 8
    cannot_stat = 9
    cannot_read = 10
    no_sig_for_time = 11
    cannot_process = 12
    process_skipped = 13

def Warn(s, code=WarningCode.generic, extra=None):
    """Shortcut used for warning messages (verbosity 2)"""
    Log(s, WARNING, code, extra)

class ErrorCode:
    """Enumeration class to hold error code values.
       These values should never change, as frontends rely upon them.
       Don't use 0 or negative numbers.  This code is returned by duplicity
       to indicate which error occurred via both exit code and log."""
    generic = 1 # Don't use if possible, please create a new code and use it
    command_line = 2
    hostname_mismatch = 3
    no_manifests = 4
    mismatched_manifests = 5
    unreadable_manifests = 6
    cant_open_filelist = 7
    bad_url = 8
    bad_archive_dir = 9
    bad_sign_key = 10
    restore_dir_exists = 11
    verify_dir_doesnt_exist = 12
    backup_dir_doesnt_exist = 13
    file_prefix_error = 14
    globbing_error = 15
    redundant_inclusion = 16
    inc_without_sigs = 17
    no_sigs = 18
    restore_dir_not_found = 19
    no_restore_files = 20
    mismatched_hash = 21
    unsigned_volume = 22
    user_error = 23
    boto_old_style = 24
    boto_lib_too_old = 25
    boto_calling_format = 26
    ftp_ncftp_missing = 27
    ftp_ncftp_too_old = 28
    #ftp_ncftp_v320 = 29 # moved to warning
    exception = 30
    gpg_failed = 31
    s3_bucket_not_style = 32
    not_implemented = 33
    get_freespace_failed = 34
    not_enough_freespace = 35
    get_ulimit_failed = 36
    maxopen_too_low = 37
    connection_failed = 38
    restart_file_not_found = 39
    gio_not_available = 40
    source_dir_mismatch = 42 # 41 is reserved for par2
    ftps_lftp_missing = 43
    volume_wrong_size = 44
    enryption_mismatch = 45
    pythonoptimize_set = 46

    dpbx_nologin       = 47

    # 50->69 reserved for backend errors
    backend_error = 50
    backend_permission_denied = 51
    backend_not_found = 52
    backend_no_space = 53
    backend_command_error = 54
    backend_code_error    = 55

    # Reserve 126 because it is used as an error code for pkexec
    # Reserve 127 because it is used as an error code for pkexec
    # Reserve 255 because it is used as an error code for gksu

def Error(s, code=ErrorCode.generic, extra=None):
    """Write error message"""
    Log(s, ERROR, code, extra)

def FatalError(s, code=ErrorCode.generic, extra=None):
    """Write fatal error message and exit"""
    Log(s, ERROR, code, extra)
    shutdown()
    sys.exit(code)

class DupLogRecord(logging.LogRecord):
    """Custom log record that holds a message code"""
    def __init__(self, controlLine, *args, **kwargs):
        global _logger
        logging.LogRecord.__init__(self, *args, **kwargs)
        self.controlLine = controlLine
        self.levelName = LevelName(self.levelno)

class DupLogger(logging.Logger):
    """Custom logger that creates special code-bearing records"""
    # controlLine is a terrible hack until duplicity depends on Python 2.5
    # and its logging 'extra' keyword that allows a custom record dictionary.
    controlLine = None
    def makeRecord(self, name, lvl, fn, lno, msg, args, exc_info, *argv, **kwargs):
        return DupLogRecord(self.controlLine, name, lvl, fn, lno, msg, args, exc_info)

class OutFilter(logging.Filter):
    """Filter that only allows warning or less important messages"""
    def filter(self, record):
        return record.msg and record.levelno <= DupToLoggerLevel(WARNING)

class ErrFilter(logging.Filter):
    """Filter that only allows messages more important than warnings"""
    def filter(self, record):
        return record.msg and record.levelno > DupToLoggerLevel(WARNING)

def setup():
    """Initialize logging"""
    global _logger
    if _logger:
        return

    logging.setLoggerClass(DupLogger)
    _logger = logging.getLogger("duplicity")

    # Default verbosity allows notices and above
    setverbosity(NOTICE)

    # stdout and stderr are for different logging levels
    outHandler = logging.StreamHandler(sys.stdout)
    outHandler.addFilter(OutFilter())
    _logger.addHandler(outHandler)

    errHandler = logging.StreamHandler(sys.stderr)
    errHandler.addFilter(ErrFilter())
    _logger.addHandler(errHandler)

class MachineFormatter(logging.Formatter):
    """Formatter that creates messages in a syntax easily consumable by other
       processes."""
    def __init__(self):
        # 'message' will be appended by format()
        # Note that we use our own, custom-created 'levelName' instead of the
        # standard 'levelname'.  This is because the standard 'levelname' can
        # be adjusted by any library anywhere in our stack without us knowing.
        # But we control 'levelName'.
        logging.Formatter.__init__(self, "%(levelName)s %(controlLine)s")

    def format(self, record):
        s = logging.Formatter.format(self, record)

        # Add user-text hint of 'message' back in, with each line prefixed by a
        # dot, so consumers know it's not part of 'controlLine'
        if record.message:
            s += ('\n' + record.message).replace('\n', '\n. ')

        # Add a newline so consumers know the message is over.
        return s + '\n'

class MachineFilter(logging.Filter):
    """Filter that only allows levels that are consumable by other processes."""
    def filter(self, record):
        # We only want to allow records that have our custom level names
        return hasattr(record, 'levelName')

def add_fd(fd):
    """Add stream to which to write machine-readable logging"""
    global _logger
    handler = logging.StreamHandler(os.fdopen(fd, 'w'))
    handler.setFormatter(MachineFormatter())
    handler.addFilter(MachineFilter())
    _logger.addHandler(handler)

def add_file(filename):
    """Add file to which to write machine-readable logging"""
    global _logger
    handler = logging.FileHandler(filename)
    handler.setFormatter(MachineFormatter())
    handler.addFilter(MachineFilter())
    _logger.addHandler(handler)

def setverbosity(verb):
    """Set the verbosity level"""
    global _logger
    _logger.setLevel(DupToLoggerLevel(verb))

def getverbosity():
    """Get the verbosity level"""
    global _logger
    return LoggerToDupLevel(_logger.getEffectiveLevel())

def shutdown():
    """Cleanup and flush loggers"""
    logging.shutdown()


# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto
# Copyright 2008 Michael Terry <mike@mterry.name>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
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

def Log(s, verb_level, code=1):
    """Write s to stderr if verbosity level low enough"""
    global _logger
    # currentCode is a terrible hack until duplicity depends on Python 2.5
    # and its logging 'extra' keyword that allows a custom record dictionary.
    _logger.currentCode = code
    _logger.log(DupToLoggerLevel(verb_level), s)
    _logger.currentCode = 1

def Debug(s):
    """Shortcut used for debug message (verbosity 9)."""
    Log(s, DEBUG)

def Info(s):
    """Shortcut used for info messages (verbosity 5)."""
    Log(s, INFO)

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

def Warn(s, code=WarningCode.generic):
    """Shortcut used for warning messages (verbosity 2)"""
    Log(s, WARNING, code)

class ErrorCode:
    """Enumeration class to hold error code values.
       These values should never change, as frontends rely upon them.
       Don't use 0 or negative numbers.  This code is returned by duplicity
       to indicate which error occurred via both exit code and log."""
    generic = 1
    command_line = 2
    source_mismatch = 3

def FatalError(s, code=ErrorCode.generic):
    """Write fatal error message and exit"""
    Log(s, ERROR, code)
    sys.exit(code)

class DupLogRecord(logging.LogRecord):
    """Custom log record that holds a message code"""
    def __init__(self, code, *args, **kwargs):
        global _logger
        logging.LogRecord.__init__(self, *args, **kwargs)
        self.code = code

class DupLogger(logging.Logger):
    """Custom logger that creates special code-bearing records"""
    # currentCode is a terrible hack until duplicity depends on Python 2.5
    # and its logging 'extra' keyword that allows a custom record dictionary.
    currentCode = 1
    def makeRecord(self, name, lvl, fn, lno, msg, args, exc_info, *argv, **kwargs):
        return DupLogRecord(self.currentCode, name, lvl, fn, lno, msg, args, exc_info)

class OutFilter(logging.Filter):
    """Filter that only allows warning or less important messages"""
    def filter(self, record):
        return record.levelno <= DupToLoggerLevel(WARNING)

class ErrFilter(logging.Filter):
    """Filter that only allows messages more important than warnings"""
    def filter(self, record):
        return record.levelno > DupToLoggerLevel(WARNING)

def setup():
    """Initialize logging"""
    global _logger
    if _logger:
        return
    
    logging.setLoggerClass(DupLogger)
    _logger = logging.getLogger("duplicity")
    
    # Set up our special level names
    logging.addLevelName(DupToLoggerLevel(ERROR), "ERROR")
    logging.addLevelName(DupToLoggerLevel(WARNING), "WARNING")
    logging.addLevelName(DupToLoggerLevel(NOTICE), "NOTICE")
    logging.addLevelName(DupToLoggerLevel(INFO), "INFO")
    logging.addLevelName(DupToLoggerLevel(DEBUG), "DEBUG")
    
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
        logging.Formatter.__init__(self, "%(levelname)s %(code)s\n%(message)s")
    
    def format(self, record):
        s = logging.Formatter.format(self, record)
        # Indent each extra line with a dot and space so that the consumer
        # knows it's a continuation, not a new message.  Add a newline so
        # consumers know the message is over.
        return s.replace('\n', '\n. ') + '\n'

class MachineFilter(logging.Filter):
    """Filter that only allows levels that are consumable by other processes."""
    def filter(self, record):
        # We only want to allow records that have level names.  If the level
        # does not have an associated name, there will be a space as the
        # logging module expands levelname to "Level %d".  This will confuse
        # consumers.  Even if we dropped the space, random levels may not
        # mean anything to consumers.
        s = logging.getLevelName(record.levelno)
        return s.find(' ') == -1

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
    handler = logging.FileHandler(filename, 'w')
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


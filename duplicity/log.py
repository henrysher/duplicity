# Copyright 2002 Ben Escoto
#
# This file is part of duplicity.
#
# duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, Inc., 675 Mass Ave, Cambridge MA
# 02139, USA; either version 2 of the License, or (at your option) any
# later version; incorporated herein by reference.

"""Log various messages depending on verbosity level"""

import sys

verbosity = 3
termverbosity = 3

def Log(s, verb_level):
	"""Write s to stderr if verbosity level low enough"""
	if verb_level <= termverbosity:
		if verb_level <= 2: sys.stderr.write(s + "\n")
		else: sys.stdout.write(s + "\n")

def Warn(s):
	"""Shortcut used for warning messages (verbosity 2)"""
	Log(s, 2)

def FatalError(s):
	"""Write fatal error message and exit"""
	sys.stderr.write(s + "\n")
	sys.exit(1)

def setverbosity(verb, termverb = None):
	"""Set the verbosity level"""
	global verbosity, termverbosity
	verbosity = verb
	if termverb: termverbosity = termverb
	else: termverbosity = verb

# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2012 Canonical Ltd
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
import sys
import time

_this_dir = os.path.dirname(os.path.abspath(__file__))
_testing_dir = os.path.dirname(_this_dir)
_top_dir = os.path.dirname(_testing_dir)
_helpers_dir = os.path.join(_testing_dir, 'helpers')
_overrides_dir = os.path.join(_testing_dir, 'overrides')

# Adjust python path for duplicity and helper modules
sys.path = [_overrides_dir, _top_dir, _helpers_dir] + sys.path

# Also set PYTHONPATH for any subprocesses
os.environ['PYTHONPATH'] = _overrides_dir + ":" + _top_dir

# Now set some variables that help standardize test behavior
os.environ['LANG'] = ''
os.environ['GNUPGHOME'] = os.path.join(_testing_dir, 'gnupg')

# Standardize time
os.environ['TZ'] = 'US/Central'
time.tzset()

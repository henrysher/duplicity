# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2011 Henrique Carvalho Alves <hcarvalhoalves@gmail.com>
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

import duplicity.backend
from duplicity import globals
import sys
from _boto_multi import BotoBackend as BotoMultiUploadBackend
from _boto_single import BotoBackend as BotoSingleUploadBackend

if globals.s3_use_multiprocessing:
    if sys.version_info[:2] < (2, 6):
        print "Sorry, S3 multiprocessing requires version 2.6 or later of python"
        sys.exit(1)
    duplicity.backend.register_backend("gs", BotoMultiUploadBackend)
    duplicity.backend.register_backend("s3", BotoMultiUploadBackend)
    duplicity.backend.register_backend("s3+http", BotoMultiUploadBackend)
else:
    duplicity.backend.register_backend("gs", BotoSingleUploadBackend)
    duplicity.backend.register_backend("s3", BotoSingleUploadBackend)
    duplicity.backend.register_backend("s3+http", BotoSingleUploadBackend)

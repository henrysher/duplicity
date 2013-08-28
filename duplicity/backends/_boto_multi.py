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

import os
import sys
import threading
import Queue

import duplicity.backend

from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport
from duplicity.filechunkio import FileChunkIO
from duplicity import progress

from _boto_single import BotoBackend as BotoSingleBackend
from _boto_single import get_connection

# Multiprocessing is not supported on *BSD
if sys.platform not in ('darwin', 'linux2'):
    from multiprocessing import dummy as multiprocessing
    log.Debug('Multiprocessing is not supported on %s, will use threads instead.' % sys.platform)
else:
    import multiprocessing


class ConsumerThread(threading.Thread):
    """
    A background thread that collects all written bytes from all
    the pool workers, and reports it to the progress module.
    Wakes up every second to check for termination
    """
    def __init__(self, queue):
        super(ConsumerThread, self).__init__()
        self.daemon = True
        self.finish = False
        self.queue = queue

    def run(self):
        while not self.finish:
            try:
                args = self.queue.get(True, 1)
                progress.report_transfer(args[0], args[1])
            except Queue.Empty, e:
                pass


class BotoBackend(BotoSingleBackend):
    """
    Backend for Amazon's Simple Storage System, (aka Amazon S3), though
    the use of the boto module, (http://code.google.com/p/boto/).

    To make use of this backend you must set aws_access_key_id
    and aws_secret_access_key in your ~/.boto or /etc/boto.cfg
    with your Amazon Web Services key id and secret respectively.
    Alternatively you can export the environment variables
    AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
    """

    def upload(self, filename, key, headers=None):
        chunk_size = globals.s3_multipart_chunk_size

        # Check minimum chunk size for S3
        if chunk_size < globals.s3_multipart_minimum_chunk_size:
            log.Warn("Minimum chunk size is %d, but %d specified." % (
                globals.s3_multipart_minimum_chunk_size, chunk_size))
            chunk_size = globals.s3_multipart_minimum_chunk_size

        # Decide in how many chunks to upload
        bytes = os.path.getsize(filename)
        if bytes < chunk_size:
            chunks = 1
        else:
            chunks = bytes / chunk_size
            if (bytes % chunk_size):
                chunks += 1

        log.Debug("Uploading %d bytes in %d chunks" % (bytes, chunks))

        mp = self.bucket.initiate_multipart_upload(key.key, headers)

        # Initiate a queue to share progress data between the pool
        # workers and a consumer thread, that will collect and report
        queue = None
        if globals.progress:
            manager = multiprocessing.Manager()
            queue = manager.Queue()
            consumer = ConsumerThread(queue)
            consumer.start()

        number_of_procs = min(chunks, globals.s3_multipart_max_procs)
        log.Debug("Setting pool to %d processes" % number_of_procs)
        pool = multiprocessing.Pool(processes=number_of_procs)
        for n in range(chunks):
            params = [self.scheme, self.parsed_url,self.storage_uri, self.bucket_name,
                      mp.id, filename, n, chunk_size, globals.num_retries,
                      queue]
            pool.apply_async(multipart_upload_worker, params)
        pool.close()
        pool.join()

        # Terminate the consumer thread, if any
        if globals.progress:
            consumer.finish = True
            consumer.join()

        if len(mp.get_all_parts()) < chunks:
            mp.cancel_upload()
            raise BackendException("Multipart upload failed. Aborted.")

        return mp.complete_upload()


def multipart_upload_worker(scheme, parsed_url, bucket_name, storage_uri, multipart_id, filename,
                            offset, bytes, num_retries, queue):
    """
    Worker method for uploading a file chunk to S3 using multipart upload.
    Note that the file chunk is read into memory, so it's important to keep
    this number reasonably small.
    """
    import traceback

    def _upload_callback(uploaded, total):
        worker_name = multiprocessing.current_process().name
        log.Debug("%s: Uploaded %s/%s bytes" % (worker_name, uploaded, total))
        if not queue is None:
            queue.put([uploaded, total])  # Push data to the consumer thread

    def _upload(num_retries):
        worker_name = multiprocessing.current_process().name
        log.Debug("%s: Uploading chunk %d" % (worker_name, offset + 1))
        try:
            conn = get_connection(scheme, parsed_url, storage_uri)
            bucket = conn.lookup(bucket_name)

            for mp in bucket.get_all_multipart_uploads():
                if mp.id == multipart_id:
                    with FileChunkIO(filename, 'r', offset=offset * bytes, bytes=bytes) as fd:
                        mp.upload_part_from_file(fd, offset + 1, cb=_upload_callback,
                                                 num_cb=max(2, 8 * bytes / (1024 * 1024))
                                                 )  # Max num of callbacks = 8 times x megabyte
                    break
        except Exception, e:
            traceback.print_exc()
            if num_retries:
                log.Debug("%s: Upload of chunk %d failed. Retrying %d more times..." % (
                    worker_name, offset + 1, num_retries - 1))
                return _upload(num_retries - 1)
            log.Debug("%s: Upload of chunk %d failed. Aborting..." % (
                worker_name, offset + 1))
            raise e
        log.Debug("%s: Upload of chunk %d complete" % (worker_name, offset + 1))

    return _upload(num_retries)

duplicity.backend.register_backend("s3", BotoBackend)
duplicity.backend.register_backend("s3+http", BotoBackend)

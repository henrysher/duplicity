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
import time
import threading
import Queue

import duplicity.backend

from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport
from duplicity.util import exception_traceback
from duplicity.backend import retry
from duplicity.filechunkio import FileChunkIO
from duplicity import progress

BOTO_MIN_VERSION = "2.1.1"

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
            

def get_connection(scheme, parsed_url):
    try:
        import boto
        assert boto.Version >= BOTO_MIN_VERSION

        from boto.s3.connection import S3Connection
        assert hasattr(S3Connection, 'lookup')

        # Newer versions of boto default to using
        # virtual hosting for buckets as a result of
        # upstream deprecation of the old-style access
        # method by Amazon S3. This change is not
        # backwards compatible (in particular with
        # respect to upper case characters in bucket
        # names); so we default to forcing use of the
        # old-style method unless the user has
        # explicitly asked us to use new-style bucket
        # access.
        #
        # Note that if the user wants to use new-style
        # buckets, we use the subdomain calling form
        # rather than given the option of both
        # subdomain and vhost. The reason being that
        # anything addressable as a vhost, is also
        # addressable as a subdomain. Seeing as the
        # latter is mostly a convenience method of
        # allowing browse:able content semi-invisibly
        # being hosted on S3, the former format makes
        # a lot more sense for us to use - being
        # explicit about what is happening (the fact
        # that we are talking to S3 servers).

        try:
            from boto.s3.connection import OrdinaryCallingFormat
            from boto.s3.connection import SubdomainCallingFormat
            cfs_supported = True
            calling_format = OrdinaryCallingFormat()
        except ImportError:
            cfs_supported = False
            calling_format = None

        if globals.s3_use_new_style:
            if cfs_supported:
                calling_format = SubdomainCallingFormat()
            else:
                log.FatalError("Use of new-style (subdomain) S3 bucket addressing was"
                               "requested, but does not seem to be supported by the "
                               "boto library. Either you need to upgrade your boto "
                               "library or duplicity has failed to correctly detect "
                               "the appropriate support.",
                               log.ErrorCode.boto_old_style)
        else:
            if cfs_supported:
                calling_format = OrdinaryCallingFormat()
            else:
                calling_format = None

    except ImportError:
        log.FatalError("This backend (s3) requires boto library, version %s or later, "
                       "(http://code.google.com/p/boto/)." % BOTO_MIN_VERSION,
                       log.ErrorCode.boto_lib_too_old)

    if scheme == 's3+http':
        # Use the default Amazon S3 host.
        conn = S3Connection(is_secure=(not globals.s3_unencrypted_connection))
    else:
        assert scheme == 's3'
        conn = S3Connection(
            host = parsed_url.hostname,
            is_secure=(not globals.s3_unencrypted_connection))

    if hasattr(conn, 'calling_format'):
        if calling_format is None:
            log.FatalError("It seems we previously failed to detect support for calling "
                           "formats in the boto library, yet the support is there. This is "
                           "almost certainly a duplicity bug.",
                           log.ErrorCode.boto_calling_format)
        else:
            conn.calling_format = calling_format

    else:
        # Duplicity hangs if boto gets a null bucket name.
        # HC: Caught a socket error, trying to recover
        raise BackendException('Boto requires a bucket name.')
    return conn


class BotoBackend(duplicity.backend.Backend):
    """
    Backend for Amazon's Simple Storage System, (aka Amazon S3), though
    the use of the boto module, (http://code.google.com/p/boto/).

    To make use of this backend you must set aws_access_key_id
    and aws_secret_access_key in your ~/.boto or /etc/boto.cfg
    with your Amazon Web Services key id and secret respectively.
    Alternatively you can export the environment variables
    AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
    """

    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        from boto.s3.key import Key
        from boto.s3.multipart import MultiPartUpload

        # This folds the null prefix and all null parts, which means that:
        #  //MyBucket/ and //MyBucket are equivalent.
        #  //MyBucket//My///My/Prefix/ and //MyBucket/My/Prefix are equivalent.
        self.url_parts = filter(lambda x: x != '', parsed_url.path.split('/'))

        if self.url_parts:
            self.bucket_name = self.url_parts.pop(0)
        else:
            # Duplicity hangs if boto gets a null bucket name.
            # HC: Caught a socket error, trying to recover
            raise BackendException('Boto requires a bucket name.')

        self.scheme = parsed_url.scheme

        self.key_class = Key

        if self.url_parts:
            self.key_prefix = '%s/' % '/'.join(self.url_parts)
        else:
            self.key_prefix = ''

        self.straight_url = duplicity.backend.strip_auth_from_url(parsed_url)
        self.parsed_url = parsed_url
        self.resetConnection()

    def resetConnection(self):
        self.bucket = None
        self.conn = get_connection(self.scheme, self.parsed_url)
        self.bucket = self.conn.lookup(self.bucket_name)

    def put(self, source_path, remote_filename=None):
        from boto.s3.connection import Location
        if globals.s3_european_buckets:
            if not globals.s3_use_new_style:
                log.FatalError("European bucket creation was requested, but not new-style "
                               "bucket addressing (--s3-use-new-style)",
                               log.ErrorCode.s3_bucket_not_style)
        #Network glitch may prevent first few attempts of creating/looking up a bucket
        for n in range(1, globals.num_retries+1):
            if self.bucket:
                break
            if n > 1:
                time.sleep(30)
            try:
                try:
                    self.bucket = self.conn.get_bucket(self.bucket_name, validate=True)
                except Exception, e:
                    if "NoSuchBucket" in str(e):
                        if globals.s3_european_buckets:
                            self.bucket = self.conn.create_bucket(self.bucket_name,
                                                                  location=Location.EU)
                        else:
                            self.bucket = self.conn.create_bucket(self.bucket_name)
                    else:
                        raise e
            except Exception, e:
                log.Warn("Failed to create bucket (attempt #%d) '%s' failed (reason: %s: %s)"
                         "" % (n, self.bucket_name,
                               e.__class__.__name__,
                               str(e)))
                self.resetConnection()

        if not remote_filename:
            remote_filename = source_path.get_filename()
        key = self.key_prefix + remote_filename
        for n in range(1, globals.num_retries+1):
            if n > 1:
                # sleep before retry (new connection to a **hopeful** new host, so no need to wait so long)
                time.sleep(10)

            if globals.s3_use_rrs:
                storage_class = 'REDUCED_REDUNDANCY'
            else:
                storage_class = 'STANDARD'
            log.Info("Uploading %s/%s to %s Storage" % (self.straight_url, remote_filename, storage_class))
            try:
                headers = {
                    'Content-Type': 'application/octet-stream',
                    'x-amz-storage-class': storage_class
                }
                self.upload(source_path.name, key, headers)
                self.resetConnection()
                return
            except Exception, e:
                log.Warn("Upload '%s/%s' failed (attempt #%d, reason: %s: %s)"
                         "" % (self.straight_url,
                               remote_filename,
                               n,
                               e.__class__.__name__,
                               str(e)))
                log.Debug("Backtrace of previous error: %s" % (exception_traceback(),))
                self.resetConnection()
        log.Warn("Giving up trying to upload %s/%s after %d attempts" %
                 (self.straight_url, remote_filename, globals.num_retries))
        raise BackendException("Error uploading %s/%s" % (self.straight_url, remote_filename))

    def get(self, remote_filename, local_path):
        key = self.key_class(self.bucket)
        key.key = self.key_prefix + remote_filename
        for n in range(1, globals.num_retries+1):
            if n > 1:
                # sleep before retry (new connection to a **hopeful** new host, so no need to wait so long)
                time.sleep(10)
            log.Info("Downloading %s/%s" % (self.straight_url, remote_filename))
            try:
                key.get_contents_to_filename(local_path.name)
                local_path.setdata()
                self.resetConnection()
                return
            except Exception, e:
                log.Warn("Download %s/%s failed (attempt #%d, reason: %s: %s)"
                         "" % (self.straight_url,
                               remote_filename,
                               n,
                               e.__class__.__name__,
                               str(e)), 1)
                log.Debug("Backtrace of previous error: %s" % (exception_traceback(),))
                self.resetConnection()
        log.Warn("Giving up trying to download %s/%s after %d attempts" %
                (self.straight_url, remote_filename, globals.num_retries))
        raise BackendException("Error downloading %s/%s" % (self.straight_url, remote_filename))

    def _list(self):
        if not self.bucket:
            raise BackendException("No connection to backend")

        for n in range(1, globals.num_retries+1):
            if n > 1:
                # sleep before retry
                time.sleep(30)
            log.Info("Listing %s" % self.straight_url)
            try:
                return self._list_filenames_in_bucket()
            except Exception, e:
                log.Warn("List %s failed (attempt #%d, reason: %s: %s)"
                         "" % (self.straight_url,
                               n,
                               e.__class__.__name__,
                               str(e)), 1)
                log.Debug("Backtrace of previous error: %s" % (exception_traceback(),))
        log.Warn("Giving up trying to list %s after %d attempts" %
                (self.straight_url, globals.num_retries))
        raise BackendException("Error listng %s" % self.straight_url)

    def _list_filenames_in_bucket(self):
        # We add a 'd' to the prefix to make sure it is not null (for boto) and
        # to optimize the listing of our filenames, which always begin with 'd'.
        # This will cause a failure in the regression tests as below:
        #   FAIL: Test basic backend operations
        #   <tracback snipped>
        #   AssertionError: Got list: []
        #   Wanted: ['testfile']
        # Because of the need for this optimization, it should be left as is.
        #for k in self.bucket.list(prefix = self.key_prefix + 'd', delimiter = '/'):
        filename_list = []
        for k in self.bucket.list(prefix = self.key_prefix, delimiter = '/'):
            try:
                filename = k.key.replace(self.key_prefix, '', 1)
                filename_list.append(filename)
                log.Debug("Listed %s/%s" % (self.straight_url, filename))
            except AttributeError:
                pass
        return filename_list

    def delete(self, filename_list):
        for filename in filename_list:
            self.bucket.delete_key(self.key_prefix + filename)
            log.Debug("Deleted %s/%s" % (self.straight_url, filename))

    @retry
    def _query_file_info(self, filename, raise_errors=False):
        try:
            key = self.bucket.lookup(self.key_prefix + filename)
            if key is None:
                return {'size': -1}
            return {'size': key.size}
        except Exception, e:
            log.Warn("Query %s/%s failed: %s"
                     "" % (self.straight_url,
                           filename,
                           str(e)))
            self.resetConnection()
            if raise_errors:
                raise e
            else:
                return {'size': None}

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

        mp = self.bucket.initiate_multipart_upload(key, headers)

        # Initiate a queue to share progress data between the pool
        # workers and a consumer thread, that will collect and report
        queue = None
        if globals.progress:
            manager = multiprocessing.Manager()
            queue = manager.Queue()
            consumer = ConsumerThread(queue)
            consumer.start()

        pool = multiprocessing.Pool(processes=chunks)
        for n in range(chunks):
             params = [self.scheme, self.parsed_url, self.bucket_name, 
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


def multipart_upload_worker(scheme, parsed_url, bucket_name, multipart_id, filename,
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
            queue.put([uploaded, total]) # Push data to the consumer thread

    def _upload(num_retries):
        worker_name = multiprocessing.current_process().name
        log.Debug("%s: Uploading chunk %d" % (worker_name, offset + 1))
        try:
            conn = get_connection(scheme, parsed_url)
            bucket = conn.lookup(bucket_name)

            for mp in bucket.get_all_multipart_uploads():
                if mp.id == multipart_id:
                    with FileChunkIO(filename, 'r', offset=offset * bytes, bytes=bytes) as fd:
                        mp.upload_part_from_file(fd, offset + 1, cb=_upload_callback,
                                                    num_cb=max(2, 8 * bytes / (1024 * 1024))
                                                ) # Max num of callbacks = 8 times x megabyte
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

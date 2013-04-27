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
#
# @author: Juan Antonio Moya Vicen <juan@nowcomputing.com>
#
"""
Functions to compute progress of compress & upload files
The heuristics try to infer the ratio between the amount of data collected
by the deltas and the total size of the changing files. It also infers the
compression and encryption ration of the raw deltas before sending them to
the backend.
With the inferred ratios, the heuristics estimate the percentage of completion
and the time left to transfer all the (yet unknown) amount of data to send.
This is a forecast based on gathered evidence.
"""


import math
import threading
import time
from datetime import datetime, timedelta
from duplicity import globals
from duplicity import log
import pickle
import os

def import_non_local(name, custom_name=None):
    """
    This function is needed to play a trick... as there exists a local
    "collections" module, that is named the same as a system module
    """
    import imp, sys

    custom_name = custom_name or name

    f, pathname, desc = imp.find_module(name, sys.path[1:])
    module = imp.load_module(custom_name, f, pathname, desc)
    f.close()

    return module

"""
Import non-local module, use a custom name to differentiate it from local
This name is only used internally for identifying the module. We decide
the name in the local scope by assigning it to the variable sys_collections.
"""
sys_collections = import_non_local('collections','sys_collections')



tracker = None
progress_thread = None

class Snapshot(sys_collections.deque):
    """
    A convenience class for storing snapshots in a space/timing efficient manner
    Stores up to 10 consecutive progress snapshots, one for each volume
    """

    @staticmethod
    def unmarshall():
        """
        De-serializes cached data it if present
        """
        snapshot = Snapshot()
        # If restarting Full, discard marshalled data and start over
        if not globals.restart is None and globals.restart.start_vol >= 1:
            try:
                progressfd = open('%s/progress' % globals.archive_dir.name, 'r')
                snapshot = pickle.load(progressfd)
                progressfd.close()
            except:
                log.Warn("Warning, cannot read stored progress information from previous backup", log.WarningCode.cannot_stat) 
                snapshot = Snapshot()
        # Reached here no cached data found or wrong marshalling
        return snapshot
        
    def marshall(self):
        """
        Serializes object to cache
        """
        progressfd = open('%s/progress' % globals.archive_dir.name, 'w+')
        pickle.dump(self, progressfd)
        progressfd.close()


    def __init__(self, iterable = [], maxlen = 10):
        super(Snapshot, self).__init__(iterable, maxlen)
        self.last_vol = 0

    def get_snapshot(self, volume):
        nitems = len(self)
        if nitems <= 0:
            return 0.0
        return self[max(0, min(nitems + volume - self.last_vol - 1, nitems - 1))]

    def push_snapshot(self, volume, snapshot_data):
        self.append(snapshot_data)
        self.last_vol = volume

    def pop_snapshot(self):
        return self.popleft()

    def clear(self):
        super(Snapshot, self).clear()
        self.last_vol = 0



class ProgressTracker():

    def __init__(self):
        self.total_stats = None
        self.nsteps = 0
        self.start_time = None
        self.change_mean_ratio = 0.0
        self.change_r_estimation = 0.0
        self.progress_estimation = 0.0
        self.time_estimation = 0
        self.total_bytecount = 0
        self.last_total_bytecount = 0
        self.last_bytecount = 0
        self.stall_last_time = None
        self.last_time = None
        self.elapsed_sum = timedelta()
        self.speed = 0.0
        self.transfers = sys_collections.deque()
        self.is_full = False
        self.current_estimation = 0.0
        self.prev_estimation = 0.0
        self.prev_data = None
            
    def snapshot_progress(self, volume):
        """
        Snapshots the current progress status for each volume into the disk cache
        If backup is interrupted, next restart will deserialize the data and try start
        progress from the snapshot
        """
        if not self.prev_data is None:
            self.prev_data.push_snapshot(volume, self.progress_estimation)
            self.prev_data.marshall() 

    def has_collected_evidence(self):
        """
        Returns true if the progress computation is on and duplicity has not
        yet started the first dry-run pass to collect some information
        """
        return (not self.total_stats is None)
    
    def log_upload_progress(self):
        """
        Aproximative and evolving method of computing the progress of upload
        """
        if not globals.progress or not self.has_collected_evidence():
            return

        current_time = datetime.now()
        if self.start_time is None:
            self.start_time = current_time
        if not self.last_time is None:
            elapsed = (current_time - self.last_time)
        else:
            elapsed = timedelta()
        self.last_time = current_time
    
        # Detect (and report) a stallment if no changing data for more than 5 seconds
        if self.stall_last_time is None:
            self.stall_last_time = current_time
        if (current_time - self.stall_last_time).seconds > max(5, 2 * globals.progress_rate):
            log.TransferProgress(100.0 * self.progress_estimation, 
                                    self.time_estimation, self.total_bytecount, 
                                    (current_time - self.start_time).seconds,
                                    self.speed, 
                                    True
                                )
            return
    
        self.nsteps += 1
    
        """
        Compute the ratio of information being written for deltas vs file sizes
        Using Knuth algorithm to estimate approximate upper bound in % of completion
        The progress is estimated on the current bytes written vs the total bytes to
        change as estimated by a first-dry-run. The weight is the ratio of changing 
        data (Delta) against the total file sizes. (pessimistic estimation)
        The method computes the upper bound for the progress, when using a sufficient 
        large volsize to accomodate and changes, as using a small volsize may inject
        statistical noise.
        """
        from duplicity import diffdir
        changes = diffdir.stats.NewFileSize + diffdir.stats.ChangedFileSize
        total_changes = self.total_stats.NewFileSize + self.total_stats.ChangedFileSize
        if total_changes == 0 or diffdir.stats.RawDeltaSize == 0:
            return
    
        # Snapshot current values for progress
        last_progress_estimation = self.progress_estimation

        if self.is_full:
            # Compute mean ratio of data transfer, assuming 1:1 data density
            self.current_estimation = float(self.total_bytecount) / float(total_changes)
        else:
            # Compute mean ratio of data transfer, estimating unknown progress
            change_ratio = float(self.total_bytecount) / float(diffdir.stats.RawDeltaSize)
            change_delta = change_ratio - self.change_mean_ratio
            self.change_mean_ratio += change_delta / float(self.nsteps) # mean cumulated ratio
            self.change_r_estimation += change_delta * (change_ratio - self.change_mean_ratio)
            change_sigma = math.sqrt(math.fabs(self.change_r_estimation / float(self.nsteps)))
        
            """
            Combine variables for progress estimation
            Fit a smoothed curve that covers the most common data density distributions, aiming for a large number of incremental changes.
            The computation is:
                Use 50% confidence interval lower bound during first half of the progression. Conversely, use 50% C.I. upper bound during
                the second half. Scale it to the changes/total ratio
            """
            self.current_estimation = float(changes) / float(total_changes) * ( 
                                            (self.change_mean_ratio - 0.67 * change_sigma) * (1.0 - self.current_estimation) + 
                                            (self.change_mean_ratio + 0.67 * change_sigma) * self.current_estimation 
                                        )
            """
            In case that we overpassed the 100%, drop the confidence and trust more the mean as the sigma may be large.
            """
            if self.current_estimation > 1.0:
                self.current_estimation = float(changes) / float(total_changes) * ( 
                                                (self.change_mean_ratio - 0.33 * change_sigma) * (1.0 - self.current_estimation) + 
                                                (self.change_mean_ratio + 0.33 * change_sigma) * self.current_estimation 
                                            )
            """
            Meh!, if again overpassed the 100%, drop the confidence to 0 and trust only the mean.
            """
            if self.current_estimation > 1.0:
                self.current_estimation = self.change_mean_ratio * float(changes) / float(total_changes)

        """
        Lastly, just cap it... nothing else we can do to approximate it better. Cap it to 99%, as the remaining 1% to 100% we reserve it
        For the last step uploading of signature and manifests
        """
        self.progress_estimation = max(0.0, min(self.prev_estimation + (1.0 - self.prev_estimation) * self.current_estimation, 0.99))
    

        """
        Estimate the time just as a projection of the remaining time, fit to a [(1 - x) / x] curve
        """
        self.elapsed_sum += elapsed # As sum of timedeltas, so as to avoid clock skew in long runs (adding also microseconds)
        projection = 1.0
        if self.progress_estimation > 0:
            projection = (1.0 - self.progress_estimation) / self.progress_estimation
        self.time_estimation = long(projection * float(self.elapsed_sum.total_seconds()))

        # Apply values only when monotonic, so the estimates look more consistent to the human eye
        if self.progress_estimation < last_progress_estimation:
            self.progress_estimation = last_progress_estimation
    
        """
        Compute Exponential Moving Average of speed as bytes/sec of the last 30 probes
        """
        if elapsed.total_seconds() > 0: 
            self.transfers.append(float(self.total_bytecount - self.last_total_bytecount) / float(elapsed.total_seconds()))
        self.last_total_bytecount = self.total_bytecount
        if len(self.transfers) > 30:
            self.transfers.popleft()
        self.speed = 0.0
        for x in self.transfers:
            self.speed = 0.3 * x + 0.7 * self.speed

        log.TransferProgress(100.0 * self.progress_estimation, 
                                self.time_estimation, 
                                self.total_bytecount, 
                                (current_time - self.start_time).seconds, 
                                self.speed,
                                False
                            )
    
    
    def annotate_written_bytes(self, bytecount):
        """
        Annotate the number of bytes that have been added/changed since last time
        this function was called.
        bytecount param will show the number of bytes since the start of the current
        volume and for the current volume
        """
        changing = max(bytecount - self.last_bytecount, 0)
        self.total_bytecount += long(changing) # Annotate only changing bytes since last probe
        self.last_bytecount = bytecount
        if changing > 0:
            self.stall_last_time = datetime.now()
    
    def set_evidence(self, stats, is_full):
        """
        Stores the collected statistics from a first-pass dry-run, to use this
        information later so as to estimate progress
        """
        self.total_stats = stats
        self.is_full = is_full
            
    def set_start_volume(self, volume):
        self.prev_data = Snapshot.unmarshall()
        self.prev_estimation = self.prev_data.get_snapshot(volume)
        self.progress_estimation = max(0.0, min(self.prev_estimation, 0.99))

    def total_elapsed_seconds(self):
        """
        Elapsed seconds since the first call to log_upload_progress method
        """
        return (datetime.now() - self.start_time).seconds
    

def report_transfer(bytecount, totalbytes):
    """
    Method to call tracker.annotate_written_bytes from outside
    the class, and to offer the "function(long, long)" signature
    which is handy to pass as callback
    """
    global tracker
    global progress_thread
    if not progress_thread is None and not tracker is None:
        tracker.annotate_written_bytes(bytecount)


class LogProgressThread(threading.Thread):
    """
    Background thread that reports progress to the log, 
    every --progress-rate seconds 
    """
    def __init__(self):
        super(LogProgressThread, self).__init__()
        self.setDaemon(True)
        self.finished = False

    def run(self):
        global tracker
        if not globals.dry_run and globals.progress and tracker.has_collected_evidence():
            while not self.finished:
                tracker.log_upload_progress()
                time.sleep(globals.progress_rate)

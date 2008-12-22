# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto
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

"""
Asynchronous job scheduler, for concurrent execution with minimalistic
dependency guarantees.
"""

import duplicity
import duplicity.log as log
import sys
import gettext

from duplicity.dup_threading import require_threading
from duplicity.dup_threading import interruptably_wait
from duplicity.dup_threading import async_split
from duplicity.dup_threading import with_lock

thread    = duplicity.dup_threading.thread_module()
threading = duplicity.dup_threading.threading_module()

class AsyncScheduler:
    """
    Easy-to-use scheduler of function calls to be executed
    concurrently. A very simple dependency mechanism exists in the
    form of barriers (see insert_barrier()).

    Each instance has a concurrency level associated with it. A
    concurrency of 0 implies that all tasks will be executed
    synchronously when scheduled. A concurrency of 1 indicates that a
    task will be executed asynchronously, but never concurrently with
    other tasks. Both 0 and 1 guarantee strict ordering among all
    tasks (i.e., they will be executed in the order scheduled).

    At concurrency levels above 1, the tasks will end up being
    executed in an order undetermined except insofar as is enforced by
    calls to insert_barrier().

    An AsynchScheduler should be created for any independent process;
    the scheduler will assume that if any background job fails (raises
    an exception), it makes further work moot.
    """

    def __init__(self, concurrency):
        """
        Create an asynchronous scheduler that executes jobs with the
        given level of concurrency.
        """
        log.Info("%s: %s" % (self.__class__.__name__,
                             _("instantiating at concurrency %d") %
                               (concurrency)))
        assert concurrency >= 0, "%s concurrency level must be >= 0" % (self.__class__.__name__,)

        self.__failed       = False        # has at least one task failed so far?
        self.__failed_waiter = None        # when __failed, the waiter of the first task that failed
        self.__concurrency  = concurrency
        self.__curconc      = 0            # current concurrency level (number of workers)
        self.__workers      = 0            # number of active workers
        self.__q            = []
        self.__cv           = threading.Condition() # for simplicity, we use a single cv with its lock
                                                    # for everything, even if the resulting notifyAll():s
                                                    # are not technically efficient.

        if concurrency > 0:
            require_threading("concurrency > 0 (%d)" % (concurrency,))

    def insert_barrier(self):
        """
        Proclaim that any tasks scheduled prior to the call to this
        method MUST be executed prior to any tasks scheduled after the
        call to this method.

        The intended use case is that if task B depends on A, a
        barrier must be inserted in between to guarantee that A
        happens before B.
        """
        log.Debug("%s: %s" % (self.__class__.__name__, _("inserting barrier")))
        # With concurrency 0 it's a NOOP, and due to the special case in
        # task scheduling we do not want to append to the queue (will never
        # be popped).
        if self.__concurrency > 0:
            def _insert_barrier():
                self.__q.append(None) # None in queue indicates barrier
                self.__cv.notifyAll()
                
            with_lock(self.__cv, _insert_barrier)

    def schedule_task(self, fn, params):
        """
        Schedule the given task (callable, typically function) for
        execution. Pass the given parameters to the function when
        calling it. Returns a callable which can optionally be used
        to wait for the task to complete, either by returning its
        return value or by propagating any exception raised by said
        task.

        This method may block or return immediately, depending on the
        configuration and state of the scheduler.

        This method may also raise an exception in order to trigger
        failures early, if the task (if run synchronously) or a previous
        task has already failed.

        NOTE: Pay particular attention to the scope in which this is
        called. In particular, since it will execute concurrently in
        the background, assuming fn is a closure, any variables used
        most be properly bound in the closure. This is the reason for
        the convenience feature of being able to give parameters to
        the call, to avoid having to wrap the call itself in a
        function in order to "fixate" variables in, for example, an
        enclosing loop.
        """
        assert fn is not None

        # Note: It is on purpose that we keep track of concurrency in
        # the front end and launch threads for each task, rather than
        # keep a pool of workers. The overhead is not relevant in the
        # situation this will be used, and it removes complexity in
        # terms of ensuring the scheduler is garbage collected/shut
        # down properly when no longer referenced/needed by calling
        # code.

        if self.__concurrency == 0:
            # special case this to not require any platform support for
            # threading at all
            log.Info("%s: %s" % (self.__class__.__name__,
                     _("running task synchronously (asynchronicity disabled)")))

            return self.__run_synchronously(fn, params)
        else:
            log.Info("%s: %s" % (self.__class__.__name__,
                     _("scheduling task for asynchronous execution")))

            return self.__run_asynchronously(fn, params)

    def wait(self):
        """
        Wait for the scheduler to become entirely empty (i.e., all
        tasks having run to completion).

        IMPORTANT: This is only useful with a single caller scheduling
        tasks, such that no call to schedule_task() is currently in
        progress or may happen subsequently to the call to wait().
        """
        def _wait():
            interruptably_wait(self.__cv, lambda: self.__curconc == 0 and len(self.__q) == 0)

        with_lock(self.__cv, _wait)

    def __run_synchronously(self, fn, params):
        success = False

        # When running synchronously, we immediately leak any exception raised
        # for immediate failure reporting to calling code.
        ret = fn(*params)

        def _waiter():
            return ret

        log.Info("%s: %s" % (self.__class__.__name__,
                 _("task completed successfully")))

        return _waiter

    def __run_asynchronously(self, fn, params):
        (waiter, caller) = async_split(lambda: fn(*params))

        def _sched():
            if self.__failed:
                # note that __start_worker() below may block waiting on
                # task execution; if so we will be one task scheduling too
                # late triggering the failure. this should be improved.
                log.Info("%s: %s" % (self.__class__.__name__,
                         _("a previously scheduled task has failed; "
                           "propagating the result immediately")))
                self.__waiter()
                raise AssertionError("%s: waiter should have raised an exception; "
                                     "this is a bug" % (self.__class__.__name__,))

            self.__q.append(caller)

            free_workers = self.__workers - self.__curconc

            log.Debug("%s: %s" % (self.__class__.__name__,
                      gettext.ngettext("tasks queue length post-schedule: %d task",
                                       "tasks queue length post-schedule: %d tasks",
                                       len(self.__q)) % len(self.__q)))
            
            assert free_workers >= 0

            if free_workers == 0:
                self.__start_worker()
        
        with_lock(self.__cv, _sched)

        return waiter

    def __start_worker(self):
        """
        Start a new worker; self.__cv must be acquired.
        """
        while self.__workers >= self.__concurrency:
            log.Info("%s: %s" % (self.__class__.__name__,
                     gettext.ngettext("no free worker slots (%d worker, and maximum "
                                      "concurrency is %d) - waiting for a background "
                                      "task to complete",
                                      "no free worker slots (%d workers, and maximum "
                                      "concurrency is %d) - waiting for a background "
                                      "task to complete", self.__workers) %
                                      (self.__workers, self.__concurrency)))
            self.__cv.wait()

        self.__workers += 1

        thread.start_new_thread(lambda: self.__worker_thread(), ())

    def __worker_thread(self):
        """
        The worker thread main loop.
        """
        # Each worker loops around waiting for work. The exception is
        # when there is no work to do right now and there is no work
        # scheduled - when this happens, all workers shut down. This
        # is to remove the need for explicit shutdown by calling code.

        done = [False]       # use list for destructive mod. in closure
        while not done[0]:
            def _prepwork():
                def workorbarrier_pending():
                    return (len(self.__q) > 0)
                def tasks_running():
                    return (self.__curconc > 0)
                def barrier_pending():
                    return (workorbarrier_pending() and self.__q[0] is None)
                
                while (not workorbarrier_pending()) or \
                      (barrier_pending() and tasks_running()):
                    if (not workorbarrier_pending()) and (not tasks_running()):
                        # no work, and no tasks in progress - quit as per comments above
                        done[0] = True
                        self.__workers -= 1
                        self.__cv.notifyAll()
                        return None
                    self.__cv.wait()
                
                # there is work to do
                work = self.__q.pop(0)

                log.Debug("%s: %s" % (self.__class__.__name__,
                          gettext.ngettext("tasks queue length post-grab: %d task",
                                           "tasks queue length post-grab: %d tasks",
                                           len(self.__q)) % len(self.__q)))

                if work: # real work, not just barrier
                    self.__curconc += 1
                    self.__cv.notifyAll()

                return work
            
            work = with_lock(self.__cv, _prepwork)

            if work:
                # the actual work here is going to be the caller half
                # of an async_split() result, which will not propagate
                # errors back to us, but rather propagate it back to
                # the "other half".
                succeeded, waiter = work()
                if not succeeded:
                    def _signal_failed():
                        if not self.__failed:
                            self.__failed = True
                            self.__waiter = waiter
                    with_lock(self.__cv, _signal_failed)

                log.Info("%s: %s" % (self.__class__.__name__,
                         _("task execution done (success: %s)") % succeeded))

                def _postwork():
                    self.__curconc -= 1
                    self.__cv.notifyAll()

                with_lock(self.__cv, _postwork)
        

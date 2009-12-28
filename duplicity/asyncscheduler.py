# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
# Copyright 2008 Peter Schuller <peter.schuller@infidyne.com>
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

"""
Asynchronous job scheduler, for concurrent execution with minimalistic
dependency guarantees.
"""

import duplicity
from duplicity import log
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

        self.__failed        = False        # has at least one task failed so far?
        self.__failed_waiter = None         # when __failed, the waiter of the first task that failed
        self.__concurrency   = concurrency
        self.__worker_count  = 0            # number of active workers
        self.__waiter_count  = 0            # number of threads waiting to submit work
        self.__barrier       = False        # barrier currently in effect?
        self.__cv            = threading.Condition() # for simplicity, we use a single cv with its lock
#                                                    # for everything, even if the resulting notifyAll():s
#                                                    # are not technically efficient.

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
                self.__barrier = True

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
                     _("running task synchronously (asynchronicity disabled)")),
                     log.InfoCode.synchronous_upload_begin)

            return self.__run_synchronously(fn, params)
        else:
            log.Info("%s: %s" % (self.__class__.__name__,
                     _("scheduling task for asynchronous execution")),
                     log.InfoCode.asynchronous_upload_begin)

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
            interruptably_wait(self.__cv, lambda: self.__worker_count == 0 and self.__waiter_count == 0)

        with_lock(self.__cv, _wait)

    def __run_synchronously(self, fn, params):

        # When running synchronously, we immediately leak any exception raised
        # for immediate failure reporting to calling code.
        ret = fn(*params)

        def _waiter():
            return ret

        log.Info("%s: %s" % (self.__class__.__name__,
                 _("task completed successfully")),
                 log.InfoCode.synchronous_upload_done)

        return _waiter

    def __run_asynchronously(self, fn, params):
        (waiter, caller) = async_split(lambda: fn(*params))

        def check_pending_failure():
            if self.__failed:
                log.Info("%s: %s" % (self.__class__.__name__,
                         _("a previously scheduled task has failed; "
                           "propagating the result immediately")),
                         log.InfoCode.asynchronous_upload_done)
                self.__failed_waiter()
                raise AssertionError("%s: waiter should have raised an exception; "
                                     "this is a bug" % (self.__class__.__name__,))

        def wait_for_and_register_launch():
            check_pending_failure()    # raise on fail
            while self.__worker_count >= self.__concurrency or self.__barrier:
                if self.__worker_count == 0:
                    assert self.__barrier, "barrier should be in effect"
                    self.__barrier = False
                    self.__cv.notifyAll()
                else:
                    self.__waiter_count += 1
                    self.__cv.wait()
                    self.__waiter_count -= 1

                check_pending_failure() # raise on fail

            self.__worker_count += 1
            log.Debug("%s: %s" % (self.__class__.__name__,
                                  _("active workers = %d") % (self.__worker_count,)))

        # simply wait for an OK condition to start, then launch our worker. the worker
        # never waits on us, we just wait for them.
        with_lock(self.__cv, wait_for_and_register_launch)

        self.__start_worker(caller)

        return waiter

    def __start_worker(self, caller):
        """
        Start a new worker.
        """
        def trampoline():
            try:
                self.__execute_caller(caller)
            finally:
                def complete_worker():
                    self.__worker_count -= 1
                    log.Debug("%s: %s" % (self.__class__.__name__,
                                          _("active workers = %d") % (self.__worker_count,)))
                    self.__cv.notifyAll()
                with_lock(self.__cv, complete_worker)

        thread.start_new_thread(trampoline, ())

    def __execute_caller(self, caller):
            # The caller half that we get here will not propagate
            # errors back to us, but rather propagate it back to the
            # "other half" of the async split.
            succeeded, waiter = caller()
            if not succeeded:
                def _signal_failed():
                    if not self.__failed:
                        self.__failed = True
                        self.__failed_waiter = waiter
                        self.__cv.notifyAll()
                with_lock(self.__cv, _signal_failed)

            log.Info("%s: %s" % (self.__class__.__name__,
                     _("task execution done (success: %s)") % succeeded),
                     log.InfoCode.asynchronous_upload_done)

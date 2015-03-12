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

"""
Duplicity specific but otherwise generic threading interfaces and
utilities.

(Not called "threading" because we do not want to conflict with
the standard threading module, and absolute imports require
at least python 2.5.)
"""

_threading_supported = True

try:
    import thread
except ImportError:
    import dummy_thread as thread
    _threading_supported = False

try:
    import threading
except ImportError:
    import dummy_threading as threading
    _threading_supported = False

import sys

from duplicity import errors


def threading_supported():
    """
    Returns whether threading is supported on the system we are
    running on.
    """
    return _threading_supported


def require_threading(reason=None):
    """
    Assert that threading is required for operation to continue. Raise
    an appropriate exception if this is not the case.

    Reason specifies an optional reason why threading is required,
    which will be used for error reporting in case threading is not
    supported.
    """
    if not threading_supported():
        if reason is None:
            reason = "(no reason given)"
        raise errors.NotSupported("threading was needed because [%s], but "
                                  "is not supported by the python "
                                  "interpreter" % (reason,))


def thread_module():
    """
    Returns the thread module, or dummy_thread if threading is not
    supported.
    """
    return thread


def threading_module():
    """
    Returns the threading module, or dummy_thread if threading is not
    supported.
    """
    return threading


def with_lock(lock, fn):
    """
    Call fn with lock acquired. Guarantee that lock is released upon
    the return of fn.

    Returns the value returned by fn, or raises the exception raised
    by fn.

    (Lock can actually be anything responding to acquire() and
    release().)
    """
    lock.acquire()

    try:
        return fn()
    finally:
        lock.release()


def interruptably_wait(cv, waitFor):
    """
    cv   - The threading.Condition instance to wait on
    test - Callable returning a boolean to indicate whether
           the criteria being waited on has been satisfied.

    Perform a wait on a condition such that it is keyboard
    interruptable when done in the main thread. Due to Python
    limitations as of <= 2.5, lock acquisition and conditions waits
    are not interruptable when performed in the main thread.

    Currently, this comes at a cost additional CPU use, compared to a
    normal wait. Future implementations may be more efficient if the
    underlying python supports it.

    The condition must be acquired.

    This function should only be used on conditions that are never
    expected to be acquired for extended periods of time, or the
    lock-acquire of the underlying condition could cause an
    uninterruptable state despite the efforts of this function.

    There is no equivalent for acquireing a lock, as that cannot be
    done efficiently.

    Example:

    Instead of:

      cv.acquire()
      while not thing_done:
        cv.wait(someTimeout)
      cv.release()

    do:

      cv.acquire()
      interruptable_condwait(cv, lambda: thing_done)
      cv.release()

    """
    # We can either poll at some interval, or wait with a short enough
    # timeout to be practical (i.e., such that it interactively seems
    # to response semi-immediately to an interrupt).
    #
    # Both approaches waste CPU, but the latter approach does not
    # imply a latency penalty in the common case of a
    # notify.
    while not waitFor():
        cv.wait(0.1)


def async_split(fn):
    """
    Splits the act of calling the given function into one front-end
    part for waiting on the result, and a back-end part for performing
    the work in another thread.

    Returns (waiter, caller) where waiter is a function to be called
    in order to wait for the results of an asynchronous invokation of
    fn to complete, returning fn's result or propagating it's
    exception.

    Caller is the function to call in a background thread in order to
    execute fn asynchronously. Caller will return (success, waiter)
    where success is a boolean indicating whether the function
    suceeded (did NOT raise an exception), and waiter is the waiter
    that was originally returned by the call to async_split().
    """
    # Implementation notes:
    #
    # We use a dictionary to track the state of the asynchronous call,
    # rather than local variables. This is to get around the way
    # closures work with respect to local variables in Python. We do
    # not care about hash lookup overhead since this is intended to be
    # used for significant amounts of work.

    cv = threading.Condition()  # @UndefinedVariable
    state = {'done': False,
             'error': None,
             'trace': None,
             'value': None}

    def waiter():
        cv.acquire()
        try:
            interruptably_wait(cv, lambda: state['done'])

            if state['error'] is None:
                return state['value']
            else:
                raise state['error'].with_traceback(state['trace'])
        finally:
            cv.release()

    def caller():
        try:
            value = fn()

            cv.acquire()
            state['done'] = True
            state['value'] = value
            cv.notify()
            cv.release()

            return (True, waiter)
        except Exception as e:
            cv.acquire()
            state['done'] = True
            state['error'] = e
            state['trace'] = sys.exc_info()[2]
            cv.notify()
            cv.release()

            return (False, waiter)

    return (waiter, caller)


class Value:
    """
    A thread-safe container of a reference to an object (but not the
    object itself).

    In particular this means it is safe to:

      value.set(1)

    But unsafe to:

      value.get()['key'] = value

    Where the latter must be done using something like:

      def _setprop():
        value.get()['key'] = value

      with_lock(value, _setprop)

    Operations such as increments are best done as:

      value.transform(lambda val: val + 1)
    """

    def __init__(self, value=None):
        """
        Initialuze with the given value.
        """
        self.__value = value

        self.__cv = threading.Condition()  # @UndefinedVariable

    def get(self):
        """
        Returns the value protected by this Value.
        """
        return with_lock(self.__cv, lambda: self.__value)

    def set(self, value):
        """
        Resets the value protected by this Value.
        """
        def _set():
            self.__value = value

        with_lock(self.__cv, _set)

    def transform(self, fn):
        """
        Call fn with the current value as the parameter, and reset the
        value to the return value of fn.

        During the execution of fn, all other access to this Value is
        prevented.

        If fn raised an exception, the value is not reset.

        Returns the value returned by fn, or raises the exception
        raised by fn.
        """
        def _transform():
            self.__value = fn(self.__value)
            return self.__value

        return with_lock(self.cv, _transform)

    def acquire(self):
        """
        Acquire this Value for mutually exclusive access. Only ever
        needed when calling code must perform operations that cannot
        be done with get(), set() or transform().
        """
        self.__cv.acquire()

    def release(self):
        """
        Release this Value for mutually exclusive access.
        """
        self.__cv.release()

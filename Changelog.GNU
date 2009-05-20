2009-05-14  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/collections.py, duplicity/diffdir.py:
    Checkpoint and abandon this approach.  The idea of splitting the signature files was good, however, it will greatly increase the number of open file handles.  Six per sig file, all open at the same time would be way too much.

    I'll look into this again when I rewrite duplicity and untangle the parallel nested iterators it uses.

    * duplicity/backends/cloudfilesbackend.py: Correct copyright.

2009-05-13  Kenneth Loafman  <kenneth@loafman.com>

    * .settings/org.eclipse.core.resources.prefs: Reset file type preferences.

    * CHANGELOG, duplicity-bin: Changed from using ulimit external command to
    resource.getrlimit to check open files limit.

    * CHANGELOG, duplicity.1, duplicity/backends/tahoebackend.py, duplicity/commandline.py:
    patch #6743: Tahoe backend for duplicity
    https://savannah.nongnu.org/patch/?6743

    * CHANGELOG, duplicity/GnuPGInterface.py:
    Only half of this bug is fixed but it's still useful.
    bug #21792: pipe call fails with an error OSError:
                [Errno 24] Too many open files
    https://savannah.nongnu.org/bugs/?21792

2009-05-07  Kenneth Loafman  <kenneth@loafman.com>

    * .settings/org.eclipse.core.resources.prefs, duplicity/log.py, duplicity.1:
    Added support for RackSpace's CloudFiles, cf+http.

    * duplicity/backends/cloudfilesbackend.py:
    Add more detail on connection failure.

    * CHANGELOG, duplicity/backends/__init__.py, duplicity/backends/cloudfilesbackend.py, duplicity/commandline.py, duplicity/log.py:
    Added support for RackSpace's CloudFiles, cf+http.

2009-05-05  Kenneth Loafman  <kenneth@loafman.com>

    * .project, .pydevproject, CHANGELOG, Changelog.GNU, dist/makedist, duplicity-bin, duplicity/collections.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/file_naming.py, duplicity/gpg.py, duplicity/log.py, duplicity/manifest.py, duplicity/selection.py, testing/config.py.tmpl, testing/file_namingtest.py, testing/roottest.py:
    Merge changes from 0.5.17 and checkpoint current work.

2009-05-04  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/__init__.py, duplicity/backends/__init__.py:
    Make sure gettext is installed at the module level.

    * Changelog.GNU, CHANGELOG: Changes for 0.5.17.

2009-05-02  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Checkpoint.

    * duplicity/selection.py: The previous revision got the wrong comment, so
    I cleaned up some code and checked back in.  The
    correct release comment should be:

    patch #6814: Ignore comments in filelists
    https://savannah.nongnu.org/patch/?6814

    * duplicity/diffdir.py, duplicity/selection.py:
    patch #6813: Making changelist easy to read
    https://savannah.nongnu.org/patch/?6813

    * duplicity-bin: Moved from using the df command to get temp space
    availability to Python's os.statvfs() call.  Not all df
    commands work the same way.

2009-04-22  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity-bin:
    I had put in some trial code that I removed incompletely that forced
    a full backup action.  This removes the last line of that code.

2009-04-21  Kenneth Loafman  <kenneth@loafman.com>

    * .pydevproject, CHANGELOG, Changelog.GNU: Changes for 0.5.16.

    * dist/makedist: Remove check for only one $version string.

    * duplicity-bin: Reduce max_open_files limit needed to 1024, was 2048.

    * duplicity-bin: Fix argument list in FatalError call re max open files.

    * duplicity/log.py: bug #24825: duplicity warn on insufficient TMPDIR
                space availability and low max open
                file limits pre-backup.
    https://savannah.nongnu.org/bugs/?24825

    * duplicity/collections.py, duplicity/gpg.py:
    bug #25976: Password requested when not needed.
    https://savannah.nongnu.org/bugs/?25976

    * duplicity-bin: bug #24825: duplicity warn on insufficient TMPDIR
                space availability and low max open
                file limits pre-backup.
    https://savannah.nongnu.org/bugs/?24825

    bug #25976: Password requested when not needed.
    https://savannah.nongnu.org/bugs/?25976

    * testing/config.py.tmpl: Make sure gettext is included first.
    Add variable at top of file for verbosity.

    * duplicity/selection.py:
    Use os.access() check on regular files and dirs only.

    * duplicity/manifest.py: Add some documentation.

    * duplicity/commandline.py:
    Added tilde and variable expansion to the source or
    target argument that is not a URL.

    * duplicity/__init__.py, duplicity/backends/__init__.py:
    Make sure gettext is available by importing first.

2009-04-13  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends/imapbackend.py, duplicity/backends/sshbackend.py, duplicity/commandline.py, duplicity/globals.py:
    Move ssh and imap backend globals to globals.py.

2009-04-12  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/file_naming.py, testing/file_namingtest.py:
    patch #6806: More graceful handling of old
                 --short-filename files
    https://savannah.nongnu.org/patch/?6806

2009-04-10  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/diffdir.py: bug #25594: wrong backup statistics
    https://savannah.nongnu.org/bugs/?25594

    * .settings/.cvsignore: Not needed.

2009-04-09  Kenneth Loafman  <kenneth@loafman.com>

    * Changelog.GNU, CHANGELOG, duplicity/.cvsignore: Changes for 0.5.15.

    * duplicity/selection.py:
    If a file is unreadable due to access rights or other
    non-fatal errors, put out error message and continue
    rather than dying messily with a traceback.

    * duplicity-bin: Move SystemExit function back to the top and put
    a large note NOT to move it back down, otherwise,
    Exception gets invoked instead.

    * duplicity/commandline.py: Remove "--restore-dir" from options[].
     It's not an option and never has been.

    * CHANGELOG, duplicity/commandline.py:
    Added tilde '~' expansion and variable expansion in the
    options that require a filename.  You can now have this
    "--archive-dir=~/ArchDir/$SYSNAME" if you need it.  No
    expansion is applied to the source or target URL's.

2009-04-07  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/ftpbackend.py:
    Unit tests were failing for ftp because of the filtering for
    duplicity-only filenames.  Corrected this and removed
    the check for the filename in the first element.

    * CHANGELOG, duplicity/robust.py:
    If a file is unreadable due to access rights or other non-
    fatal errors, put out error message and continue.

2009-04-03  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/ftpbackend.py:
    FTP backend was failing on PureFTPd when the "-x ''"
    option was removed from the second ncftpls popen, a fix
    that was implemented due to bug #24741.  This fix does
    the ls in one pass by extracting either the first or the
    last entry on the 'ls -l'.  [Standard FTP would be nice!]

2009-04-02  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, Changelog.GNU: Changes for 0.5.14.

    * CHANGELOG, Changelog.GNU, duplicity-bin, duplicity/asyncscheduler.py, duplicity/backend.py, duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/imapbackend.py, duplicity/backends/localbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_threading.py, duplicity/dup_time.py, duplicity/file_naming.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/statistics.py, duplicity/tempdir.py, rdiffdir, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/manifesttest.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/selectiontest.py, testing/statictest.py, testing/statisticstest.py, testing/tempdirtest.py, testing/test_tarfile.py:
    Normalized include statements and tried to insure that all
    duplicity includes were from the duplicity module.

2009-04-01  Kenneth Loafman  <kenneth@loafman.com>

    * po/Makevars, CHANGELOG, COPYING, dist/makedist, dist/makerpm, dist/makeweb, dist/setup.py, duplicity-bin, duplicity/__init__.py, duplicity/_librsyncmodule.c, duplicity/asyncscheduler.py, duplicity/backend.py, duplicity/backends/__init__.py, duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/hsibackend.py, duplicity/backends/imapbackend.py, duplicity/backends/localbackend.py, duplicity/backends/rsyncbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/compilec.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_threading.py, duplicity/dup_time.py, duplicity/errors.py, duplicity/file_naming.py, duplicity/globals.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/static.py, duplicity/statistics.py, duplicity/tempdir.py, duplicity/util.py, rdiffdir, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/config.py.tmpl, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/logtest.py, testing/manifesttest.py, testing/misctest.py, testing/parsedurltest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/run-a-test.sh, testing/run-all-tests.sh, testing/run-coverage.sh, testing/selectiontest.py, testing/statictest.py, testing/statisticstest.py, testing/tempdirtest.py, testing/test_tarfile.py:
    After email voting among known duplicity contributors,
    the decision was reached to revert to the GPL Version 2
    license, so with their consensus, duplicity is now under
    GPL Version 2.

2009-03-31  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity.1, CHANGELOG, duplicity/commandline.py:
    The -vN option has not changed.  Verbosity may also be one
    of: character [ewnid], or word ['error', 'warning', 'notice',
     'info', 'debug'].  The default is 4 (Notice).  The options
     -v4, -vn, and -vnotice are functionally equivalent, as are
     the mixed-case versions, -vN, -vNotice, -vNOTICE.

2009-03-30  Kenneth Loafman  <kenneth@loafman.com>

    * testing/GnuPGInterfacetest.py:
    Add '../' to Python path so we find our GnuPGInterface and not another.

    * CHANGELOG, duplicity.1, duplicity/commandline.py, duplicity/log.py, duplicity/selection.py:
    patch #6790: Add --exclude-if-present
    https://savannah.nongnu.org/patch/?6790

    * CHANGELOG: Clarify recent log entries.

2009-03-29  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin, duplicity/backend.py, duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/imapbackend.py, duplicity/backends/localbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/lazy.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/tempdir.py, testing/file_namingtest.py:
    Changed from log.Log with numbered log levels to log.Debug,
    log.Info, log.Notice, log.Warn, log.FatalError as below:
        0  log.FatalError
        1  log.Warn
        2  log.Warn
        3  log.Notice
        4  log.Notice
        5  log.Info
        6  log.Info
        7  log.Info
        8  log.Info
        9 log.Debug
    The -vN option has not changed at this point.

    * CHANGELOG, duplicity/backends/ftpbackend.py, duplicity/log.py:
    Revert to calling NcFTP utilities (ls, get, put) directly
    rather than scripting ncftp via pexpect.  Move fatal error
    regarding version 3.2.0 to a warning message since it has
    been reported that the segfault problem does not occur on
    most distributions.

2009-03-26  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, Changelog.GNU, dist/makedist, dist/mkGNUChangelog.sh:
    Add Changelog.GNU to website and distribution to add a bit of detail
    showing the CVS changes via rcs2log.  Added dist/mkGNUChangelog.sh.

2009-03-25  Kenneth Loafman  <kenneth@loafman.com>

    * testing/.cvsignore: Add testing/manual dir.

    * CHANGELOG, duplicity-bin, duplicity.1, duplicity/commandline.py, duplicity/globals.py, duplicity/gpg.py:
    bug #22908: Don't block gpg-agent
    https://savannah.nongnu.org/bugs/?22908

    To fix the above, --use-agent was added as a command line option.
    When this is specified and asymetric encryption is enabled, then all
    GnuPG passphrases will come from the gpg-agent or equivalent program
    and no passphrase prompt will be issued.

2009-03-23  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin: bug #25976: Signed Backups Now Required
    https://savannah.nongnu.org/bugs/?25976

2009-03-21  Kenneth Loafman  <kenneth@loafman.com>

    * .pydevproject, .settings/de.loskutov.anyedit.AnyEditTools.prefs, .settings/org.eclipse.ltk.core.refactoring.prefs:
    Project setting changes.

    * CHANGELOG, duplicity/gpg.py, testing/GnuPGInterfacetest.py, testing/gpgtest2.py:
    patch #6787: import duplicity.GnuPGInterface explicitly
    https://savannah.nongnu.org/patch/?6787

    * duplicity/manifest.py: One statement per line.
    Indent text of error message to code level.

2009-03-19  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/collections.py:
    Fixed bug where an extra comma caused a traceback during a warning
    about unnecessary sig files.  Plus fixed print so the real filename
    would show up and not a Python object representation.

    * .project, CHANGELOG, duplicity/backend.py, testing/parsedurltest.py:
    bug #25787: Usernames with escaped @-sign are not handled properly
    https://savannah.nongnu.org/bugs/?25787

2009-03-18  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/ftpbackend.py, duplicity/backends/sshbackend.py:
    Adjust log levels so errors show up without verbosity.

2009-03-17  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin:
    BackendException does not cause traceback except when
    verbosity is at level 9 (debug).

    * CHANGELOG, duplicity/backend.py, duplicity/backends/botobackend.py, duplicity/backends/sshbackend.py:
    Fix backends so sleep does not occur after last retry.

    * duplicity/backends/ftpbackend.py:
    Add more error detection to FTP backend.

    Fix backends so sleep does not occur after last retry.

2009-03-15  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/gpg.py, duplicity/log.py:
    GPG errors will no longer cause tracebacks, but will produce a
    log entry, from gpg, similar to the following:
    ===== Begin GnuPG log =====
    gpg: BAD0BAD0: skipped: public key not found
    gpg: [stdin]: encryption failed: public key not found
    ===== End GnuPG log =====
    This will let the user know what really caused the GPG process
    to fail, and what really caused errors like 'broken pipe'.

    * CHANGELOG, duplicity/backends/rsyncbackend.py:
    patch #6773: Make user name optional in rsync backend
    https://savannah.nongnu.org/patch/?6773

    * CHANGELOG, duplicity/backends/botobackend.py:
    bug #25853: duplicity fails with boto passwords coming from ~/.boto
    https://savannah.nongnu.org/bugs/?25853

2009-03-12  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/ftpbackend.py:
    bug #25838: Backup fails / ncftp - remote file already exists
    https://savannah.nongnu.org/bugs/?25838

2009-03-11  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin, duplicity/backend.py, duplicity/backends/webdavbackend.py:
    Add / modify / repair Epydoc docstrings and format.

    * duplicity/backends/rsyncbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/hsibackend.py, duplicity/backends/localbackend.py:
    One statement per line.

2009-03-08  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.5.11.

    * duplicity/collections.py:
    Bug #333057: GnuPGInterface prints exit statuses incorrectly
    https://bugs.launchpad.net/bugs/333057

    * CHANGELOG, duplicity/backends/imapbackend.py:
    bug #25787: Usernames with @-sign are not handled properly
    https://savannah.nongnu.org/bugs/?25787

    * duplicity/GnuPGInterface.py: Detabify (was tab-width 8).

2009-03-07  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, dist/makedist:
    Bug #333057: GnuPGInterface prints exit statuses incorrectly
    https://bugs.launchpad.net/bugs/333057

    * duplicity/GnuPGInterface.py:
    Fix issue on return from waitpid where the result was shifted left and not right, producing 131072 instead of 2, as it should.

    Fixed some indent problems that PyDev complained about (Eclipse IDE).

    * rdiffdir: One statement per line.

    * CHANGELOG, duplicity/backends/ftpbackend.py:
    bug #25696: ncftp error with 0.5.09
    https://savannah.nongnu.org/bugs/?25696

2009-03-06  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends/ftpbackend.py: Also log the quit command.

2009-03-02  Kenneth Loafman  <kenneth@loafman.com>

    * rdiffdir: One statement per line.

    * CHANGELOG, duplicity/path.py:
    bug #15664: When restoring backup: "OverflowError:
                long int too large to convert to int"
    https://savannah.nongnu.org/bugs/?15664

    * duplicity/lazy.py, duplicity/commandline.py: One statement per line.

    * CHANGELOG, duplicity/backends/sshbackend.py:
    patch #6761: More robust pexpect handling of SSH authentication
    https://savannah.nongnu.org/patch/?6761

    * CHANGELOG, duplicity-bin:
    patch #6762: Wrong exit() used for 2.3/2.4 Python
    https://savannah.nongnu.org/patch/?6762

2009-03-01  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Explain new filenames and --time-separator better.

    * CHANGELOG, duplicity/commandline.py: Changes for 0.5.10.

    * duplicity/commandline.py:
    Add deprecation warnings for options affected by old filenames.

    * .cvsignore, CHANGELOG, duplicity.1, duplicity/collections.py, duplicity/commandline.py, duplicity/dup_time.py, duplicity/globals.py, testing/.cvsignore, testing/dup_timetest.py, testing/finaltest.py:
    bug #19988: Incompatibility to Samba/SMB share
    https://savannah.nongnu.org/bugs/?19988

2009-02-28  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/librsync.py, duplicity/patchdir.py, duplicity/misc.py:
    One statement per line.

2009-02-27  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/statistics.py: One statement per line and other cleanup.

    * duplicity-bin, rdiffdir:
    Module gettext should be imported and installed prior to importing any other modules.  This allows long strings to be translated when put at the module level rather than at the function call level.  See dup_time.py for examples.

2009-02-24  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin:
    bug #25550: Error codes do not propagate from log to exit status
    https://savannah.nongnu.org/bugs/?25550

2009-02-21  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin, duplicity.1, duplicity/collections.py, duplicity/commandline.py:
    bug #25097: Allow listing files from any time, not just current time
    https://savannah.nongnu.org/bugs/?25097

2009-02-20  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backend.py, testing/parsedurltest.py:
    Bug #229826 duplicity crashed with ValueError in port()
    https://bugs.launchpad.net/duplicity/+bug/229826

2009-02-17  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.5.09.

2009-02-13  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/tempdir.py:
    If tempdir.py is included, but not instantiated, then deleted, it throws an exception,
    as happens during testing when duplicity main is not used to instantiate tempdir.
    The fix is to make sure instantiation has happened before calling cleanup().

    * duplicity/backends/ftpbackend.py:
    These are changes to make debugging easier.
    - Filter ANSI control (bolding) characters from NcFTP responses.
    - Turn off ad for ncftp server at close of each session.

2009-02-10  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/sshbackend.py:
    bug #25530: commandline passwd not working
    https://savannah.nongnu.org/bugs/?25530

    * CHANGELOG: FTP is now driven with pexpect rather than NcFTP utilities.
    This closes the following bugs:
    bug #24741: ncftpls -x '' causes failure on Yahoo FTP server
    bug #23516: duplicity/ncftpget not closing unlinked files, ...

    * duplicity/backends/ftpbackend.py, testing/run-a-test.sh, testing/run-all-tests.sh:
    Merge from pexpect_ftp.

    * testing/run-all-tests.sh:
    Undo last change re logging compilec.py.  For some reason pushd and popd
    do not work when redirection is used.

    * duplicity/backends/ftpbackend.py: - Fix error message re NcFTP version.
    - Shorten command list processing.

    * testing/run-all-tests.sh: Make sure logging is done everywhere.

    * duplicity/backends/ftpbackend.py:
    If delete list is empty, do not run ncftp.

    * testing/run-a-test.sh, testing/run-all-tests.sh:
    Fix so compilec.py is run for each Python version.

2009-02-09  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends/ftpbackend.py:
    First working verion, more testing needed.

    * duplicity/backends/imapbackend.py:
    Applied retryImap2.patch from bug 25512.

2009-02-08  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/imapbackend.py:
    bug #25509: Logic error in imapbackend.py [IMAP_SERVER]
    https://savannah.nongnu.org/bugs/?25512

    bug #25512: [Patch] Retry on Imap failure
    https://savannah.nongnu.org/bugs/?25509

    * dist/makedist, duplicity/dup_time.py:
    Replace rdiff-backup with duplicity in strings.

2009-02-07  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends/ftpbackend.py: Checkpoint.

    * duplicity/asyncscheduler.py, duplicity/backends/imapbackend.py:
    Add copyright for author.

    * CHANGELOG, testing/alltests, testing/backendtest.py, testing/parsedurltest.py:
    Split parsedurl test from backendtest and add test cases.

2009-02-05  Kenneth Loafman  <kenneth@loafman.com>

    * README: Add NcFTP 3.2.0 exception clause to dependencies.

2009-02-02  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity-bin, po/Makevars, CHANGELOG, dist/makedist, dist/makerpm, dist/makeweb, dist/setup.py, duplicity/__init__.py, duplicity/_librsyncmodule.c, duplicity/asyncscheduler.py, duplicity/backend.py, duplicity/backends/__init__.py, duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/hsibackend.py, duplicity/backends/imapbackend.py, duplicity/backends/localbackend.py, duplicity/backends/rsyncbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/compilec.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_threading.py, duplicity/dup_time.py, duplicity/errors.py, duplicity/file_naming.py, duplicity/globals.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/static.py, duplicity/statistics.py, duplicity/tempdir.py, duplicity/util.py, rdiffdir, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/config.py.tmpl, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/logtest.py, testing/manifesttest.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/run-a-test.sh, testing/run-all-tests.sh, testing/run-coverage.sh, testing/selectiontest.py, testing/statictest.py, testing/statisticstest.py, testing/tempdirtest.py, testing/test_tarfile.py:
    Turns out going backwards in the license is not as easy as
    forwards.  Restoring GPLv3 license until consensus reached.

2009-02-01  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/compilec.py:
    Add/update copyright statements in all distribution source files
    and revert duplicity to GPL version 2 license.

2009-01-31  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.5.07.

    * testing/backendtest.py:
    Python 2.3 unittest.py tried to call to a test-local variable named
    'test_id' and failed.  Changed to 'my_test_id' and all is well.

2009-01-30  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/log.py:
    Original fix to disallow use of ncftpput 3.2.0 mistyped the ErrorCode used.

2009-01-28  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/imapbackend.py:
    patch #6733: Improve error handling in imapbackend.py
    https://savannah.nongnu.org/patch/?6733

2009-01-27  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, dist/makedist, dist/makerpm, dist/makeweb, dist/setup.py, duplicity-bin, duplicity/__init__.py, duplicity/_librsyncmodule.c, duplicity/asyncscheduler.py, duplicity/backend.py, duplicity/backends/__init__.py, duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/hsibackend.py, duplicity/backends/imapbackend.py, duplicity/backends/localbackend.py, duplicity/backends/rsyncbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_threading.py, duplicity/dup_time.py, duplicity/errors.py, duplicity/file_naming.py, duplicity/globals.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/static.py, duplicity/statistics.py, duplicity/tempdir.py, duplicity/util.py, po/Makevars, rdiffdir, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/config.py.tmpl, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/logtest.py, testing/manifesttest.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/run-a-test.sh, testing/run-all-tests.sh, testing/run-coverage.sh, testing/selectiontest.py, testing/statictest.py, testing/statisticstest.py, testing/tempdirtest.py, testing/test_tarfile.py:
    Add/update copyright statements in all distribution source files
    and revert duplicity to GPL version 2 license.

    * dist/makedist:
    patch #6729: New imap backend. Replaces current gmail backend
    https://savannah.nongnu.org/patch/?6729

2009-01-25  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/diffdir.py:
    bug #25293: IOError: [Errno 22] Invalid argument
    https://savannah.nongnu.org/bugs/?25293

    * duplicity/backends/sshbackend.py:
    Modify patch #6730: Fix timing out for SSH backend
    Do not take out the first line from the return buffer (#4).

    * CHANGELOG, duplicity/backends/sshbackend.py:
    patch #6730: Fix timing out for SSH backend
    https://savannah.nongnu.org/patch/?6730

    * CHANGELOG, duplicity.1, duplicity/backend.py, duplicity/backends/__init__.py, duplicity/backends/gmailimapbackend.py, duplicity/backends/imapbackend.py, duplicity/commandline.py, duplicity/globals.py, duplicity/urlparse_2_5.py:
    patch #6729: New imap backend. Replaces current gmail backend
    https://savannah.nongnu.org/patch/?6729

    * CHANGELOG:
    Removed ref to bug 25331 since the analysis and fix were both wrong.
    The issue was fixed correctly in bug 25403.

    * duplicity-bin, CHANGELOG, duplicity/gpg.py:
    bug #25403: 0.5.06 "manifests not equal because different volume numbers"
    https://savannah.nongnu.org/bugs/?25403

    * duplicity/manifest.py: One statement per line.

2009-01-24  Kenneth Loafman  <kenneth@loafman.com>

    * testing/alltests, testing/run-all-tests.sh, testing/run-coverage.sh:
    Move alltests list to separate file.

    * testing/.cvsignore: Add coverage output to .cvsignore.

    * testing/run-a-test.sh, testing/run-all-tests.sh:
    Turn on verbose for unit tests.

    * CHANGELOG, testing/backendtest.py, testing/config.py.tmpl:
    Fix backendtest.py so that empty URL's in config.py cause the
    backend test to be skipped rather than erroring.  Added notes
    in config.py.tmpl explaining the change.

2009-01-23  Kenneth Loafman  <kenneth@loafman.com>

    * .pydevproject: Make default Python be system default version.

    * .cvsignore: Add Releases directory.

    * testing/run-coverage.sh:
    First pass at coverage analysis, collect the data.

    * testing/run-a-test.sh: Remove LOG entries.  Not needed.

    * po/Makevars, po/POTFILES.in, testing/run-a-test.sh:
    Change to ASCII (-kkv)

    * testing/run-a-test.sh: Run a single unit test.

2009-01-22  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity.1, duplicity/globals.py:
    Increase default volume size (--volsize) to 25M from 5M.  This
    reduces the number of volumes to accomodate larger backups.

    * CHANGELOG, duplicity-bin:
    bug #25379: sys.exit() causes traceback and should not
    https://savannah.nongnu.org/bugs/index.php?25379

2009-01-18  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin, duplicity/log.py:
    Reworked patch 6701 to list collection one at a time rather than
    writing all as one huge list.  Was causing memeory problems when
    the collections got large.

2009-01-15  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin:
    bug #25331: When --archive-dir and --encrypt-key are used together, incremental fails.
    https://savannah.nongnu.org/bugs/index.php?25331

2009-01-09  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.5.06.

2009-01-08  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity.1: Fix illegal macro .PP. by removing extraneous period on end.

2009-01-07  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/ftpbackend.py, duplicity/log.py:
    NcFTP version 3.2.0 will not work with duplicity since we require the
    use of both -f and -C options on ncftpput.  3.1.9, 3.2.1+ work fine.
    I put in error checks for this situation in the FTP backend code.

2009-01-06  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, README, dist/makedist, dist/setup.py, duplicity/backends/sshbackend.py, duplicity/pexpect.py, testing/run-all-tests.sh:
    Noah Spurrier has given us permission to distribute pexpect.py along
    with duplicity, so this will no longer be an install requirement.

    * CHANGELOG, testing/run-all-tests.sh:
    Added loop to run-all-tests.sh to run all tests against all supported
    versions of Python if available.  Looks for 2.3, 2.4, 2.5, 2.6.

    * CHANGELOG, duplicity/gpg.py:
    Fix to deprecation warnings about sha and md5 modules.
    Uses hashlib if available, otherwise original module.

2009-01-05  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/selection.py:
    Missed the most basic case, no selection functions.  Fixed.

    * CHANGELOG, duplicity/selection.py, testing/selectiontest.py:
    bug #25230: --include-globbing-filelist only including first entry.
    https://savannah.nongnu.org/bugs/?25230

2009-01-04  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity.1:
    sr #106583: document the need to use the --force option
    https://savannah.nongnu.org/support/?106583

2009-01-03  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin:
    patch #6709: Report correct number of volumes when restoring
    https://savannah.nongnu.org/patch/?6709

    * CHANGELOG, duplicity-bin:
    bug #25239: Error during clean, wrong case in duplcicity
    https://savannah.nongnu.org/bugs/?25239

2008-12-30  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.5.05.

    * dist/makedist: Add po files back into distribution.

    * duplicity-bin:
    Cosmetic - reformat FatalError calls at end for readability.

2008-12-29  Kenneth Loafman  <kenneth@loafman.com>

    * dist/setup.py: Change "test" to "$version".

    * dist/setup.py: Build list of .mo files to be installed from po directory.

    * .settings/.cvsignore, CHANGELOG, dist/makedist, dist/setup.py, po/POTFILES.in, po/io.po, po/io/duplicity.mo, po/io/duplicity.po:
    bug #25194: Duplicity 5.04 requires python-distutils-extra...
    https://savannah.nongnu.org/bugs/?25194

2008-12-28  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity-bin, duplicity.1, rdiffdir.1:
    Use reldate expansion to include release date.

    * dist/makedist: - Use os.path.join() instead of hardcoded strings
    - Make VersionedCopy replace $reldate as well as $version

2008-12-27  Kenneth Loafman  <kenneth@loafman.com>

    * dist/duplicity.spec.template: Adjust RPM spec file for translations.

    * CHANGELOG: Changes for 0.5.04.

2008-12-22  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/robust.py:
    patch #6702: handle unknown errnos in robust.py
    https://savannah.nongnu.org/patch/?6702

    * rdiffdir, testing/config.py.tmpl:
    patch #6700: Make duplicity translatable
    https://savannah.nongnu.org/patch/?6700
    [not in patch - added after unit tests]

    * CHANGELOG, duplicity-bin, duplicity/log.py:
    patch #6701: Make current-list command machine-readable
    https://savannah.nongnu.org/patch/?6701

    * CHANGELOG, dist/makedist, dist/setup.py, duplicity-bin, duplicity/asyncscheduler.py, duplicity/backend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/lazy.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/tempdir.py, po/Makevars, po/POTFILES.in, po/io.po:
    patch #6700: Make duplicity translatable
    https://savannah.nongnu.org/patch/?6700

    * CHANGELOG, duplicity/gpg.py:
    GPG was throwing "gpg: [don't know]: invalid packet (ctb=14)" and apparently this is non-fatal.
    There is a fix for this being rolled into GPG 2.x.
    http://lists.gnupg.org/pipermail/gnupg-devel/2006-September/023180.html
    Copied from collections.py.  Fix supplied by Simon Blandford <simon@onepointltd.com>

2008-12-15  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/selection.py, duplicity/path.py:
    One statement per line.  No other changes.

    * testing/backendtest.py: Print backend name for each test started.

    * testing/backendtest.py:
    Remove test for assert on non-existing delete.  Not all backends will raise an exception when the target of a delete does not exist.

    * duplicity/patchdir.py:
    Log correct file name in line 67.  Use diff_ropath, not basis_path.

    * duplicity/diffdir.py, duplicity/log.py:
    Fix patch applied during Patch #6696.  Applied fixiter.diff.

    * CHANGELOG, duplicity-bin:
    patch #6697: Always log at least one progress during dry run
    https://savannah.nongnu.org/patch/?6697

    * CHANGELOG, duplicity/diffdir.py:
    patch #6696: Consolidate get_delta_iter and get_delta_iter_w_sig
    https://savannah.nongnu.org/patch/?6696

    * CHANGELOG, duplicity/diffdir.py, duplicity/log.py, duplicity/patchdir.py, duplicity/util.py:
    patch #6695: Log filenames
    https://savannah.nongnu.org/patch/?6695

    * CHANGELOG, duplicity-bin, duplicity/log.py: patch #6694: Log exceptions
    https://savannah.nongnu.org/patch/?6694

    * duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/sshbackend.py, duplicity/log.py:
    patch #6693: Some FatalError's don't have codes still
    https://savannah.nongnu.org/patch/?6693

    * CHANGELOG, duplicity/collections.py, duplicity/log.py, duplicity-bin:
    patch #6692: Print collection status in a machine-readable way
    https://savannah.nongnu.org/patch/?6692

2008-12-14  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity/backends/ftpbackend.py:
    bug #24889: NCFTP cannot deal with some FTP servers
    https://savannah.nongnu.org/bugs/?24889

    * CHANGELOG, duplicity.1, duplicity/.cvsignore:
    bug #25090: Typos and trailing whitespace in duplicity manpage
    https://savannah.nongnu.org/bugs/?25090

2008-12-10  Kenneth Loafman  <kenneth@loafman.com>

    * .project, .pydevproject, CHANGELOG, duplicity-bin, duplicity/collections.py, duplicity/commandline.py, duplicity/log.py, duplicity/selection.py:
    patch #6686: Add error codes for all fatal errors
    https://savannah.nongnu.org/patch/?6686

2008-11-18  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin, duplicity/diffdir.py, duplicity/log.py, duplicity/statistics.py:
    patch #6678: Add progress metering
    https://savannah.nongnu.org/patch/?6678

2008-11-17  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.5.03.

2008-11-16  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/diffdir.py:
    patch #6676: Raw delta stats aren't right for multivolumes
    https://savannah.nongnu.org/patch/?6676

    * dist/makedist, dist/makerpm, dist/makeweb, dist/setup.py, duplicity-bin, duplicity/asyncscheduler.py, duplicity/backend.py, duplicity/backends/__init__.py, duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/gmailimapbackend.py, duplicity/backends/hsibackend.py, duplicity/backends/localbackend.py, duplicity/backends/rsyncbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/compilec.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_threading.py, duplicity/dup_time.py, duplicity/errors.py, duplicity/file_naming.py, duplicity/globals.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/static.py, duplicity/statistics.py, duplicity/tarfile.py, duplicity/tempdir.py, duplicity/urlparse_2_5.py, duplicity/util.py, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/logtest.py, testing/manifesttest.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/selectiontest.py, testing/statictest.py, testing/statisticstest.py, testing/tempdirtest.py, testing/test_tarfile.py:
    patch #6675: Add modelines
    https://savannah.nongnu.org/patch/?6675

    * duplicity.1: patch #6674: Add --log-* options to man page
    https://savannah.nongnu.org/patch/?6674

    * duplicity.1, duplicity/commandline.py, duplicity/diffdir.py, duplicity/globals.py, duplicity-bin:
    patch #6673: Add --dry-run option
    https://savannah.nongnu.org/patch/?6673

2008-11-15  Kenneth Loafman  <kenneth@loafman.com>

    * dist/makedist: patch #6672: makedist doesn't ship util.py
    https://savannah.nongnu.org/patch/?6672

2008-11-12  Kenneth Loafman  <kenneth@loafman.com>

    * rdiffdir: Add log.setup() call to main() to support new logging.

    * .cvsignore: *** empty log message ***

    * testing/config.py.tmpl: Add log.setup() to support new logging.

    * CHANGELOG: Checkpoint 2 prior to 5.03.

    * duplicity-bin, duplicity/collections.py, duplicity/commandline.py, duplicity/gpg.py, duplicity/log.py, duplicity/manifest.py:
    patch #6670: Machine Readable Output
    https://savannah.nongnu.org/patch/?6670

    * duplicity/backends/webdavbackend.py:
    Correct spelling of parsed_url (parsed_urk) in patch #6662.

    * duplicity/backends/gmailimapbackend.py:
    sr #106534: GMail backups aren't stored in the correct location
    https://savannah.nongnu.org/support/?106534

    * CVS-README: sr #106496: put install-from-cvs-notes in CVS-README
    https://savannah.nongnu.org/support/?106496

    * CHANGELOG: Checkpoint prior to 5.03.

    * duplicity/backends/botobackend.py:
    patch #6638: correct typo in reporting lack of sufficiently new boto backend
    https://savannah.nongnu.org/patch/?6638

    * duplicity/backend.py:
    patch #6642: make ParsedUrl() thread-safe with respect to itself
    https://savannah.nongnu.org/patch/?6642

    * duplicity/asyncscheduler.py, duplicity/dup_threading.py:
    patch #6652: improve asynch scheduler (including the synchronous case)
    https://savannah.nongnu.org/patch/?6652

    * duplicity/backends/botobackend.py, duplicity/util.py:
    patch #6662: improve s3 backend error reporting
    https://savannah.nongnu.org/patch/?6662

    * LOG-README, testing/logtest.py, testing/run-all-tests.sh:
    patch #6670: Machine Readable Output
    https://savannah.nongnu.org/patch/?6670

    * duplicity/backends/webdavbackend.py:
    bug #24775: Digest Auth for WebDAV backend
    https://savannah.nongnu.org/bugs/?24775

    * duplicity.1:
    bug #24731: Documentation error: "if... if" in remove-older-than paragraph
    https://savannah.nongnu.org/bugs/?24731

2008-09-21  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity-bin: Changes for 0.5.02

    * dist/makedist, duplicity.1: patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/index.php?6297

2008-09-16  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backend.py, duplicity/backends/__init__.py, duplicity/backends/gmailimapbackend.py, duplicity/commandline.py, duplicity/urlparse_2_5.py:
    patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/index.php?6297

    * duplicity/dup_temp.py: Change to one statement per line.

2008-09-15  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/gpg.py:
    Change use of logger so that gpg logs are always collected.
    The log is always printed in the case of gpg IO errors.
    Verbosity level 5 or greater will also print the logs the
    same as previous versions.

    * duplicity/diffdir.py: Make one statement per line.  No other changes.

    * duplicity/commandline.py: - add -h option for help

    * duplicity/asyncscheduler.py:
    bug #24274: asyncscheduler.py missing sys import
    https://savannah.nongnu.org/bugs/index.php?24274

2008-09-14  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backend.py: bug #24260: backend.py missing re import
    https://savannah.nongnu.org/bugs/index.php?24260

2008-09-11  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.5.01

2008-09-09  Kenneth Loafman  <kenneth@loafman.com>

    * testing/.cvsignore: Ignore test log file.

    * testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/manifesttest.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/selectiontest.py, testing/statictest.py, testing/statisticstest.py, testing/tempdirtest.py, testing/test_tarfile.py, CHANGELOG, README, dist/makedist, dist/makerpm, dist/makeweb, dist/setup.py, duplicity-bin, duplicity/_librsyncmodule.c, duplicity/backend.py, duplicity/backends/sshbackend.py, duplicity/collections.py, duplicity/commandline.py, duplicity/compilec.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_time.py, duplicity/file_naming.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/static.py, duplicity/statistics.py, rdiffdir, testing/backendtest.py, testing/collectionstest.py, testing/config.py.tmpl, testing/diffdirtest.py, duplicity/tarfile.py:
    Untabify all files.  To compare against previous
    versions use 'cvs diff -w' or 'diff -w'.

2008-09-08  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends/webdavbackend.py:
    Create target dir (collection) if needed.

    * testing/.cvsignore: Ignore testfiles dir.

    * testing/backendtest.py, testing/config.py.tmpl:
    Add tests for webdav and webdavs.

    * duplicity/backends/webdavbackend.py:
    bug #24223: WebDAV backend broken in 0.5.00
    https://savannah.nongnu.org/bugs/index.php?24223

2008-09-06  Kenneth Loafman  <kenneth@loafman.com>

    * dist/makedist, dist/setup.py, CHANGELOG: Changes for 0.5.00

2008-09-04  Kenneth Loafman  <kenneth@loafman.com>

    * testing/run-all-tests.sh, testing/temp2.tar, testing/test_tarfile.py:
    temp2.tar was a test-created file that had to be present
    at the beginning of test_tarfile.py.  Removed the need for
    it to be present and removed the file from CVS.

2008-09-03  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends/botobackend.py, duplicity/backends/ftpbackend.py, duplicity/backends/hsibackend.py, duplicity/backends/localbackend.py, duplicity/backends/rsyncbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, duplicity/gpg.py, duplicity/patchdir.py, duplicity/path.py, testing/backendtest.py, testing/roottest.py, testing/run-all-tests.sh:
    Changes to get unit tests working again:
      - resolve circular imports during unit tests
      - resolve exception error import - now in errors.py

    * duplicity/tempdir.py:
    patch #6623: slightly augment tempdir cleanup logging
    https://savannah.nongnu.org/patch/index.php?6623

2008-08-03  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: No longer needed, see backends dir.

    * duplicity/backends/.cvsignore: no comment

    * CHANGELOG, duplicity/backends.py, duplicity/backends/sshbackend.py:
    bug #23988: scp destination fails if no username is specified
    https://savannah.nongnu.org/bugs/index.php?23988

    * CHANGELOG, duplicity-bin:
    bug #23985: --no-encryption option does not work in 0.4.12
    https://savannah.nongnu.org/bugs/index.php?23985

2008-08-02  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends/ftpbackend.py, duplicity/backends/hsibackend.py, duplicity/backends/localbackend.py, duplicity/backends/rsyncbackend.py, duplicity/backends/sshbackend.py, duplicity/backends/webdavbackend.py, testing/backendtest.py, testing/collectionstest.py, testing/finaltest.py, testing/temp2.tar, CHANGELOG, duplicity-bin, duplicity/backend.py, duplicity/backends/__init__.py, duplicity/backends/botobackend.py, duplicity/commandline.py, duplicity/dup_threading.py, duplicity/errors.py, duplicity/lazy.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py:
    patch #6596: re-organize backend module structure
    https://savannah.nongnu.org/patch/index.php?6596

2008-08-01  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity-bin, duplicity.1, duplicity/asyncscheduler.py, duplicity/commandline.py, duplicity/dup_threading.py, duplicity/errors.py, duplicity/globals.py:
    patch #6353: Concurrency for volume encryption and upload.
    https://savannah.nongnu.org/patch/index.php?6353

    * duplicity.1, duplicity/backends.py, duplicity/commandline.py, duplicity/globals.py:
    patch #6589: S3 european bucket support
    https://savannah.nongnu.org/patch/index.php?6589

2008-07-22  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.12.

    * duplicity.1, duplicity/commandline.py:
    bug #23362: Documentation for --version, --time-separator <char>
    https://savannah.nongnu.org/bugs/index.php?23362

    * duplicity/file_naming.py: Cosmetic only.

    * duplicity.1: bug #23540: doc bug in man page (environment FTP_PASSWORD)
    https://savannah.nongnu.org/bugs/?23540

2008-06-23  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity-bin:
    Dan Muresan created a patch that tries to minimize the number of password
    prompts.  To do so, it sometimes requests a password once without
    confirmation; if later it turns out that a full backup is needed, the
    user is prompted for confirmation.

2008-05-16  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py:
    bug #23066: ssh uris with given portnumbers are not handled correctly
    https://savannah.nongnu.org/bugs/index.php?23066

2008-05-15  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/collections.py: Fix sort() for Python 2.3

2008-05-07  Kenneth Loafman  <kenneth@loafman.com>

    * dist/setup.py: Change back to requiring Python 2.3.

2008-05-05  Kenneth Loafman  <kenneth@loafman.com>

    * README: Change requirements back to Python 2.3.

    * CHANGELOG, testing/run-all-tests.sh, testing/temp2.tar:
    Changes for 0.4.11

    * duplicity/backends.py, duplicity/urlparse_2_5.py, testing/run-all-tests.sh:
    Modified to run on Python 2.3.

2008-04-04  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: bug #22826: regressions caused by boto 1.1c
    https://savannah.nongnu.org/bugs/?22826

2008-04-01  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: Reinstate patch #6340 with a detailed explanation.
    http://savannah.nongnu.org/patch/index.php?6340

2008-03-26  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.10.

    * dist/makerpm: Remove --sign for now.

    * duplicity/backends.py: bug #22728: FTP backend fails on empty directory
    https://savannah.nongnu.org/bugs/?22728

2008-03-25  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/collections.py: Fix log.debug to log.Debug

    * duplicity/backends.py:
    patch #6453: handle absolute urls in webdav backend
    https://savannah.nongnu.org/patch/index.php?6453

    * duplicity/collections.py: patch #6449: add additional debug level logging
    https://savannah.nongnu.org/patch/index.php?6449

2008-02-06  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/commandline.py, duplicity/patchdir.py, duplicity/path.py:
    patch #6403: Restore by overwriting files/directories by using --force option
    https://savannah.nongnu.org/patch/?6403

    * testing/config.py.tmpl: Password should be None, not empty string.

    * testing/config.py.tmpl: Add config for S3 tests.

    * duplicity/file_naming.py: Reformat to one statement per line.

    * duplicity/backends.py:
    Fix problem where S3 prefix was appended with 'd'.  This caused
    a failure in the regression tests.  Unsure where it came from.

    * duplicity/selection.py:
    patch #6389: Possible Fix for pagefile.sys on Win32 systems
    https://savannah.nongnu.org/patch/?6389

    * duplicity/log.py: patch #6380: add additional named logging levels
    https://savannah.nongnu.org/patch/?6380

    * duplicity.1: patch #6374: Duplicity --tempdir patch documentation.
    https://savannah.nongnu.org/patch/?6374

    * duplicity-bin:
    patch #6375: Duplicity reports the epoch for a nonexistant last full backup date
    https://savannah.nongnu.org/patch/?6375

    * duplicity/dup_time.py: - remove sleep() from dup_time.py - not used.
    - make one statement per line format change.

    * testing/dup_timetest.py:
    Remove testSleeping since sleep() removed from dup_time.py.

    * testing/backendtest.py: Add S3 backend test.

2008-02-03  Kenneth Loafman  <kenneth@loafman.com>

    * testing/roottest.pyc: do not store object

2008-01-08  Kenneth Loafman  <kenneth@loafman.com>

    * README: Add requirements for source package install.

2008-01-04  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, testing/temp2.tar: Changes for 0.4.9.

    * duplicity.1: Add more info on URL formats.

2007-12-31  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/commandline.py: Updated URL Formats in the Help Screen.

    * CHANGELOG: Added section URL FORMAT in the duplicity man page.

2007-12-30  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py:
    Make sure to strip extraneous single colon when dealing
    with non-module URLs.  We provide the colon as needed.

    * duplicity/path.py:
    bug #21909: Problematic typo in compare_verbose() method
    https://savannah.nongnu.org/bugs/index.php?21909

2007-12-29  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/commandline.py:
    patch #6357: Explicit restore action is missing from the command list,
    https://savannah.nongnu.org/patch/?6357

    * duplicity/commandline.py, duplicity/globals.py, duplicity/tempdir.py:
    patch #6356: Command line option for the temporary directory root.
    https://savannah.nongnu.org/patch/?6356

2007-12-26  Kenneth Loafman  <kenneth@loafman.com>

    * testing/backendtest.py, testing/config.py.tmpl:
    Added regression tests for absolute, relative, and
    module pathing in the rsync scheme.

    * duplicity/commandline.py: Fixed rsync URL description text in --help.

    * duplicity/backends.py:
    Added 2nd patch to bug #21475 that forces all versions of
    Python to use the fixed urlparse.py.

    Fixed issue with Pure-FTPd that would always return an empty
    directory listing and thus force a full backup every time.
    A side effect of the change is that we now only make one call
    to ncftpls to get the listing, thereby reducing the overhead
    on systems with a large number of backup files.

    bug #21896: Two problems with rsync under 0.4.8 + patch
    https://savannah.nongnu.org/bugs/index.php?21896

    patch #6354: S3 staight typo results in a bogus exception
    https://savannah.nongnu.org/patch/?6354

    * duplicity-bin: Fixed so that remove-older-than and remove-all-but-n-full
    will not request a GPG passphrase.

    * duplicity/urlparse_2_5.py:
    Fixed regression caused by changeover to new urlparse.py.
    bug #21475: FTP Usernames that contain '@' are not recognized
    https://savannah.nongnu.org/bugs/index.php?21475

2007-12-15  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, testing/run-all-tests.sh, testing/temp2.tar:
    Changes for 0.4.8.

    * duplicity/gpg.py: Format to one statement per line.

    * duplicity/backends.py:
    Allow pexpect to force the close of the child on sftp
    calls.  We already do that with scp calls.  This cleans
    up that exception.

2007-12-13  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: patch #6344: S3 bad bad key key handling
    http://savannah.nongnu.org/patch/?6344

    * testing/backendtest.py, testing/config.py.tmpl, testing/finaltest.py, testing/roottest.pyc:
    Replace set_password/phrase with set_environ and
    clarify meaning in config.py.

2007-12-12  Kenneth Loafman  <kenneth@loafman.com>

    * README: Complete description of install using --prefix=.

    * README: Fix version of boto needed plus formatting.

    * duplicity/backends.py: patch #6340: S3 short filename regression
    https://savannah.nongnu.org/patch/?6340

    * testing/.cvsignore: Make sure config.py not checked in.

    * testing/config.py.tmpl: Initial release.

    * testing/memcheck.py: This test requires a file that no longer exists.
    Plus, it is unclear what this test is supposed
    to accomplish.  Tar is tested by the other tests.

    * testing/roottest.py, testing/run-all-tests.sh, testing/selectiontest.py, testing/statictest.py, testing/statisticstest.py, testing/temp2.tar, testing/tempdirtest.py, testing/test_tarfile.py, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/manifesttest.py, testing/memcheck.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py:
    First pass at getting tests up to date:
      -- isolate config in 'config.py' (see config.py.tmpl)
      -- silence noisy tests as much as possible
      -- fix code on both sides as needed

2007-12-09  Kenneth Loafman  <kenneth@loafman.com>

    * testing/run-all-tests.sh: Initial release.

    * duplicity-bin:
    Remove 2nd call to dup_time.settimestr() since it overrides
    the time that may be set by --current-time (used for testing).

    * duplicity/commandline.py:
    Regen dup_time.curtimestr if time-separator changed.

    * duplicity/backends.py: Fixed previous patch that assumed the presence
    of the user and password in the rsync URL.

    * testing/tempdirtest.py, testing/collectionstest.py, testing/dup_timetest.py, testing/finaltest.py:
    Bring tests up to date.

2007-12-07  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: bug #21751: rsync module urls do not work in 0.4.7
    https://savannah.nongnu.org/bugs/index.php?21751

    bug #21752: Boto backend needs version 0.9d or later
    https://savannah.nongnu.org/bugs/index.php?21752

    * CHANGELOG: Changes for version 0.4.7.

    * dist/setup.py: Change to require Python 2.4 or later.

    * dist/makedist: Formatted list and added tempdir.py and urllib_2_5.py
    to the released files list.

2007-12-06  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py:
    Fix confusion over patches applied to different versions.
    Patch #6300 should now be applied completely.

    Added back munge_password() so entire commandline could
    be logged without the password showing.

    * duplicity/backends.py: Hole imapbackend till next release.

    * duplicity/imapbackend.py: Hold till next release.

2007-12-05  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py, duplicity/urlparse_2_5.py:
    patch #6300: Standard library replacement for ParsedUrl class
    https://savannah.nongnu.org/patch/?6300

    I had to fix the ssh/scp scheme to remove the leading '/' in
    parsed_url.path, otherwise it tried to treat the path as absolute.

2007-12-02  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: Backed out the following patch until bugs fixed...
    patch #6300: Standard library replacement for ParsedUrl class
    https://savannah.nongnu.org/patch/?6300

    * duplicity/backends.py: patch #6301: log sftp commands at verbosity 5
    https://savannah.nongnu.org/patch/?6301

    * duplicity/backends.py:
    patch #6300: Standard library replacement for ParsedUrl class
    https://savannah.nongnu.org/patch/?6300

2007-12-01  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/tempdir.py, testing/tempdirtest.py, duplicity-bin, duplicity/backends.py, duplicity/dup_temp.py:
    patch #6299: re-design tempfile handling
    https://savannah.nongnu.org/patch/?6299

    * duplicity/backends.py: Move import of imapbackend to the end of the
    module.  Circular dependency.  Needs fixing.

    * duplicity/backends.py: Undo regression of bug #21508 contained in
    patch #6298: URI unquoting patch for FTP backend
    https://savannah.nongnu.org/patch/?6298

    Some cosmetic cleanup.

    * duplicity/backends.py: patch #6298: URI unquoting patch for FTP backend
    https://savannah.nongnu.org/patch/?6298

    * duplicity/imapbackend.py: patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/?6297

    Added 2nd patch for above.

    * duplicity/backends.py, duplicity/imapbackend.py:
    patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/?6297

    * duplicity/backends.py, duplicity/commandline.py:
    patch #6292: Amazon S3 bucket creation deferral for Duplicity 0.4.6
    https://savannah.nongnu.org/patch/?6292

2007-11-30  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/dup_temp.py:
    bug #21686: NcFTPGet 3.2.0 tempfile incompatibility
    https://savannah.nongnu.org/bugs/index.php?21686

    * duplicity/backends.py:
    Applied patch from Eric Hanchrow to fix logging error in
    botoBackend, and fix delete() in rsyncBackend.

    bug #21686: NcFTPGet 3.2.0 tempfile incompatibility
    https://savannah.nongnu.org/bugs/index.php?21686

2007-11-29  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/commandline.py:
    bug #21673: remove-all-but-n-full wrong arg usage
    https://savannah.nongnu.org/bugs/index.php?21673

    patch #6293: [patch] left-over patching from
    remove-all-but-n-full patch
    https://savannah.nongnu.org/patch/?6293

2007-11-28  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: more Changes for 0.4.6.

    * CHANGELOG, README, duplicity.1: Changes for 0.4.6.

    * duplicity/collections.py:
    Fixed coding problem where matched_sig_chain could be
    referenced before it was defined.

    * duplicity/backends.py, duplicity/commandline.py:
    https://savannah.nongnu.org/patch/index.php?6291
    patch #6291: Alternative WebDAV HTTPS patch

    * duplicity/backends.py: https://savannah.nongnu.org/patch/index.php?6289
    patch #6289: Amazon S3 key prefix patch for Duplicity 0.4.5

    * duplicity/backends.py, duplicity/dup_temp.py:
    https://savannah.nongnu.org/patch/?6284
    patch #6285: security fix: eliminate use of mktemp()

    * duplicity.1: https://savannah.nongnu.org/bugs/index.php?21651
    bug #21651, add https support for webdav.

    https://savannah.nongnu.org/patch/?6284
    patch #6284: document TMPDIR and friends

2007-11-27  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: https://savannah.nongnu.org/bugs/index.php?21657
    bug #21657: ncftpls fails to create dir in ver 0.4.5

    * duplicity/commandline.py, duplicity/globals.py:
    https://savannah.nongnu.org/bugs/index.php?21651
    bug #21651, add https support for webdav.

    * duplicity/collections.py:
    Try, the second.  See comments in the bug tracker.
    https://savannah.nongnu.org/bugs/index.php?21646
    bug #21646: --archive-dir causes delete of remote full
    sigs and orphaned sig files

    * duplicity/backends.py: https://savannah.nongnu.org/bugs/index.php?21651
    bug #21651, add https support for webdav

2007-11-26  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Fix release date in 0.4.5.

    * CHANGELOG: Changes for 0.4.5.

    * duplicity-bin, duplicity.1, duplicity/backends.py, duplicity/collections.py, duplicity/commandline.py, duplicity/dup_temp.py, duplicity/globals.py, duplicity/path.py:
    https://savannah.nongnu.org/bugs/index.php?21646
    Fix to handling of collections when --archive-dir is used.
    Prior to this, duplicity would write the full sig files to
    both local and remote, then delete the remote.  Now, it does
    not delete the remote full sigs.

    Applied the following patches from Peter Schuller
    patch #6279, add command 'remove-all-but-n-full'
    patch #6280, clarify --archive-dir option
    patch #6281, --help should print to stdout, not stderr
    patch #6282, collection-status: output in more consistent order

2007-11-23  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity.1: Changes for version 0.4.4.

    * duplicity/dup_time.py, CHANGELOG:
    Applied a patch from Gregory Hartman to correct handling of DST
    in time calculations.  This affects backups made the night of
    a DST time switch.

    * duplicity/collections.py: Cosmetic - Use True and False, not 1 and None.

    * duplicity/backends.py: Fix version checking code in ftpBackend.

2007-11-19  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/commandline.py:
    Changes to commandline processing to allow non-ambiguous short
    strings for commands, i.e. 'i', 'inc', 'incr' for 'incremental',
    'f' for 'full', etc..  A warning message is printed if the short
    command is not unique.

    * duplicity/backends.py:
    Changes to ftpBackend to use the login config file rather than
    putting the username and password on the command line.  This
    requires the use of NcFTP 3.1.9 or later.

    Thanks to a patch from Greg Hewgill the Amazon S3 backend now
    uses --num-retries to retry IO repeatedly if needed.

2007-10-26  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.4.RC4 try 2

    * CHANGELOG, duplicity.1: Changes for 0.4.4.RC4

    * COPYING: Replace with Version 3 GPL text.

    * duplicity-bin:
    Fixed issue in --time-separator where the current time string
    was being set prior to setting the separator, causing errors
    when trying to set the --time-separator for Windows systems.

    * duplicity/commandline.py:
    There is a new command line syntax to separate actions and
    options.  Refer to the new man page for full details.

    * duplicity/collections.py:
    Correct calling sequence in calls to get_signature_chains().

    * duplicity/backends.py:
    Fix so that ftpBackend.delete() does not print file list.

    * duplicity/path.py:
    Fix so that file mtime is always compared in full seconds.

2007-10-02  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.4.RC3 -- Corrected.

    * CHANGELOG: Changes for 0.4.4.RC3.

2007-09-29  Kenneth Loafman  <kenneth@loafman.com>

    * .cvsignore: Add 'patch' dir to ignore list.

    * duplicity/backends.py:
    Patch from Olivier Croquette to add :port option in FTP.

    * duplicity-bin, duplicity.1, duplicity/collections.py, duplicity/commandline.py, duplicity/globals.py:
    Patch from Olivier Croquette to add --full-if-older-than=<time>
    option to force a full backup at <time> rather than incremental.

2007-09-28  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py:
    Patch from Olivier Croquette to add :port option in FTP.

    Patch from Mitchell Garnaat to get all keys from S3, rather
    than just the first 1000.

    Fix to sshBackend to version check for python-pexpect 2.1.

    Fix one case in ftpBackend where host string was used instead of
    url_string.  This only affected the creation of the target dir on
    the remote system, if it did not exist, and only if the user or
    port needed to be specified.

2007-09-26  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.4.RC2.

    * duplicity/commandline.py:
    Added --timeout <seconds> (default 30) to allow users to change
    duplicity's network timeout settings.

    Added --time-separator <char> to allow users to change the time
    separator from ':' to another character that will work on their
    system.  HINT: For Windows SMB shares, use --time-separator='_'.
    NOTE: '-' is not valid as it conflicts with date separator.

    Changed usage message to separate options and commands.

    * duplicity/backends.py:
    Add patch from Olivier Croquette to allow user@domain usernames,
    making ftp://user@domain@domain.com/path a valid URL.

    Added a bit of debug print to sshBackend for --verbosity=9.

    * duplicity-bin:
    Add patch from Alexander Zangerl to suppress the GPG passphrase
    prompt when a passphrase is not needed.
     - full and pubkey enc:  doesn't depend on old encrypted info
     - inc and pubkey enc and archive-dir: need manifest and sigs,
       which the archive dir contains unencrypted
     - with encryption disabled
     - listing files:  needs manifest, but the archive dir has that
     - collection status:  only looks at a repository

2007-09-19  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.4.RC1.

    * dist/setup.py: https://savannah.nongnu.org/patch/index.php?6205
    Add option --librsync-dir for when its not found.

    * duplicity/backends.py:
    Bug #21123: duplicity 0.4.3 does not find any backup chains
    https://savannah.nongnu.org/bugs/?21123

    * duplicity/dup_temp.py: Make tempfiles with useful names.

    * duplicity/commandline.py:
    Fixes manual page and usage msg for rsync url and --remove-older-than.

    * duplicity/collections.py:
    Fix for Debian bug #228388: old/aborted/offending sig files
    prohibit any further action.

    * duplicity.1:
    Fixes manual page and usage msg for rsync url and --remove-older-than.

    * duplicity-bin: Do not ask for passphrase when none is needed.

2007-09-16  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/diffdir.py:
    Final patch for Peter Schuller's fix to max read size.
    The first one was broken (revision previous to this).

2007-09-10  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py:
    Add patch submitted by Peter Schuller which removes the
    default SSH options that ignored known hosts files and
    disabled strict host checking.  This patch also handles
    the authentication failures from these issues.

2007-09-06  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/diffdir.py: Fixed so that max read size is 64k, not the
    volume size which can be quite large.

2007-08-20  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Fix release date.

    * CHANGELOG, README, duplicity.1: Changes for 0.4.3 release.

    * duplicity/patchdir.py:
    Removed use of tempfile.TemporaryFile().  This fixes the
    restore problem on Windows that was due to Python bug
    1776696 reported on Sourceforge.

    * duplicity/gpg.py: Removed hardwired options to use bzip2 compression.

    Added gpg-options to allow users to add options to
    the gpg process.

    * duplicity/commandline.py:
    Changed ssh-command to ssh-options to allow users
    to add options to the scp and sftp commmands.

    Added gpg-options to allow users to add options to
    the gpg process.

    * duplicity/backends.py:
    Move get_password() to Backend class to standardize.

    Fix problem with ftpBackend to create target directory if needed.

2007-08-13  Kenneth Loafman  <kenneth@loafman.com>

    * COPYING, duplicity-bin, duplicity/_librsyncmodule.c, duplicity/backends.py, duplicity/collections.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_time.py, duplicity/file_naming.py, duplicity/globals.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/static.py, duplicity/statistics.py, rdiffdir:
    Upgrade to GPL version 3 license.

    * duplicity/backends.py: Do not pass :port part of URL to scp backend.
    Its taken as the target file and errors out.

    * duplicity/backends.py, duplicity/commandline.py:
    Change ssh_command option to be ssh_options.  This adds
    options to the scp and sftp commands that are used by
    the ssh backend.

    * duplicity/backends.py:
    Fixed bug 20764 - unable to use port in ssh backend.
    https://savannah.nongnu.org/bugs/?20764

    Change ssh backend to send 'quit' instead of EOF when
    using sftp.  This allows it to run under cron as long
    as the password is supplied non-interactively.

2007-08-09  Kenneth Loafman  <kenneth@loafman.com>

    * dist/setup.py, CHANGELOG: Changes for 0.4.3.RC12

    * duplicity/backends.py: Changed the file:, ftp:, and ssh: backends so that
    the target directory will be created at start.

    Changed the ftp: backend so that empty target dirs
    do not error out.

    * duplicity/commandline.py: Clean up help list formatting.

    * duplicity/collections.py:
    Fix index out of range in Bug 20730, triggered when there
    is only one incremental and no previous in list.
    https://savannah.nongnu.org/bugs/?20730

    * dist/setup.py: - Print warning if pexpect version is less than 2.1.
    - Fix author and maintainer settings.

    * duplicity.1: Fix environment var name for ssh backend.

2007-07-21  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG, duplicity.1: Changes for 0.4.3.RC11.

    * duplicity/commandline.py: Add --ssh-askpass option.

    * duplicity/backends.py:
    Duplicity now correctly processes scp URL's of the form:
      scp://user@host[:port]/
    where the directory spec is empty.  This fixes a bug where the
    user could not write into the home directory on the target.

    The SSH/SCP backend has had an overhaul.  It now requires the
    python-pexpect module.  Normally this can be obtained from your
    distro's repository, but if you want, you can download pexpect
    from http://pexpect.sourceforge.net.

    The SSH/SCP backend work was done to allow the user to use password
    authentication rather than public-key.  You may now enter a password,
    either through the FTP_PASSWORD environment variable, or at the
    console.  To activate this feature you will need to use the option
    --ssh-askpass on the command line.  The default is public-key, which
    does *not* look for a password from either source.

2007-07-15  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: patch #6094, Boto Backend Fixes for RC10

2007-07-14  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.3.RC10

    * duplicity/backends.py: Add support for:
      --ftp-passive,
      --ftp-regular,
      --num-retries

    Removed -m option on FTP put command.  This means that
    the remote directory must exist prior to backup.

    Changed ftpBackend from -f option back to commandline.
    Various versions of ncftp* interact differently when
    both -f and commandline options are supplied.

    The FTP password is munged in all log operations.

    Added logging of filenames in the bucket when -v9 is
    used on Amazon S3.

    * duplicity/commandline.py, duplicity/globals.py: Add support for:
      --ftp-passive,
      --ftp-regular,
      --num-retries

    * duplicity.1: Add descriptions for:
      --ftp-passive,
      --ftp-regular,
      --num-retries

2007-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/commandline.py: Replace missing comma in argument list.

2007-07-09  Kenneth Loafman  <kenneth@loafman.com>

    * dist/makedist: Changes for 0.4.3.RC9.
    Drop ftplib.py.

    * duplicity/ftplib.py: No longer needed.

    * CHANGELOG: Changes for 0.4.3.RC9.

    * duplicity/globals.py, duplicity/commandline.py:
    Added a commandline option, '--num-retries=<int>', to set the number
    of retries.  The default is 5.

    * duplicity/backends.py:
    New S3 backend, Boto, from Eric Evans, replaces bitBucket.  Boto can
    be obtained from http://code.google.com/p/boto/.  I did not make this
    a requirement for setup since its not in the normal repositories.

    New FTP backend from Thorsten Schnebeck that uses ncftp instead of
    Pythons ftplib.  This seems to be much more solid.  I added the -f
    option with a secure temp file to contain host, user, and password,
    rather than having them on the command line.  I also added the -m
    option to the put command to create the target directory and the -t
    option to make sure it times out if there is a network problem.

    The Backend class now contains a popen_persist function that acts like
    run_command_persist.  Both use the new num_retries global.

2007-06-29  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/diffdir.py: Change to a max block size of 2048 bytes for
    rsync difference buffer.  This may slow things
    down for truly large files, but will give much
    smaller deltas on files with numerous small
    changes, such as database files.

2007-06-27  Kenneth Loafman  <kenneth@loafman.com>

    * .cvsignore, duplicity/.cvsignore: Initial release.

    * CHANGELOG: Changes for 0.4.3.RC8

    * duplicity/gpg.py: Bug 20039 - Andreas Schildbach: --and--
    Patch 6030 - Alexander Zangerl <az@debian.org>:
    Duplicity now uses bzip2 for compression.  This matches the way
    the Debian distribution handles it.  I'll think about adding an
    option to override later, if its needed.

    * duplicity/collections.py: Bug 20282 - Thomas Tuttle:
    An out of range index when checking past history in the backup
    sets caused a failure when trying to access later.

    Bug 20149 - dAniel hAhler:
    dAniel submitted a second patch for this for further cleanup.
    The new patch prefers the latest intact backup set.

2007-06-19  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.3.RC7

    * duplicity/collections.py: Patch 6029 - Alexander Zangerl <az@debian.org>:
    http://bugs.debian.org/370206
    archive-dir together with incremental backup results in crash. the
    patch is simple, the code in 0.4.2 did attempt to access strings as
    objects.

    * duplicity/commandline.py: Patch 6033 - Alexander Zangerl <az@debian.org>:
    let's add a --help terse usage message and don't just direct the user
    to the manual. this should come handy if somebody needs to restore
    stuff without having the manual available.

    * duplicity-bin, duplicity.1, duplicity/commandline.py, duplicity/globals.py:
    Patch 6032 - Alexander Zangerl <az@debian.org>:
    a new feature patch: i've recently gotten annoyed with having gazillions of
    5mb files and therefore added a --volsize option to allow the user setting
    the chunk size. the patch is simple and contains a manpage update as well.

    * duplicity-bin: Add -u (unbuffered) to shebang line.

    * duplicity/log.py: Add stderr.flush() in FatalError().

    * duplicity/backends.py:
    Bug 20179 - dAniel hAhler: When errors cause login to fail in FTP,
    reset and try again.

2007-06-13  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/tarfile.py.old, duplicity/selection.py.old: Not needed.

    * duplicity/backends.py:
    Cosmetic change to force new log.  The log for revision 1.28
    is not correct.  It should read as follows:

    Patch 5993 - daacyy302@sneakemail.com: Make Amazon S3 backend
    incrementally more robust for recovery.

    * CHANGELOG: Changes for 0.4.3.RC6.

    * duplicity/path.py:
    Patch 5998 - Kuang-che Wu: Cache uid and gid lookup to speed
    operations.

    * duplicity/collections.py, duplicity/backends.py:
    Bug 20419 - dAniel hAhler: When errors cause an incomplete backup set,
    flag the error with a message, rather than erroring out.  The user
    then knows to run --cleanup.

2007-06-04  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.3.RC5.

    * duplicity/selection.py:
    dAniel hAhler submitted a patch to change "Error initializing file
    foo" (log level 2), where foo was a socket, to "Skipping socket foo"
    (log level 7).  https://savannah.nongnu.org/patch/?5985

    * duplicity/log.py:
    Change logging to flush after every write, unbuffering stdout and
    stderr, thus producing logs that are coherent.

    * duplicity-bin, duplicity/gpg.py:
    GnuPG fails when trying to access stdin on an empty passphrase.
    Changes allow empty passphrase on public-key encryption and now
    respond gracefully on empty passphrase for symmetric encryption.

2007-06-02  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes for 0.4.3.RC4.

    * duplicity/backends.py:
    Move catch of NLST errors back to self.error_retry()

    * duplicity/backends.py, CHANGELOG: More FTP fixes:
    - clean up error handling
    - change initial error delay to zero
    - move catch of NLST errors to self.list()

2007-05-31  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Changes to release 0.4.3.RC3.

2007-05-30  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: - Fix so that FTP connection/login is closed and
    reopened when errors 221 or 421 are reported.

    - Fix grammer in error message.

    * CHANGELOG: Changes to release 0.4.3.RC2.

2007-05-29  Kenneth Loafman  <kenneth@loafman.com>

    * dist/duplicity.spec.template, dist/makedist, dist/makerpm, dist/setup.py:
    Remove GnuPGInterface.py

    * duplicity/tarfile.py: Apply patch for bug 19998, ValueError exception.

2007-05-26  Kenneth Loafman  <kenneth@loafman.com>

    * CHANGELOG: Added change notices for FTP password and rsync backend.

    * duplicity/backends.py:
    Fix request password in ftpBackend if environ not set.

    * duplicity/backends.py: - allow connection after 226 in NLST (ProFTPD)
    - request password in ftpBackend if environ not set
    - rsyncBackend was using the full URL, now uses server:path

    * CHANGELOG: Document changes for 0.4.3.

2007-05-25  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py: Do not set FTP to active mode at start of session.

2007-05-24  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/backends.py:
    1) WebDAV needs a Depth: 1 header otherwise infinite depth
    is assumed and may be restricted due to load.

    2) Used the allprop XML command to get back properties that
    included the filenames.  Refer to RFC 2518.

2007-05-23  Kenneth Loafman  <kenneth@loafman.com>

    * duplicity/ftplib.py: Fixes bug:
      https://savannah.nongnu.org/bugs/?19940

    * README, duplicity/GnuPGInterface.py, duplicity/gpg.py: Applied patches:
      https://savannah.nongnu.org/patch/?5680
      https://savannah.nongnu.org/patch/?5681

    * duplicity/backends.py: Added patches:
      https://savannah.nongnu.org/patch/?4486
      https://savannah.nongnu.org/patch/?5183
      https://savannah.nongnu.org/patch/?5185
      https://savannah.nongnu.org/patch/?5412
      https://savannah.nongnu.org/patch/?5413
      https://savannah.nongnu.org/patch/?5680
      https://savannah.nongnu.org/patch/?5681
      https://savannah.nongnu.org/patch/?5682
      https://savannah.nongnu.org/patch/?5794
      https://savannah.nongnu.org/patch/?5830

    Fixed bugs:
      https://savannah.nongnu.org/bugs/?2441
      https://savannah.nongnu.org/bugs/?16711

    Miscellaneous cosmetic fixes (spelling and spacing).

2006-05-09  Brian Sutherland  <jinty@lentejasverdes.ath.cx>

    * duplicity/backends.py: BitBucketBackend:
        * if something goes wrong and we need to re-connect, dump the exception
          on stderr. Be very noisy so that whatever is wrong will be fixed.

2006-05-03  Ben Escoto  <ben@emrose.org>

    * duplicity/collections.py: Typo fix for error message

2006-05-02  Brian Sutherland  <jinty@lentejasverdes.ath.cx>

    * duplicity/backends.py: Fix a bug in the bitbucket backend:
    We need to get a new bits from the new bucket if we re-connect.

2006-05-01  Brian Sutherland  <jinty@lentejasverdes.ath.cx>

    * duplicity/backends.py: Changes to the bitbucket backend:
    * Update to work with bitbucket 0.3b.
    * Add some docimentation.
    * Implement a suggestion by Ben Escoto to move the access and secret keys to
      environment variables.
    * Implement a very simplistic error correction mechanisim that will re-connect
      on an operation failure and re-try the operation. Note that this is just a
      band-aid for issues that should be resolved at lower levels.

2006-04-30  Ben Escoto  <ben@emrose.org>

    * CHANGELOG:
    Removed time_separator entry from changelog when I backed out patch

    * duplicity/globals.py:
    Went back to old time_separator, because I realized new way wouldn't
    handle some cases, and could break backwards compatibility

    * CHANGELOG, duplicity/backends.py, duplicity/globals.py:
    Andre Beckedorf's patches for ftp and rsync backends, and time_separator

    * CHANGELOG, duplicity.1, duplicity/backends.py:
    Checked in Brian Sutherland's Amazon S3 code

    * CHANGELOG: Added --sftp-command to changelog

    * duplicity.1, duplicity/commandline.py:
    Added --sftp-command option and man page documentation

    * CHANGELOG: Fixed Jiri's name.  Sorry about that :-)

2006-02-02  Ben Escoto  <ben@emrose.org>

    * CHANGELOG: final changes for version 0.4.2

    * CHANGELOG, duplicity/backends.py, duplicity/dup_temp.py:
    Fixes to the scp backend

2006-02-01  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, duplicity-bin, duplicity/collections.py, testing/finaltest.py:
    Stop --remove-older-than from deleting current chain

2006-01-31  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, duplicity/backends.py:
    Catch ftp error 450 when listing directory

    * CHANGELOG, duplicity.1, duplicity/collections.py:
    cleaned up and documented --collection-status

2006-01-12  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, duplicity/tarfile.py: asdf's tarfile large uid/gid patch

    * duplicity/backends.py: Jiri Tyr's scp/sftp patch

2006-01-01  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, duplicity-bin: Eric Hanchrow's remove signature patch

2005-12-31  Ben Escoto  <ben@emrose.org>

    * duplicity/gpg.py, testing/gpgtest.py, testing/rdiffdirtest.py, testing/statisticstest.py:
    A few minor updates so test pass on my system again

2003-11-21  Ben Escoto  <ben@emrose.org>

    * duplicity-bin, duplicity/_librsyncmodule.c, duplicity/collections.py, duplicity/dup_temp.py:
    MDR patch allows signing with different key

2003-08-14  Ben Escoto  <ben@emrose.org>

    * CHANGELOG: Added note about passphrase confirmation

    * duplicity-bin:
    When collecting password from user, make type it twice to confirm

2003-08-09  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, dist/makeweb: Final changes for 0.4.1

    * dist/duplicity.spec.template, dist/makedist, dist/makerpm:
    Updating rpm for Fedora

    * dist/duplicity.spec: Trying to remove...

    * dist/duplicity.spec, duplicity/path.py, duplicity/tarfile.py:
    Small changes for 0.4.1 and python 2.3

    * CHANGELOG: variable block size, librsync 0.9.6

    * TODO:
    Remove large file note now that block size chosen based on file size

    * duplicity/_librsyncmodule.c, duplicity/compilec.py, duplicity/diffdir.py, duplicity/librsync.py:
    Ported some code from rdiff-backup:  choose sig block based on file
    length, and work with librsync 0.9.6.

    * TODO, duplicity.1: Mention problem with /proc

2003-08-08  Ben Escoto  <ben@emrose.org>

    * duplicity/tarfile.py, testing/temp2.tar, testing/test_tarfile.py:
    Cache pwd and group files

    * duplicity.1, duplicity/commandline.py:
    Added --version switch, small change to man page

2003-08-07  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, TODO, duplicity.1, duplicity/backends.py, testing/backendtest.py, testing/finaltest.py:
    Sebastian Wilhelmi's update for rsync backend

    * duplicity/commandline.py:
    Applied Stephen Isard's patch for --exclude-globbing-filelist

2003-04-05  Ben Escoto  <ben@emrose.org>

    * duplicity.1: Added mention of rsync backend.

    * duplicity/backends.py: added rsync contributed by Sebastian Wilhelmi

2003-03-13  Ben Escoto  <ben@emrose.org>

    * testing/finaltest.py, duplicity/tarfile.py.old, duplicity/tarfile.py, CHANGELOG:
    Added test and fix for long symlink to long file bug

2003-03-09  Ben Escoto  <ben@emrose.org>

    * TODO, duplicity-bin, duplicity/patchdir.py, testing/finaltest.py:
    Raise error (instead of exiting silently) if no files found to restore

    * testing/finaltest.py: Added long filenames test

2003-03-08  Ben Escoto  <ben@emrose.org>

    * TODO, duplicity.1: Added man page info on --short-filenames option

2003-02-02  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, TODO, duplicity-bin, duplicity/path.py:
    (version of) Helmut Schneider's patch to display mtimes with list files

2002-11-30  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, duplicity-bin, duplicity/commandline.py, duplicity/diffdir.py, duplicity/globals.py, duplicity/gpg.py, testing/finaltest.py, testing/gpgtest.py:
    Added --no-encryption option, fixed crash on inc when no changed files

    * CHANGELOG, duplicity-bin, duplicity.1, duplicity/backends.py, duplicity/commandline.py, duplicity/gpg.py, duplicity/path.py, testing/finaltest.py:
    Added --verify option, tweaked some verbosity levels

    * duplicity/path.py, testing/pathtest.py:
    Added compare_verbose and test to path module

2002-11-24  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, duplicity-bin, duplicity/diffdir.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, testing/finaltest.py, testing/patchdirtest.py:
    Changed restore procedure.  Now all sets integrated simultaneously.

2002-11-19  Ben Escoto  <ben@emrose.org>

    * duplicity/path.py: Fixed typo in get_ropath

2002-11-17  Ben Escoto  <ben@emrose.org>

    * dist/makeweb: Added a few options for only doing upload/move/checkin/etc

    * CHANGELOG, duplicity-bin, duplicity/diffdir.py, duplicity/gpg.py, testing/gpgtest.py:
    Changed way difftars are split between volumes to waste less space

    * duplicity/file_naming.py: Slight tweak to base36 code

    * CHANGELOG, duplicity/file_naming.py, testing/file_namingtest.py:
    Added extra tests for base36 conversion

    * CHANGELOG, duplicity/file_naming.py, testing/file_namingtest.py:
    Shorted short filenames (use base36)

    * CHANGELOG, duplicity/gpg.py:
    Swallow GPG logging output if verbosity 3 or less

    * CHANGELOG, duplicity-bin, duplicity.1, duplicity/collections.py, duplicity/commandline.py, duplicity/globals.py:
    Added --remove-older-than option, changed --current-time behavior

2002-11-16  Ben Escoto  <ben@emrose.org>

    * duplicity-bin, duplicity.1, duplicity/commandline.py:
    Added --cleanup option

    * duplicity.1, duplicity/commandline.py, duplicity/globals.py:
    Added --force option.

    * duplicity/collections.py, testing/collectionstest.py:
    Added code for finding extraneous and old files

    * duplicity/backends.py:
    For ssh, deleted in groups of 10 so command line doesn't overflow

    * CHANGELOG, duplicity/collections.py, duplicity/file_naming.py, duplicity/path.py, testing/collectionstest.py:
    Fixed a few minor collections bugs, added get_extraneous

2002-11-14  Ben Escoto  <ben@emrose.org>

    * TODO: Added note on one pass restores/verifies

    * CHANGELOG: Added --restore-time bug fix note

2002-11-11  Ben Escoto  <ben@emrose.org>

    * duplicity-bin: Better fix for same (current_time) bug

    * testing/finaltest.py: Fixed minor bug erasing output dir too early

    * duplicity-bin:
    Restores now default to current time if restore time not specified

    * TODO, duplicity-bin, duplicity/collections.py, duplicity/commandline.py:
    Added undocumended --collection-status option for testing purposes

    * TODO: More misc updates for 0.3.0

2002-11-10  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, dist/makedist, duplicity.1, testing/collectionstest.py, testing/dup_timetest.py:
    Few last minute tweaks to prepare for 0.3.0 release

    * CHANGELOG, duplicity.1, duplicity/backends.py, duplicity/commandline.py, testing/finaltest.py:
    Added --ssh-command and --scp-command options

    * duplicity/backends.py, duplicity/collections.py, duplicity/dup_time.py, testing/file_namingtest.py, testing/finaltest.py:
    Fixed time-must-be-int bug with --short-filenames, added test

    * duplicity-bin, duplicity/backends.py, testing/backendtest.py, testing/finaltest.py:
    Various bugfixes so ftp backend passes final test

    * CHANGELOG, duplicity/commandline.py, duplicity/file_naming.py, duplicity/globals.py, testing/file_namingtest.py:
    Added --short-filenames option

    * CHANGELOG, duplicity/backends.py, testing/backendtest.py:
    Added ftp backend support

2002-11-03  Ben Escoto  <ben@emrose.org>

    * duplicity.1: Added man page entry for --file-to-restore option

    * CHANGELOG, TODO, duplicity-bin, duplicity.1, duplicity/backends.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/globals.py, duplicity/path.py, duplicity/statistics.py, testing/statisticstest.py:
    Added statistics reporting after successful backup

2002-11-02  Ben Escoto  <ben@emrose.org>

    * dist/setup.py, duplicity-bin, duplicity.1, duplicity/commandline.py, duplicity/diffdir.py:
    Added --list-current-files option

    * CVS-README, dist/makedist, dist/makerpm, duplicity/compilec.py, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/manifesttest.py, testing/memcheck.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/selectiontest.py, testing/statictest.py, testing/test_tarfile.py:
    Make CVS more friendly; don't depend on src symlink

    * duplicity.1, rdiffdir.1: Updated documentation on new globbing options

    * CHANGELOG, duplicity/patchdir.py, testing/finaltest.py:
    Fixed bug & added test when root was reg file, not dir

    * CHANGELOG, TODO, duplicity/commandline.py, duplicity/selection.py, rdiffdir, testing/selectiontest.py:
    Added --include/exclude-globbing-filelist options

2002-11-01  Ben Escoto  <ben@emrose.org>

    * CHANGELOG, duplicity/patchdir.py, testing/patchdirtest.py:
    Fixed tar '..' security bug

2002-10-31  Ben Escoto  <ben@emrose.org>

    * testing/diffdirtest.py, testing/testfiles.tar.gz:
    Added 2 test cases: neg mtimes, missing u/gnames

    Now check to make sure these files aren't spuriously marked as
    changed.

    * duplicity/path.py: Fixed dumb st_time/st_mtime typo

2002-10-29  Ben Escoto  <ben@emrose.org>

    * README: Updated with new web page/mailing list information.

    * duplicity-bin, duplicity/backends.py, duplicity/collections.py, duplicity/commandline.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_time.py, duplicity/file_naming.py, duplicity/globals.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/static.py, rdiffdir:
    Added full GPL statement in source files at request of Jaime Villate
    of the Savannah site.  Also updated address of FSF.

2002-10-28  Ben Escoto  <ben@emrose.org>

    * duplicity/GnuPGInterface.py, duplicity/__init__.py, duplicity/_librsyncmodule.c, duplicity/backends.py, duplicity/collections.py, duplicity/commandline.py, duplicity/compilec.py, duplicity/diffdir.py, duplicity/dup_temp.py, duplicity/dup_time.py, duplicity/file_naming.py, duplicity/globals.py, duplicity/gpg.py, duplicity/lazy.py, duplicity/librsync.py, duplicity/log.py, duplicity/manifest.py, duplicity/misc.py, duplicity/patchdir.py, duplicity/path.py, duplicity/robust.py, duplicity/selection.py, duplicity/selection.py.old, duplicity/static.py, duplicity/tarfile.py, duplicity/tarfile.py.old, CHANGELOG, COPYING, README, TODO, dist/duplicity.spec, dist/makedist, dist/makerpm, dist/setup.py, duplicity-bin, duplicity.1, rdiffdir, rdiffdir.1, tarfile-LICENSE, testing/GnuPGInterfacetest.py, testing/backendtest.py, testing/collectionstest.py, testing/diffdirtest.py, testing/dup_temptest.py, testing/dup_timetest.py, testing/file_namingtest.py, testing/finaltest.py, testing/gpgtest.py, testing/gpgtest2.py, testing/lazytest.py, testing/manifesttest.py, testing/memcheck.py, testing/misctest.py, testing/patchdirtest.py, testing/pathtest.py, testing/rdiffdirtest.py, testing/roottest.py, testing/roottest.pyc, testing/selectiontest.py, testing/statictest.py, testing/temp2.tar, testing/test_tarfile.py, testing/testfiles.tar.gz, testing/testtar.tar:
    Initial checkin


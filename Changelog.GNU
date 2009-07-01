------------------------------------------------------------
revno: 546
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Wed 2009-07-01 10:03:52 -0500
message:
  Fixed issues in Checkpoint/Restart:
  * The --name backupname" option was added to allow the
    user to separate one archive from another.  If not
    specified, the default is an MD5 hash of the target
    URL, which should suffice for most uses.
  
  * The archive_dir (cache) is now stored in a standard
    location, defaulting to ~/.cache/duplicity.  See
    http://standards.freedesktop.org/basedir-spec/latest/
  
  * The interaction between the --archive-dir option and
    the --name option allows for four possible results
    for the location of the archive dir.
      - neither specified (default)
        ~/.cache/duplicity/hash-of-url
      - --archive-dir=~/arch, no --name
        ~/arch/hash-of-url
      - no --archive-dir, --name=foo
        ~/.cache/duplicity/foo
      - --archive-dir=~/arch, --name=foo
        ~/arch/foo
  
  * duplicity will now copy needed metadata from the
    remote store to the local cache as needed.  This
    means that the first use after upgraded from 0.5.x
    will have the metadata copied to the local archive
    dir in order to sync both.
  
  * cleanup will now work correctly with the archive
    dir and separates the local from the remote files.
modified:
  duplicity-bin
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/dup_temp.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/path.py
------------------------------------------------------------
revno: 545
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Sat 2009-06-27 08:30:45 -0500
message:
  Fixes bug 392905.  Allow omission of remote file name if the same as the source file name.
modified:
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 544
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Thu 2009-06-25 09:04:19 -0500
message:
  merge of lp:~kenneth-loafman/duplicity/smart-archive-v2
modified:
  .project
  duplicity/commandline.py
  duplicity/globals.py
    ------------------------------------------------------------
    revno: 541.2.2
    committer: kenneth@loafman.com
    branch nick: smart-archive-v2
    timestamp: Tue 2009-06-23 14:37:55 -0500
    message:
      * Change to use XDG_ convention per http://standards.freedesktop.org/basedir-spec/latest/
    modified:
      .project
      .pydevproject
      duplicity/globals.py
    ------------------------------------------------------------
    revno: 541.2.1
    committer: kenneth@loafman.com
    branch nick: duplicity-src
    timestamp: Tue 2009-06-23 13:57:00 -0500
    message:
      * Change handling of smart archive dir so both archive and name can be changed.
    modified:
      duplicity/commandline.py
      duplicity/globals.py
------------------------------------------------------------
revno: 543
committer: Michael Terry <michael.terry@canonical.com>
branch nick: trunk
timestamp: Wed 2009-06-24 15:08:27 -0400
message:
  merge lp:~mterry/duplicity/gio-dist-fix to distribute gio backend
modified:
  dist/makedist
    ------------------------------------------------------------
    revno: 541.1.2
    committer: Michael Terry <michael.terry@canonical.com>
    branch nick: gio-dist-fix
    timestamp: Wed 2009-06-24 15:06:35 -0400
    message:
      merge from trunk
    modified:
      duplicity/backends/sshbackend.py
    ------------------------------------------------------------
    revno: 541.1.1
    committer: Michael Terry <michael.terry@canonical.com>
    branch nick: duplicity-bzr
    timestamp: Wed 2009-06-24 13:02:34 -0400
    message:
      actually distribute the gio backend
    modified:
      dist/makedist
------------------------------------------------------------
revno: 542
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Wed 2009-06-24 14:03:05 -0500
message:
  Fix "external file not found" to show command and file names.
modified:
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 541
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Tue 2009-06-23 04:36:50 -0500
message:
  merge of lp:~scode/duplicity/smart-default-archive
modified:
  duplicity.1
  duplicity/backend.py
  duplicity/commandline.py
  duplicity/globals.py
    ------------------------------------------------------------
    revno: 525.1.10
    committer: kenneth@loafman.com
    branch nick: smart-default-archive
    timestamp: Tue 2009-06-23 04:09:48 -0500
    message:
      Avoid deprecation warning for md5 in Python 2.6.
    modified:
      duplicity/commandline.py
    ------------------------------------------------------------
    revno: 525.1.9
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-22 23:29:33 +0200
    message:
      * --name affects *expansion*, not default value, of --archive-dir
    modified:
      duplicity.1
    ------------------------------------------------------------
    revno: 525.1.8
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-22 23:27:33 +0200
    message:
      * fix a man page mistake from previous merge
      * remove last remnants of DUPLICITY_ARGS_HASH
    modified:
      duplicity.1
    ------------------------------------------------------------
    revno: 525.1.7
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-22 23:21:45 +0200
    message:
      * correct man page to claim hash of backend url rather than has of args
    modified:
      duplicity.1
    ------------------------------------------------------------
    revno: 525.1.6
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-22 23:19:11 +0200
    message:
      * figure out which arg is a backend url without actually instantiating a backend
    modified:
      duplicity/backend.py
      duplicity/commandline.py
    ------------------------------------------------------------
    revno: 525.1.5
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-22 23:09:47 +0200
    message:
      * make default value to --name be the has of the backend URL specifically, rather than
        the has of remaining args
      * outstanding issue: in order to figure out which arg is a backend we call get_backend();
        must either fix this or feel comfortable that instantiating (and not using) a backend
        is side-effect free
    modified:
      duplicity/commandline.py
    ------------------------------------------------------------
    revno: 525.1.4
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-22 22:44:33 +0200
    message:
      * introduce --name parameter to specify symbolic name of a backup
      * change --archive-dir expansion to look for %DUPLICITY_BACKUP_NAME%
      * which in turn defaults to the args hash previously used for
        --archive-dir and %DUPLICITY_ARGS_HASH% expansion
    modified:
      duplicity.1
      duplicity/commandline.py
      duplicity/globals.py
    ------------------------------------------------------------
    revno: 525.1.3
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-22 22:20:22 +0200
    message:
      * merge from trunk
    added:
      .bzrignore
      duplicity/backends/giobackend.py
    modified:
      duplicity.1
      duplicity/asyncscheduler.py
      duplicity/backend.py
      duplicity/backends/__init__.py
      duplicity/backends/sshbackend.py
      duplicity/commandline.py
      duplicity/gpg.py
      duplicity/log.py
      testing/backendtest.py
    ------------------------------------------------------------
    revno: 525.1.2
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: smart-default-archive
    timestamp: Mon 2009-06-15 23:58:29 +0200
    message:
      * support expansion of %DUPLICITY_ARGS_HASH% in --archive-dir value
      * default to ~/.duplicity/%DUPLICITY_ARGS_HASH$ so that default behavior
        works well even when the user has multiple backup destinations
      * update the manpage accordingly
    modified:
      duplicity.1
      duplicity/commandline.py
      duplicity/globals.py
------------------------------------------------------------
revno: 540
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Tue 2009-06-23 04:22:42 -0500
message:
  Misc project changes.
modified:
  .project
------------------------------------------------------------
revno: 539
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Tue 2009-06-23 04:21:09 -0500
message:
  If python is run setuid, it's only partway set, so make sure to run with euid/egid of root.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 538
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Tue 2009-06-23 04:18:39 -0500
message:
  Create testfiles/output in SetUp routine so it will run standalone.
modified:
  testing/collectionstest.py
------------------------------------------------------------
revno: 537
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Sun 2009-06-21 13:48:19 -0500
message:
  Surround --gio option with try/except so user will not see traceback.
modified:
  duplicity/commandline.py
  duplicity/log.py
------------------------------------------------------------
revno: 536
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Sun 2009-06-21 12:54:22 -0500
message:
  Make GIO tests dependent on presence of gio module.
modified:
  testing/backendtest.py
------------------------------------------------------------
revno: 535
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Sun 2009-06-21 12:53:20 -0500
message:
  Fix 'get' command args.
modified:
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 534
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Sun 2009-06-21 10:19:31 -0500
message:
  merge of lp:~cjwatson/duplicity/always-sftp
modified:
  duplicity/backends/sshbackend.py
    ------------------------------------------------------------
    revno: 508.1.1
    committer: Colin Watson <cjwatson@canonical.com>
    branch nick: always-sftp
    timestamp: Wed 2009-05-06 17:24:39 +0100
    message:
      initial attempt at using only sftp on the client (https://savannah.nongnu.org/bugs/index.php?26464)
    modified:
      duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 533
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Sun 2009-06-21 10:14:54 -0500
message:
  Add .bzrignore
added:
  .bzrignore
    ------------------------------------------------------------
    revno: 518.3.2
    committer: Michael Terry <michael.terry@canonical.com>
    branch nick: duplicity.logworker
    timestamp: Thu 2009-06-18 20:42:30 -0400
    message:
      merge with trunk
    modified:
      CHANGELOG
      Changelog.GNU
      duplicity-bin
      duplicity.1
      duplicity/GnuPGInterface.py
      duplicity/asyncscheduler.py
      duplicity/backend.py
      duplicity/collections.py
      duplicity/commandline.py
      duplicity/diffdir.py
      duplicity/dup_temp.py
      duplicity/file_naming.py
      duplicity/globals.py
      duplicity/gpg.py
      duplicity/log.py
      duplicity/manifest.py
      duplicity/path.py
      duplicity/tempdir.py
      testing/GnuPGInterfacetest.py
      testing/backendtest.py
      testing/collectionstest.py
      testing/diffdirtest.py
      testing/dup_temptest.py
      testing/file_namingtest.py
      testing/finaltest.py
      testing/gpgtest.py
      testing/manifesttest.py
      testing/misctest.py
      testing/patchdirtest.py
      testing/pathtest.py
      testing/rdiffdirtest.py
      testing/roottest.py
      testing/run-a-test.sh
      testing/run-all-tests.sh
      testing/run-coverage.sh
      testing/selectiontest.py
      testing/statisticstest.py
------------------------------------------------------------
revno: 532
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Sat 2009-06-20 12:20:32 -0500
message:
  merge of lp:~scode/duplicity/bug-387102
modified:
  duplicity/asyncscheduler.py
    ------------------------------------------------------------
    revno: 525.3.3
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: bug-387102
    timestamp: Thu 2009-06-18 23:30:03 +0200
    message:
      * merge lp:~mterry/duplicity/log-upload-events since I created conflicts with my
        changes
    modified:
      duplicity/asyncscheduler.py
      duplicity/log.py
    ------------------------------------------------------------
    revno: 525.3.2
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: bug-387102
    timestamp: Tue 2009-06-16 23:16:34 +0200
    message:
      * s/self.__waiter/self.__failed_waiter/
    modified:
      duplicity/asyncscheduler.py
    ------------------------------------------------------------
    revno: 525.3.1
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: bug-387102
    timestamp: Tue 2009-06-16 22:45:35 +0200
    message:
      * significantly re-design the asynch scheduler to be much simpler; instead of keeping workers
        and queues, simply launch a thread for each unit of work, blocking when called for by
        a concurrency limit or a barrier. the old design was a result of initially designing for
        keeping a persistent set of workers, only to then drop that idea. when dropping that idea,
        I should have re-done it like this from the start instead of retaining the complexity
        i introduced for the persistent worker design.
    modified:
      duplicity/asyncscheduler.py
------------------------------------------------------------
revno: 531
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Sat 2009-06-20 10:44:27 -0500
message:
  merge of lp:~scode/duplicity/reasonable-io-blocksize
modified:
  duplicity/gpg.py
    ------------------------------------------------------------
    revno: 525.2.1
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: reasonable-io-blocksize
    timestamp: Tue 2009-06-16 20:45:58 +0200
    message:
      * GPGWriteFile: what was previously the minimum block is is now just the block size; meaning
        the maximum block size used for individual I/O operations, but still the minimum in terms
        of when to give up on the iteration
      * GZipWriteFile: similar change, though blocksize handling was a bit different
    modified:
      duplicity/gpg.py
------------------------------------------------------------
revno: 530
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Sat 2009-06-20 10:29:33 -0500
message:
  Fix regression -- add tahoebackend back in.
modified:
  duplicity/backends/__init__.py
------------------------------------------------------------
revno: 529
committer: Kenneth Loafman <kenneth@loafman.com>
branch nick: duplicity-src
timestamp: Fri 2009-06-19 08:09:16 -0500
message:
  s/src.name/self.src.name/ in exception handling path
modified:
  duplicity/dup_temp.py
    ------------------------------------------------------------
    revno: 525.1.1
    committer: Peter Schuller <peter.schuller@infidyne.com>
    branch nick: misc
    timestamp: Mon 2009-06-15 22:45:33 +0200
    message:
      * s/src.name/self.src.name/ in exception handling path
    modified:
      duplicity/dup_temp.py
------------------------------------------------------------
revno: 528
committer: Michael Terry <michael.terry@canonical.com>
branch nick: duplicity
timestamp: Thu 2009-06-18 20:46:29 -0400
message:
  merge log worker event info codes
modified:
  duplicity/asyncscheduler.py
  duplicity/log.py
    ------------------------------------------------------------
    revno: 518.3.1
    committer: Michael Terry <michael.terry@canonical.com>
    branch nick: duplicity.logworker
    timestamp: Sun 2009-05-31 06:53:34 -0400
    message:
      add log codes for upload events
    modified:
      duplicity/asyncscheduler.py
      duplicity/log.py
------------------------------------------------------------
revno: 527
committer: Michael Terry <michael.terry@canonical.com>
branch nick: duplicity
timestamp: Thu 2009-06-18 20:31:56 -0400
message:
  Merge GIO branch, supporting the --gio argument
added:
  duplicity/backends/giobackend.py
modified:
  duplicity.1
  duplicity/backend.py
  duplicity/commandline.py
  testing/backendtest.py
    ------------------------------------------------------------
    revno: 518.2.2
    committer: Michael Terry <michael.terry@canonical.com>
    branch nick: duplicity-bzr
    timestamp: Thu 2009-06-04 14:07:07 -0400
    message:
      don't be so specific about exceptions we catch
    modified:
      duplicity/backends/giobackend.py
    ------------------------------------------------------------
    revno: 518.2.1
    committer: Michael Terry <michael.terry@canonical.com>
    branch nick: duplicity-bzr
    timestamp: Thu 2009-06-04 13:57:56 -0400
    message:
      add GIO backend
    added:
      duplicity/backends/giobackend.py
    modified:
      duplicity.1
      duplicity/backend.py
      duplicity/commandline.py
      testing/backendtest.py
    ------------------------------------------------------------
    revno: 518.1.1
    committer: Michael Terry <michael.terry@canonical.com>
    branch nick: duplicity
    timestamp: Sat 2009-05-30 15:18:40 +0200
    message:
      add info codes for upload events
    added:
      duplicity/backends/giobackend.py
    modified:
      duplicity/asyncscheduler.py
      duplicity/log.py
------------------------------------------------------------
revno: 526
committer: kenneth@loafman.com
branch nick: duplicity-src
timestamp: Thu 2009-06-18 14:58:18 -0500
message:
  Fix omitted changes in duplicity manpage.
modified:
  duplicity.1
------------------------------------------------------------
revno: 525
committer: loafman
timestamp: Mon 2009-06-08 13:39:44 +0000
message:
  Changes for 0.6.0.
modified:
  CHANGELOG
  Changelog.GNU
------------------------------------------------------------
revno: 524
committer: loafman
timestamp: Mon 2009-06-08 13:01:52 +0000
message:
  Some cleanup on the forced assertion test code to allow
  multiple failures and no traceback for the assert.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 523
committer: loafman
timestamp: Mon 2009-06-08 12:59:52 +0000
message:
  Add code for testing of Checkpoint/Restore that I had been doing by hand, both single and multiple failure tests, with verify at the end.
modified:
  testing/finaltest.py
------------------------------------------------------------
revno: 522
committer: loafman
timestamp: Sun 2009-06-07 12:51:51 +0000
message:
  Fix getrlimit usage for Cygwin, which was returning -1 for the hard limit on max open files.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 521
committer: loafman
timestamp: Sat 2009-06-06 17:35:19 +0000
message:
  After merge of Checkpoint/Restart.
modified:
  CHANGELOG
  duplicity-bin
  duplicity/GnuPGInterface.py
  duplicity/backend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/path.py
  duplicity/tempdir.py
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/manifesttest.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/run-a-test.sh
  testing/run-all-tests.sh
  testing/run-coverage.sh
  testing/selectiontest.py
  testing/statisticstest.py
------------------------------------------------------------
revno: 520
committer: loafman
timestamp: Sat 2009-06-06 17:23:44 +0000
message:
  Checkpoint - Prep for merge of duplicity-cprs.
modified:
  Changelog.GNU
------------------------------------------------------------
revno: 519
committer: loafman
timestamp: Sat 2009-06-06 17:22:47 +0000
message:
  Allow handling of unicode filenames in log messages.
modified:
  duplicity/log.py
------------------------------------------------------------
revno: 518
committer: loafman
timestamp: Wed 2009-05-20 18:17:23 +0000
message:
  Changes for 0.5.18.
modified:
  CHANGELOG
  Changelog.GNU
------------------------------------------------------------
revno: 517
committer: loafman
timestamp: Wed 2009-05-20 18:42:39 +0000
message:
  Changes for 0.5.18.
modified:
  dist/makedist
------------------------------------------------------------
revno: 516
committer: loafman
timestamp: Thu 2009-05-14 13:57:42 +0000
message:
  Correct copyright.
modified:
  duplicity/backends/cloudfilesbackend.py
------------------------------------------------------------
revno: 515
committer: loafman
timestamp: Wed 2009-05-13 18:50:23 +0000
message:
  Reset file type preferences.
removed:
  .settings/org.eclipse.core.resources.prefs
------------------------------------------------------------
revno: 514
committer: loafman
timestamp: Wed 2009-05-13 18:24:03 +0000
message:
  Changed from using ulimit external command to
  resource.getrlimit to check open files limit.
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 513
committer: loafman
timestamp: Wed 2009-05-13 18:20:25 +0000
message:
  patch #6743: Tahoe backend for duplicity
  https://savannah.nongnu.org/patch/?6743
added:
  duplicity/backends/tahoebackend.py
modified:
  CHANGELOG
  duplicity.1
  duplicity/commandline.py
------------------------------------------------------------
revno: 512
committer: loafman
timestamp: Wed 2009-05-13 17:15:44 +0000
message:
  Only half of this bug is fixed but it's still useful.
  bug #21792: pipe call fails with an error OSError:
              [Errno 24] Too many open files
  https://savannah.nongnu.org/bugs/?21792
modified:
  CHANGELOG
  duplicity/GnuPGInterface.py
------------------------------------------------------------
revno: 511
committer: loafman
timestamp: Thu 2009-05-07 16:33:39 +0000
message:
  Added support for RackSpace's CloudFiles, cf+http.
added:
  .settings/org.eclipse.core.resources.prefs
modified:
  duplicity.1
  duplicity/log.py
------------------------------------------------------------
revno: 510
committer: loafman
timestamp: Thu 2009-05-07 16:30:29 +0000
message:
  Add more detail on connection failure.
modified:
  duplicity/backends/cloudfilesbackend.py
------------------------------------------------------------
revno: 509
committer: loafman
timestamp: Thu 2009-05-07 14:57:48 +0000
message:
  Added support for RackSpace's CloudFiles, cf+http.
added:
  duplicity/backends/cloudfilesbackend.py
modified:
  CHANGELOG
  duplicity/backends/__init__.py
  duplicity/commandline.py
  duplicity/log.py
------------------------------------------------------------
revno: 508
committer: loafman
timestamp: Mon 2009-05-04 12:29:23 +0000
message:
  Changes for 0.5.17.
modified:
  CHANGELOG
  Changelog.GNU
------------------------------------------------------------
revno: 507
committer: loafman
timestamp: Sat 2009-05-02 14:42:35 +0000
message:
  Checkpoint.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 506
committer: loafman
timestamp: Sat 2009-05-02 12:24:19 +0000
message:
  The previous revision got the wrong comment, so
  I cleaned up some code and checked back in.  The
  correct release comment should be:
  
  patch #6814: Ignore comments in filelists
  https://savannah.nongnu.org/patch/?6814
modified:
  duplicity/selection.py
------------------------------------------------------------
revno: 505
committer: loafman
timestamp: Sat 2009-05-02 12:06:19 +0000
message:
  patch #6813: Making changelist easy to read
  https://savannah.nongnu.org/patch/?6813
modified:
  duplicity/diffdir.py
  duplicity/selection.py
------------------------------------------------------------
revno: 504
committer: loafman
timestamp: Sat 2009-05-02 12:03:22 +0000
message:
  Moved from using the df command to get temp space
  availability to Python's os.statvfs() call.  Not all df
  commands work the same way.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 503
committer: loafman
timestamp: Wed 2009-04-22 11:36:09 +0000
message:
  I had put in some trial code that I removed incompletely that forced
  a full backup action.  This removes the last line of that code.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 502
committer: loafman
timestamp: Tue 2009-04-21 19:50:05 +0000
message:
  Changes for 0.5.16.
modified:
  .pydevproject
  CHANGELOG
  Changelog.GNU
------------------------------------------------------------
revno: 501
committer: loafman
timestamp: Tue 2009-04-21 19:34:17 +0000
message:
  Reduce max_open_files limit needed to 1024, was 2048.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 500
committer: loafman
timestamp: Tue 2009-04-21 19:29:10 +0000
message:
  Fix argument list in FatalError call re max open files.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 499
committer: loafman
timestamp: Tue 2009-04-21 18:24:36 +0000
message:
  bug #24825: duplicity warn on insufficient TMPDIR
              space availability and low max open
              file limits pre-backup.
  https://savannah.nongnu.org/bugs/?24825
  
  bug #25976: Password requested when not needed.
  https://savannah.nongnu.org/bugs/?25976
modified:
  duplicity-bin
------------------------------------------------------------
revno: 498
committer: loafman
timestamp: Tue 2009-04-21 17:40:02 +0000
message:
  Use os.access() check on regular files and dirs only.
modified:
  duplicity/selection.py
------------------------------------------------------------
revno: 497
committer: loafman
timestamp: Tue 2009-04-21 17:26:36 +0000
message:
  Added tilde and variable expansion to the source or
  target argument that is not a URL.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 496
committer: loafman
timestamp: Tue 2009-04-21 19:46:28 +0000
message:
  Remove check for only one $version string.
modified:
  dist/makedist
------------------------------------------------------------
revno: 495
committer: loafman
timestamp: Tue 2009-04-21 18:26:59 +0000
message:
  bug #24825: duplicity warn on insufficient TMPDIR
              space availability and low max open
              file limits pre-backup.
  https://savannah.nongnu.org/bugs/?24825
modified:
  duplicity/log.py
------------------------------------------------------------
revno: 494
committer: loafman
timestamp: Tue 2009-04-21 18:26:26 +0000
message:
  bug #25976: Password requested when not needed.
  https://savannah.nongnu.org/bugs/?25976
modified:
  duplicity/collections.py
  duplicity/gpg.py
------------------------------------------------------------
revno: 493
committer: loafman
timestamp: Tue 2009-04-21 17:46:07 +0000
message:
  Make sure gettext is included first.
  Add variable at top of file for verbosity.
modified:
  testing/config.py.tmpl
------------------------------------------------------------
revno: 492
committer: loafman
timestamp: Tue 2009-04-21 17:38:31 +0000
message:
  Add some documentation.
modified:
  duplicity/manifest.py
------------------------------------------------------------
revno: 491
committer: loafman
timestamp: Tue 2009-04-21 17:21:06 +0000
message:
  Make sure gettext is available by importing first.
modified:
  duplicity/__init__.py
  duplicity/backends/__init__.py
------------------------------------------------------------
revno: 490
committer: loafman
timestamp: Mon 2009-04-13 15:32:00 +0000
message:
  Move ssh and imap backend globals to globals.py.
modified:
  duplicity/backends/imapbackend.py
  duplicity/backends/sshbackend.py
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 489
committer: loafman
timestamp: Sun 2009-04-12 19:56:31 +0000
message:
  patch #6806: More graceful handling of old
               --short-filename files
  https://savannah.nongnu.org/patch/?6806
modified:
  CHANGELOG
  duplicity/file_naming.py
  testing/file_namingtest.py
------------------------------------------------------------
revno: 488
committer: loafman
timestamp: Sat 2009-04-11 02:06:01 +0000
message:
  bug #25594: wrong backup statistics
  https://savannah.nongnu.org/bugs/?25594
modified:
  CHANGELOG
  duplicity/diffdir.py
------------------------------------------------------------
revno: 487
committer: loafman
timestamp: Fri 2009-04-10 11:30:50 +0000
message:
  Not needed.
removed:
  .settings/.cvsignore
------------------------------------------------------------
revno: 486
committer: loafman
timestamp: Thu 2009-04-09 17:06:25 +0000
message:
  Changes for 0.5.15.
modified:
  CHANGELOG
  Changelog.GNU
  duplicity/.cvsignore
------------------------------------------------------------
revno: 485
committer: loafman
timestamp: Thu 2009-04-09 17:04:29 +0000
message:
  If a file is unreadable due to access rights or other
  non-fatal errors, put out error message and continue
  rather than dying messily with a traceback.
modified:
  duplicity/selection.py
------------------------------------------------------------
revno: 484
committer: loafman
timestamp: Thu 2009-04-09 16:32:15 +0000
message:
  Move SystemExit function back to the top and put
  a large note NOT to move it back down, otherwise,
  Exception gets invoked instead.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 483
committer: loafman
timestamp: Thu 2009-04-09 16:18:45 +0000
message:
  Remove "--restore-dir" from options[].
   It's not an option and never has been.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 482
committer: loafman
timestamp: Thu 2009-04-09 14:47:21 +0000
message:
  Added tilde '~' expansion and variable expansion in the
  options that require a filename.  You can now have this
  "--archive-dir=~/ArchDir/$SYSNAME" if you need it.  No
  expansion is applied to the source or target URL's.
modified:
  CHANGELOG
  duplicity/commandline.py
------------------------------------------------------------
revno: 481
committer: loafman
timestamp: Tue 2009-04-07 18:32:02 +0000
message:
  Unit tests were failing for ftp because of the filtering for
  duplicity-only filenames.  Corrected this and removed
  the check for the filename in the first element.
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 480
committer: loafman
timestamp: Tue 2009-04-07 14:51:13 +0000
message:
  If a file is unreadable due to access rights or other non-
  fatal errors, put out error message and continue.
modified:
  CHANGELOG
  duplicity/robust.py
------------------------------------------------------------
revno: 479
committer: loafman
timestamp: Fri 2009-04-03 15:22:26 +0000
message:
  FTP backend was failing on PureFTPd when the "-x ''"
  option was removed from the second ncftpls popen, a fix
  that was implemented due to bug #24741.  This fix does
  the ls in one pass by extracting either the first or the
  last entry on the 'ls -l'.  [Standard FTP would be nice!]
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 478
committer: loafman
timestamp: Thu 2009-04-02 15:48:06 +0000
message:
  Changes for 0.5.14.
modified:
  CHANGELOG
  Changelog.GNU
------------------------------------------------------------
revno: 477
committer: loafman
timestamp: Thu 2009-04-02 14:47:12 +0000
message:
  Normalized include statements and tried to insure that all
  duplicity includes were from the duplicity module.
modified:
  CHANGELOG
  Changelog.GNU
  duplicity-bin
  duplicity/asyncscheduler.py
  duplicity/backend.py
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/imapbackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_threading.py
  duplicity/dup_time.py
  duplicity/file_naming.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/statistics.py
  duplicity/tempdir.py
  rdiffdir
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/manifesttest.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/selectiontest.py
  testing/statictest.py
  testing/statisticstest.py
  testing/tempdirtest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 476
committer: loafman
timestamp: Wed 2009-04-01 15:07:45 +0000
message:
  After email voting among known duplicity contributors,
  the decision was reached to revert to the GPL Version 2
  license, so with their consensus, duplicity is now under
  GPL Version 2.
modified:
  CHANGELOG
  COPYING
  dist/makedist
  dist/makerpm
  dist/makeweb
  dist/setup.py
  duplicity-bin
  duplicity/__init__.py
  duplicity/_librsyncmodule.c
  duplicity/asyncscheduler.py
  duplicity/backend.py
  duplicity/backends/__init__.py
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/hsibackend.py
  duplicity/backends/imapbackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/rsyncbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/compilec.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_threading.py
  duplicity/dup_time.py
  duplicity/errors.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/static.py
  duplicity/statistics.py
  duplicity/tempdir.py
  duplicity/util.py
  po/Makevars
  rdiffdir
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/config.py.tmpl
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/logtest.py
  testing/manifesttest.py
  testing/misctest.py
  testing/parsedurltest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/run-a-test.sh
  testing/run-all-tests.sh
  testing/run-coverage.sh
  testing/selectiontest.py
  testing/statictest.py
  testing/statisticstest.py
  testing/tempdirtest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 475
committer: loafman
timestamp: Tue 2009-03-31 19:56:53 +0000
message:
  The -vN option has not changed.  Verbosity may also be one
  of: character [ewnid], or word ['error', 'warning', 'notice',
   'info', 'debug'].  The default is 4 (Notice).  The options
   -v4, -vn, and -vnotice are functionally equivalent, as are
   the mixed-case versions, -vN, -vNotice, -vNOTICE.
modified:
  duplicity.1
------------------------------------------------------------
revno: 474
committer: loafman
timestamp: Tue 2009-03-31 18:01:27 +0000
message:
  The -vN option has not changed.  Verbosity may also be one
  of: character [ewnid], or word ['error', 'warning', 'notice',
   'info', 'debug'].  The default is 4 (Notice).  The options
   -v4, -vn, and -vnotice are functionally equivalent, as are
   the mixed-case versions, -vN, -vNotice, -vNOTICE.
modified:
  CHANGELOG
  duplicity/commandline.py
------------------------------------------------------------
revno: 473
committer: loafman
timestamp: Mon 2009-03-30 15:39:01 +0000
message:
  patch #6790: Add --exclude-if-present
  https://savannah.nongnu.org/patch/?6790
modified:
  CHANGELOG
  duplicity.1
  duplicity/commandline.py
  duplicity/log.py
  duplicity/selection.py
------------------------------------------------------------
revno: 472
committer: loafman
timestamp: Mon 2009-03-30 13:21:13 +0000
message:
  Clarify recent log entries.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 471
committer: loafman
timestamp: Mon 2009-03-30 15:47:58 +0000
message:
  Add '../' to Python path so we find our GnuPGInterface and not another.
modified:
  testing/GnuPGInterfacetest.py
------------------------------------------------------------
revno: 470
committer: loafman
timestamp: Sun 2009-03-29 19:28:22 +0000
message:
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
modified:
  CHANGELOG
  duplicity-bin
  duplicity/backend.py
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/imapbackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/lazy.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/tempdir.py
  testing/file_namingtest.py
------------------------------------------------------------
revno: 469
committer: loafman
timestamp: Sun 2009-03-29 15:41:07 +0000
message:
  Revert to calling NcFTP utilities (ls, get, put) directly
  rather than scripting ncftp via pexpect.  Move fatal error
  regarding version 3.2.0 to a warning message since it has
  been reported that the segfault problem does not occur on
  most distributions.
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
  duplicity/log.py
------------------------------------------------------------
revno: 468
committer: loafman
timestamp: Thu 2009-03-26 17:08:52 +0000
message:
  Add Changelog.GNU to website and distribution to add a bit of detail
  showing the CVS changes via rcs2log.  Added dist/mkGNUChangelog.sh.
added:
  Changelog.GNU
  dist/mkGNUChangelog.sh
modified:
  CHANGELOG
  dist/makedist
------------------------------------------------------------
revno: 467
committer: loafman
timestamp: Wed 2009-03-25 17:18:04 +0000
message:
  bug #22908: Don't block gpg-agent
  https://savannah.nongnu.org/bugs/?22908
  
  To fix the above, --use-agent was added as a command line option.
  When this is specified and asymetric encryption is enabled, then all
  GnuPG passphrases will come from the gpg-agent or equivalent program
  and no passphrase prompt will be issued.
modified:
  CHANGELOG
  duplicity-bin
  duplicity.1
  duplicity/commandline.py
  duplicity/globals.py
  duplicity/gpg.py
------------------------------------------------------------
revno: 466
committer: loafman
timestamp: Wed 2009-03-25 18:28:14 +0000
message:
  Add testing/manual dir.
modified:
  testing/.cvsignore
------------------------------------------------------------
revno: 465
committer: loafman
timestamp: Mon 2009-03-23 19:18:44 +0000
message:
  bug #25976: Signed Backups Now Required
  https://savannah.nongnu.org/bugs/?25976
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 464
committer: loafman
timestamp: Sat 2009-03-21 18:58:51 +0000
message:
  patch #6787: import duplicity.GnuPGInterface explicitly
  https://savannah.nongnu.org/patch/?6787
modified:
  CHANGELOG
  duplicity/gpg.py
  testing/GnuPGInterfacetest.py
  testing/gpgtest2.py
------------------------------------------------------------
revno: 463
committer: loafman
timestamp: Sat 2009-03-21 19:02:07 +0000
message:
  Project setting changes.
added:
  .settings/de.loskutov.anyedit.AnyEditTools.prefs
  .settings/org.eclipse.ltk.core.refactoring.prefs
modified:
  .pydevproject
------------------------------------------------------------
revno: 462
committer: loafman
timestamp: Sat 2009-03-21 18:58:09 +0000
message:
  One statement per line.
  Indent text of error message to code level.
modified:
  duplicity/manifest.py
------------------------------------------------------------
revno: 461
committer: loafman
timestamp: Thu 2009-03-19 20:12:45 +0000
message:
  Fixed bug where an extra comma caused a traceback during a warning
  about unnecessary sig files.  Plus fixed print so the real filename
  would show up and not a Python object representation.
modified:
  CHANGELOG
  duplicity/collections.py
------------------------------------------------------------
revno: 460
committer: loafman
timestamp: Thu 2009-03-19 12:29:07 +0000
message:
  bug #25787: Usernames with escaped @-sign are not handled properly
  https://savannah.nongnu.org/bugs/?25787
modified:
  .project
  CHANGELOG
  duplicity/backend.py
  testing/parsedurltest.py
------------------------------------------------------------
revno: 459
committer: loafman
timestamp: Wed 2009-03-18 11:48:53 +0000
message:
  Adjust log levels so errors show up without verbosity.
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 458
committer: loafman
timestamp: Tue 2009-03-17 14:40:04 +0000
message:
  BackendException does not cause traceback except when
  verbosity is at level 9 (debug).
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 457
committer: loafman
timestamp: Tue 2009-03-17 14:37:44 +0000
message:
  Fix backends so sleep does not occur after last retry.
modified:
  CHANGELOG
  duplicity/backend.py
  duplicity/backends/botobackend.py
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 456
committer: loafman
timestamp: Tue 2009-03-17 14:35:46 +0000
message:
  Add more error detection to FTP backend.
  
  Fix backends so sleep does not occur after last retry.
modified:
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 455
committer: loafman
timestamp: Sun 2009-03-15 19:19:49 +0000
message:
  patch #6773: Make user name optional in rsync backend
  https://savannah.nongnu.org/patch/?6773
modified:
  CHANGELOG
  duplicity/backends/rsyncbackend.py
------------------------------------------------------------
revno: 454
committer: loafman
timestamp: Sun 2009-03-15 18:00:56 +0000
message:
  bug #25853: duplicity fails with boto passwords coming from ~/.boto
  https://savannah.nongnu.org/bugs/?25853
modified:
  CHANGELOG
  duplicity/backends/botobackend.py
------------------------------------------------------------
revno: 453
committer: loafman
timestamp: Sun 2009-03-15 19:20:37 +0000
message:
  GPG errors will no longer cause tracebacks, but will produce a
  log entry, from gpg, similar to the following:
  ===== Begin GnuPG log =====
  gpg: BAD0BAD0: skipped: public key not found
  gpg: [stdin]: encryption failed: public key not found
  ===== End GnuPG log =====
  This will let the user know what really caused the GPG process
  to fail, and what really caused errors like 'broken pipe'.
modified:
  duplicity/gpg.py
  duplicity/log.py
------------------------------------------------------------
revno: 452
committer: loafman
timestamp: Thu 2009-03-12 14:03:43 +0000
message:
  bug #25838: Backup fails / ncftp - remote file already exists
  https://savannah.nongnu.org/bugs/?25838
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 451
committer: loafman
timestamp: Wed 2009-03-11 20:12:27 +0000
message:
  Add / modify / repair Epydoc docstrings and format.
modified:
  CHANGELOG
  duplicity-bin
  duplicity/backend.py
  duplicity/backends/webdavbackend.py
------------------------------------------------------------
revno: 450
committer: loafman
timestamp: Wed 2009-03-11 20:00:44 +0000
message:
  One statement per line.
modified:
  duplicity/backends/rsyncbackend.py
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 449
committer: loafman
timestamp: Wed 2009-03-11 14:08:15 +0000
message:
  One statement per line.
modified:
  duplicity/backends/hsibackend.py
  duplicity/backends/localbackend.py
------------------------------------------------------------
revno: 448
committer: loafman
timestamp: Sun 2009-03-08 16:26:32 +0000
message:
  Changes for 0.5.11.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 447
committer: loafman
timestamp: Sun 2009-03-08 16:22:33 +0000
message:
  Bug #333057: GnuPGInterface prints exit statuses incorrectly
  https://bugs.launchpad.net/bugs/333057
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 446
committer: loafman
timestamp: Sun 2009-03-08 13:35:06 +0000
message:
  bug #25787: Usernames with @-sign are not handled properly
  https://savannah.nongnu.org/bugs/?25787
modified:
  CHANGELOG
  duplicity/backends/imapbackend.py
------------------------------------------------------------
revno: 445
committer: loafman
timestamp: Sun 2009-03-08 13:28:12 +0000
message:
  Detabify (was tab-width 8).
modified:
  duplicity/GnuPGInterface.py
------------------------------------------------------------
revno: 444
committer: loafman
timestamp: Sat 2009-03-07 22:01:37 +0000
message:
  Bug #333057: GnuPGInterface prints exit statuses incorrectly
  https://bugs.launchpad.net/bugs/333057
modified:
  CHANGELOG
  dist/makedist
------------------------------------------------------------
revno: 443
committer: loafman
timestamp: Sat 2009-03-07 21:30:52 +0000
message:
  Fix issue on return from waitpid where the result was shifted left and not right, producing 131072 instead of 2, as it should.
  
  Fixed some indent problems that PyDev complained about (Eclipse IDE).
added:
  duplicity/GnuPGInterface.py
------------------------------------------------------------
revno: 442
committer: loafman
timestamp: Sat 2009-03-07 18:11:25 +0000
message:
  One statement per line.
modified:
  rdiffdir
------------------------------------------------------------
revno: 441
committer: loafman
timestamp: Sat 2009-03-07 18:04:53 +0000
message:
  bug #25696: ncftp error with 0.5.09
  https://savannah.nongnu.org/bugs/?25696
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 440
committer: loafman
timestamp: Fri 2009-03-06 14:46:04 +0000
message:
  Also log the quit command.
modified:
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 439
committer: loafman
timestamp: Mon 2009-03-02 18:19:56 +0000
message:
  One statement per line.
modified:
  rdiffdir
------------------------------------------------------------
revno: 438
committer: loafman
timestamp: Mon 2009-03-02 15:54:00 +0000
message:
  bug #15664: When restoring backup: "OverflowError:
              long int too large to convert to int"
  https://savannah.nongnu.org/bugs/?15664
modified:
  CHANGELOG
  duplicity/path.py
------------------------------------------------------------
revno: 437
committer: loafman
timestamp: Mon 2009-03-02 14:17:08 +0000
message:
  One statement per line.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 436
committer: loafman
timestamp: Mon 2009-03-02 13:41:25 +0000
message:
  patch #6761: More robust pexpect handling of SSH authentication
  https://savannah.nongnu.org/patch/?6761
modified:
  CHANGELOG
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 435
committer: loafman
timestamp: Mon 2009-03-02 13:28:21 +0000
message:
  patch #6762: Wrong exit() used for 2.3/2.4 Python
  https://savannah.nongnu.org/patch/?6762
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 434
committer: loafman
timestamp: Mon 2009-03-02 15:09:59 +0000
message:
  One statement per line.
modified:
  duplicity/lazy.py
------------------------------------------------------------
revno: 433
committer: loafman
timestamp: Sun 2009-03-01 17:15:07 +0000
message:
  Explain new filenames and --time-separator better.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 432
committer: loafman
timestamp: Sun 2009-03-01 17:04:42 +0000
message:
  Changes for 0.5.10.
modified:
  CHANGELOG
  duplicity/commandline.py
------------------------------------------------------------
revno: 431
committer: loafman
timestamp: Sun 2009-03-01 16:37:12 +0000
message:
  Add deprecation warnings for options affected by old filenames.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 430
committer: loafman
timestamp: Sun 2009-03-01 13:20:34 +0000
message:
  bug #19988: Incompatibility to Samba/SMB share
  https://savannah.nongnu.org/bugs/?19988
modified:
  .cvsignore
  CHANGELOG
  duplicity.1
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/dup_time.py
  duplicity/globals.py
  testing/.cvsignore
  testing/dup_timetest.py
  testing/finaltest.py
------------------------------------------------------------
revno: 429
committer: loafman
timestamp: Sat 2009-02-28 22:37:45 +0000
message:
  One statement per line.
modified:
  duplicity/librsync.py
------------------------------------------------------------
revno: 428
committer: loafman
timestamp: Sat 2009-02-28 16:34:41 +0000
message:
  One statement per line.
modified:
  duplicity/misc.py
  duplicity/patchdir.py
------------------------------------------------------------
revno: 427
committer: loafman
timestamp: Fri 2009-02-27 22:12:14 +0000
message:
  Module gettext should be imported and installed prior to importing any other modules.  This allows long strings to be translated when put at the module level rather than at the function call level.  See dup_time.py for examples.
modified:
  duplicity-bin
  rdiffdir
------------------------------------------------------------
revno: 426
committer: loafman
timestamp: Fri 2009-02-27 22:16:12 +0000
message:
  One statement per line and other cleanup.
modified:
  duplicity/statistics.py
------------------------------------------------------------
revno: 425
committer: loafman
timestamp: Tue 2009-02-24 14:04:35 +0000
message:
  bug #25550: Error codes do not propagate from log to exit status
  https://savannah.nongnu.org/bugs/?25550
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 424
committer: loafman
timestamp: Sat 2009-02-21 15:31:27 +0000
message:
  bug #25097: Allow listing files from any time, not just current time
  https://savannah.nongnu.org/bugs/?25097
modified:
  CHANGELOG
  duplicity-bin
  duplicity.1
  duplicity/collections.py
  duplicity/commandline.py
------------------------------------------------------------
revno: 423
committer: loafman
timestamp: Fri 2009-02-20 17:57:30 +0000
message:
  Bug #229826 duplicity crashed with ValueError in port()
  https://bugs.launchpad.net/duplicity/+bug/229826
modified:
  CHANGELOG
  duplicity/backend.py
  testing/parsedurltest.py
------------------------------------------------------------
revno: 422
committer: loafman
timestamp: Tue 2009-02-17 12:55:58 +0000
message:
  Changes for 0.5.09.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 421
committer: loafman
timestamp: Fri 2009-02-13 19:08:14 +0000
message:
  If tempdir.py is included, but not instantiated, then deleted, it throws an exception,
  as happens during testing when duplicity main is not used to instantiate tempdir.
  The fix is to make sure instantiation has happened before calling cleanup().
modified:
  duplicity/tempdir.py
------------------------------------------------------------
revno: 420
committer: loafman
timestamp: Fri 2009-02-13 14:07:28 +0000
message:
  These are changes to make debugging easier.
  - Filter ANSI control (bolding) characters from NcFTP responses.
  - Turn off ad for ncftp server at close of each session.
modified:
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 419
committer: loafman
timestamp: Tue 2009-02-10 20:46:35 +0000
message:
  bug #25530: commandline passwd not working
  https://savannah.nongnu.org/bugs/?25530
modified:
  CHANGELOG
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 418
committer: loafman
timestamp: Tue 2009-02-10 19:02:27 +0000
message:
  FTP is now driven with pexpect rather than NcFTP utilities.
  This closes the following bugs:
  bug #24741: ncftpls -x '' causes failure on Yahoo FTP server
  bug #23516: duplicity/ncftpget not closing unlinked files, ...
modified:
  CHANGELOG
------------------------------------------------------------
revno: 417
committer: loafman
timestamp: Tue 2009-02-10 18:29:51 +0000
message:
  Merge from pexpect_ftp.
modified:
  duplicity/backends/ftpbackend.py
  testing/run-a-test.sh
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 416
committer: loafman
timestamp: Mon 2009-02-09 15:50:54 +0000
message:
  Applied retryImap2.patch from bug 25512.
modified:
  duplicity/backends/imapbackend.py
------------------------------------------------------------
revno: 415
committer: loafman
timestamp: Sun 2009-02-08 16:32:57 +0000
message:
  bug #25509: Logic error in imapbackend.py [IMAP_SERVER]
  https://savannah.nongnu.org/bugs/?25512
  
  bug #25512: [Patch] Retry on Imap failure
  https://savannah.nongnu.org/bugs/?25509
modified:
  CHANGELOG
  duplicity/backends/imapbackend.py
------------------------------------------------------------
revno: 414
committer: loafman
timestamp: Sun 2009-02-08 15:22:00 +0000
message:
  Replace rdiff-backup with duplicity in strings.
modified:
  dist/makedist
  duplicity/dup_time.py
------------------------------------------------------------
revno: 413
committer: loafman
timestamp: Sat 2009-02-07 14:08:20 +0000
message:
  Add copyright for author.
modified:
  duplicity/asyncscheduler.py
  duplicity/backends/imapbackend.py
------------------------------------------------------------
revno: 412
committer: loafman
timestamp: Sat 2009-02-07 13:06:01 +0000
message:
  Split parsedurl test from backendtest and add test cases.
added:
  testing/parsedurltest.py
modified:
  CHANGELOG
  testing/alltests
  testing/backendtest.py
------------------------------------------------------------
revno: 411
committer: loafman
timestamp: Thu 2009-02-05 17:26:48 +0000
message:
  Add NcFTP 3.2.0 exception clause to dependencies.
modified:
  README
------------------------------------------------------------
revno: 410
committer: loafman
timestamp: Mon 2009-02-02 15:36:44 +0000
message:
  Turns out going backwards in the license is not as easy as
  forwards.  Restoring GPLv3 license until consensus reached.
modified:
  CHANGELOG
  dist/makedist
  dist/makerpm
  dist/makeweb
  dist/setup.py
  duplicity-bin
  duplicity/__init__.py
  duplicity/_librsyncmodule.c
  duplicity/asyncscheduler.py
  duplicity/backend.py
  duplicity/backends/__init__.py
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/hsibackend.py
  duplicity/backends/imapbackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/rsyncbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/compilec.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_threading.py
  duplicity/dup_time.py
  duplicity/errors.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/static.py
  duplicity/statistics.py
  duplicity/tempdir.py
  duplicity/util.py
  po/Makevars
  rdiffdir
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/config.py.tmpl
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/logtest.py
  testing/manifesttest.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/run-a-test.sh
  testing/run-all-tests.sh
  testing/run-coverage.sh
  testing/selectiontest.py
  testing/statictest.py
  testing/statisticstest.py
  testing/tempdirtest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 409
committer: loafman
timestamp: Sun 2009-02-01 16:18:55 +0000
message:
  Add/update copyright statements in all distribution source files
  and revert duplicity to GPL version 2 license.
modified:
  duplicity/compilec.py
------------------------------------------------------------
revno: 408
committer: loafman
timestamp: Sat 2009-01-31 16:16:33 +0000
message:
  Changes for 0.5.07.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 407
committer: loafman
timestamp: Sat 2009-01-31 16:15:29 +0000
message:
  Python 2.3 unittest.py tried to call to a test-local variable named
  'test_id' and failed.  Changed to 'my_test_id' and all is well.
modified:
  testing/backendtest.py
------------------------------------------------------------
revno: 406
committer: loafman
timestamp: Fri 2009-01-30 13:29:15 +0000
message:
  Original fix to disallow use of ncftpput 3.2.0 mistyped the ErrorCode used.
modified:
  CHANGELOG
  duplicity/log.py
------------------------------------------------------------
revno: 405
committer: loafman
timestamp: Wed 2009-01-28 12:52:19 +0000
message:
  patch #6733: Improve error handling in imapbackend.py
  https://savannah.nongnu.org/patch/?6733
modified:
  CHANGELOG
  duplicity/backends/imapbackend.py
------------------------------------------------------------
revno: 404
committer: loafman
timestamp: Tue 2009-01-27 14:24:11 +0000
message:
  Add/update copyright statements in all distribution source files
  and revert duplicity to GPL version 2 license.
modified:
  CHANGELOG
  dist/makedist
  dist/makerpm
  dist/makeweb
  dist/setup.py
  duplicity-bin
  duplicity/__init__.py
  duplicity/_librsyncmodule.c
  duplicity/asyncscheduler.py
  duplicity/backend.py
  duplicity/backends/__init__.py
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/hsibackend.py
  duplicity/backends/imapbackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/rsyncbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_threading.py
  duplicity/dup_time.py
  duplicity/errors.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/static.py
  duplicity/statistics.py
  duplicity/tempdir.py
  duplicity/util.py
  po/Makevars
  rdiffdir
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/config.py.tmpl
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/logtest.py
  testing/manifesttest.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/run-a-test.sh
  testing/run-all-tests.sh
  testing/run-coverage.sh
  testing/selectiontest.py
  testing/statictest.py
  testing/statisticstest.py
  testing/tempdirtest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 403
committer: loafman
timestamp: Tue 2009-01-27 12:47:27 +0000
message:
  patch #6729: New imap backend. Replaces current gmail backend
  https://savannah.nongnu.org/patch/?6729
modified:
  dist/makedist
------------------------------------------------------------
revno: 402
committer: loafman
timestamp: Sun 2009-01-25 21:11:34 +0000
message:
  bug #25293: IOError: [Errno 22] Invalid argument
  https://savannah.nongnu.org/bugs/?25293
modified:
  CHANGELOG
  duplicity/diffdir.py
------------------------------------------------------------
revno: 401
committer: loafman
timestamp: Sun 2009-01-25 16:33:30 +0000
message:
  Modify patch #6730: Fix timing out for SSH backend
  Do not take out the first line from the return buffer (#4).
modified:
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 400
committer: loafman
timestamp: Sun 2009-01-25 15:25:18 +0000
message:
  patch #6730: Fix timing out for SSH backend
  https://savannah.nongnu.org/patch/?6730
modified:
  CHANGELOG
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 399
committer: loafman
timestamp: Sun 2009-01-25 15:08:56 +0000
message:
  patch #6729: New imap backend. Replaces current gmail backend
  https://savannah.nongnu.org/patch/?6729
removed:
  duplicity/backends/gmailimapbackend.py
added:
  duplicity/backends/imapbackend.py
modified:
  CHANGELOG
  duplicity.1
  duplicity/backend.py
  duplicity/backends/__init__.py
  duplicity/commandline.py
  duplicity/globals.py
  duplicity/urlparse_2_5.py
------------------------------------------------------------
revno: 398
committer: loafman
timestamp: Sun 2009-01-25 13:30:20 +0000
message:
  Removed ref to bug 25331 since the analysis and fix were both wrong.
  The issue was fixed correctly in bug 25403.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 397
committer: loafman
timestamp: Sun 2009-01-25 13:17:24 +0000
message:
  bug #25403: 0.5.06 "manifests not equal because different volume numbers"
  https://savannah.nongnu.org/bugs/?25403
modified:
  duplicity-bin
------------------------------------------------------------
revno: 396
committer: loafman
timestamp: Sun 2009-01-25 12:58:31 +0000
message:
  bug #25403: 0.5.06 "manifests not equal because different volume numbers"
  https://savannah.nongnu.org/bugs/?25403
modified:
  CHANGELOG
  duplicity/gpg.py
------------------------------------------------------------
revno: 395
committer: loafman
timestamp: Sun 2009-01-25 11:42:03 +0000
message:
  One statement per line.
modified:
  duplicity/manifest.py
------------------------------------------------------------
revno: 394
committer: loafman
timestamp: Sat 2009-01-24 22:16:17 +0000
message:
  Move alltests list to separate file.
added:
  testing/alltests
modified:
  testing/run-all-tests.sh
  testing/run-coverage.sh
------------------------------------------------------------
revno: 393
committer: loafman
timestamp: Sat 2009-01-24 16:58:08 +0000
message:
  Add coverage output to .cvsignore.
modified:
  testing/.cvsignore
------------------------------------------------------------
revno: 392
committer: loafman
timestamp: Sat 2009-01-24 16:57:05 +0000
message:
  Turn on verbose for unit tests.
modified:
  testing/run-a-test.sh
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 391
committer: loafman
timestamp: Sat 2009-01-24 16:56:03 +0000
message:
  Fix backendtest.py so that empty URL's in config.py cause the
  backend test to be skipped rather than erroring.  Added notes
  in config.py.tmpl explaining the change.
modified:
  CHANGELOG
  testing/backendtest.py
  testing/config.py.tmpl
------------------------------------------------------------
revno: 390
committer: loafman
timestamp: Fri 2009-01-23 21:09:42 +0000
message:
  Make default Python be system default version.
modified:
  .pydevproject
------------------------------------------------------------
revno: 389
committer: loafman
timestamp: Fri 2009-01-23 21:08:05 +0000
message:
  Add Releases directory.
modified:
  .cvsignore
------------------------------------------------------------
revno: 388
committer: loafman
timestamp: Fri 2009-01-23 21:06:37 +0000
message:
  First pass at coverage analysis, collect the data.
added:
  testing/run-coverage.sh
------------------------------------------------------------
revno: 387
committer: loafman
timestamp: Fri 2009-01-23 21:05:18 +0000
message:
  Remove LOG entries.  Not needed.
modified:
  testing/run-a-test.sh
------------------------------------------------------------
revno: 386
committer: loafman
timestamp: Fri 2009-01-23 13:22:49 +0000
message:
  Change to ASCII (-kkv)
------------------------------------------------------------
revno: 385
committer: loafman
timestamp: Fri 2009-01-23 10:53:08 +0000
message:
  Run a single unit test.
added:
  testing/run-a-test.sh
------------------------------------------------------------
revno: 384
committer: loafman
timestamp: Thu 2009-01-22 15:46:32 +0000
message:
  Increase default volume size (--volsize) to 25M from 5M.  This
  reduces the number of volumes to accomodate larger backups.
modified:
  CHANGELOG
  duplicity.1
  duplicity/globals.py
------------------------------------------------------------
revno: 383
committer: loafman
timestamp: Thu 2009-01-22 14:57:10 +0000
message:
  bug #25379: sys.exit() causes traceback and should not
  https://savannah.nongnu.org/bugs/index.php?25379
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 382
committer: loafman
timestamp: Sun 2009-01-18 17:24:03 +0000
message:
  Reworked patch 6701 to list collection one at a time rather than
  writing all as one huge list.  Was causing memeory problems when
  the collections got large.
modified:
  CHANGELOG
  duplicity-bin
  duplicity/log.py
------------------------------------------------------------
revno: 381
committer: loafman
timestamp: Thu 2009-01-15 16:45:59 +0000
message:
  bug #25331: When --archive-dir and --encrypt-key are used together, incremental fails.
  https://savannah.nongnu.org/bugs/index.php?25331
modified:
  CHANGELOG
------------------------------------------------------------
revno: 380
committer: loafman
timestamp: Thu 2009-01-15 14:58:50 +0000
message:
  bug #25331: When --archive-dir and --encrypt-key are used together, incremental fails.
  https://savannah.nongnu.org/bugs/index.php?25331
modified:
  duplicity-bin
------------------------------------------------------------
revno: 379
committer: loafman
timestamp: Fri 2009-01-09 13:57:01 +0000
message:
  Changes for 0.5.06.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 378
committer: loafman
timestamp: Thu 2009-01-08 15:31:18 +0000
message:
  Fix illegal macro .PP. by removing extraneous period on end.
modified:
  duplicity.1
------------------------------------------------------------
revno: 377
committer: loafman
timestamp: Wed 2009-01-07 15:05:39 +0000
message:
  NcFTP version 3.2.0 will not work with duplicity since we require the
  use of both -f and -C options on ncftpput.  3.1.9, 3.2.1+ work fine.
  I put in error checks for this situation in the FTP backend code.
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
  duplicity/log.py
------------------------------------------------------------
revno: 376
committer: loafman
timestamp: Tue 2009-01-06 22:11:37 +0000
message:
  Noah Spurrier has given us permission to distribute pexpect.py along
  with duplicity, so this will no longer be an install requirement.
added:
  duplicity/pexpect.py
modified:
  CHANGELOG
  README
  dist/makedist
  dist/setup.py
  duplicity/backends/sshbackend.py
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 375
committer: loafman
timestamp: Tue 2009-01-06 17:32:08 +0000
message:
  Added loop to run-all-tests.sh to run all tests against all supported
  versions of Python if available.  Looks for 2.3, 2.4, 2.5, 2.6.
modified:
  CHANGELOG
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 374
committer: loafman
timestamp: Tue 2009-01-06 17:28:00 +0000
message:
  Fix to deprecation warnings about sha and md5 modules.
  Uses hashlib if available, otherwise original module.
modified:
  CHANGELOG
  duplicity/gpg.py
------------------------------------------------------------
revno: 373
committer: loafman
timestamp: Mon 2009-01-05 20:36:04 +0000
message:
  Missed the most basic case, no selection functions.  Fixed.
modified:
  duplicity/selection.py
------------------------------------------------------------
revno: 372
committer: loafman
timestamp: Mon 2009-01-05 20:18:23 +0000
message:
  bug #25230: --include-globbing-filelist only including first entry.
  https://savannah.nongnu.org/bugs/?25230
modified:
  CHANGELOG
  duplicity/selection.py
  testing/selectiontest.py
------------------------------------------------------------
revno: 371
committer: loafman
timestamp: Sun 2009-01-04 17:25:09 +0000
message:
  sr #106583: document the need to use the --force option
  https://savannah.nongnu.org/support/?106583
modified:
  CHANGELOG
  duplicity.1
------------------------------------------------------------
revno: 370
committer: loafman
timestamp: Sat 2009-01-03 15:00:53 +0000
message:
  patch #6709: Report correct number of volumes when restoring
  https://savannah.nongnu.org/patch/?6709
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 369
committer: loafman
timestamp: Sat 2009-01-03 14:54:48 +0000
message:
  bug #25239: Error during clean, wrong case in duplcicity
  https://savannah.nongnu.org/bugs/?25239
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 368
committer: loafman
timestamp: Tue 2008-12-30 16:06:22 +0000
message:
  Changes for 0.5.05.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 367
committer: loafman
timestamp: Tue 2008-12-30 15:22:56 +0000
message:
  Add po files back into distribution.
modified:
  dist/makedist
------------------------------------------------------------
revno: 366
committer: loafman
timestamp: Tue 2008-12-30 13:28:44 +0000
message:
  Cosmetic - reformat FatalError calls at end for readability.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 365
committer: loafman
timestamp: Mon 2008-12-29 17:32:55 +0000
message:
  Change "test" to "$version".
modified:
  dist/setup.py
------------------------------------------------------------
revno: 364
committer: loafman
timestamp: Mon 2008-12-29 15:56:59 +0000
message:
  Build list of .mo files to be installed from po directory.
modified:
  dist/setup.py
------------------------------------------------------------
revno: 363
committer: loafman
timestamp: Mon 2008-12-29 14:50:41 +0000
message:
  bug #25194: Duplicity 5.04 requires python-distutils-extra...
  https://savannah.nongnu.org/bugs/?25194
removed:
  po/io.po
added:
  .settings/
  .settings/.cvsignore
  po/io/
  po/io/duplicity.mo
  po/io/duplicity.po
modified:
  CHANGELOG
  dist/makedist
  dist/setup.py
  po/POTFILES.in
------------------------------------------------------------
revno: 362
committer: loafman
timestamp: Mon 2008-12-29 00:25:11 +0000
message:
  Use reldate expansion to include release date.
modified:
  duplicity-bin
  duplicity.1
  rdiffdir.1
------------------------------------------------------------
revno: 361
committer: loafman
timestamp: Mon 2008-12-29 00:21:27 +0000
message:
  - Use os.path.join() instead of hardcoded strings
  - Make VersionedCopy replace $reldate as well as $version
modified:
  dist/makedist
------------------------------------------------------------
revno: 360
committer: loafman
timestamp: Sat 2008-12-27 22:42:18 +0000
message:
  Adjust RPM spec file for translations.
modified:
  dist/duplicity.spec.template
------------------------------------------------------------
revno: 359
committer: loafman
timestamp: Sat 2008-12-27 16:07:14 +0000
message:
  Changes for 0.5.04.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 358
committer: loafman
timestamp: Mon 2008-12-22 19:53:01 +0000
message:
  patch #6702: handle unknown errnos in robust.py
  https://savannah.nongnu.org/patch/?6702
modified:
  CHANGELOG
  duplicity/robust.py
------------------------------------------------------------
revno: 357
committer: loafman
timestamp: Mon 2008-12-22 19:49:40 +0000
message:
  patch #6700: Make duplicity translatable
  https://savannah.nongnu.org/patch/?6700
  [not in patch - added after unit tests]
modified:
  rdiffdir
  testing/config.py.tmpl
------------------------------------------------------------
revno: 356
committer: loafman
timestamp: Mon 2008-12-22 19:01:06 +0000
message:
  patch #6701: Make current-list command machine-readable
  https://savannah.nongnu.org/patch/?6701
modified:
  CHANGELOG
  duplicity-bin
  duplicity/log.py
------------------------------------------------------------
revno: 355
committer: loafman
timestamp: Mon 2008-12-22 17:22:44 +0000
message:
  patch #6700: Make duplicity translatable
  https://savannah.nongnu.org/patch/?6700
added:
  po/
  po/Makevars
  po/POTFILES.in
  po/io.po
modified:
  CHANGELOG
  dist/makedist
  dist/setup.py
  duplicity-bin
  duplicity/asyncscheduler.py
  duplicity/backend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/lazy.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/tempdir.py
------------------------------------------------------------
revno: 354
committer: loafman
timestamp: Mon 2008-12-22 16:24:31 +0000
message:
  GPG was throwing "gpg: [don't know]: invalid packet (ctb=14)" and apparently this is non-fatal.
  There is a fix for this being rolled into GPG 2.x.
  http://lists.gnupg.org/pipermail/gnupg-devel/2006-September/023180.html
  Copied from collections.py.  Fix supplied by Simon Blandford <simon@onepointltd.com>
modified:
  CHANGELOG
  duplicity/gpg.py
------------------------------------------------------------
revno: 353
committer: loafman
timestamp: Mon 2008-12-15 23:03:42 +0000
message:
  One statement per line.  No other changes.
modified:
  duplicity/selection.py
------------------------------------------------------------
revno: 352
committer: loafman
timestamp: Mon 2008-12-15 22:53:20 +0000
message:
  One statement per line.  No other changes.
modified:
  duplicity/path.py
------------------------------------------------------------
revno: 351
committer: loafman
timestamp: Mon 2008-12-15 22:15:37 +0000
message:
  Print backend name for each test started.
modified:
  testing/backendtest.py
------------------------------------------------------------
revno: 350
committer: loafman
timestamp: Mon 2008-12-15 21:29:51 +0000
message:
  Remove test for assert on non-existing delete.  Not all backends will raise an exception when the target of a delete does not exist.
modified:
  testing/backendtest.py
------------------------------------------------------------
revno: 349
committer: loafman
timestamp: Mon 2008-12-15 21:16:56 +0000
message:
  Log correct file name in line 67.  Use diff_ropath, not basis_path.
modified:
  duplicity/patchdir.py
------------------------------------------------------------
revno: 348
committer: loafman
timestamp: Mon 2008-12-15 15:28:11 +0000
message:
  Fix patch applied during Patch #6696.  Applied fixiter.diff.
modified:
  duplicity/diffdir.py
  duplicity/log.py
------------------------------------------------------------
revno: 347
committer: loafman
timestamp: Mon 2008-12-15 13:33:56 +0000
message:
  patch #6697: Always log at least one progress during dry run
  https://savannah.nongnu.org/patch/?6697
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 346
committer: loafman
timestamp: Mon 2008-12-15 13:28:39 +0000
message:
  patch #6696: Consolidate get_delta_iter and get_delta_iter_w_sig
  https://savannah.nongnu.org/patch/?6696
modified:
  CHANGELOG
  duplicity/diffdir.py
------------------------------------------------------------
revno: 345
committer: loafman
timestamp: Mon 2008-12-15 13:02:50 +0000
message:
  patch #6695: Log filenames
  https://savannah.nongnu.org/patch/?6695
modified:
  CHANGELOG
  duplicity/diffdir.py
  duplicity/log.py
  duplicity/patchdir.py
  duplicity/util.py
------------------------------------------------------------
revno: 344
committer: loafman
timestamp: Mon 2008-12-15 12:49:03 +0000
message:
  patch #6694: Log exceptions
  https://savannah.nongnu.org/patch/?6694
modified:
  CHANGELOG
  duplicity-bin
  duplicity/log.py
------------------------------------------------------------
revno: 343
committer: loafman
timestamp: Mon 2008-12-15 12:43:16 +0000
message:
  patch #6693: Some FatalError's don't have codes still
  https://savannah.nongnu.org/patch/?6693
modified:
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/sshbackend.py
  duplicity/log.py
------------------------------------------------------------
revno: 342
committer: loafman
timestamp: Mon 2008-12-15 12:35:17 +0000
message:
  patch #6692: Print collection status in a machine-readable way
  https://savannah.nongnu.org/patch/?6692
modified:
  CHANGELOG
  duplicity-bin
  duplicity/collections.py
  duplicity/log.py
------------------------------------------------------------
revno: 341
committer: loafman
timestamp: Sun 2008-12-14 13:23:25 +0000
message:
  bug #24889: NCFTP cannot deal with some FTP servers
  https://savannah.nongnu.org/bugs/?24889
modified:
  CHANGELOG
  duplicity/backends/ftpbackend.py
------------------------------------------------------------
revno: 340
committer: loafman
timestamp: Sun 2008-12-14 13:14:55 +0000
message:
  bug #25090: Typos and trailing whitespace in duplicity manpage
  https://savannah.nongnu.org/bugs/?25090
modified:
  CHANGELOG
  duplicity.1
  duplicity/.cvsignore
------------------------------------------------------------
revno: 339
committer: loafman
timestamp: Wed 2008-12-10 16:05:49 +0000
message:
  patch #6686: Add error codes for all fatal errors
  https://savannah.nongnu.org/patch/?6686
added:
  .project
  .pydevproject
modified:
  CHANGELOG
  duplicity-bin
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/log.py
  duplicity/selection.py
------------------------------------------------------------
revno: 338
committer: loafman
timestamp: Tue 2008-11-18 12:33:40 +0000
message:
  patch #6678: Add progress metering
  https://savannah.nongnu.org/patch/?6678
modified:
  CHANGELOG
  duplicity-bin
  duplicity/diffdir.py
  duplicity/log.py
  duplicity/statistics.py
------------------------------------------------------------
revno: 337
committer: loafman
timestamp: Mon 2008-11-17 22:02:42 +0000
message:
  Changes for 0.5.03.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 336
committer: loafman
timestamp: Sun 2008-11-16 18:52:30 +0000
message:
  patch #6676: Raw delta stats aren't right for multivolumes
  https://savannah.nongnu.org/patch/?6676
modified:
  duplicity/diffdir.py
------------------------------------------------------------
revno: 335
committer: loafman
timestamp: Sun 2008-11-16 18:48:13 +0000
message:
  patch #6675: Add modelines
  https://savannah.nongnu.org/patch/?6675
modified:
  dist/makedist
  dist/makerpm
  dist/makeweb
  dist/setup.py
  duplicity-bin
  duplicity/asyncscheduler.py
  duplicity/backend.py
  duplicity/backends/__init__.py
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/gmailimapbackend.py
  duplicity/backends/hsibackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/rsyncbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/compilec.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_threading.py
  duplicity/dup_time.py
  duplicity/errors.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/static.py
  duplicity/statistics.py
  duplicity/tarfile.py
  duplicity/tempdir.py
  duplicity/urlparse_2_5.py
  duplicity/util.py
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/logtest.py
  testing/manifesttest.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/selectiontest.py
  testing/statictest.py
  testing/statisticstest.py
  testing/tempdirtest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 334
committer: loafman
timestamp: Sun 2008-11-16 18:46:17 +0000
message:
  patch #6674: Add --log-* options to man page
  https://savannah.nongnu.org/patch/?6674
modified:
  duplicity.1
------------------------------------------------------------
revno: 333
committer: loafman
timestamp: Sun 2008-11-16 18:45:08 +0000
message:
  patch #6673: Add --dry-run option
  https://savannah.nongnu.org/patch/?6673
modified:
  duplicity-bin
  duplicity.1
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/globals.py
------------------------------------------------------------
revno: 332
committer: loafman
timestamp: Sat 2008-11-15 19:10:59 +0000
message:
  patch #6672: makedist doesn't ship util.py
  https://savannah.nongnu.org/patch/?6672
modified:
  dist/makedist
------------------------------------------------------------
revno: 331
committer: loafman
timestamp: Wed 2008-11-12 18:11:17 +0000
message:
  Add log.setup() call to main() to support new logging.
modified:
  rdiffdir
------------------------------------------------------------
revno: 330
committer: loafman
timestamp: Wed 2008-11-12 15:49:50 +0000
message:
  *** empty log message ***
modified:
  .cvsignore
------------------------------------------------------------
revno: 329
committer: loafman
timestamp: Wed 2008-11-12 15:49:28 +0000
message:
  Add log.setup() to support new logging.
modified:
  testing/config.py.tmpl
------------------------------------------------------------
revno: 328
committer: loafman
timestamp: Wed 2008-11-12 15:23:59 +0000
message:
  Checkpoint 2 prior to 5.03.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 327
committer: loafman
timestamp: Wed 2008-11-12 15:23:00 +0000
message:
  patch #6670: Machine Readable Output
  https://savannah.nongnu.org/patch/?6670
modified:
  duplicity-bin
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/gpg.py
  duplicity/log.py
  duplicity/manifest.py
------------------------------------------------------------
revno: 326
committer: loafman
timestamp: Wed 2008-11-12 15:00:52 +0000
message:
  Correct spelling of parsed_url (parsed_urk) in patch #6662.
modified:
  duplicity/backends/webdavbackend.py
------------------------------------------------------------
revno: 325
committer: loafman
timestamp: Wed 2008-11-12 14:09:44 +0000
message:
  sr #106534: GMail backups aren't stored in the correct location
  https://savannah.nongnu.org/support/?106534
modified:
  duplicity/backends/gmailimapbackend.py
------------------------------------------------------------
revno: 324
committer: loafman
timestamp: Wed 2008-11-12 13:53:17 +0000
message:
  sr #106496: put install-from-cvs-notes in CVS-README
  https://savannah.nongnu.org/support/?106496
modified:
  CVS-README
------------------------------------------------------------
revno: 323
committer: loafman
timestamp: Wed 2008-11-12 13:39:16 +0000
message:
  Checkpoint prior to 5.03.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 322
committer: loafman
timestamp: Wed 2008-11-12 13:38:16 +0000
message:
  patch #6638: correct typo in reporting lack of sufficiently new boto backend
  https://savannah.nongnu.org/patch/?6638
modified:
  duplicity/backends/botobackend.py
------------------------------------------------------------
revno: 321
committer: loafman
timestamp: Wed 2008-11-12 13:35:36 +0000
message:
  patch #6642: make ParsedUrl() thread-safe with respect to itself
  https://savannah.nongnu.org/patch/?6642
modified:
  duplicity/backend.py
------------------------------------------------------------
revno: 320
committer: loafman
timestamp: Wed 2008-11-12 13:29:40 +0000
message:
  patch #6652: improve asynch scheduler (including the synchronous case)
  https://savannah.nongnu.org/patch/?6652
modified:
  duplicity/asyncscheduler.py
  duplicity/dup_threading.py
------------------------------------------------------------
revno: 319
committer: loafman
timestamp: Wed 2008-11-12 13:23:04 +0000
message:
  patch #6662: improve s3 backend error reporting
  https://savannah.nongnu.org/patch/?6662
added:
  duplicity/util.py
modified:
  duplicity/backends/botobackend.py
------------------------------------------------------------
revno: 318
committer: loafman
timestamp: Wed 2008-11-12 13:13:04 +0000
message:
  patch #6670: Machine Readable Output
  https://savannah.nongnu.org/patch/?6670
added:
  LOG-README
  testing/logtest.py
modified:
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 317
committer: loafman
timestamp: Wed 2008-11-12 12:42:49 +0000
message:
  bug #24775: Digest Auth for WebDAV backend
  https://savannah.nongnu.org/bugs/?24775
modified:
  duplicity/backends/webdavbackend.py
------------------------------------------------------------
revno: 316
committer: loafman
timestamp: Wed 2008-11-12 12:39:00 +0000
message:
  bug #24731: Documentation error: "if... if" in remove-older-than paragraph
  https://savannah.nongnu.org/bugs/?24731
modified:
  duplicity.1
------------------------------------------------------------
revno: 315
committer: loafman
timestamp: Sun 2008-09-21 14:21:37 +0000
message:
  Changes for 0.5.02
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 314
committer: loafman
timestamp: Sun 2008-09-21 14:18:57 +0000
message:
  patch #6297: Add IMAP/s/gmail support
  https://savannah.nongnu.org/patch/index.php?6297
modified:
  dist/makedist
  duplicity.1
------------------------------------------------------------
revno: 313
committer: loafman
timestamp: Tue 2008-09-16 15:11:01 +0000
message:
  patch #6297: Add IMAP/s/gmail support
  https://savannah.nongnu.org/patch/index.php?6297
added:
  duplicity/backends/gmailimapbackend.py
modified:
  duplicity/backend.py
  duplicity/backends/__init__.py
  duplicity/commandline.py
  duplicity/urlparse_2_5.py
------------------------------------------------------------
revno: 312
committer: loafman
timestamp: Tue 2008-09-16 15:05:50 +0000
message:
  Change to one statement per line.
modified:
  duplicity/dup_temp.py
------------------------------------------------------------
revno: 311
committer: loafman
timestamp: Mon 2008-09-15 22:42:06 +0000
message:
  Change use of logger so that gpg logs are always collected.
  The log is always printed in the case of gpg IO errors.
  Verbosity level 5 or greater will also print the logs the
  same as previous versions.
modified:
  duplicity/gpg.py
------------------------------------------------------------
revno: 310
committer: loafman
timestamp: Mon 2008-09-15 22:37:49 +0000
message:
  Make one statement per line.  No other changes.
modified:
  duplicity/diffdir.py
------------------------------------------------------------
revno: 309
committer: loafman
timestamp: Mon 2008-09-15 22:32:25 +0000
message:
  - add -h option for help
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 308
committer: loafman
timestamp: Mon 2008-09-15 22:28:51 +0000
message:
  bug #24274: asyncscheduler.py missing sys import
  https://savannah.nongnu.org/bugs/index.php?24274
modified:
  duplicity/asyncscheduler.py
------------------------------------------------------------
revno: 307
committer: loafman
timestamp: Sun 2008-09-14 18:18:12 +0000
message:
  bug #24260: backend.py missing re import
  https://savannah.nongnu.org/bugs/index.php?24260
modified:
  duplicity/backend.py
------------------------------------------------------------
revno: 306
committer: loafman
timestamp: Thu 2008-09-11 13:26:04 +0000
message:
  Changes for 0.5.01
modified:
  CHANGELOG
------------------------------------------------------------
revno: 305
committer: loafman
timestamp: Tue 2008-09-09 19:59:33 +0000
message:
  Ignore test log file.
modified:
  testing/.cvsignore
------------------------------------------------------------
revno: 304
committer: loafman
timestamp: Tue 2008-09-09 19:57:46 +0000
message:
  Untabify all files.  To compare against previous
  versions use 'cvs diff -w' or 'diff -w'.
modified:
  CHANGELOG
  README
  dist/makedist
  dist/makerpm
  dist/makeweb
  dist/setup.py
  duplicity-bin
  duplicity/_librsyncmodule.c
  duplicity/backend.py
  duplicity/backends/sshbackend.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/compilec.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_time.py
  duplicity/file_naming.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/static.py
  duplicity/statistics.py
  duplicity/tarfile.py
  rdiffdir
  testing/backendtest.py
  testing/collectionstest.py
  testing/config.py.tmpl
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/manifesttest.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/selectiontest.py
  testing/statictest.py
  testing/statisticstest.py
  testing/tempdirtest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 303
committer: loafman
timestamp: Mon 2008-09-08 17:25:26 +0000
message:
  Create target dir (collection) if needed.
modified:
  duplicity/backends/webdavbackend.py
------------------------------------------------------------
revno: 302
committer: loafman
timestamp: Mon 2008-09-08 17:25:00 +0000
message:
  Ignore testfiles dir.
modified:
  testing/.cvsignore
------------------------------------------------------------
revno: 301
committer: loafman
timestamp: Mon 2008-09-08 17:23:42 +0000
message:
  Add tests for webdav and webdavs.
modified:
  testing/backendtest.py
  testing/config.py.tmpl
------------------------------------------------------------
revno: 300
committer: loafman
timestamp: Mon 2008-09-08 12:37:40 +0000
message:
  bug #24223: WebDAV backend broken in 0.5.00
  https://savannah.nongnu.org/bugs/index.php?24223
modified:
  duplicity/backends/webdavbackend.py
------------------------------------------------------------
revno: 299
committer: loafman
timestamp: Sat 2008-09-06 15:41:49 +0000
message:
  Changes for 0.5.00
modified:
  dist/makedist
  dist/setup.py
------------------------------------------------------------
revno: 298
committer: loafman
timestamp: Sat 2008-09-06 13:00:29 +0000
message:
  Changes for 0.5.00
modified:
  CHANGELOG
------------------------------------------------------------
revno: 297
committer: loafman
timestamp: Thu 2008-09-04 11:57:53 +0000
message:
  temp2.tar was a test-created file that had to be present
  at the beginning of test_tarfile.py.  Removed the need for
  it to be present and removed the file from CVS.
removed:
  testing/temp2.tar
modified:
  testing/run-all-tests.sh
  testing/test_tarfile.py
------------------------------------------------------------
revno: 296
committer: loafman
timestamp: Wed 2008-09-03 21:45:24 +0000
message:
  Changes to get unit tests working again:
    - resolve circular imports during unit tests
    - resolve exception error import - now in errors.py
modified:
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/hsibackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/rsyncbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
  duplicity/gpg.py
  duplicity/patchdir.py
  duplicity/path.py
  testing/backendtest.py
  testing/roottest.py
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 295
committer: loafman
timestamp: Wed 2008-09-03 12:00:08 +0000
message:
  patch #6623: slightly augment tempdir cleanup logging
  https://savannah.nongnu.org/patch/index.php?6623
modified:
  duplicity/tempdir.py
------------------------------------------------------------
revno: 294
committer: loafman
timestamp: Sun 2008-08-03 18:07:59 +0000
message:
  No longer needed, see backends dir.
removed:
  duplicity/backends.py
------------------------------------------------------------
revno: 293
committer: loafman
timestamp: Sun 2008-08-03 18:06:15 +0000
message:
  no comment
added:
  duplicity/backends/.cvsignore
------------------------------------------------------------
revno: 292
committer: loafman
timestamp: Sun 2008-08-03 18:05:45 +0000
message:
  bug #23988: scp destination fails if no username is specified
  https://savannah.nongnu.org/bugs/index.php?23988
modified:
  CHANGELOG
  duplicity/backends.py
  duplicity/backends/sshbackend.py
------------------------------------------------------------
revno: 291
committer: loafman
timestamp: Sun 2008-08-03 13:29:13 +0000
message:
  bug #23985: --no-encryption option does not work in 0.4.12
  https://savannah.nongnu.org/bugs/index.php?23985
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 290
committer: loafman
timestamp: Sat 2008-08-02 14:15:57 +0000
message:
  patch #6596: re-organize backend module structure
  https://savannah.nongnu.org/patch/index.php?6596
added:
  duplicity/backend.py
  duplicity/backends/
  duplicity/backends/__init__.py
  duplicity/backends/botobackend.py
  duplicity/backends/ftpbackend.py
  duplicity/backends/hsibackend.py
  duplicity/backends/localbackend.py
  duplicity/backends/rsyncbackend.py
  duplicity/backends/sshbackend.py
  duplicity/backends/webdavbackend.py
modified:
  CHANGELOG
  duplicity-bin
  duplicity/commandline.py
  duplicity/dup_threading.py
  duplicity/errors.py
  duplicity/lazy.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/finaltest.py
  testing/temp2.tar
------------------------------------------------------------
revno: 289
committer: loafman
timestamp: Fri 2008-08-01 18:15:50 +0000
message:
  patch #6353: Concurrency for volume encryption and upload.
  https://savannah.nongnu.org/patch/index.php?6353
added:
  duplicity/asyncscheduler.py
  duplicity/dup_threading.py
  duplicity/errors.py
modified:
  duplicity-bin
  duplicity.1
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 288
committer: loafman
timestamp: Fri 2008-08-01 18:02:52 +0000
message:
  patch #6589: S3 european bucket support
  https://savannah.nongnu.org/patch/index.php?6589
modified:
  duplicity.1
  duplicity/backends.py
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 287
committer: loafman
timestamp: Tue 2008-07-22 15:18:57 +0000
message:
  Changes for 0.4.12.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 286
committer: loafman
timestamp: Tue 2008-07-22 15:05:14 +0000
message:
  bug #23362: Documentation for --version, --time-separator <char>
  https://savannah.nongnu.org/bugs/index.php?23362
modified:
  duplicity.1
  duplicity/commandline.py
------------------------------------------------------------
revno: 285
committer: loafman
timestamp: Tue 2008-07-22 12:25:48 +0000
message:
  Cosmetic only.
modified:
  duplicity/file_naming.py
------------------------------------------------------------
revno: 284
committer: loafman
timestamp: Tue 2008-07-22 12:24:46 +0000
message:
  bug #23540: doc bug in man page (environment FTP_PASSWORD)
  https://savannah.nongnu.org/bugs/?23540
modified:
  duplicity.1
------------------------------------------------------------
revno: 283
committer: loafman
timestamp: Mon 2008-06-23 14:06:20 +0000
message:
  Dan Muresan created a patch that tries to minimize the number of password
  prompts.  To do so, it sometimes requests a password once without
  confirmation; if later it turns out that a full backup is needed, the
  user is prompted for confirmation.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 282
committer: loafman
timestamp: Fri 2008-05-16 22:07:22 +0000
message:
  bug #23066: ssh uris with given portnumbers are not handled correctly
  https://savannah.nongnu.org/bugs/index.php?23066
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 281
committer: loafman
timestamp: Thu 2008-05-15 19:00:32 +0000
message:
  Fix sort() for Python 2.3
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 280
committer: loafman
timestamp: Wed 2008-05-07 11:53:23 +0000
message:
  Change back to requiring Python 2.3.
modified:
  dist/setup.py
------------------------------------------------------------
revno: 279
committer: loafman
timestamp: Mon 2008-05-05 17:19:05 +0000
message:
  Change requirements back to Python 2.3.
modified:
  README
------------------------------------------------------------
revno: 278
committer: loafman
timestamp: Mon 2008-05-05 15:38:45 +0000
message:
  Changes for 0.4.11
modified:
  CHANGELOG
  testing/run-all-tests.sh
  testing/temp2.tar
------------------------------------------------------------
revno: 277
committer: loafman
timestamp: Mon 2008-05-05 14:00:26 +0000
message:
  Modified to run on Python 2.3.
modified:
  duplicity/backends.py
  duplicity/urlparse_2_5.py
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 276
committer: loafman
timestamp: Fri 2008-04-04 14:48:33 +0000
message:
  bug #22826: regressions caused by boto 1.1c
  https://savannah.nongnu.org/bugs/?22826
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 275
committer: loafman
timestamp: Tue 2008-04-01 14:44:27 +0000
message:
  Reinstate patch #6340 with a detailed explanation.
  http://savannah.nongnu.org/patch/index.php?6340
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 274
committer: loafman
timestamp: Wed 2008-03-26 21:50:58 +0000
message:
  Changes for 0.4.10.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 273
committer: loafman
timestamp: Wed 2008-03-26 21:48:47 +0000
message:
  Remove --sign for now.
modified:
  dist/makerpm
------------------------------------------------------------
revno: 272
committer: loafman
timestamp: Wed 2008-03-26 13:12:51 +0000
message:
  bug #22728: FTP backend fails on empty directory
  https://savannah.nongnu.org/bugs/?22728
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 271
committer: loafman
timestamp: Tue 2008-03-25 20:15:02 +0000
message:
  Fix log.debug to log.Debug
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 270
committer: loafman
timestamp: Tue 2008-03-25 14:25:00 +0000
message:
  patch #6453: handle absolute urls in webdav backend
  https://savannah.nongnu.org/patch/index.php?6453
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 269
committer: loafman
timestamp: Tue 2008-03-25 14:24:25 +0000
message:
  patch #6449: add additional debug level logging
  https://savannah.nongnu.org/patch/index.php?6449
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 268
committer: loafman
timestamp: Wed 2008-02-06 17:14:07 +0000
message:
  patch #6403: Restore by overwriting files/directories by using --force option
  https://savannah.nongnu.org/patch/?6403
modified:
  duplicity/commandline.py
  duplicity/patchdir.py
  duplicity/path.py
------------------------------------------------------------
revno: 267
committer: loafman
timestamp: Wed 2008-02-06 15:45:44 +0000
message:
  Password should be None, not empty string.
modified:
  testing/config.py.tmpl
------------------------------------------------------------
revno: 266
committer: loafman
timestamp: Wed 2008-02-06 15:43:44 +0000
message:
  Add config for S3 tests.
modified:
  testing/config.py.tmpl
------------------------------------------------------------
revno: 265
committer: loafman
timestamp: Wed 2008-02-06 15:23:16 +0000
message:
  Reformat to one statement per line.
modified:
  duplicity/file_naming.py
------------------------------------------------------------
revno: 264
committer: loafman
timestamp: Wed 2008-02-06 15:21:34 +0000
message:
  Fix problem where S3 prefix was appended with 'd'.  This caused
  a failure in the regression tests.  Unsure where it came from.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 263
committer: loafman
timestamp: Wed 2008-02-06 15:18:36 +0000
message:
  patch #6389: Possible Fix for pagefile.sys on Win32 systems
  https://savannah.nongnu.org/patch/?6389
modified:
  duplicity/selection.py
------------------------------------------------------------
revno: 262
committer: loafman
timestamp: Wed 2008-02-06 15:17:18 +0000
message:
  patch #6380: add additional named logging levels
  https://savannah.nongnu.org/patch/?6380
modified:
  duplicity/log.py
------------------------------------------------------------
revno: 261
committer: loafman
timestamp: Wed 2008-02-06 15:14:39 +0000
message:
  patch #6374: Duplicity --tempdir patch documentation.
  https://savannah.nongnu.org/patch/?6374
modified:
  duplicity.1
------------------------------------------------------------
revno: 260
committer: loafman
timestamp: Wed 2008-02-06 15:13:42 +0000
message:
  patch #6375: Duplicity reports the epoch for a nonexistant last full backup date
  https://savannah.nongnu.org/patch/?6375
modified:
  duplicity-bin
------------------------------------------------------------
revno: 259
committer: loafman
timestamp: Wed 2008-02-06 15:12:35 +0000
message:
  - remove sleep() from dup_time.py - not used.
  - make one statement per line format change.
modified:
  duplicity/dup_time.py
------------------------------------------------------------
revno: 258
committer: loafman
timestamp: Wed 2008-02-06 15:09:27 +0000
message:
  Remove testSleeping since sleep() removed from dup_time.py.
modified:
  testing/dup_timetest.py
------------------------------------------------------------
revno: 257
committer: loafman
timestamp: Wed 2008-02-06 15:08:35 +0000
message:
  Add S3 backend test.
modified:
  testing/backendtest.py
------------------------------------------------------------
revno: 256
committer: loafman
timestamp: Sun 2008-02-03 20:44:33 +0000
message:
  do not store object
removed:
  testing/roottest.pyc
------------------------------------------------------------
revno: 255
committer: loafman
timestamp: Tue 2008-01-08 13:38:39 +0000
message:
  Add requirements for source package install.
modified:
  README
------------------------------------------------------------
revno: 254
committer: loafman
timestamp: Fri 2008-01-04 18:32:54 +0000
message:
  Changes for 0.4.9.
modified:
  CHANGELOG
  testing/temp2.tar
------------------------------------------------------------
revno: 253
committer: loafman
timestamp: Fri 2008-01-04 18:10:03 +0000
message:
  Add more info on URL formats.
modified:
  duplicity.1
------------------------------------------------------------
revno: 252
committer: loafman
timestamp: Mon 2007-12-31 11:49:52 +0000
message:
  Updated URL Formats in the Help Screen.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 251
committer: loafman
timestamp: Mon 2007-12-31 11:49:03 +0000
message:
  Added section URL FORMAT in the duplicity man page.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 250
committer: loafman
timestamp: Sun 2007-12-30 15:42:39 +0000
message:
  Make sure to strip extraneous single colon when dealing
  with non-module URLs.  We provide the colon as needed.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 249
committer: loafman
timestamp: Sun 2007-12-30 12:30:18 +0000
message:
  bug #21909: Problematic typo in compare_verbose() method
  https://savannah.nongnu.org/bugs/index.php?21909
modified:
  duplicity/path.py
------------------------------------------------------------
revno: 248
committer: loafman
timestamp: Sat 2007-12-29 12:34:27 +0000
message:
  patch #6357: Explicit restore action is missing from the command list,
  https://savannah.nongnu.org/patch/?6357
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 247
committer: loafman
timestamp: Sat 2007-12-29 12:30:30 +0000
message:
  patch #6356: Command line option for the temporary directory root.
  https://savannah.nongnu.org/patch/?6356
modified:
  duplicity/commandline.py
  duplicity/globals.py
  duplicity/tempdir.py
------------------------------------------------------------
revno: 246
committer: loafman
timestamp: Thu 2007-12-27 01:21:00 +0000
message:
  Added regression tests for absolute, relative, and
  module pathing in the rsync scheme.
modified:
  testing/backendtest.py
  testing/config.py.tmpl
------------------------------------------------------------
revno: 245
committer: loafman
timestamp: Thu 2007-12-27 01:18:19 +0000
message:
  Fixed rsync URL description text in --help.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 244
committer: loafman
timestamp: Thu 2007-12-27 01:16:59 +0000
message:
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
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 243
committer: loafman
timestamp: Thu 2007-12-27 01:14:59 +0000
message:
  Fixed so that remove-older-than and remove-all-but-n-full
  will not request a GPG passphrase.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 242
committer: loafman
timestamp: Wed 2007-12-26 11:40:38 +0000
message:
  Fixed regression caused by changeover to new urlparse.py.
  bug #21475: FTP Usernames that contain '@' are not recognized
  https://savannah.nongnu.org/bugs/index.php?21475
modified:
  duplicity/urlparse_2_5.py
------------------------------------------------------------
revno: 241
committer: loafman
timestamp: Sat 2007-12-15 19:04:38 +0000
message:
  Changes for 0.4.8.
modified:
  CHANGELOG
  testing/run-all-tests.sh
  testing/temp2.tar
------------------------------------------------------------
revno: 240
committer: loafman
timestamp: Sat 2007-12-15 12:59:33 +0000
message:
  Format to one statement per line.
modified:
  duplicity/gpg.py
------------------------------------------------------------
revno: 239
committer: loafman
timestamp: Sat 2007-12-15 12:58:51 +0000
message:
  Allow pexpect to force the close of the child on sftp
  calls.  We already do that with scp calls.  This cleans
  up that exception.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 238
committer: loafman
timestamp: Fri 2007-12-14 00:33:22 +0000
message:
  patch #6344: S3 bad bad key key handling
  http://savannah.nongnu.org/patch/?6344
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 237
committer: loafman
timestamp: Thu 2007-12-13 18:34:38 +0000
message:
  Replace set_password/phrase with set_environ and
  clarify meaning in config.py.
modified:
  testing/backendtest.py
  testing/config.py.tmpl
  testing/finaltest.py
  testing/roottest.pyc
------------------------------------------------------------
revno: 236
committer: loafman
timestamp: Wed 2007-12-12 18:57:50 +0000
message:
  Complete description of install using --prefix=.
modified:
  README
------------------------------------------------------------
revno: 235
committer: loafman
timestamp: Wed 2007-12-12 18:44:59 +0000
message:
  Fix version of boto needed plus formatting.
modified:
  README
------------------------------------------------------------
revno: 234
committer: loafman
timestamp: Wed 2007-12-12 18:42:32 +0000
message:
  patch #6340: S3 short filename regression
  https://savannah.nongnu.org/patch/?6340
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 233
committer: loafman
timestamp: Wed 2007-12-12 17:14:03 +0000
message:
  Make sure config.py not checked in.
added:
  testing/.cvsignore
------------------------------------------------------------
revno: 232
committer: loafman
timestamp: Wed 2007-12-12 17:06:18 +0000
message:
  Initial release.
added:
  testing/config.py.tmpl
------------------------------------------------------------
revno: 231
committer: loafman
timestamp: Wed 2007-12-12 17:03:01 +0000
message:
  This test requires a file that no longer exists.
  Plus, it is unclear what this test is supposed
  to accomplish.  Tar is tested by the other tests.
removed:
  testing/memcheck.py
------------------------------------------------------------
revno: 230
committer: loafman
timestamp: Wed 2007-12-12 17:00:29 +0000
message:
  First pass at getting tests up to date:
    -- isolate config in 'config.py' (see config.py.tmpl)
    -- silence noisy tests as much as possible
    -- fix code on both sides as needed
modified:
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/manifesttest.py
  testing/memcheck.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/run-all-tests.sh
  testing/selectiontest.py
  testing/statictest.py
  testing/statisticstest.py
  testing/temp2.tar
  testing/tempdirtest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 229
committer: loafman
timestamp: Sun 2007-12-09 21:01:26 +0000
message:
  Initial release.
added:
  testing/run-all-tests.sh
------------------------------------------------------------
revno: 228
committer: loafman
timestamp: Sun 2007-12-09 21:00:36 +0000
message:
  Remove 2nd call to dup_time.settimestr() since it overrides
  the time that may be set by --current-time (used for testing).
modified:
  duplicity-bin
------------------------------------------------------------
revno: 227
committer: loafman
timestamp: Sun 2007-12-09 20:55:35 +0000
message:
  Regen dup_time.curtimestr if time-separator changed.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 226
committer: loafman
timestamp: Sun 2007-12-09 20:54:21 +0000
message:
  Fixed previous patch that assumed the presence
  of the user and password in the rsync URL.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 225
committer: loafman
timestamp: Sun 2007-12-09 20:11:04 +0000
message:
  Bring tests up to date.
modified:
  testing/collectionstest.py
  testing/dup_timetest.py
  testing/finaltest.py
  testing/tempdirtest.py
------------------------------------------------------------
revno: 224
committer: loafman
timestamp: Sat 2007-12-08 04:27:41 +0000
message:
  bug #21751: rsync module urls do not work in 0.4.7
  https://savannah.nongnu.org/bugs/index.php?21751
  
  bug #21752: Boto backend needs version 0.9d or later
  https://savannah.nongnu.org/bugs/index.php?21752
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 223
committer: loafman
timestamp: Fri 2007-12-07 15:21:38 +0000
message:
  Changes for version 0.4.7.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 222
committer: loafman
timestamp: Fri 2007-12-07 15:19:29 +0000
message:
  Change to require Python 2.4 or later.
modified:
  dist/setup.py
------------------------------------------------------------
revno: 221
committer: loafman
timestamp: Fri 2007-12-07 15:18:34 +0000
message:
  Formatted list and added tempdir.py and urllib_2_5.py
  to the released files list.
modified:
  dist/makedist
------------------------------------------------------------
revno: 220
committer: loafman
timestamp: Thu 2007-12-06 15:09:41 +0000
message:
  Fix confusion over patches applied to different versions.
  Patch #6300 should now be applied completely.
  
  Added back munge_password() so entire commandline could
  be logged without the password showing.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 219
committer: loafman
timestamp: Thu 2007-12-06 12:55:13 +0000
message:
  Hole imapbackend till next release.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 218
committer: loafman
timestamp: Thu 2007-12-06 12:52:56 +0000
message:
  Hold till next release.
removed:
  duplicity/imapbackend.py
------------------------------------------------------------
revno: 217
committer: loafman
timestamp: Wed 2007-12-05 21:47:44 +0000
message:
  patch #6300: Standard library replacement for ParsedUrl class
  https://savannah.nongnu.org/patch/?6300
  
  I had to fix the ssh/scp scheme to remove the leading '/' in
  parsed_url.path, otherwise it tried to treat the path as absolute.
added:
  duplicity/urlparse_2_5.py
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 216
committer: loafman
timestamp: Sun 2007-12-02 23:27:12 +0000
message:
  Backed out the following patch until bugs fixed...
  patch #6300: Standard library replacement for ParsedUrl class
  https://savannah.nongnu.org/patch/?6300
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 215
committer: loafman
timestamp: Sun 2007-12-02 13:50:46 +0000
message:
  patch #6301: log sftp commands at verbosity 5
  https://savannah.nongnu.org/patch/?6301
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 214
committer: loafman
timestamp: Sun 2007-12-02 13:42:08 +0000
message:
  patch #6300: Standard library replacement for ParsedUrl class
  https://savannah.nongnu.org/patch/?6300
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 213
committer: loafman
timestamp: Sun 2007-12-02 00:06:00 +0000
message:
  patch #6299: re-design tempfile handling
  https://savannah.nongnu.org/patch/?6299
added:
  duplicity/tempdir.py
  testing/tempdirtest.py
modified:
  duplicity-bin
  duplicity/backends.py
  duplicity/dup_temp.py
------------------------------------------------------------
revno: 212
committer: loafman
timestamp: Sat 2007-12-01 21:43:26 +0000
message:
  Move import of imapbackend to the end of the
  module.  Circular dependency.  Needs fixing.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 211
committer: loafman
timestamp: Sat 2007-12-01 21:38:54 +0000
message:
  Undo regression of bug #21508 contained in
  patch #6298: URI unquoting patch for FTP backend
  https://savannah.nongnu.org/patch/?6298
  
  Some cosmetic cleanup.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 210
committer: loafman
timestamp: Sat 2007-12-01 21:29:10 +0000
message:
  patch #6298: URI unquoting patch for FTP backend
  https://savannah.nongnu.org/patch/?6298
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 209
committer: loafman
timestamp: Sat 2007-12-01 21:15:38 +0000
message:
  patch #6297: Add IMAP/s/gmail support
  https://savannah.nongnu.org/patch/?6297
  
  Added 2nd patch for above.
modified:
  duplicity/imapbackend.py
------------------------------------------------------------
revno: 208
committer: loafman
timestamp: Sat 2007-12-01 18:11:58 +0000
message:
  patch #6297: Add IMAP/s/gmail support
  https://savannah.nongnu.org/patch/?6297
added:
  duplicity/imapbackend.py
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 207
committer: loafman
timestamp: Sat 2007-12-01 17:44:32 +0000
message:
  patch #6292: Amazon S3 bucket creation deferral for Duplicity 0.4.6
  https://savannah.nongnu.org/patch/?6292
modified:
  duplicity/backends.py
  duplicity/commandline.py
------------------------------------------------------------
revno: 206
committer: loafman
timestamp: Sat 2007-12-01 01:08:47 +0000
message:
  bug #21686: NcFTPGet 3.2.0 tempfile incompatibility
  https://savannah.nongnu.org/bugs/index.php?21686
modified:
  duplicity/dup_temp.py
------------------------------------------------------------
revno: 205
committer: loafman
timestamp: Sat 2007-12-01 01:08:29 +0000
message:
  Applied patch from Eric Hanchrow to fix logging error in
  botoBackend, and fix delete() in rsyncBackend.
  
  bug #21686: NcFTPGet 3.2.0 tempfile incompatibility
  https://savannah.nongnu.org/bugs/index.php?21686
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 204
committer: loafman
timestamp: Thu 2007-11-29 20:49:17 +0000
message:
  bug #21673: remove-all-but-n-full wrong arg usage
  https://savannah.nongnu.org/bugs/index.php?21673
  
  patch #6293: [patch] left-over patching from
  remove-all-but-n-full patch
  https://savannah.nongnu.org/patch/?6293
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 203
committer: loafman
timestamp: Wed 2007-11-28 18:08:29 +0000
message:
  more Changes for 0.4.6.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 202
committer: loafman
timestamp: Wed 2007-11-28 18:06:33 +0000
message:
  Changes for 0.4.6.
modified:
  CHANGELOG
  README
  duplicity.1
------------------------------------------------------------
revno: 201
committer: loafman
timestamp: Wed 2007-11-28 14:41:40 +0000
message:
  Fixed coding problem where matched_sig_chain could be
  referenced before it was defined.
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 200
committer: loafman
timestamp: Wed 2007-11-28 14:16:35 +0000
message:
  https://savannah.nongnu.org/patch/index.php?6291
  patch #6291: Alternative WebDAV HTTPS patch
modified:
  duplicity/backends.py
  duplicity/commandline.py
------------------------------------------------------------
revno: 199
committer: loafman
timestamp: Wed 2007-11-28 14:05:05 +0000
message:
  https://savannah.nongnu.org/patch/index.php?6289
  patch #6289: Amazon S3 key prefix patch for Duplicity 0.4.5
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 198
committer: loafman
timestamp: Wed 2007-11-28 13:58:05 +0000
message:
  https://savannah.nongnu.org/patch/?6284
  patch #6285: security fix: eliminate use of mktemp()
modified:
  duplicity/backends.py
  duplicity/dup_temp.py
------------------------------------------------------------
revno: 197
committer: loafman
timestamp: Wed 2007-11-28 13:55:38 +0000
message:
  https://savannah.nongnu.org/bugs/index.php?21651
  bug #21651, add https support for webdav.
  
  https://savannah.nongnu.org/patch/?6284
  patch #6284: document TMPDIR and friends
modified:
  duplicity.1
------------------------------------------------------------
revno: 196
committer: loafman
timestamp: Wed 2007-11-28 01:54:31 +0000
message:
  https://savannah.nongnu.org/bugs/index.php?21657
  bug #21657: ncftpls fails to create dir in ver 0.4.5
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 195
committer: loafman
timestamp: Wed 2007-11-28 01:05:48 +0000
message:
  https://savannah.nongnu.org/bugs/index.php?21651
  bug #21651, add https support for webdav.
modified:
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 194
committer: loafman
timestamp: Wed 2007-11-28 01:04:43 +0000
message:
  Try, the second.  See comments in the bug tracker.
  https://savannah.nongnu.org/bugs/index.php?21646
  bug #21646: --archive-dir causes delete of remote full
  sigs and orphaned sig files
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 193
committer: loafman
timestamp: Wed 2007-11-28 00:47:47 +0000
message:
  https://savannah.nongnu.org/bugs/index.php?21651
  bug #21651, add https support for webdav
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 192
committer: loafman
timestamp: Mon 2007-11-26 15:47:35 +0000
message:
  Fix release date in 0.4.5.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 191
committer: loafman
timestamp: Mon 2007-11-26 15:24:34 +0000
message:
  Changes for 0.4.5.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 190
committer: loafman
timestamp: Mon 2007-11-26 15:23:46 +0000
message:
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
modified:
  duplicity-bin
  duplicity.1
  duplicity/backends.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/dup_temp.py
  duplicity/globals.py
  duplicity/path.py
------------------------------------------------------------
revno: 189
committer: loafman
timestamp: Fri 2007-11-23 19:35:50 +0000
message:
  Changes for version 0.4.4.
modified:
  CHANGELOG
  duplicity.1
------------------------------------------------------------
revno: 188
committer: loafman
timestamp: Fri 2007-11-23 19:31:10 +0000
message:
  Applied a patch from Gregory Hartman to correct handling of DST
  in time calculations.  This affects backups made the night of
  a DST time switch.
modified:
  CHANGELOG
  duplicity/dup_time.py
------------------------------------------------------------
revno: 187
committer: loafman
timestamp: Fri 2007-11-23 19:25:06 +0000
message:
  Cosmetic - Use True and False, not 1 and None.
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 186
committer: loafman
timestamp: Fri 2007-11-23 19:21:56 +0000
message:
  Fix version checking code in ftpBackend.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 185
committer: loafman
timestamp: Mon 2007-11-19 15:31:42 +0000
message:
  Changes to commandline processing to allow non-ambiguous short
  strings for commands, i.e. 'i', 'inc', 'incr' for 'incremental',
  'f' for 'full', etc..  A warning message is printed if the short
  command is not unique.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 184
committer: loafman
timestamp: Mon 2007-11-19 15:30:03 +0000
message:
  Changes to ftpBackend to use the login config file rather than
  putting the username and password on the command line.  This
  requires the use of NcFTP 3.1.9 or later.
  
  Thanks to a patch from Greg Hewgill the Amazon S3 backend now
  uses --num-retries to retry IO repeatedly if needed.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 183
committer: loafman
timestamp: Fri 2007-10-26 19:30:55 +0000
message:
  Changes for 0.4.4.RC4 try 2
modified:
  CHANGELOG
------------------------------------------------------------
revno: 182
committer: loafman
timestamp: Fri 2007-10-26 19:05:37 +0000
message:
  Changes for 0.4.4.RC4
modified:
  CHANGELOG
  duplicity.1
------------------------------------------------------------
revno: 181
committer: loafman
timestamp: Fri 2007-10-26 19:02:28 +0000
message:
  Replace with Version 3 GPL text.
modified:
  COPYING
------------------------------------------------------------
revno: 180
committer: loafman
timestamp: Fri 2007-10-26 19:01:40 +0000
message:
  Fixed issue in --time-separator where the current time string
  was being set prior to setting the separator, causing errors
  when trying to set the --time-separator for Windows systems.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 179
committer: loafman
timestamp: Fri 2007-10-26 18:59:01 +0000
message:
  There is a new command line syntax to separate actions and
  options.  Refer to the new man page for full details.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 178
committer: loafman
timestamp: Fri 2007-10-26 18:58:09 +0000
message:
  Correct calling sequence in calls to get_signature_chains().
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 177
committer: loafman
timestamp: Fri 2007-10-26 18:54:37 +0000
message:
  Fix so that ftpBackend.delete() does not print file list.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 176
committer: loafman
timestamp: Fri 2007-10-26 15:17:34 +0000
message:
  Fix so that file mtime is always compared in full seconds.
modified:
  duplicity/path.py
------------------------------------------------------------
revno: 175
committer: loafman
timestamp: Tue 2007-10-02 12:48:04 +0000
message:
  Changes for 0.4.4.RC3 -- Corrected.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 174
committer: loafman
timestamp: Tue 2007-10-02 12:06:19 +0000
message:
  Changes for 0.4.4.RC3.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 173
committer: loafman
timestamp: Sat 2007-09-29 15:10:45 +0000
message:
  Add 'patch' dir to ignore list.
modified:
  .cvsignore
------------------------------------------------------------
revno: 172
committer: loafman
timestamp: Sat 2007-09-29 14:24:12 +0000
message:
  Patch from Olivier Croquette to add :port option in FTP.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 171
committer: loafman
timestamp: Sat 2007-09-29 14:23:35 +0000
message:
  Patch from Olivier Croquette to add --full-if-older-than=<time>
  option to force a full backup at <time> rather than incremental.
modified:
  duplicity-bin
  duplicity.1
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 170
committer: loafman
timestamp: Fri 2007-09-28 13:45:31 +0000
message:
  Patch from Olivier Croquette to add :port option in FTP.
  
  Patch from Mitchell Garnaat to get all keys from S3, rather
  than just the first 1000.
  
  Fix to sshBackend to version check for python-pexpect 2.1.
  
  Fix one case in ftpBackend where host string was used instead of
  url_string.  This only affected the creation of the target dir on
  the remote system, if it did not exist, and only if the user or
  port needed to be specified.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 169
committer: loafman
timestamp: Wed 2007-09-26 18:12:03 +0000
message:
  Changes for 0.4.4.RC2.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 168
committer: loafman
timestamp: Wed 2007-09-26 18:11:08 +0000
message:
  Added --timeout <seconds> (default 30) to allow users to change
  duplicity's network timeout settings.
  
  Added --time-separator <char> to allow users to change the time
  separator from ':' to another character that will work on their
  system.  HINT: For Windows SMB shares, use --time-separator='_'.
  NOTE: '-' is not valid as it conflicts with date separator.
  
  Changed usage message to separate options and commands.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 167
committer: loafman
timestamp: Wed 2007-09-26 18:09:37 +0000
message:
  Add patch from Olivier Croquette to allow user@domain usernames,
  making ftp://user@domain@domain.com/path a valid URL.
  
  Added a bit of debug print to sshBackend for --verbosity=9.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 166
committer: loafman
timestamp: Wed 2007-09-26 18:07:41 +0000
message:
  Add patch from Alexander Zangerl to suppress the GPG passphrase
  prompt when a passphrase is not needed.
   - full and pubkey enc:  doesn't depend on old encrypted info
   - inc and pubkey enc and archive-dir: need manifest and sigs,
     which the archive dir contains unencrypted
   - with encryption disabled
   - listing files:  needs manifest, but the archive dir has that
   - collection status:  only looks at a repository
modified:
  duplicity-bin
------------------------------------------------------------
revno: 165
committer: loafman
timestamp: Wed 2007-09-19 15:32:11 +0000
message:
  Changes for 0.4.4.RC1.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 164
committer: loafman
timestamp: Wed 2007-09-19 15:28:52 +0000
message:
  https://savannah.nongnu.org/patch/index.php?6205
  Add option --librsync-dir for when its not found.
modified:
  dist/setup.py
------------------------------------------------------------
revno: 163
committer: loafman
timestamp: Wed 2007-09-19 14:42:44 +0000
message:
  Bug #21123: duplicity 0.4.3 does not find any backup chains
  https://savannah.nongnu.org/bugs/?21123
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 162
committer: loafman
timestamp: Wed 2007-09-19 14:37:24 +0000
message:
  Make tempfiles with useful names.
modified:
  duplicity/dup_temp.py
------------------------------------------------------------
revno: 161
committer: loafman
timestamp: Wed 2007-09-19 14:36:06 +0000
message:
  Fixes manual page and usage msg for rsync url and --remove-older-than.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 160
committer: loafman
timestamp: Wed 2007-09-19 14:34:49 +0000
message:
  Fix for Debian bug #228388: old/aborted/offending sig files
  prohibit any further action.
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 159
committer: loafman
timestamp: Wed 2007-09-19 14:32:50 +0000
message:
  Fixes manual page and usage msg for rsync url and --remove-older-than.
modified:
  duplicity.1
------------------------------------------------------------
revno: 158
committer: loafman
timestamp: Wed 2007-09-19 14:26:04 +0000
message:
  Do not ask for passphrase when none is needed.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 157
committer: loafman
timestamp: Sun 2007-09-16 11:47:48 +0000
message:
  Final patch for Peter Schuller's fix to max read size.
  The first one was broken (revision previous to this).
modified:
  duplicity/diffdir.py
------------------------------------------------------------
revno: 156
committer: loafman
timestamp: Mon 2007-09-10 12:59:23 +0000
message:
  Add patch submitted by Peter Schuller which removes the
  default SSH options that ignored known hosts files and
  disabled strict host checking.  This patch also handles
  the authentication failures from these issues.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 155
committer: loafman
timestamp: Thu 2007-09-06 14:42:48 +0000
message:
  Fixed so that max read size is 64k, not the
  volume size which can be quite large.
modified:
  duplicity/diffdir.py
------------------------------------------------------------
revno: 154
committer: loafman
timestamp: Mon 2007-08-20 17:48:15 +0000
message:
  Fix release date.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 153
committer: loafman
timestamp: Mon 2007-08-20 15:17:21 +0000
message:
  Changes for 0.4.3 release.
modified:
  CHANGELOG
  README
  duplicity.1
------------------------------------------------------------
revno: 152
committer: loafman
timestamp: Mon 2007-08-20 14:59:20 +0000
message:
  Removed use of tempfile.TemporaryFile().  This fixes the
  restore problem on Windows that was due to Python bug
  1776696 reported on Sourceforge.
modified:
  duplicity/patchdir.py
------------------------------------------------------------
revno: 151
committer: loafman
timestamp: Mon 2007-08-20 14:56:09 +0000
message:
  Removed hardwired options to use bzip2 compression.
  
  Added gpg-options to allow users to add options to
  the gpg process.
modified:
  duplicity/gpg.py
------------------------------------------------------------
revno: 150
committer: loafman
timestamp: Mon 2007-08-20 14:53:59 +0000
message:
  Changed ssh-command to ssh-options to allow users
  to add options to the scp and sftp commmands.
  
  Added gpg-options to allow users to add options to
  the gpg process.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 149
committer: loafman
timestamp: Mon 2007-08-20 14:50:18 +0000
message:
  Move get_password() to Backend class to standardize.
  
  Fix problem with ftpBackend to create target directory if needed.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 148
committer: loafman
timestamp: Mon 2007-08-13 18:16:41 +0000
message:
  Upgrade to GPL version 3 license.
modified:
  COPYING
  duplicity-bin
  duplicity/_librsyncmodule.c
  duplicity/backends.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_time.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/static.py
  duplicity/statistics.py
  rdiffdir
------------------------------------------------------------
revno: 147
committer: loafman
timestamp: Mon 2007-08-13 16:14:28 +0000
message:
  Do not pass :port part of URL to scp backend.
  Its taken as the target file and errors out.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 146
committer: loafman
timestamp: Mon 2007-08-13 15:45:10 +0000
message:
  Change ssh_command option to be ssh_options.  This adds
  options to the scp and sftp commands that are used by
  the ssh backend.
modified:
  duplicity/backends.py
  duplicity/commandline.py
------------------------------------------------------------
revno: 145
committer: loafman
timestamp: Mon 2007-08-13 11:49:34 +0000
message:
  Fixed bug 20764 - unable to use port in ssh backend.
  https://savannah.nongnu.org/bugs/?20764
  
  Change ssh backend to send 'quit' instead of EOF when
  using sftp.  This allows it to run under cron as long
  as the password is supplied non-interactively.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 144
committer: loafman
timestamp: Thu 2007-08-09 22:37:16 +0000
message:
  Changes for 0.4.3.RC12
modified:
  dist/setup.py
------------------------------------------------------------
revno: 143
committer: loafman
timestamp: Thu 2007-08-09 22:18:33 +0000
message:
  Changes for 0.4.3.RC12
modified:
  CHANGELOG
------------------------------------------------------------
revno: 142
committer: loafman
timestamp: Thu 2007-08-09 14:44:07 +0000
message:
  Changed the file:, ftp:, and ssh: backends so that
  the target directory will be created at start.
  
  Changed the ftp: backend so that empty target dirs
  do not error out.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 141
committer: loafman
timestamp: Thu 2007-08-09 14:17:27 +0000
message:
  Clean up help list formatting.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 140
committer: loafman
timestamp: Thu 2007-08-09 13:10:37 +0000
message:
  Fix index out of range in Bug 20730, triggered when there
  is only one incremental and no previous in list.
  https://savannah.nongnu.org/bugs/?20730
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 139
committer: loafman
timestamp: Thu 2007-08-09 13:05:53 +0000
message:
  - Print warning if pexpect version is less than 2.1.
  - Fix author and maintainer settings.
modified:
  dist/setup.py
------------------------------------------------------------
revno: 138
committer: loafman
timestamp: Thu 2007-08-09 13:04:28 +0000
message:
  Fix environment var name for ssh backend.
modified:
  duplicity.1
------------------------------------------------------------
revno: 137
committer: loafman
timestamp: Sat 2007-07-21 10:38:37 +0000
message:
  Changes for 0.4.3.RC11.
modified:
  CHANGELOG
  duplicity.1
------------------------------------------------------------
revno: 136
committer: loafman
timestamp: Sat 2007-07-21 10:37:47 +0000
message:
  Add --ssh-askpass option.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 135
committer: loafman
timestamp: Sat 2007-07-21 10:36:23 +0000
message:
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
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 134
committer: loafman
timestamp: Sun 2007-07-15 11:27:19 +0000
message:
  patch #6094, Boto Backend Fixes for RC10
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 133
committer: loafman
timestamp: Sat 2007-07-14 16:27:37 +0000
message:
  Changes for 0.4.3.RC10
modified:
  CHANGELOG
------------------------------------------------------------
revno: 132
committer: loafman
timestamp: Sat 2007-07-14 16:02:49 +0000
message:
  Add support for:
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
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 131
committer: loafman
timestamp: Sat 2007-07-14 15:54:22 +0000
message:
  Add support for:
    --ftp-passive,
    --ftp-regular,
    --num-retries
modified:
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 130
committer: loafman
timestamp: Sat 2007-07-14 15:50:43 +0000
message:
  Add descriptions for:
    --ftp-passive,
    --ftp-regular,
    --num-retries
modified:
  duplicity.1
------------------------------------------------------------
revno: 129
committer: loafman
timestamp: Tue 2007-07-10 11:45:33 +0000
message:
  Replace missing comma in argument list.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 128
committer: loafman
timestamp: Mon 2007-07-09 20:25:49 +0000
message:
  Changes for 0.4.3.RC9.
  Drop ftplib.py.
modified:
  dist/makedist
------------------------------------------------------------
revno: 127
committer: loafman
timestamp: Mon 2007-07-09 20:18:34 +0000
message:
  No longer needed.
removed:
  duplicity/ftplib.py
------------------------------------------------------------
revno: 126
committer: loafman
timestamp: Mon 2007-07-09 20:13:28 +0000
message:
  Changes for 0.4.3.RC9.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 125
committer: loafman
timestamp: Mon 2007-07-09 20:11:45 +0000
message:
  Added a commandline option, '--num-retries=<int>', to set the number
  of retries.  The default is 5.
modified:
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 124
committer: loafman
timestamp: Mon 2007-07-09 20:09:35 +0000
message:
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
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 123
committer: loafman
timestamp: Fri 2007-06-29 20:09:26 +0000
message:
  Change to a max block size of 2048 bytes for
  rsync difference buffer.  This may slow things
  down for truly large files, but will give much
  smaller deltas on files with numerous small
  changes, such as database files.
modified:
  duplicity/diffdir.py
------------------------------------------------------------
revno: 122
committer: loafman
timestamp: Thu 2007-06-28 00:22:14 +0000
message:
  Initial release.
added:
  .cvsignore
  duplicity/.cvsignore
------------------------------------------------------------
revno: 121
committer: loafman
timestamp: Wed 2007-06-27 19:44:09 +0000
message:
  Changes for 0.4.3.RC8
modified:
  CHANGELOG
------------------------------------------------------------
revno: 120
committer: loafman
timestamp: Wed 2007-06-27 19:43:16 +0000
message:
  Bug 20039 - Andreas Schildbach: --and--
  Patch 6030 - Alexander Zangerl <az@debian.org>:
  Duplicity now uses bzip2 for compression.  This matches the way
  the Debian distribution handles it.  I'll think about adding an
  option to override later, if its needed.
modified:
  duplicity/gpg.py
------------------------------------------------------------
revno: 119
committer: loafman
timestamp: Wed 2007-06-27 19:42:18 +0000
message:
  Bug 20282 - Thomas Tuttle:
  An out of range index when checking past history in the backup
  sets caused a failure when trying to access later.
  
  Bug 20149 - dAniel hAhler:
  dAniel submitted a second patch for this for further cleanup.
  The new patch prefers the latest intact backup set.
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 118
committer: loafman
timestamp: Tue 2007-06-19 17:02:03 +0000
message:
  Changes for 0.4.3.RC7
modified:
  CHANGELOG
------------------------------------------------------------
revno: 117
committer: loafman
timestamp: Tue 2007-06-19 15:49:12 +0000
message:
  Patch 6029 - Alexander Zangerl <az@debian.org>:
  http://bugs.debian.org/370206
  archive-dir together with incremental backup results in crash. the
  patch is simple, the code in 0.4.2 did attempt to access strings as
  objects.
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 116
committer: loafman
timestamp: Tue 2007-06-19 15:15:29 +0000
message:
  Patch 6033 - Alexander Zangerl <az@debian.org>:
  let's add a --help terse usage message and don't just direct the user
  to the manual. this should come handy if somebody needs to restore
  stuff without having the manual available.
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 115
committer: loafman
timestamp: Tue 2007-06-19 14:47:20 +0000
message:
  Patch 6032 - Alexander Zangerl <az@debian.org>:
  a new feature patch: i've recently gotten annoyed with having gazillions of
  5mb files and therefore added a --volsize option to allow the user setting
  the chunk size. the patch is simple and contains a manpage update as well.
modified:
  duplicity-bin
  duplicity.1
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 114
committer: loafman
timestamp: Tue 2007-06-19 13:26:32 +0000
message:
  Add -u (unbuffered) to shebang line.
modified:
  duplicity-bin
------------------------------------------------------------
revno: 113
committer: loafman
timestamp: Tue 2007-06-19 13:25:26 +0000
message:
  Add stderr.flush() in FatalError().
modified:
  duplicity/log.py
------------------------------------------------------------
revno: 112
committer: loafman
timestamp: Tue 2007-06-19 13:24:25 +0000
message:
  Bug 20179 - dAniel hAhler: When errors cause login to fail in FTP,
  reset and try again.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 111
committer: loafman
timestamp: Wed 2007-06-13 13:13:39 +0000
message:
  Not needed.
removed:
  duplicity/selection.py.old
  duplicity/tarfile.py.old
------------------------------------------------------------
revno: 110
committer: loafman
timestamp: Wed 2007-06-13 13:09:47 +0000
message:
  Cosmetic change to force new log.  The log for revision 1.28
  is not correct.  It should read as follows:
  
  Patch 5993 - daacyy302@sneakemail.com: Make Amazon S3 backend
  incrementally more robust for recovery.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 109
committer: loafman
timestamp: Wed 2007-06-13 12:59:06 +0000
message:
  Changes for 0.4.3.RC6.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 108
committer: loafman
timestamp: Wed 2007-06-13 12:58:27 +0000
message:
  Patch 5998 - Kuang-che Wu: Cache uid and gid lookup to speed
  operations.
modified:
  duplicity/path.py
------------------------------------------------------------
revno: 107
committer: loafman
timestamp: Wed 2007-06-13 12:56:30 +0000
message:
  Bug 20419 - dAniel hAhler: When errors cause an incomplete backup set,
  flag the error with a message, rather than erroring out.  The user
  then knows to run --cleanup.
modified:
  duplicity/backends.py
  duplicity/collections.py
------------------------------------------------------------
revno: 106
committer: loafman
timestamp: Mon 2007-06-04 11:40:01 +0000
message:
  Changes for 0.4.3.RC5.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 105
committer: loafman
timestamp: Mon 2007-06-04 11:36:03 +0000
message:
  dAniel hAhler submitted a patch to change "Error initializing file
  foo" (log level 2), where foo was a socket, to "Skipping socket foo"
  (log level 7).  https://savannah.nongnu.org/patch/?5985
modified:
  duplicity/selection.py
------------------------------------------------------------
revno: 104
committer: loafman
timestamp: Mon 2007-06-04 11:35:22 +0000
message:
  Change logging to flush after every write, unbuffering stdout and
  stderr, thus producing logs that are coherent.
modified:
  duplicity/log.py
------------------------------------------------------------
revno: 103
committer: loafman
timestamp: Mon 2007-06-04 11:34:47 +0000
message:
  GnuPG fails when trying to access stdin on an empty passphrase.
  Changes allow empty passphrase on public-key encryption and now
  respond gracefully on empty passphrase for symmetric encryption.
modified:
  duplicity-bin
  duplicity/gpg.py
------------------------------------------------------------
revno: 102
committer: loafman
timestamp: Sat 2007-06-02 13:15:41 +0000
message:
  Changes for 0.4.3.RC4.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 101
committer: loafman
timestamp: Sat 2007-06-02 13:14:19 +0000
message:
  Move catch of NLST errors back to self.error_retry()
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 100
committer: loafman
timestamp: Sat 2007-06-02 12:51:46 +0000
message:
  More FTP fixes:
  - clean up error handling
  - change initial error delay to zero
  - move catch of NLST errors to self.list()
modified:
  CHANGELOG
  duplicity/backends.py
------------------------------------------------------------
revno: 99
committer: loafman
timestamp: Thu 2007-05-31 15:11:28 +0000
message:
  Changes to release 0.4.3.RC3.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 98
committer: loafman
timestamp: Wed 2007-05-30 17:50:54 +0000
message:
  - Fix so that FTP connection/login is closed and
  reopened when errors 221 or 421 are reported.
  
  - Fix grammer in error message.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 97
committer: loafman
timestamp: Wed 2007-05-30 11:14:22 +0000
message:
  Changes to release 0.4.3.RC2.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 96
committer: loafman
timestamp: Wed 2007-05-30 00:34:55 +0000
message:
  Remove GnuPGInterface.py
modified:
  dist/duplicity.spec.template
  dist/makedist
  dist/makerpm
  dist/setup.py
------------------------------------------------------------
revno: 95
committer: loafman
timestamp: Wed 2007-05-30 00:30:57 +0000
message:
  Apply patch for bug 19998, ValueError exception.
modified:
  duplicity/tarfile.py
------------------------------------------------------------
revno: 94
committer: loafman
timestamp: Sat 2007-05-26 16:31:14 +0000
message:
  Added change notices for FTP password and rsync backend.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 93
committer: loafman
timestamp: Sat 2007-05-26 16:16:15 +0000
message:
  Fix request password in ftpBackend if environ not set.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 92
committer: loafman
timestamp: Sat 2007-05-26 16:00:01 +0000
message:
  - allow connection after 226 in NLST (ProFTPD)
  - request password in ftpBackend if environ not set
  - rsyncBackend was using the full URL, now uses server:path
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 91
committer: loafman
timestamp: Sat 2007-05-26 15:52:35 +0000
message:
  Document changes for 0.4.3.
modified:
  CHANGELOG
------------------------------------------------------------
revno: 90
committer: loafman
timestamp: Fri 2007-05-25 19:03:30 +0000
message:
  Do not set FTP to active mode at start of session.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 89
committer: loafman
timestamp: Thu 2007-05-24 22:37:53 +0000
message:
  1) WebDAV needs a Depth: 1 header otherwise infinite depth
  is assumed and may be restricted due to load.
  
  2) Used the allprop XML command to get back properties that
  included the filenames.  Refer to RFC 2518.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 88
committer: loafman
timestamp: Wed 2007-05-23 20:24:11 +0000
message:
  Fixes bug:
    https://savannah.nongnu.org/bugs/?19940
added:
  duplicity/ftplib.py
------------------------------------------------------------
revno: 87
committer: loafman
timestamp: Wed 2007-05-23 20:01:30 +0000
message:
  Applied patches:
    https://savannah.nongnu.org/patch/?5680
    https://savannah.nongnu.org/patch/?5681
removed:
  duplicity/GnuPGInterface.py
modified:
  README
  duplicity/gpg.py
------------------------------------------------------------
revno: 86
committer: loafman
timestamp: Wed 2007-05-23 19:58:00 +0000
message:
  Added patches:
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
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 85
committer: jinty
timestamp: Tue 2006-05-09 07:24:36 +0000
message:
  BitBucketBackend:
      * if something goes wrong and we need to re-connect, dump the exception
        on stderr. Be very noisy so that whatever is wrong will be fixed.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 84
committer: bescoto
timestamp: Thu 2006-05-04 01:13:11 +0000
message:
  Typo fix for error message
modified:
  duplicity/collections.py
------------------------------------------------------------
revno: 83
committer: jinty
timestamp: Tue 2006-05-02 21:44:15 +0000
message:
  Fix a bug in the bitbucket backend:
  We need to get a new bits from the new bucket if we re-connect.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 82
committer: jinty
timestamp: Mon 2006-05-01 18:06:58 +0000
message:
  Changes to the bitbucket backend:
  * Update to work with bitbucket 0.3b.
  * Add some docimentation.
  * Implement a suggestion by Ben Escoto to move the access and secret keys to
    environment variables.
  * Implement a very simplistic error correction mechanisim that will re-connect
    on an operation failure and re-try the operation. Note that this is just a
    band-aid for issues that should be resolved at lower levels.
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 81
committer: bescoto
timestamp: Mon 2006-05-01 01:41:58 +0000
message:
  Removed time_separator entry from changelog when I backed out patch
modified:
  CHANGELOG
------------------------------------------------------------
revno: 80
committer: bescoto
timestamp: Mon 2006-05-01 01:40:34 +0000
message:
  Went back to old time_separator, because I realized new way wouldn't
  handle some cases, and could break backwards compatibility
modified:
  duplicity/globals.py
------------------------------------------------------------
revno: 79
committer: bescoto
timestamp: Mon 2006-05-01 01:31:16 +0000
message:
  Andre Beckedorf's patches for ftp and rsync backends, and time_separator
modified:
  CHANGELOG
  duplicity/backends.py
  duplicity/globals.py
------------------------------------------------------------
revno: 78
committer: bescoto
timestamp: Sun 2006-04-30 23:43:01 +0000
message:
  Checked in Brian Sutherland's Amazon S3 code
modified:
  CHANGELOG
  duplicity.1
  duplicity/backends.py
------------------------------------------------------------
revno: 77
committer: bescoto
timestamp: Sun 2006-04-30 23:02:17 +0000
message:
  Added --sftp-command to changelog
modified:
  CHANGELOG
------------------------------------------------------------
revno: 76
committer: bescoto
timestamp: Sun 2006-04-30 22:56:39 +0000
message:
  Added --sftp-command option and man page documentation
modified:
  duplicity.1
  duplicity/commandline.py
------------------------------------------------------------
revno: 75
committer: bescoto
timestamp: Sun 2006-04-30 22:21:44 +0000
message:
  Fixed Jiri's name.  Sorry about that :-)
modified:
  CHANGELOG
------------------------------------------------------------
revno: 74
committer: bescoto
timestamp: Fri 2006-02-03 03:43:36 +0000
message:
  final changes for version 0.4.2
modified:
  CHANGELOG
------------------------------------------------------------
revno: 73
committer: bescoto
timestamp: Fri 2006-02-03 03:40:00 +0000
message:
  Fixes to the scp backend
modified:
  CHANGELOG
  duplicity/backends.py
  duplicity/dup_temp.py
------------------------------------------------------------
revno: 72
committer: bescoto
timestamp: Thu 2006-02-02 03:49:33 +0000
message:
  Stop --remove-older-than from deleting current chain
modified:
  CHANGELOG
  duplicity-bin
  duplicity/collections.py
  testing/finaltest.py
------------------------------------------------------------
revno: 71
committer: bescoto
timestamp: Wed 2006-02-01 04:57:48 +0000
message:
  Catch ftp error 450 when listing directory
modified:
  CHANGELOG
  duplicity/backends.py
------------------------------------------------------------
revno: 70
committer: bescoto
timestamp: Wed 2006-02-01 04:42:16 +0000
message:
  cleaned up and documented --collection-status
modified:
  CHANGELOG
  duplicity.1
  duplicity/collections.py
------------------------------------------------------------
revno: 69
committer: bescoto
timestamp: Thu 2006-01-12 16:29:53 +0000
message:
  asdf's tarfile large uid/gid patch
modified:
  CHANGELOG
  duplicity/tarfile.py
------------------------------------------------------------
revno: 68
committer: bescoto
timestamp: Thu 2006-01-12 16:23:39 +0000
message:
  Jiri Tyr's scp/sftp patch
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 67
committer: bescoto
timestamp: Mon 2006-01-02 02:36:12 +0000
message:
  Eric Hanchrow's remove signature patch
modified:
  CHANGELOG
  duplicity-bin
------------------------------------------------------------
revno: 66
committer: bescoto
timestamp: Sun 2006-01-01 02:17:09 +0000
message:
  A few minor updates so test pass on my system again
modified:
  duplicity/gpg.py
  testing/gpgtest.py
  testing/rdiffdirtest.py
  testing/statisticstest.py
------------------------------------------------------------
revno: 65
committer: bescoto
timestamp: Fri 2003-11-21 08:44:14 +0000
message:
  MDR patch allows signing with different key
modified:
  duplicity-bin
  duplicity/_librsyncmodule.c
  duplicity/collections.py
  duplicity/dup_temp.py
------------------------------------------------------------
revno: 64
committer: bescoto
timestamp: Thu 2003-08-14 06:18:22 +0000
message:
  Added note about passphrase confirmation
modified:
  CHANGELOG
------------------------------------------------------------
revno: 63
committer: bescoto
timestamp: Thu 2003-08-14 06:16:33 +0000
message:
  When collecting password from user, make type it twice to confirm
modified:
  duplicity-bin
------------------------------------------------------------
revno: 62
committer: bescoto
timestamp: Sun 2003-08-10 02:15:00 +0000
message:
  Final changes for 0.4.1
modified:
  CHANGELOG
  dist/makeweb
------------------------------------------------------------
revno: 61
committer: bescoto
timestamp: Sun 2003-08-10 02:08:22 +0000
message:
  Updating rpm for Fedora
added:
  dist/duplicity.spec.template
modified:
  dist/makedist
  dist/makerpm
------------------------------------------------------------
revno: 60
committer: bescoto
timestamp: Sun 2003-08-10 02:07:35 +0000
message:
  Trying to remove...
removed:
  dist/duplicity.spec
------------------------------------------------------------
revno: 59
committer: bescoto
timestamp: Sun 2003-08-10 01:05:17 +0000
message:
  Small changes for 0.4.1 and python 2.3
modified:
  dist/duplicity.spec
  duplicity/path.py
  duplicity/tarfile.py
------------------------------------------------------------
revno: 58
committer: bescoto
timestamp: Sat 2003-08-09 20:31:08 +0000
message:
  variable block size, librsync 0.9.6
modified:
  CHANGELOG
------------------------------------------------------------
revno: 57
committer: bescoto
timestamp: Sat 2003-08-09 20:09:13 +0000
message:
  Remove large file note now that block size chosen based on file size
modified:
  TODO
------------------------------------------------------------
revno: 56
committer: bescoto
timestamp: Sat 2003-08-09 20:08:40 +0000
message:
  Ported some code from rdiff-backup:  choose sig block based on file
  length, and work with librsync 0.9.6.
modified:
  duplicity/_librsyncmodule.c
  duplicity/compilec.py
  duplicity/diffdir.py
  duplicity/librsync.py
------------------------------------------------------------
revno: 55
committer: bescoto
timestamp: Sat 2003-08-09 19:10:54 +0000
message:
  Mention problem with /proc
modified:
  TODO
  duplicity.1
------------------------------------------------------------
revno: 54
committer: bescoto
timestamp: Fri 2003-08-08 19:13:36 +0000
message:
  Cache pwd and group files
modified:
  duplicity/tarfile.py
  testing/temp2.tar
  testing/test_tarfile.py
------------------------------------------------------------
revno: 53
committer: bescoto
timestamp: Fri 2003-08-08 05:45:27 +0000
message:
  Added --version switch, small change to man page
modified:
  duplicity.1
  duplicity/commandline.py
------------------------------------------------------------
revno: 52
committer: bescoto
timestamp: Thu 2003-08-07 21:34:36 +0000
message:
  Sebastian Wilhelmi's update for rsync backend
modified:
  CHANGELOG
  TODO
  duplicity.1
  duplicity/backends.py
  testing/backendtest.py
  testing/finaltest.py
------------------------------------------------------------
revno: 51
committer: bescoto
timestamp: Thu 2003-08-07 20:37:58 +0000
message:
  Applied Stephen Isard's patch for --exclude-globbing-filelist
modified:
  duplicity/commandline.py
------------------------------------------------------------
revno: 50
committer: bescoto
timestamp: Sun 2003-04-06 03:30:03 +0000
message:
  Added mention of rsync backend.
modified:
  duplicity.1
------------------------------------------------------------
revno: 49
committer: bescoto
timestamp: Sun 2003-04-06 03:28:43 +0000
message:
  added rsync contributed by Sebastian Wilhelmi
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 48
committer: bescoto
timestamp: Fri 2003-03-14 01:34:57 +0000
message:
  Added test and fix for long symlink to long file bug
modified:
  CHANGELOG
  duplicity/tarfile.py
  duplicity/tarfile.py.old
  testing/finaltest.py
------------------------------------------------------------
revno: 47
committer: bescoto
timestamp: Sun 2003-03-09 07:36:36 +0000
message:
  Raise error (instead of exiting silently) if no files found to restore
modified:
  TODO
  duplicity-bin
  duplicity/patchdir.py
  testing/finaltest.py
------------------------------------------------------------
revno: 46
committer: bescoto
timestamp: Sun 2003-03-09 06:17:01 +0000
message:
  Added long filenames test
modified:
  testing/finaltest.py
------------------------------------------------------------
revno: 45
committer: bescoto
timestamp: Sat 2003-03-08 16:28:24 +0000
message:
  Added man page info on --short-filenames option
modified:
  TODO
  duplicity.1
------------------------------------------------------------
revno: 44
committer: bescoto
timestamp: Sun 2003-02-02 07:48:05 +0000
message:
  (version of) Helmut Schneider's patch to display mtimes with list files
modified:
  CHANGELOG
  TODO
  duplicity-bin
  duplicity/path.py
------------------------------------------------------------
revno: 43
committer: bescoto
timestamp: Sat 2002-11-30 22:38:38 +0000
message:
  Added --no-encryption option, fixed crash on inc when no changed files
modified:
  CHANGELOG
  duplicity-bin
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/globals.py
  duplicity/gpg.py
  testing/finaltest.py
  testing/gpgtest.py
------------------------------------------------------------
revno: 42
committer: bescoto
timestamp: Sat 2002-11-30 20:10:20 +0000
message:
  Added --verify option, tweaked some verbosity levels
modified:
  CHANGELOG
  duplicity-bin
  duplicity.1
  duplicity/backends.py
  duplicity/commandline.py
  duplicity/gpg.py
  duplicity/path.py
  testing/finaltest.py
------------------------------------------------------------
revno: 41
committer: bescoto
timestamp: Sat 2002-11-30 18:16:34 +0000
message:
  Added compare_verbose and test to path module
modified:
  duplicity/path.py
  testing/pathtest.py
------------------------------------------------------------
revno: 40
committer: bescoto
timestamp: Sun 2002-11-24 08:38:54 +0000
message:
  Changed restore procedure.  Now all sets integrated simultaneously.
modified:
  CHANGELOG
  duplicity-bin
  duplicity/diffdir.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  testing/finaltest.py
  testing/patchdirtest.py
------------------------------------------------------------
revno: 39
committer: bescoto
timestamp: Tue 2002-11-19 19:56:30 +0000
message:
  Fixed typo in get_ropath
modified:
  duplicity/path.py
------------------------------------------------------------
revno: 38
committer: bescoto
timestamp: Mon 2002-11-18 02:06:32 +0000
message:
  Added a few options for only doing upload/move/checkin/etc
added:
  dist/makeweb
------------------------------------------------------------
revno: 37
committer: bescoto
timestamp: Mon 2002-11-18 00:18:51 +0000
message:
  Changed way difftars are split between volumes to waste less space
modified:
  CHANGELOG
  duplicity-bin
  duplicity/diffdir.py
  duplicity/gpg.py
  testing/gpgtest.py
------------------------------------------------------------
revno: 36
committer: bescoto
timestamp: Sun 2002-11-17 18:32:29 +0000
message:
  Slight tweak to base36 code
modified:
  duplicity/file_naming.py
------------------------------------------------------------
revno: 35
committer: bescoto
timestamp: Sun 2002-11-17 18:16:48 +0000
message:
  Added extra tests for base36 conversion
modified:
  CHANGELOG
  duplicity/file_naming.py
  testing/file_namingtest.py
------------------------------------------------------------
revno: 34
committer: bescoto
timestamp: Sun 2002-11-17 09:11:19 +0000
message:
  Shorted short filenames (use base36)
modified:
  CHANGELOG
  duplicity/file_naming.py
  testing/file_namingtest.py
------------------------------------------------------------
revno: 33
committer: bescoto
timestamp: Sun 2002-11-17 08:21:57 +0000
message:
  Swallow GPG logging output if verbosity 3 or less
modified:
  CHANGELOG
  duplicity/gpg.py
------------------------------------------------------------
revno: 32
committer: bescoto
timestamp: Sun 2002-11-17 07:43:36 +0000
message:
  Added --remove-older-than option, changed --current-time behavior
modified:
  CHANGELOG
  duplicity-bin
  duplicity.1
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 31
committer: bescoto
timestamp: Sun 2002-11-17 03:50:16 +0000
message:
  Added --cleanup option
modified:
  duplicity-bin
  duplicity.1
  duplicity/commandline.py
------------------------------------------------------------
revno: 30
committer: bescoto
timestamp: Sun 2002-11-17 03:29:02 +0000
message:
  Added --force option.
modified:
  duplicity.1
  duplicity/commandline.py
  duplicity/globals.py
------------------------------------------------------------
revno: 29
committer: bescoto
timestamp: Sun 2002-11-17 03:23:48 +0000
message:
  Added code for finding extraneous and old files
modified:
  duplicity/collections.py
  testing/collectionstest.py
------------------------------------------------------------
revno: 28
committer: bescoto
timestamp: Sun 2002-11-17 00:01:18 +0000
message:
  For ssh, deleted in groups of 10 so command line doesn't overflow
modified:
  duplicity/backends.py
------------------------------------------------------------
revno: 27
committer: bescoto
timestamp: Sat 2002-11-16 22:30:36 +0000
message:
  Fixed a few minor collections bugs, added get_extraneous
modified:
  CHANGELOG
  duplicity/collections.py
  duplicity/file_naming.py
  duplicity/path.py
  testing/collectionstest.py
------------------------------------------------------------
revno: 26
committer: bescoto
timestamp: Thu 2002-11-14 17:29:07 +0000
message:
  Added note on one pass restores/verifies
modified:
  TODO
------------------------------------------------------------
revno: 25
committer: bescoto
timestamp: Thu 2002-11-14 17:18:58 +0000
message:
  Added --restore-time bug fix note
modified:
  CHANGELOG
------------------------------------------------------------
revno: 24
committer: bescoto
timestamp: Tue 2002-11-12 05:47:28 +0000
message:
  Better fix for same (current_time) bug
modified:
  duplicity-bin
------------------------------------------------------------
revno: 23
committer: bescoto
timestamp: Tue 2002-11-12 05:46:57 +0000
message:
  Fixed minor bug erasing output dir too early
modified:
  testing/finaltest.py
------------------------------------------------------------
revno: 22
committer: bescoto
timestamp: Tue 2002-11-12 02:38:03 +0000
message:
  Restores now default to current time if restore time not specified
modified:
  duplicity-bin
------------------------------------------------------------
revno: 21
committer: bescoto
timestamp: Tue 2002-11-12 02:30:21 +0000
message:
  Added undocumended --collection-status option for testing purposes
modified:
  TODO
  duplicity-bin
  duplicity/collections.py
  duplicity/commandline.py
------------------------------------------------------------
revno: 20
committer: bescoto
timestamp: Mon 2002-11-11 16:18:05 +0000
message:
  More misc updates for 0.3.0
modified:
  TODO
------------------------------------------------------------
revno: 19
committer: bescoto
timestamp: Sun 2002-11-10 20:44:14 +0000
message:
  Few last minute tweaks to prepare for 0.3.0 release
modified:
  CHANGELOG
  dist/makedist
  duplicity.1
  testing/collectionstest.py
  testing/dup_timetest.py
------------------------------------------------------------
revno: 18
committer: bescoto
timestamp: Sun 2002-11-10 20:25:06 +0000
message:
  Added --ssh-command and --scp-command options
modified:
  CHANGELOG
  duplicity.1
  duplicity/backends.py
  duplicity/commandline.py
  testing/finaltest.py
------------------------------------------------------------
revno: 17
committer: bescoto
timestamp: Sun 2002-11-10 19:19:23 +0000
message:
  Fixed time-must-be-int bug with --short-filenames, added test
modified:
  duplicity/backends.py
  duplicity/collections.py
  duplicity/dup_time.py
  testing/file_namingtest.py
  testing/finaltest.py
------------------------------------------------------------
revno: 16
committer: bescoto
timestamp: Sun 2002-11-10 17:52:51 +0000
message:
  Various bugfixes so ftp backend passes final test
modified:
  duplicity-bin
  duplicity/backends.py
  testing/backendtest.py
  testing/finaltest.py
------------------------------------------------------------
revno: 15
committer: bescoto
timestamp: Sun 2002-11-10 09:00:38 +0000
message:
  Added --short-filenames option
modified:
  CHANGELOG
  duplicity/commandline.py
  duplicity/file_naming.py
  duplicity/globals.py
  testing/file_namingtest.py
------------------------------------------------------------
revno: 14
committer: bescoto
timestamp: Sun 2002-11-10 08:12:46 +0000
message:
  Added ftp backend support
modified:
  CHANGELOG
  duplicity/backends.py
  testing/backendtest.py
------------------------------------------------------------
revno: 13
committer: bescoto
timestamp: Sun 2002-11-03 07:53:57 +0000
message:
  Added man page entry for --file-to-restore option
modified:
  duplicity.1
------------------------------------------------------------
revno: 12
committer: bescoto
timestamp: Sun 2002-11-03 07:50:43 +0000
message:
  Added statistics reporting after successful backup
added:
  duplicity/statistics.py
  testing/statisticstest.py
modified:
  CHANGELOG
  TODO
  duplicity-bin
  duplicity.1
  duplicity/backends.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/globals.py
  duplicity/path.py
------------------------------------------------------------
revno: 11
committer: bescoto
timestamp: Sat 2002-11-02 22:08:34 +0000
message:
  Added --list-current-files option
modified:
  dist/setup.py
  duplicity-bin
  duplicity.1
  duplicity/commandline.py
  duplicity/diffdir.py
------------------------------------------------------------
revno: 10
committer: bescoto
timestamp: Sat 2002-11-02 20:35:00 +0000
message:
  Make CVS more friendly; don't depend on src symlink
added:
  CVS-README
modified:
  dist/makedist
  dist/makerpm
  duplicity/compilec.py
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/manifesttest.py
  testing/memcheck.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/selectiontest.py
  testing/statictest.py
  testing/test_tarfile.py
------------------------------------------------------------
revno: 9
committer: bescoto
timestamp: Sat 2002-11-02 19:14:51 +0000
message:
  Updated documentation on new globbing options
modified:
  duplicity.1
  rdiffdir.1
------------------------------------------------------------
revno: 8
committer: bescoto
timestamp: Sat 2002-11-02 19:02:19 +0000
message:
  Fixed bug & added test when root was reg file, not dir
modified:
  CHANGELOG
  duplicity/patchdir.py
  testing/finaltest.py
------------------------------------------------------------
revno: 7
committer: bescoto
timestamp: Sat 2002-11-02 18:16:15 +0000
message:
  Added --include/exclude-globbing-filelist options
modified:
  CHANGELOG
  TODO
  duplicity/commandline.py
  duplicity/selection.py
  rdiffdir
  testing/selectiontest.py
------------------------------------------------------------
revno: 6
committer: bescoto
timestamp: Fri 2002-11-01 06:28:56 +0000
message:
  Fixed tar '..' security bug
modified:
  CHANGELOG
  duplicity/patchdir.py
  testing/patchdirtest.py
------------------------------------------------------------
revno: 5
committer: bescoto
timestamp: Fri 2002-11-01 05:02:33 +0000
message:
  Added 2 test cases: neg mtimes, missing u/gnames
  
  Now check to make sure these files aren't spuriously marked as
  changed.
modified:
  testing/diffdirtest.py
  testing/testfiles.tar.gz
------------------------------------------------------------
revno: 4
committer: bescoto
timestamp: Thu 2002-10-31 18:14:50 +0000
message:
  Fixed dumb st_time/st_mtime typo
modified:
  duplicity/path.py
------------------------------------------------------------
revno: 3
committer: bescoto
timestamp: Tue 2002-10-29 07:55:51 +0000
message:
  Updated with new web page/mailing list information.
modified:
  README
------------------------------------------------------------
revno: 2
committer: bescoto
timestamp: Tue 2002-10-29 07:50:42 +0000
message:
  Added full GPL statement in source files at request of Jaime Villate
  of the Savannah site.  Also updated address of FSF.
modified:
  duplicity-bin
  duplicity/backends.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_time.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/static.py
  rdiffdir
------------------------------------------------------------
revno: 1
committer: bescoto
timestamp: Tue 2002-10-29 01:49:46 +0000
message:
  Initial checkin
added:
  CHANGELOG
  COPYING
  README
  TODO
  dist/
  dist/duplicity.spec
  dist/makedist
  dist/makerpm
  dist/setup.py
  duplicity/
  duplicity-bin
  duplicity.1
  duplicity/GnuPGInterface.py
  duplicity/__init__.py
  duplicity/_librsyncmodule.c
  duplicity/backends.py
  duplicity/collections.py
  duplicity/commandline.py
  duplicity/compilec.py
  duplicity/diffdir.py
  duplicity/dup_temp.py
  duplicity/dup_time.py
  duplicity/file_naming.py
  duplicity/globals.py
  duplicity/gpg.py
  duplicity/lazy.py
  duplicity/librsync.py
  duplicity/log.py
  duplicity/manifest.py
  duplicity/misc.py
  duplicity/patchdir.py
  duplicity/path.py
  duplicity/robust.py
  duplicity/selection.py
  duplicity/selection.py.old
  duplicity/static.py
  duplicity/tarfile.py
  duplicity/tarfile.py.old
  rdiffdir
  rdiffdir.1
  tarfile-LICENSE
  testing/
  testing/GnuPGInterfacetest.py
  testing/backendtest.py
  testing/collectionstest.py
  testing/diffdirtest.py
  testing/dup_temptest.py
  testing/dup_timetest.py
  testing/file_namingtest.py
  testing/finaltest.py
  testing/gpgtest.py
  testing/gpgtest2.py
  testing/lazytest.py
  testing/manifesttest.py
  testing/memcheck.py
  testing/misctest.py
  testing/patchdirtest.py
  testing/pathtest.py
  testing/rdiffdirtest.py
  testing/roottest.py
  testing/roottest.pyc
  testing/selectiontest.py
  testing/statictest.py
  testing/temp2.tar
  testing/test_tarfile.py
  testing/testfiles.tar.gz
  testing/testtar.tar

2017-10-31  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1720159 - Cannot allocate memory with large manifest file since 0.7.03
      - filelist is not read if --file-changed option in collection-status not present
      - This will keep memory usage lower in non collection-status operations

2017-10-26  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1448094 with patch from Tomáš Zvala
      - Don't log incremental deletes for chains that have no incrementals
    * Fixed bug #1724144 "--gpg-options unused with some commands"
      - Add --gpg-options to get version run command

2017-10-16  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1654756 with new b2backend.py module from Vincent Rouille
      - Faster (big files are uploaded in chunks)
      - Added upload progress reporting support

2017-10-12  Kenneth Loafman  <kenneth@loafman.com>

    * Patched in lp:~mterry/duplicity/rename-dep
      - Make rename command a dependency for LP build

2017-09-22  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1714663 "Volume signed by XXXXXXXXXXXXXXXX, not XXXXXXXX"
      - Normalized comparison length to min length of compared keys before comparison
      - Avoids comparing mix of short, long, or fingerprint size keys.

2017-09-13  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1715650 with patch from Mattheww S
      - Fix to make duplicity attempt a get first, then create, a container
        in order to support container ACLs.

2017-09-07  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/more-decode-issues
      - Here's some fixes for another couple UnicodeDecodeErrors.
      - The duplicity/dup_time.py fixes when a user passes a utf8 date string (or a string with bogus
        utf8 characters, but they have to really try to do that). This is bug 1334436.
      - The bin/duplicity change from str(e) to util.uexc(e) fixes bug 1324188.
      - The rest of the changes (util.exception_traceback and bin/duplicity changes to use it) are to
        make the printing of exceptions prettier. Without this, if you see a French exception, you see
        "accept\xe9es" instead of "acceptées".
      - You can test all of these changes in one simple line:
        $ LANGUAGE=fr duplicity remove-older-than $'accept\xffées'
    * Fix backend.py to allow string, list, and tuple types to support megabackend.py.

2017-09-06  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug introduced in new megabackend.py where process_commandline()
      takes a string not a list.  Now it takes both.
    * Updated web page for new megabackend requirements.

2017-09-01  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1538333 Assertion error in manifest.py: assert filecount == ...
      - Made sure to never pass .part files as true manifest files
      - Changed assert to log.Error to warn about truncated/corrupt filelist
      - Added unit test to make sure detection works
      - Note: while this condition is serious, it will not affect the basic backup and restore
        functions.  Interactive options like --list-files-changed and --file-changed will not
        work correctly for this backup set, so it is advised to run a full backup as soon as
        possible after this error occurs.
    * Fixed bug #1638033 Remove leading slash on --file-to-restore
      - code already used rstrip('/') so change to just strip('/')

2017-08-29  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1394386 with new module megabackend.py from Tomas Vondra
      - uses megatools from https://megatools.megous.com/ instead of mega.py library
        which has been deprecated
      - fixed copyright and PEP8 issues
      - replaced subprocess.call() with self.subprocess_popen() to standardize

2017-08-28  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1711905 with suggestion from Schneider
      - log.Warn was invoked with log.warn in webdavbackend.py
    * Merged in lp:~mterry/duplicity/gpg-tag-versions
      - Support gpg versions numbers that have tags on them.
      - This can happen if you build gpg from git trunk (e.g. 2.1.15-beta20). Or if you run
        against the freedesktop flatpak runtime (e.g. 2.1.14-unknown).

2017-08-15  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1709047 with suggestion from Gary Hasson
      - fixed so default was to use original filename
    * Fixed PEP8 errors in bin/duplicity
    * Merged in lp:~mterry/duplicity/gio_child_for_display_name
      - gio: be slightly more correct and get child GFiles based on display name

2017-08-06  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/giobackend-display-name
      - giobackend: handle a wider variety of gio backends by making less assumptions;
        in particular, this fixes the google-drive: backend

2017-07-20  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed encrypted remote manifest handling to merely put out a non-fatal
      error message and continue if the private key is not available.

2017-07-19  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed slowness in 'collection-status' by basing the status on the
      remote system only.  The local cache is treated as empty.

2017-07-11  Kenneth Loafman  <kenneth@loafman.com>

    * Patched in lp:~dawgfoto/duplicity/skip_sync_collection_status
      - collection-status should not sync metadata
      - up-to-date local metadata is not needed as collection-status is
        generated from remote file list
      - syncing metadata might require to download several GBs

2017-06-30  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~xlucas/duplicity/multibackend-prefix-affinity
      - Support prefix affinity in multibackend.
    * Merged in lp:~xlucas/duplicity/pca-backend
      - Add support for OVH Public Cloud Archive backend.
    * Fixed PEP8 and 2to3 issues.

2017-06-23  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dawgfoto/duplicity/replicate
      - Add integration test for newly added replicate command.
      - Also see https://code.launchpad.net/~dawgfoto/duplicity/replicate/+merge/322836.

2017-06-19  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed problem in dist/makedist when building on Mac where AppleDouble
      files were being created in the tarball.  See:
      https://superuser.com/questions/61185/why-do-i-get-files-like-foo-in-my-tarball-on-os-x

2017-06-10  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1265765 with patches from Matthias Larisch and Edgar Soldin
      - SSH Paramiko backend now uses BufferedFile implementation to enable
        collecting the entire list of files on the backend.
    * Copy.com is gone so remove copycombackend.py.
    * Merged in lp:~xlucas/duplicity/swift-multibackend-bug
      - Fix a bug when swift backend is used in a multibackend configuration.

2017-06-04  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/08-fix-man-verify
      - Fix description of --verify and --compare-data in the man page. Now
        clarifies that verify compares the restored files to hashes stored at
        backup date, while --compare-data compares restored files to files
        in target_path.

2017-06-03  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dernils/duplicity/docker-compose
      - Test Infrastructure now utilizing docker-compose

2017-06-02  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug #1672540 with patch from Benoit Nadeau
      - Rename would fail to move par files when moving across filesystems.
      - Patch uses shutil.move() to do the rename instead.

2017-05-31  Kenneth Loafman  <kenneth@loafman.com>

    * Revisited bug #670891 with patch from Edgar Soldin
      - Forced librsync.PatchedFile() to extract file object from TemporaryFile()
        object when on Windows or Cygwin systems.  This allows us to avoid the
        problem of tmpfile() use which creates temp files in the wrong place.
      - See discussion at https://bugs.launchpad.net/duplicity/+bug/670891

2017-05-17  Kenneth Loafman  <kenneth@loafman.com>

    * May have finally fixed bug #1556553, "Too many open files...".
      - Applied patch from Howard Kaye, question #631423.  The fix is to dup
        the file descriptor, and then close the file in the deallocator
        routine in the glue code. Duping the file lets the C code and the Python
        code each close the file when they are done with it.
      - Invalidated and removed the fix put in for bug #1320832.
      - Caveat: long incremental chains will still eat up a large number of file
        descriptors.  It's a very risky practice, so I'm not inclined to fix it.

2017-05-15  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dernils/duplicity/Dockerfile
      - Now have subnet name and IP of the subnet for testing as a variable.

2017-05-14  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~xlucas/duplicity/swift-storage-policies
      - This brings support for Swift storage policies: when using a Swift
        backend, you can specify the policy containers should be operating on.
      - This is similar to AWS Cloud Storage classes (ia, rrs, glacier and so on).
    * Merged in lp:~dernils/duplicity/Dockerfile
      - Added another backend to the docker test infrastructure, updated the setup
        for testing and updated the documentation.

2017-05-12  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/tox_pylint_fixes
      - Changes needed to run-tests without pylint E0401(import-error) errors

2017-05-11  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1320641 and others regarding lockfile
      - swap from lockfile to fasteners module
      - use an fcntl() style lock for process lock of duplicity cache
      - lockfile will now clear if duplicity is killed or crashes

2017-05-09  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1689632 with patch from Howard Kaye
      - On MacOS, the tempfile.TemporaryFile call erroneously raises an
        IOError exception saying that too many files are open. This causes
        restores to fail randomly, after thousands of files have been restored.

2017-05-06  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dernils/duplicity/DockerfileConvenience
      - Add a few files that are the beginning of further infrastructure based
        on docker. It contains a Dockerfile for a simple ftp server (used for
        backend testing) and a setup script that can be used to set up the
        complete test environment.
    * Moved Dockerfile for duplicitytest into testinfrastructure/duplicity_test
    * Moved some things around in testing/infrastructure to clean up

2017-05-05  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dernils/duplicity/DockerfileConvenience
      - Added a few tools to the Dockerfile that make life easier
    * Fixed bug #1320832 with suggestion from Oskar Wycislak
      - Use chunks instead of reading it all in swiftbackend

2017-05-04  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dawgfoto/duplicity/replicate
      - Add replicate command to replicate a backup (or backup
        sets older than a given time) to another backend, leveraging
        duplicity's backend and compression/encryption infrastructure.
    * Fixed some incoming PyLint and PEP-8 errors.
    * Merged in lp:~marix/duplicity/add-azure-arguments
      - Using the Azure backend to store large amounts of data we found that
        performance is sub-optimal. The changes on this branch add command line
        parameters to fine-tune some parameters of the Azure storage library,
        allowing to push write performance towards Azure above 1 Gb/s for large
        back-ups. If a user does not provide the parameters the defaults of the
        Azure storage library will continue to be used.
    * Replace incoming non-ASCII chars in commandline.py
    * bzr does not honor perms so fix the perms at the start of the testing and
      avoid annoying error regarding testing/gnupg having too lenient perms

2017-04-23  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dernils/duplicity/testing
      - Fixed minor stuff in requirements.txt.
      - Added a Dockerfile for testing.
      - Minor changes to README files.
      - Added README-TESTING with some information on testing.
    * Merged in lp:~dernils/duplicity/documentation
      - Minor changes to README-REPO, README-TESTING
      - Also redo the changes to requirements.txt and Dockerfile

2017-04-22  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1680682 with patch supplied from Dave Allan
      - Only specify --pinentry-mode=loopback when --use-agent is not specified
    * Fixed man page that had 'cancel' instead of 'loopback' for pinentry mode
    * Fixed bug #1684312 with suggestion from Wade Rossman
      - Use shutil.copyfile instead of os.system('cp ...')
      - Should reduce overhead of os.system() memory usage.

2017-03-13  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1668750 - Don't mask backend errors
      - added exception prints to module import errors

2017-03-11  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1671852 - Code regression caused by revision 1108
      - change util.uexc() back to bare uexc()

2017-03-05  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in p:~aaron-whitehouse/duplicity/pep8_E402_fixes
      - Fixed PEP8 errors: E402 module level import not at top of file

2017-03-02  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~benoit.bertholon/duplicity/duplicity
      - Use the globals.archive_dir variable to store only a string
        in the case of a path, uses globals.archive_dir_path

2017-02-21  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~marix/duplicity/azure-storage-0.30.0-plus
      - This makes the Azure backend compatible with version 0.30.0 and up of the
        underlying azure-storage package.
    * Merged in lp:~marix/duplicity/azure-storage-sas
      - This branch adds support for Shared Access Signature to the Azure backend
        which allows to run Duplicity with a minimal set of permissions.
    * Merged in lp:~aaron-whitehouse/duplicity/pep8_test_fixes
      - Fix PEP-8 testing by moving to using pycodestyle library.
      - Temporarily add ignores to allow these tests to pass.
      - Fix E305 PEP8 errors: expected 2 blank lines after class or function definition, found 1.
    * Merged in lp:~benoit.bertholon/duplicity/duplicity
      - Fixes bug #1666194 - ProcessCommandLine function called twice fail and arglist argument not used
    * Fixed variable name change in last merge which broke a bunch of tests
      - Changed archive_dir_root back to archive_dir
    * Fixed bug #1367675 - IMAP Backend does not work with Yahoo server
      - added the split() as needed in 'nums=list[0].strip().split(" ")'
      - the other fixes mentioned in the bug report comments were already done

2017-02-12  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/08-python-futurize-stage-1
      - Made many of the safer changes for improved Python 3 support (python-future's futurize -stage1)
        without functional change to the code (and leaving the isinstance(s, types.StringType) tests unchanged).
      - Created Python 2/3 compatible tests for int and long.
      - Update setup.py to show only Python 2.7 support.

2017-02-11  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1603704 with patch supplied by Maciej Bliziński
      - Crash with UnicodeEncodeError

2017-02-08  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/08-refactor-unit-test-globmatch
      - Rename path_matches_glob_fn to select_fn_from_glob, as this more accurately reflects the return value.
      - Significantly refactored unit/test_globmatch.py to make this cleaner and clearer.
    * Fixed bug #1657916 with patch supplied by Daniel Harvey
      - B2 provider cannot handle two backups in the same bucket

2017-02-07  Kenneth Loafman  <kenneth@loafman.com>

    * Add detail about import exceptions in onedrivebackend.py

2017-01-30  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/08-merge-glob-parsers
      - Use a single code path for glob strings whether or not these contain special
        characters/wildcards (glob_get_normal_sf) and remove glob_get_filename_sf and glob_get_tuple_sf.
      - Remove run-tests-ve as this was identical to run-tests.

2017-01-24  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~matthew-t-bentley/duplicity/duplicity
      - Sets a user agent. Backblaze asked for this in case there are errors that originate
        from the Duplicity B2 backend
      - Only retrieves a new upload URL when the current one expires, to bring it in line
        with their best practices for integrations: https://www.backblaze.com/b2/docs/integration_checklist.html

2017-01-19  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1655268 "--gpg-binary option not working"
      - If gpg binary is specified rebuild gpg profile using new binary location

2017-01-16  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1623342 with patch supplied by Daniel Jakots
      - Failing test on OpenBSD because tar/gtar not found
    * Fixed bug #1654220 with patch supplied by Kenneth Newwood
      - Duplicity fails on MacOS because GPG version parsing fails
    * Merged in lp:~aaron-whitehouse/duplicity/0-8-merge_selection_tests
      - Merge in TestExcludeIfPresent from 0.7-series, which tests the behaviour of
        duplicity's --exclude-if-present option.
      - Move and rename TestTrailingSlash2 test (was duplicate name) as in 0.7-series.
      - Fix PEP error on adbackend.py.
      - Add jottalib as a tox dep to fix pylint error.
      - Remove unnecessary skipUnless Linux as per 0.7-series.

2016-12-29  Kenneth Loafman  <kenneth@loafman.com>

    * Fix Bug #1642813 with patch from Ravi
      - If stat() returns None, don't attempt to set perms.
    * Merged in lp:~breunigs/duplicity/amazondrive3
      - As reported on the mailinglist, if a space is entered while duplicity asks for the URL, it fails.
        Since all important spaces are URL encoded anyway, this should be fine even if there are spaces in
        the URL at all. I also patched it in the onedrive backend, because it must have similar issues.

2016-12-25  Kenneth Loafman  <kenneth@loafman.com>

    * Fix some issues with testing on MacOS
    * Fix problem with gpg2 in yakety and zesty

2016-12-11  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/Bug_1624725_files_within_folder_slash
      - Fixed Bug #1624725, so that an include glob ending in "/" now includes folder contents (for globs with
        and without special characters). This preserves the behaviour that an expression ending in "/" only
        matches a folder, but now the contents of any matching folder is included.

2016-12-08  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~horgh/duplicity/copy-symlink-targets-721599
      - Add --copy-links to copy symlink contents, not just the link itself.

2016-11-21  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug using 40-char sign keys, from Richard McGraw on mail list
      - Remove truncation of argument and adjust comments
    * Merged in lp:~dernils/duplicity/robust-dropbox-backend
      - Added new command line option --backend-retry-delay
        that allows to determine the time that duplicity sleeps
        before retrying after an error has occured.
      - Added some robustness to dpbxbackend.py that ensures re-authentication
        happens in case that a socket is changed (e.g. due to a forced reconnect
        of a dynamic internet connection).
    * Merged in lp:~ed.so/duplicity/manpage.fixes
      - Fix html output via rman on the website

2016-11-16  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1642098 - does not create PAR2 archives when '--par2-options' is used
      - Missing space between par2-options plus default options

2016-11-07  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~breunigs/duplicity/amazondrive2
      - Fixed variable renaming issue

2016-11-01  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1621194 with code from Tornhoof
      - Do backup to google drive working without a service account
    * Merged in lp:~havard/duplicity/jottacloudbackend
      - Adds support for a new backend, jottacloud.com, using the scheme `jottacloud:/<folder>`.
      - Reverse-engineered library, `jottalib`: http://github.com/havardgulldahl/jottalib
      - Here's how you set up jottalib https://github.com/havardgulldahl/jottalib/wiki
    * Merged in lp:~breunigs/duplicity/amazondrive
      - Provide a native backend for AmazonDrive

2016-10-22  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mwilck/duplicity/duplicity
      - GPG: enable truly non-interactive operation with gpg2
      - This patch fixes the IMO unexpected behavior that, when using GnuPG2, a pass phrase dialog always pops up for
        saving backups. This is particularly annoying when trying to do unattended / fully automatic backups.

2016-09-16  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1623342 with patch from Daniel Jakots
      - failing test on OpenBSD because tar/gtar not found

2016-08-22  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bugs #815510 and #1615480
      - Changed default --volsize to 200MB
    * Merged in lp:~mstoll-de/duplicity/duplicity
      - Backblaze announced a new domain for the b2 api

2016-08-18  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~fenisilius/duplicity/acd_init_mkdir
      - Allow duplicity to create remote folder

2016-08-12  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1612472 with patch from David Cuthbert
      - Restore from S3 fails with --with-prefix-archive if prefix includes '/'
    * Merged in lp:~arashad.ahamad/duplicity/duplicity_latest
      - Changes for connecting to IBM Bluemix ObjectStorage.  See man page.

2016-07-31  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed conflict in merge from Martin Wilck and applied
      - https://code.launchpad.net/~mwilck/duplicity/0.7-series/+merge/301492
      - merge fixes setsid usage in functional testing.

2016-07-28  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mwilck/duplicity/duplicity
      - Speedup of path_matches_glob() by about 8x.  See
        https://code.launchpad.net/~mwilck/duplicity/duplicity/+merge/301268
        for more details.

2016-07-24  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/07-fix_deja_dup_error_on_locked_files
      - Revert log.Error to log.Warn, as it was prior to the merge in rev 1224,
        as this was affecting other applications (e.g. deja dup; Bug #1605939).

2016-07-20  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1600692 with patch from Wolfgang Rohdewald
      - Allow symlink to have optional trailing slash during verify.

2016-07-03  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/remove-python26
      - Remove Python 2.6 support references and tests.

2016-07-02  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/PEP8_W503_fixes
      - Fix PEP8 W503 errors (line break before binary operator) and enable the
        PEP8 test for this in test_code.CodeTest.
    * Merged in lp:~aaron-whitehouse/duplicity/PEP8_line_length
      - Set line length error length to 120 (matching tox.ini) for PEP8 and
        fixed E501(line too long) errors.
    * Merged in lp:~duplicity-team/duplicity/po-updates
    * Prep for 0.7.08

2016-06-24  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1594780 with patches from B. Reitsma
      - Use re.finditer() to speed processing

2016-06-13  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed README-REPO to no longer mention 0.6-series
    * Merged in lp:~aaron-whitehouse/duplicity/fix_stat_errors
      - Only give an error about not being able to access possibly locked file if
        that file is supposed to be included or scanned (i.e. not excluded).
        Fixes Bug #1089131

2016-06-12  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #822697 ssh-options not passed in rsync over ssh
      - Added globals.ssh_options to rsync command line
    * Increased default volume size to 200M, was 25M

2016-06-11  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/fix_pep8
      - Fix PEP8 error in onedrivebackend.py (space before bracket)

2016-06-06  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1589038 with patches from Malte Schröder
      - Added ignore_case option to selection functions
    * Merged in lp:~mstoll-de/duplicity/b2-reauth
      - Fixes bug #1588503 b2: large uploads fail due to expired auth token

2016-06-01  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1586992 with patches from Dmitry Nezhevenko
      - Patch adds _delete_list to Par2Backend. And _delete_list fallbacks to
        _delete calls if wrapped backend has no _delete_list.

2016-05-30  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ghoz/duplicity/swift-prefix
      - adds the abiliy to use path in the swift backend, in order to have multiple
        backups to the same container neatly organized.
    * Fixed bug #1573957 with patches from Dmitry Nezhevenko
      - upload last chunk with files_upload_session_finish to avoid extra request
      - upload small files using non-chunked api
    * Fixed bug #1586934 with patches from Dmitry Nezhevenko
      - fixes error handling in wrapper

2016-05-12  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~noizyland/duplicity/fix_azurebackend_typo
      - Fix typo in error handling code

2016-04-19  Kenneth Loafman  <kenneth@loafman.com>

    * Prep for 0.7.07.1 critical bug fixes

2016-04-18  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1571134 incompatible with python-oauth2client version 2.x
      and #1558155 PyDrive backend broken, needs update to oauth2client library
      - used patch from https://bugs.debian.org/820725 but made changes
        to allow the user to continue using the old version
    * Fixed bug #1570293 duplicity is very slow due to excessive fsync
      - removed flush() after write.
      - revert to previous version

2016-04-12  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1568677 duplicity fails to use existing S3 bucket in boto backend
      - bug introduced by incomplete fix of bug #1296793
      - simplified setting of bucket locations
    * Fixed bug #1569523 get_bucket unknown keyword location and my_location name error
      - bug introduced in improper fix of bug #1568677
      - gotta love those inconsistent APIs

2016-04-11  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1568677 with suggestions from Florian Kruse
      - bug introduced by incomplete fix of bug 1296793

2016-04-10  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~duplicity-team/duplicity/po-updates
    * Prep for 0.7.07

2016-03-07  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug reported on the mailing list from Mark Grandi (assertion error
      while backing up).  In file_naming.parse() the filename was being lower
      cased prior to parsing.  If you had used a prefix with mixed case, we
      were writing the file properly, but could not find it in the backend.

2016-03-07  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/split_glob_matching_from_select
      - Move glob matching code out of selection.py's Select function and
        into globmatch.py.

2016-03-05  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/improve_present_get_sf_man_page
      - Improve man page entry for --exclude-if-present

2016-03-04  Kenneth Loafman  <kenneth@loafman.com>

    * More fixes to dist/makedist to make it more OS agnostic.
    * Merged in lp:~ed.so/duplicity/webdav.lftp.ssl-overhaul
        duplicity.1, commandline.py, globals.py
        - added --ssl-cacert-path parameter
        backend.py
        - make sure url path component is properly url decoded,
          in case it contains special chars (eg. @ or space)
        lftpbackend.py
        - quote _all_ cmd line params
        - added missing lftp+ftpes protocol
        - fix empty list result when chdir failed silently
        - added ssl_cacert_path support
        webdavbackend.py
        - add ssl default context support for python 2.7.9+
          (using system certs eg. in /etc/ssl/certs)
        - added ssl_cacert_path support for python 2.7.9+
        - gettext wrapped all log messages
        - minor refinements
    * Applied patch from Dmitry Nezhevenko to upgrade dropbox backend:
      - update to SDK v2
      - use chunked upload

2016-02-28  Kenneth Loafman  <kenneth@loafman.com>

    * Reverted changes made in rev 1164 w.r.t. getting the source from
      VCS rather than local directory.  Fixes bug #1548080.

2016-02-15  Kenneth Loafman  <kenneth@loafman.com>

    * Added acdclibackend.py from Stefan Breunig and Malay Shah
      - renamed from amazoncloudbackend to stress use of acd_cli
    * Fixed some 2to3 and Pep8 issues that had crept in
    * Backed out changes made by patching for bug #1541314.  These
      patches should not have been applied to the 0.7 series.
    * Merged in lp:~rye/duplicity/mediafire
      - Backend for https://www.mediafire.com
      - Requires https://pypi.python.org/pypi/mediafire/ installed.

2016-02-15  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~harningt/duplicity/multibackend-mirror
      - This changeset addresses multibackend handling to permit a
        mirroring option in addition to its "stripe" mode to make it
        a redundancy tool vs space-expansion tool. To do this without
        changing the configuration too much, I used the query string
        that would generally go unused for files to specify behavior
        that applies to all items inside the configuration file.

2016-02-05  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed a patching error in ssh_pexpect_backend.py
    * Merged in lp:~fpytloun/duplicity/webdav-gssapi-fix
      - Make kerberos optional for webdav backend

2016-02-03  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patch from kay-diam to fix error handling in ssh pexpect,
      fixes bug #1541314

2016-02-02  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug #1540279 - mistake in --help

2016-01-29  Kenneth Loafman  <kenneth@loafman.com>

    * Add more pylint ignore warnings tags
    * Adjust so test_restart.py can run on Mac as well
    * Fix for bug #1538333 - assert filecount == len(self.files_changed)
      - added flush after every write for all FileobjHooked files which
        should prevent some errors when duplicity is forcibly closed.

2016-01-28  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~fpytloun/duplicity/webdav-gssapi
      - support GSSAPI authentication in webdav backend

2016-01-24  Kenneth Loafman  <kenneth@loafman.com>

    * Pep8 corrections for recently released code.
    * Fixed bug #1260666 universally by splitting the filelist for
      delete before passing to backend.
    * Fixed bug #1369243 by adjusting messages to be more readable.
    * Fixed bug #1375019 with patch from Eric Bavier (home to tmp).
    * Fixed bug #1379575 with patch from Tim Ruffing (shorten webdav response).
    * Fixed bug #1492301 with patch from askretov (manually refresh oauth).

2016-01-23  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1296793 - Failed to create bucket
      - use S3Connection.lookup() to check bucket exists
      - skips Boto's Exception processing for this check
      - dupe of bug #1507109 and bug #1537185
    * Merged in lp:~mifchip/duplicity/duplicity
      - fix bug #1313964, absolute path doesn't work for FTP

2016-01-11  Kenneth Loafman  <kenneth@loafman.com>

    * Applied changes from ralle-ubuntu to fix bug 1072130.
      - duplicity does not support ftpes://

2016-01-10  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patch from abeverly to fix bug #1475890
      - allow port to be specified along with hostname on S3
      - adjusted help text and man page to reflect the change
    * Undo changes to test_restart.py.  GNU tar is needed.
    * Fix minor pep8 nit in collections.py

2016-01-07  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patch from shaochun to fix bug #1531154,
      - --file-changed failed when file contains spaces

2016-01-06  Kenneth Loafman  <kenneth@loafman.com>

    * Partial fix for bug #1529606 - shell code injection in lftpbackend
      - still need to fix the other backends that spawn shell commands
    * Make test_restart compatible with both GNUtar and BSDtar
    * Fix stupid issue with functional test path for duplicity

2016-01-04  Kenneth Loafman  <kenneth@loafman.com>

    Random stuff:
      - supply correct path for pydevd under Mac
      - fix some tests to run under Mac as well

2015-12-23  Kenneth Loafman  <kenneth@loafman.com>

    Random stuff:
      - remove RPM stuff from makedist
      - have makedist pull directly from VCS, not local dir
      - update po translation directory and build process
      - clean up some odd error messages
      - move Pep8 ignores to tox.ini

2015-12-11  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~matthew-t-bentley/duplicity/b2
      - A couple fixes allowing multiple backups to be hosted in different
        folders in the same bucket as well as some logging for -v9.

2015-12-09  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~matthew-t-bentley/duplicity/b2
      - Fix import and error typos.
      - Allow multiple backups in the same bucket.
      - Fixes bug #1523498.

2015-12-07  Kenneth Loafman  <kenneth@loafman.com>

    * Prep for 0.7.06

2015-12-04  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~matthew-t-bentley/duplicity/b2
      - Adds a backed for BackBlaze's (currently beta) B2 backup service.
      - This adds backends/b2backend.py, modifies log.py to add an
        error code and modifies commandline.py to add the b2://
        example to the help text.

2015-12-03  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~noizyland/duplicity/azurebackend-fixes
      - Support new version of Azure Storage SDK
      - Refactor _list method to support containers with >5000 blobs

2015-11-30  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug #1520691 - Shell Code Injection in hsi backend (2)
      - Added code to expand relative program path to full path.
      - Fix hisbackend where it expected a list not a string.

2015-11-28  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug #1520691 - Shell Code Injection in hsi backend
      - Replace use of os.popen3() with subprocess equivalent.

2015-11-25  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~feraudet/duplicity/fix
      - Fix missing SWIFT_ENDPOINT_TYPE env var, bug 1519694.

2015-11-24  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~michal-s/duplicity/duplicity
      - Fix azurebackend storage class import

2015-11-05  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1511308 - Cannot restore no-encryption, no-compression backup
      - Corrected code to include plain file in write_multivolume()
      - Added PlainWriteFile() to gpg.py

2015-11-01  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/tempfile.tempdir
      - make sure packages using python's tempfile create temp files in
          duplicity's temp dir

2015-10-31  Kenneth Loafman  <kenneth@loafman.com>

    * Reversed previous changes to lockfile.  Now it will take any version
      extant in the LP build repository.  (PyPi is not avail in LP build).

2015-10-27  Kenneth Loafman  <kenneth@loafman.com>

    * Cleanup issues around Launchpad build, mainly lockfile >= 0.9.
    * Merged in lp:~michal-s/duplicity/duplicity
      - WindowsAzureMissingResourceError and WindowsAzureConflictError
        changed due to SDK changes.

2015-10-26  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patch from Alexander Zangerl to update to changes in lockfile
      API 0.9 and later.  Updated README to notify users.
    * Modded tox.ini to use the latest lockfile.
    * Merged in lp:~ed.so/duplicity/setup.shebang
      - Having the python interpreter searched in the PATH is much more
        flexible than the /usr/bin/python inserted into our scripts shebang
        by setuptools.  This patch prevents that. don't touch my shebang! :)

2015-10-12  Kenneth Loafman  <kenneth@loafman.com>

    * Upgrade to newest version of pep8 and pylint.   Add three ignores
      to test_pep8 and one to test_pylint to get the rest to pass.  They
      are all valid in our case.

2015-10-10  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mnjul/duplicity/s3-infreq-access
      - This adds support for AWS S3's newly announced Infrequent Access
        storage class and is intended to implement Blueprint:
        https://blueprints.launchpad.net/duplicity/+spec/aws-s3-std-ia-class .
      - A new command line option, --s3-use-ia, is added, and boto backend
        will automatically use the correct storage class value depending on
        whether --s3-use-rrs and --s3-use-ia is set. Command line parser will
        prompt error if both --s3-use-ia and --s3-use-rrs are used together,
        as they conflict with each other.
      - The manpage has been updated giving a short explanation on the new
        option. Its wording derives from Amazon's official announcement:
        https://aws.amazon.com/about-aws/whats-new/2015/09/announcing-new-\
        amazon-s3-storage-class-and-lower-glacier-prices/
    * The ptyprocess module no longer supports Python 2.6, so fix tox.ini to
      use an older version.  Make explicit environs for all tests.


2015-09-15  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~duplicity-team/duplicity/po-updates
    * Prep for 0.7.05

2015-09-14  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~bmerry/duplicity/pydrive-id-cache
      - This fixes the issue a number of users (including myself) have been
        having with duplicity creating files with duplicate filenames on
        Google Drive. It keeps a runtime cache of filename to object ID
        mappings, so that once it has uploaded an object it won't be fooled
        by weakly consistent directory listings.

2015-09-06  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug #1493573.  Correct option name in man page.
    * Fix bug #1494228 CygWin: TypeError: basis_file must be a (true) file
      - The problem that caused the change to tempfile.TemporaryFile was due
        to the fact that os.tmpfile always creates its file in the system
        temp directory, not in the directory specified.  The fix applied was
        to use os.tmpfile in cygwin/windows and tempfile.TemporaryFile in all
        the rest.  This means that cygwin is now broken with respect to temp
        file placement of this one file (deleted automatically on close).

2015-09-06  Kenneth Loafman  <kenneth@loafman.com>

    * Updated man pages to reflect more contributors.

2015-08-25  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~germar/duplicity/par2removefix
      - After reorganisation in revision 981 and the fix for bug #1406173 the
        par2backend does not remove .par2 files anymore when removing
        duplicity-*.gpg files.
      - This banch adds an unfiltered_list() method which is used in
        delete() and delete_list()

2015-08-22  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~w.baranowski/duplicity/selection_debug
      - This little patch logs debug messages concerning path selection process,
        and so allows users to debug their include/exclude configuration.

2015-08-19  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed Bug 1438170 duplicity crashes on resume when using gpg-agent with
      patch from Artur Bodera (abodera).  Applied the same patch to incremental
      resumes as well.

2015-08-04  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed Bug 1476019 S3 storage bucket not being automatically created
      with patch from abeverley
    * Merged in lp:~aaron-whitehouse/duplicity/launchpad_tox_profile
      - Add tox testing profile that mimics the packages installed on the
        Launchpad build server, to reduce the likelihood of tests passing
        our test suite, but failing on the build server (e.g. because of
        the out-of-date mock version).
    * Merged in lp:~aaron-whitehouse/duplicity/disable_code_tests_for_lpbuildd
      - Set RUN_CODE_TESTS to 0 for lpbuildd tox profile, reflecting its value
        on the Launchpad build server (and therefore skipping PEP8, 2to3 and
        pylint). More accurately reflects the system we are mimicking and saves
        approximately 1 minute per test run.

2015-08-03  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/fix_patch_error
      - Change use of mock.patch in unit tests to accommodate the obsolete
        version of python-mock on the build server.

2015-08-02  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~dag-stenstad/duplicity/swift_authversion_3_support
      - Added support for Openstack Identity v3 in the Swift backend.
    * Merged in lp:~aaron-whitehouse/duplicity/fix_2to3_issues
      - Fixed 2to3 issues. Updated README-REPO with more test information. Updated pylint and
        test_diff2 descriptions to make it clear these require packages to be installed on the
        sytem to pass. All tests pass on Python 2.6 and Python 2.7 as at this revision.
    * Prep for 0.7.04

2015-07-31  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/trailing_slash_match_dirs
      - Made globs with trailing slashes only match directories, not files, fixing Bug #1479545.
    * Merged in lp:~aaron-whitehouse/duplicity/improve_tox_and_python2-6_testing
      - Testing improvements, particularly in relation to testing against Python version 2.6:
        * tox.ini fixed so that it is possible to run individual tests against both Python 2.6 and 2.7;
        * updated test_code.py to use unittest2 for Python versions < 2.7 (instead of failing);
        * ./run-tests now correctly runs all tests against both Python 2.6 and 2.7; and
        * improved testing directions in README-REPO.

2015-07-29  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/bug_884371
      - Fixed Bug #884371 - Stopped an exclude glob trumping an earlier scan glob, but also
        ensured that an exclude glob is not trumped by a later include. This fix is important,
        as without it files that are specified to be included are not being backed up as expected.
      - Fixed Bug #932482 - a trailing slash at the end of globs no longer prevents them working
        as expected.
    * Merged in lp:~aaron-whitehouse/duplicity/reenable_tests
      - Re-enable unit.test_selection tests that had been temporarily commented out.

2015-07-04  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1471348 Multi back-end doesn't work with hubiC
      - added init of superclass in both cases.
    * Fixed bug 1471348 Multi back-end doesn't work with hubiC (again)
      - hubiC should reach up to duplicity.backend.__init__

2015-07-03  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/fix_POTFILES.in_and_run-tests
      - Fixed two filename references in po/POTFILES.in, a mistake which crept in in
        rev 1093 and caused testing/run-tests to fail with "IndexError: list index
        out of range".
    * Merged in lp:~aaron-whitehouse/duplicity/reactivate_progress_test
      - Re-enable the test of the --progress option (test_exclude_filelist_progress_option),
        which was marked as an expected failure. The issue causing this test to fail was
        fixed in revision 1095 and the test now passes.

2015-06-21  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/gpg.binary
      - new parameter --gpg-binary allows user to point to a different gpg binary,
        not necessarily in path

2015-06-20  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1466582 - reduce unnecessary syscall with --exclude-if-present - with
      patch from Kuang-che Wu to make sure resulting path is a directory.

2015-06-17  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1466160 - pydrive backend is slow to remove old backup set - with
      patch from Kuang-che Wu to implement _delete_list().

2015-06-16  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1465335 - pydrive still use files in trash can - with patch
      from Kuang-che Wu to ignore trashed files.
    * Fixed bug 1452263 - par2 option not working on small processors - with patch
      from Kuang-che Wu to ignore default 30 second timeout.

2015-06-14  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 791794 - description of --gpg-options is misleading, Simply
      needed to add the '--' before the options as in "--opt1 --opt2=parm".

2015-05-31  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~bmerry/duplicity/pydrive-regular
      - This implements the proposal made by somebody else
        (http://lists.gnu.org/archive/html/duplicity-talk/2015-02/msg00037.html)
        to allow the pydrive backend to work with a normal drive account instead
        of a service account. It seems to be working for me: I was able to migrate
        seamlessly from the gdocs backend. It's set up so that a service account
        can still be used, depending on which environment variable is set.
        The man page is updated to describe how to use the new functionality.
    * Merged in lp:~ed.so/duplicity/gdocs.pydrive
      - make pydrive new gdocs default backend
      - keep gdata backend as gdata+gdocs://
    * Fix a couple of PEP8 glitches.

2015-05-27  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~noizyland/duplicity/fix-progress
      - Fixes bug 1264744.  selection.filelist_globbing_get_sfs leaves the
        filelist file object's position at the end of the file. When the
        --progress option is used the filelists need to be read twice. On
        the second read nothing is read from the file because file has
        already been read and the position is EOF.  This patch calls seek(0)
        on the filelist to reset the position to BOF so that subsequent
        read() calls will return data.
    * Added pylint ignore error in webdavbackend.py.

2015-05-11  Kenneth Loafman  <kenneth@loafman.com>

    * Prep for 0.7.03

2015-05-10  Kenneth Loafman  <kenneth@loafman.com>

    * Merge in lp:~sjakthol/duplicity/onedrive-error-message
      - Add proper error message for OneDrive backend when python-requests or
        python-requests-oauthlib is not installed (bug 1453355).

2015-05-08  Kenneth Loafman  <kenneth@loafman.com>

    * Added ability to get single file status from collection-status with
      patch from jitao (bug 1044715), like so:
      $ duplicity collection-status --file-changed c1 file://./foo

2015-05-01  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1448249 and bug 1449151 thanks to David Coppit.
      - When patching, close base file before renaming
      - Enable --ignore-errors flag in rdiffdir

2015-04-20  Kenneth Loafman  <kenneth@loafman.com>

    * Merge in lp:~cemsbr/duplicity/duplicity
      - Fix bug 1432229 in Copy.com backend:
        Reply header has no content-type for JSON detection. Now, we also check
        whether the content starts with '{'.
    * Fixed bug 1444404 with patch from Samu Nuutamo
      - rdiffdir patch crashes if a regular file is changed to a non-regular
        file (symlink, fifo, ...)

2015-04-12  Kenneth Loafman  <kenneth@loafman.com>

    * Merge in lp:~stynor/duplicity/multi-backend
      - A new backend that allows use of more than one backend stores (e.g. to
        combine the available space from more than one cloud provider to make
        a larger store available to duplicity).
    * Move requirements section lower in manpage.

2015-03-29  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug 1437789 with patch from pdf
      - par2backend.py incorrect syntax in get()

2015-03-22  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug 1434702 with help from Robin Nehls
      - incorrect response BackendException while downloading signatures file.

2015-03-18  Kenneth Loafman  <kenneth@loafman.com>

    * Fix bug 1432999 with hint from Antoine Afalo.
      - '/'s at end of destination cause problems with onedrivebackend.

2015-03-13  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/filelist_combine
      - Merged globbing and non-globbing filelists to use the same code path
        and all accept globbing characters. Added deprecation warning to the
        --exclude-globbing-filelist and include-globbing-filelist options in
        commandline.py and hid them from help output. Updated the manual
        (and unit tests) accordingly.
      - Note that this does trigger a change in behaviour for duplicity.
        Previously, include patterns in include-filelist did not match files
        in a directory that was included, so /usr/local in an include file
        would not have matched /usr/local/doc. Now, this folder would be
        included, as would occur if --include or the old
        --include-globbing-filelist was used. Additional lines will therefore
        need to be added to filelists to unambiguously exclude unwanted
        subfolders, if this is intended.
      - Mark --include-filelist-stdin and --exclude-fielist-stdin for
        deprecation and hide from --help output.

2015-03-11  Kenneth Loafman  <kenneth@loafman.com>

    * Prep for 0.7.02.

2015-03-10  Kenneth Loafman  <kenneth@loafman.com>

    * remove extraneous string format arg in previous scp fix.

2015-03-09  Kenneth Loafman  <kenneth@loafman.com>

    * Fix for --pydevd debug environment and location under Eclipse.
    * Fix for bug where scp was actually working as scp and not working with
      rsync.net because of using extraneous test command in restricted shell.
      Was trying "test -d 'foo' || mkdir -p 'foo'", now only "mkdir -p foo".

2015-02-12  Kenneth Loafman  <kenneth@loafman.com>

    * Really fix bug 1416344 based on comment #5 by Roman Tereshonkov.

2015-02-09  Kenneth Loafman  <kenneth@loafman.com>

    * Fix _librsyncmodule.c compilation, bug 1416344, thanks to Kari Hautio.

2015-02-08  Kenneth Loafman  <kenneth@loafman.com>

    * Fix spelling error in manpage, bug 1419314.

2015-02-01  Kenneth Loafman  <kenneth@loafman.com>

    * Misc fixes for the following PEP8 issues:
      - E401
      - see http://pep8.readthedocs.org

2015-01-31  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~aaron-whitehouse/duplicity/bug_932482_trailing_slashes_and_wildcards_error
      - Added functional and unit tests to show Bug #932482 - that selection does
        not work correctly when excludes (in a filelist or in a commandline option)
        contain both a single or double asterisk and a trailing slash.
    * Misc fixes for the following PEP8 issues:
      - E231, E241, E251, E261, E262, E271, E272, E301, E302, E303, E502,
        E701, E702, E703, E711, E721, W291, W292, W293, W391
      - see http://pep8.readthedocs.org
    * Fixes for 2to3 issues

2015-01-29  Kenneth Loafman  <kenneth@loafman.com>

    * Ongoing pep8 corrections.
    * Merged in lp:~angusgr/duplicity/exclude-older-than
      - Add "--exclude-older-than" commandline option, that allows you to only
        back up files with a modification date newer than a particular threshold.
    * Merged in lp:~aaron-whitehouse/duplicity/bug_884371_asterisks_in_includes
      - Added tests to unit/test_selection.py and funtional/test_selection.py
        to show the behaviour reported in Bug #884371, i.e. that selection is
        incorrect when there is a * or ** on an include line of a filelist or
        commandline --include.

2015-01-22  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug # 1414418
      - Aligned commandline.py options and help display contents.
      - Aligned commandline.py options and manpage contents.
    * Changed --s3_multipart_max_timeout to --s3-multipart-max-timeout to be
      consistent with commandline option naming conventions.
    * Applied patch from Adam Reichold to fix bug # 1413792.

2015-01-22  Kenneth Loafman  <kenneth@loafman.com>

    * Misc fixes for the following PEP8 issues:
      - E127, E128, E201, E202, E203
      - see http://pep8.readthedocs.org

2015-01-18  Kenneth Loafman  <kenneth@loafman.com>

    * Misc fixes for the following PEP8 issues:
      - E111, E121, E122, E124, E125, E126
      - see http://pep8.readthedocs.org

2015-01-17  Kenneth Loafman  <kenneth@loafman.com>

    * Remove 'gs' and 's3+http' from uses_netloc[].  Fixes Bug 1411803.

2015-01-15  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed variable typo in commandline.py that was causing build fails.
    * Merged in lp:~duplicity-team/duplicity/po-updates

2015-01-13  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~noizyland/duplicity/fix_azurebackend_container_names
      - Azure Backend examples have underscores in the container names.  These
        are not valid Azure container names.  The underscores have been replaced
        with hypens and a note about valid container names added to the man page.
      - Also corrects a problem where Azure Exceptions were returing unicode
        strings that were not being handled correctly.
    * Merged in lp:~user3942934/duplicity/pydrive
      - Currently duplicity uses gdocs backend for Google Drive backups.
        gdocs uses deprecated API and don't allow backups for managed Google
        accounts.  (see https://bugs.launchpad.net/duplicity/+bug/1315684)
      - Added pydrive backend that solves both of those problems. Published
        also on https://github.com/westerngateguard/duplicity-pydrive-backend.
    * Fixed some tabs/spaces problems that were causing install failures.

2015-01-13  Kenneth Loafman  <kenneth@loafman.com>

* Merged in lp:~aaron-whitehouse/duplicity/progress_option_error
  - Added test_exclude_globbing_filelist_progress_option into
    functional/test_selection.py, which shows the error reported in
    Bug #1264744 - that the --exclude-globbing-filelist does not backup
    the correct files if the --progress option is used. Test is marked as
    an expected failure so as not to cause the test suite to fail.

2015-01-12  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed some recently added 2to3 and pep8 issues.
    * Merged in lp:~vincegt/duplicity/swift_regionname
      - Fixes bug #1376628
      - Add mapping of SWIFT_REGIONNAME to select region inside SWIFT when a
        provider proposes more than one region.

2015-01-11  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~9-sa/duplicity/FixBug1408289
      - Fix bug #1408289
      - Wrong attribute name prevented raise of client exception, working now
    * Merged in lp:~noizyland/duplicity/azurebackend
      - Add backend for Azure Blob Storage Service
    * Prep for 0.7.01

2015-01-08  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~stapelberg+ubuntu/duplicity/add-onedrive-backend
      - Add a Microsoft OneDrive backend
    * Merged in lp:~hooloovoo/duplicity/filelist_select_bug_1408411
      - Adds functional test cases that fail because of Bug #1408411 (commented
        out), to assist in fixing that bug.
    * Merged in lp:~hooloovoo/duplicity/process_filelists_for_spaces_etc
      - Process filelists to remove imperfections such as blank lines, comments
        and leading/trailing whitespace. Also correctly processes quoted folders
        containing spaces in their names. Extensive unit and functional tests to
        test these changes (and selection more generally).
      - The branch does add an additional folder to testfiles.tar.gz called
        select2. This included a folder with a trailing space, to test the quote
        test. The subfolders also have clearer names than in the "select" folder
        (eg "1sub2sub3") which makes it easier to keep track of issues in tests.

2015-01-01  Kenneth Loafman  <kenneth@loafman.com>

    * Misc fixes for the following PEP8 issues:
       - E211, E221, E222, E225, E226, E228
       - see http://pep8.readthedocs.org
    * Fixed bug 1278529 by applying patch supplied in report
      - Use get_bucket() rather than lookup() on S3 to get proper error msg.

2014-12-29  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1406173 by applying patch supplied in report
      - Ignore .par2 files in remote file list
    * Removed redundant shell test testing/verify_test.sh

2014-12-28  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~hooloovoo/duplicity/add-additional-verify-tests-for-corrupted-archives
      - Add tests to test_verify.py to test that verify fails if the archive
        file is corrupted. Changed file objects to use the with keyword to ensure
        that the file is properly closed.
      - Small edit to find statement in verify_test.sh to make it work as
        expected (enclose string in quotes).
    * Merged in lp:~hooloovoo/duplicity/add-else-to-badupload-try-except
      - Badupload test previously did not have an else in the try-except. The
        test passed if the except was triggered, but would also pass if the
        test did not trigger an error at all.

2014-12-18  Kenneth Loafman  <kenneth@loafman.com>

    * Merge in lp:~hooloovoo/duplicity/test-verify-improvements
      - Fix up test_verify, which was a bit of a mess:
      - Simplify test_verify.py to just do a simple backup and verify on a
        single file in each test.
      - Modify tests to correctly use --compare-data option.
      - Add tests for when the source files have atime/mtime manipulated.
    * Fix duplicity verify to ignore the file system when globals.compare_data is
      False.  This means that verify only validates the viability of the backup
      itself unless --compare-data is specified.
    * Reenable test_verify_changed_source_file test

2014-12-17  Kenneth Loafman  <kenneth@loafman.com>

    * Merge in lp:~hooloovoo/duplicity/verify-not-check-source
      - Tests to validate that duplicity does not check filesystem source during
        verify unless --compare-data is specified
    * Merge in lp:~ed.so/duplicity/move_netloc
      - move netloc usage definitions into respective backends
      - fix "[Question #259173]: rsync backend fails"
        https://answers.launchpad.net/duplicity/+question/259173
    * Make ssh an unsupported backend scheme
    * Temporarily disable RsyncBackendTest and test_verify_changed_source_file

2014-12-12  Kenneth Loafman  <kenneth@loafman.com>

    * Source formatted, using PyDev, all source files to fix some easily fixed
      PEP8 issues. Use ignore space when comparing against previous versions.
    * Merge in lp:~andol/duplicity/signkeyformat
      - Allow --sign-key to use short format, long format alt. full fingerprint.

2014-12-11  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/paramiko.identyfile
      - fix identity file parsing of --ssh-options for paramiko
      - manpage fixes

2014-12-10  Kenneth Loafman  <kenneth@loafman.com>

    * Manually merged in lp:~m4ktub/duplicity/0.6-reliability
      - Per fix proposed in Bug #1395341.
    * Modded .bzrignore to ignore *.egg test dependencies, normalized, sorted.

2014-12-01  Kenneth Loafman  <kenneth@loafman.com>

    * Partial fix of bug 1236248 with changes by az, manpage warning about
      --extra-clean, however, recovery with missing sig files is broken.
    * Fixed bug 1255453 with changes by Gaudenz Steinlin, report backend import
      results, both normal and failed, at INFO log level.

2014-11-30  Kenneth Loafman  <kenneth@loafman.com>

    * In webdavbackend.py:
      - Fixed bug 1396106 with change by Tim Ruffing, mispelled member.
      - Added missing 'self.' before member in error message.
    * Merged in lp:~adrien-delhorme/duplicity/hubic
      - Add Hubic support through pyrax and a custom pyrax_identity module.
    * Fixed bug 1385599 with changes by Yannick Molin. SSL settings are now
      conditioned on protocol ftp or ftps.

2014-11-20  Kenneth Loafman  <kenneth@loafman.com>

    * Undid move of testing/test_code.py.  Instead I fixed it
      so that it would not run during PPA build.  It now needs
      the setting RUN_CODE_TESTS=1 in the environment which is
      supplied in the tox.ini file.

2014-11-19  Kenneth Loafman  <kenneth@loafman.com>

    * Remove valid_extension() check from file_naming.py.  It was
      causing failed tests for short filenames.  Thanks edso.
    * Moved testing/test_code.py to testing/manual/code_test.py
      so PPA builds would succeed.  Should be moved back later.

2014-11-13  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/fix.dpbx.import
      - fix dpbx import error import lazily
    * Partial fix for PPA build failures, new backend name.

2014-11-10  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/lftp.ncftp.and.prefixes
      - retire --ssh-backend, --use-scp parameters
      - introduce scheme prefixes for alternative backend selection
        e.g. ncftp+ftp://, see manpage
      - scp is now selected via scheme e.g. scp://
      - added lftp fish, webdav(s), sftp support
    * Merged in lp:~mterry/duplicity/missing-unicode-escape
      - Convert restore_dir to unicode before printing.
    * Merged in lp:~hooloovoo/duplicity/fix-typo-in-test-description
      - Fixed spelling mistake/typo in a description of a test.

2014-10-27  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/code-nits
      - Fix some pylint/pep8 nits that prevented the test_code.py test from passing.
    * Merged in lp:~mterry/duplicity/debian-dir
      - Add a debian/ directory to make it easier to manage the PPAs for duplicity.

2014-10-23  Kenneth Loafman  <kenneth@loafman.com>

    * Prep for 0.7.0
    * Merged in lp:~ed.so/duplicity/manpage.blocksize
      - add --max_blocksize doc
      - reorder 'a note on filename prefixes' into alphabetical order

2014-10-18  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~johnleach/duplicity/1315437-swift-container-create
      - Check to see if the swift container exists before trying to create it,
        in case we don't have permissions to create containers. Fixes #1315437
    * Merged in lp:~moritzm/duplicity/duplicity
      - Use lftp for both FTP and FTPS
    * Adjust unit tests to expect single FTP backend

2014-10-16  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/0.7-dpbx.importfix
      - fix this showstopper with the dropbox backend
        "NameError: global name 'rest' is not defined"

2014-10-12  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~hooloovoo/duplicity/updated-README-REPO
      - Changes to README-REPO to reflect the restructuring of the directories.
    * Merged in lp:~jflaker/duplicity/BugFix1325215
      - The reference to "--progress_rate" in the man page as a parameter is
        incorrect. Should be "--progress-rate".

2014-09-30  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug 1375304 with patch supplied by Aleksandar Ivanovic

2014-08-17  Kenneth Loafman  <kenneth@loafman.com>

    * Added sxbacked.py, Skylable backend.  Waiting on man page updates.
    * Merged in lp:~ed.so/duplicity/manpage.verify
      - Clarify verify's functionality as wished for by a user surprised with a big
        bandwidth bill from rackspace.
    * Merged in lp:~jeffreydavidrogers/duplicity/duplicity
      - This change fixes two small typos in the duplicity man page.

2014-06-28  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~3v1n0/duplicity/copy.com-backend
      - I've added a backend for Copy.com cloud storage, this supports all the
        required operations and works as it should from my tests.
      - You can use it by calling duplicity with something like:
        copy://account@email.com:your-password@copy.com/duplicity
      - The only thing I've concerns with is the optimized support for _delete_list
        which can't be enabled here because the test_delete_list tries also to
        delete a not-existing files, and it requires the backend not to raise an
        exception in that case (is this somewhat wanted or could we do the same as
        for _delete or _query?)
    * Merged in lp:~ed.so/duplicity/webdav200fix-0.7
      - webdav backend fix "BackendException: Bad status code 200 reason OK. " when
        restarting an interrupted backup and overwriting partially uploaded volumes.
    * Merged in lp:~mterry/duplicity/webdav-fixes
      - This branch fixes two issues I saw when testing the webdav backend:
      - 1) Errors like the following: "Attempt 1 failed. BackendException: File
        /tmp/duplicity-LQ1a0i-tempdir/mktemp-u2aiyX-2 not found locally after get
        from backend".  These were caused by the _get() method not calling setdata()
        on the local path object, so the rest of the code thought it didn't exist.
      - 2) Some odd issues from stale responses/data. We have a couple places in
        webdavbackend.py where we close the connection before making a request
        because of this problem. But I've changed it to do it every time, more
        reliably, by putting a _close() call inside the request() method.
      - With this, the webdav backend seems fine to me.
    * Merged in lp:~antmak/duplicity/0.7-par2-fix
      - Useful fix for verbatim par2cmdline options (like "-t" in par2-tbb version)
    * Fixed bug 1327550: OverflowError: signed integer is greater than maximum
      - Major and minor device numbers are supposed to be one byte each.  Someone
        has crafted a special system image using OpenVZ where the major and minor
        device numbers are much larger (ploop devices).  We treat them as (0,0).

2014-05-11  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/py2.6.0
      - Support python 2.6.0.
      - Without this branch, we only support python >= 2.6.5 because that's when
        python's urlparse.py module became its more modern incarnation. (I won't
        get into the wisdom of them making such a change in the middle of the
        2.6 lifecycle.)
      - Also, the version of lockfile that I have (0.8) doesn't work with python
        2.6.0 or 2.6.1 due to their implementation of
        threading.current_thread().ident returning None unexpectedly. So this
        branch tells lockfile not to worry about adding the current thread's
        identifier to the lock filename (we don't need a separate lock per thread,
        since our locking is per process).
      - I've tested with 2.6.0 and 2.7.6 (both extremes of our current support).
    * Update shebang line to python2 instead of python to avoid confusion.

2014-05-07  Kenneth Loafman  <kenneth@loafman.com>

    * Applied expat fix from edso.  See answer #12 in
      https://answers.launchpad.net/duplicity/+question/248020

2014-04-30  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/encode-exceptions
      - Because exceptions often contain file paths, they have the same problem
        with Python 2.x's implicit decoding using the 'ascii' encoding that we've
        experienced before.  So I added a new util.uexc() method that uses the
        util.ufn() method to convert an exception to a unicode string and used it
        around the place.
      - Bugs fixed: 1289288, 1311176, 1313966

2014-04-29  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/backend-unification
      - Reorganize and simplify backend code.  Specifically:
        - Formalize the expected API between backends and duplicity.  See the new
          file duplicity/backends/README for the instructions I've given authors.
        - Add some tests for our backend wrapper class as well as some tests for
          individual backends.  For several backends that have some commands do all
          the heavy lifting (hsi, tahoe, ftp), I've added fake little mock commands
          so that we can test them locally.  This doesn't truly test our integration
          with those commands, but at least lets us test the backend glue code.
        - Removed a lot of duplicate and unused code which backends were using (or
          not using).  This branch drops 700 lines of code (~20%)
          in duplicity/backends!
        - Simplified expectations of backends.  Our wrapper code now does all the
          retrying, and all the exception handling.  Backends can 'fire and forget'
          trusting our wrappers to give the user a reasonable error message.
          Obviously, backends can also add more details and make nicer error
          messages.  But they don't *have* to.
        - Separate out the backend classes from our wrapper class.  Now there is no
          possibility of namespace collision.  All our API methods use one
          underscore.  Anything else (zero or two underscores) are for the backend
          class's use.
        - Added the concept of a 'backend prefix' which is used by par2 and gio
          backends to provide generic support for "schema+" in urls -- like par2+
          or gio+.  I've since marked the '--gio' flag as deprecated, in favor of
          'gio+'.  Now you can even nest such backends like
          par2+gio+file://blah/blah.
        - The switch to control which cloudfiles backend had a typo.  I fixed this,
          but I'm not sure I should have?  If we haven't had complaints, maybe we
          can just drop the old backend.
        - I manually tested all the backends we have (except hsi and tahoe -- but
          those are simple wrappers around commands and I did test those via mocks
          per above).  I also added a bunch more manual backend tests to
          ./testing/manual/backendtest.py, which can now be run like the above to
          test all the files you have configured in config.py or you can pass it a
          URL which it will use for testing (useful for backend authors).

2014-04-26  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/py3-map-filter
      - In py3, map and filter return iterable objects, not lists. So in each case
        we use them, I've either imported the future version or switched to a list
        comprehension if we really wanted a list.

2014-04-25  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed bug #1312328 WebDAV backend can't understand 200 OK response to DELETE
      - Allow both 200 and 204 as valid response to delete

2014-04-20  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/more-test-reorg
      - Here's another test reorganization / modernization branch. It does the
        following things:
        - Drop duplicity/misc.py. It is confusing to have both misc.py and util.py,
          and most of the code in misc.py was no longer used. I moved the one
          function that was still used into util.py.
        - Consolidated the various ways to run tests into just one. I made tox runs
          go through ./setup.py test, rather than nosetests. And I made the
          ./testing/run-tests scripts just call tox. Now we no longer need nosetests
          as a test dependency (although you can still use it if you want).
        - Added two more code quality automated tests: a pep8 one and a pylint one.
          I disabled almost all checks in each program that gave a warning. These
          tests just establish a baseline for future improvement.
        - Moved the test helper code into TestCase subclasses that all tests can
          use. And used more code sharing and setUp/tearDown cleverness to remove
          duplicated code.
        - Reorganized the tests in ./testing/tests into ./testing/functional and
          ./testing/unit -- for whether they drive duplicity as a subprocess or
          whether they import and test code directly. Each dir can have specialized
          TestCase subclasses now.
        - Renamed the files in ./testing/unit to more clearly indicate which file
          in ./duplicity they are unit testing.
        - Added some helper methods for tests to set environment and globals.*
          parameters more safely (i.e. without affecting other tests) by
          automatically cleaning up any such changes during test tearDown.
        - Removed test_unicode.py, since it is kind of dumb. It used to be more
          useful, but now with py2.6, we are just testing that one line of code
          in it is actually there.

2014-04-19  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/2.6isms
      - Here's a whole stack of minor syntax modernizations that will become
        necessary in python3. They all work in python2.6.
      - I've added a new test to keep us honest and prevent backsliding on these
        modernizations. It runs 2to3 and will fail the test if 2to3 finds anything
        that needs fixing (with a specific set of exceptions carved out).
      - This branch has most of the easy 2to3 fixes, the ones with obvious and
        safe syntax changes.
      - We could just let 2to3 do them for us, but ideally we use 2to3 as little
        as possible, since it doesn't always know how to solve a given problem.
        I will propose a branch later that actually does use 2to3 to generate
        python3 versions of duplicity if they are requested. But this is a first
        step to clean up the code base.
    * Merged in lp:~mterry/duplicity/drop-static
      - Drop static.py.
      - This is some of the oldest code in duplicity! A bzr blame says it is
        unmodified (except for whitespace / comment changes) since revision 1.
      - But it's not needed anymore. Not really even since we updated to python2.4,
        which introduced the @staticmethod decorator. So this branch drops it and
        its test file.
    * Merged in lp:~mterry/duplicity/encode-for-print
      - Encode translated strings before passing them to 'print'.
      - The print command can only apparently handle bytes. So when we pass it
        unicode, it freaks out. There were only four instances I saw where we used
        print, so I figured it was easiest to just convert them to use the log
        framework too.
      - That way all user-visible strings go through that framework and are subject
        to the same encoding rules.

2014-04-17  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~fredrik-loch/duplicity/duplicity-S3-SSE
      - Adds support for server side encryption as requested in Bug #996660
    * Merged in lp:~mterry/duplicity/consolidate-tests
      - Consolidate all the duplicity-running code in the test framework.
      - This takes the four test files [1] that run duplicity itself (i.e. the
        high-level functional test files) and consolidates their code. Before, it
        was madness. Each one had its own run_duplicity method, with its own
        slightly tweaked features. This should reduce a lot of duplication.
      - [1] cleanuptest.py, finaltest.py, restarttest.py, and badupload.py
    * Merged in lp:~mterry/duplicity/modern-testing
      - Enable/use more modern testing tools like nosetests and tox as well as more
        common setup.py hooks like test and sdist.
      - Specifically:
        * move setup.py to toplevel where most tools and users expect it
        * Move and adjust test files to work when running "nosetests" in toplevel
          directory. Specifically, do a lot more of the test setup in
          tests/__init__.py rather than the run-tests scripts
        * Add small tox.ini file for using tox, which is a wrapper for using
          virtualenv. Only enable for py26 and py27 right now, since modern
          setuptools dropped support for <2.6 (and tox 1.7 recently dropped <2.6)
        * Add setup.py hooks for test and sdist which are both standard targets
          (sdist just outsources to dist/makedist right now)
    * Merged in lp:~mterry/duplicity/require-2.6
      - Require at least Python 2.6.
      - Our code base already requires 2.6, because 2.6-isms have crept in. Usually
        because we or a contributor didn't think to test with 2.4. And frankly,
        I'm not even sure how to test with 2.4 on a modern system.
    * Merged in lp:~mterry/duplicity/drop-u1
      - Ubuntu One is closing shop. So no need to support a u1 backend anymore.
    * Merged in lp:~mterry/duplicity/fix-drop-u1
      - Looks like when the drop-u1 branch got merged, its conflict got resolved
        badly. Here is the right version of backend.py to use (and also drops
        u1backend.py from POTFILES).
    * Merged in lp:~mterry/duplicity/drop-pexpect
      - Drop our local copy of pexpect in favor of a system version.
      - It's only used by the pexpect ssh backend (and if you're opting into that,
        you probably can expect that you will need pexpect) and the tests.
      - I've done a quick smoketest (backed up and restored using
        --ssh-backend=pexpect) and it seemed to work fine with a modern version
        of pexpect.

2014-03-10  Kenneth Loafman  <kenneth@loafman.com>

     * Merged in lp:~germer/duplicity/par2
      - This branch adds Par2 recovery files to duplicity. It is a wrapper backend
        which will create the recovery files and upload them all together with the
        wrapped backend. Corrupt archives will be detected and repaired (if
        possible) on the fly during restore.
      - It can be used with url-string par2+webdavs://USER@HOST/PATH
      - Fixes https://bugs.launchpad.net/duplicity/+bug/426282

2014-03-06  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/fix.dpbx
      - Fix dpbx backend "NameError: global name 'rest' is not defined"
    * Merged in lp:~prateek/duplicity/botoimportfix
      - Switches the boto backend back to using lazy imports so there are no
        complaints during the importing of backends.

2014-02-26  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~prateek/duplicity/s3-glacier
      - Fixes https://bugs.launchpad.net/duplicity/+bug/1039511
        - Adds support to detect when a file is on Glacier and initiates a restore
          to S3. Also merges overlapping code in the boto backends
      - Fixes https://bugs.launchpad.net/duplicity/+bug/1243246
        - Adds a --s3_multipart_max_timeout input option to limit the max execution
          time of a chunked upload to S3. Also adds debug message to calculate
          upload speed.

2014-02-24  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/pexpect-fix
      - duplicity has its own copy of pexpect. Use that instead of requiring one
        from the system.

2014-02-05  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/gpg-encode
      - getpass.getpass(prompt) eventually calls str(prompt). Which is a no go,
        if the prompt contains unicode. Here's a patch to always pass getpass() a
        byte string.
      - Our tests didn't catch this because they always set PASSPHRASE. I've added
        a test that passes the passphrase via stdin.

2014-01-31  Kenneth Loafman  <kenneth@loafman.com>

    * Applied two patches from mailing list message at:
      https://lists.nongnu.org/archive/html/duplicity-talk/2014-01/msg00030.html
      "Added command line options to use different prefixes for manifest/sig/archive files"
      This resolves https://bugs.launchpad.net/duplicity/+bug/1170161 and provides
      a workaround for https://bugs.launchpad.net/duplicity/+bug/1170113

2014-01-24  Kenneth Loafman  <kenneth@loafman.com>

    * Prep for 0.6.23 release.

2014-01-17  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~louis-bouchard/duplicity/add-allow-concurrency
      - Implement locking mechanism to avoid concurrent execution under the same
        cache directory. This is the default behavior.
      - Also implement --alllow-concurrency option to disable the locking
        if required.
      - This functionality adds a dependency to python-lockfile

2014-01-13  Kenneth Loafman  <kenneth@loafman.com>

    * Restored patch of gdocsbackend.py from original author (thanks ede)
    * Applied patch from bug 1266753: Boto backend removes local cache if
      connection cannot be made

2014-01-02  Kenneth Loafman  <kenneth@loafman.com>

    * Restored missing line from patch of gdocsbackend.py
    * Reverted changes to gdocsbackend.py

2013-12-30  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/encoding
      - This branch hopefully fixes two filename encoding issues:
      - Users in bug 989496 were noticing a UnicodeEncodeError exception which
        happens (as far as I can tell) because some backends (like webdav) are
        returning unicode filenames from list(). When these filenames are combined
        with the utf8 translations of log messages, either (A) the default ascii
        encoding can't handle promoting the utf8 bytes or -- if there aren't any
        utf8 bytes in the translation -- (B) the resulting unicode string raises
        an error later when log.py tries to upgrade the string again to unicode
        for printing.
      - This fix is largely implemented by adding a wrapper for backend list()
        implementations. This wrapper ensures that duplicity internals always see
        a byte string. (I'd like to eventually use this same wrapping strategy to
        implement generic retry support without backends having to add any logic,
        but that's just a thought for the future.)
      - That is, the fix for issue #1 is completely inside backend.py and the
        changes to backends/*.py.
      - The rest of the invasive changes deal with filenames that may not be valid
        utf8. This is much rarer, but possible. For proper handling of this, we
        need to print using unicode, and convert filenames from the system filename
        encoding to unicode, gracefully handling conversion errors. Some of the
        filenames we print are remote names. Who knows what encoding they are in;
        it could be different than the system filename encoding. 99% of the time,
        everything will be utf8 and we're fine. If we do get conversion errors,
        the only effect should be some question mark characters in duplicity
        logging output.
      - I tried to convert as much of the actual codebase to use unicode for
        printing. But I stopped short of adding an assert in log.py to enforce
        unicode, because I didn't want to go through all the backend code and
        manually adjust those bits without being able to test each one.

2013-12-28  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~verb/duplicity/boto-min-version
      - Update documentation and error messages to match the current actual version
        requirements of boto backend.
    * Merged in changes from main trunk.
    * Merged in lp:~ed.so/duplicity/debian.paramiko.log
      - upstream debian patch "paramiko logging"
        http://patch-tracker.debian.org/package/duplicity/0.6.22-2
    * Merged in lp:~ed.so/duplicity/debian.dav.mkdir
      - upstream debian patch "webdav create folder recursively"
        http://patch-tracker.debian.org/package/duplicity/0.6.22-2
    * Nuke tabs

2013-11-24  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~jkrauss/duplicity/pyrax
      - Rackspace has deprecated python-cloudfiles in favor of their pyrax
        library, which consolidates all Rackspace Cloud API functionality into
        a single library.  Tested it with Duplicity 0.6.21 on both Arch Linux
        and FreeBSD 8.3.0.
    * Changed to default to pyrax backend rather than cloudfiles backend.
      To revert to the cloudfiles backend use '--cf-backend=cloudfiles'

2013-11-19  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patch to fix "Access GDrive through gdocs backend failing"
      - see https://lists.nongnu.org/archive/html/duplicity-talk/2013-07/msg00007.html

2013-11-17  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~verb/duplicity/bucket_root_fix
      - Fix bug that prevents backing up to the root of a bucket with boto backend.
    * Merged in lp:~gliptak/duplicity/415619
      - Better error message when chown fails
    * Merged in lp:~mterry/duplicity/log-path-type
      - Any backup browser built on top of duplicity will need to indicate which
        files in the backup are folders and which are files. The current logging
        information doesn't provide this detail. So I've added a field to the
        log.InfoCode.file_list output that includes the path type.
    * Merged in lp:~mterry/duplicity/manifest-oddities
      - We may accidentally end up with an oddly inconsistent manifest like so:
        Volume 1
        Volume 2
        Volume 3
        Volume 2
        As did get reported recently on the mailing list:
        http://lists.nongnu.org/archive/html/duplicity-talk/2013-11/msg00009.html
      - One way this can happen (the only way?) is if you back up, then duplicity
        gets interrupted between writing the manifest and uploading the volume.
        Then, when restarted, there is no longer enough data to create as many
        volumes as existed previously.
      - This situation can cause an exception when trying to restart the backup.
      - This branch fixes it by deleting any excess volume information encountered
        when loading in the manifest. We discard volume with higher numbers
        than the last one read.
    * Merged in lp:~mterry/duplicity/disappearing-source
      - When restarting a backup, we may accidentally skip the first chunk of one of
        the source files. To reproduce this,:
        1) interrupt a backup
        2) delete the source file it was in the middle of
        3) restart the backup
      - When replaying the source iterator to find where to resume from, we can't
        notice that the file is gone until we've already iterated past where it
        would be!
      - The solution I came up with is to just let duplicity stuff the data we
        accidentally read back into the source iterator.
      - This is actually a data loss bug, because it's possible to back up
        corrupted files (that are missing their first chunk).
    * Merged in lp:~mterry/duplicity/normalize-before-using
      - Avoid throwing an exception due to a None element in a patch sequence.
      - None elements in a (non-normalized) patch sequence are perfectly normal.
        With the current code in the patched function, it is certainly possible to
        hit a crash due a None.
        See http://lists.nongnu.org/archive/html/duplicity-talk/2013-11/msg00005.html
      - This branch fixes that by normalizing the sequence before using it in the
        logging code. It's acceptable to bring the normalize_ps() call outside the
        try/except block because normalize_ps is not expected to throw. It's
        relatively simple and doesn't really use its objects besides checking if
        they are None.

2013-09-23  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/catch-seq-copy-error
      - Any* exception when running patch_seq2ropath should be ignored (though
        logged) and duplicity should move on. This covers the two asserts in that
        function (bug 1155345 and bug 720525) as well as errors that happen during
        file copying (bug 662442).
    * Merged in lp:~mterry/duplicity/argv
      - Fix use of argv when calling os.execve

2013-09-14  Kenneth Loafman  <kenneth@loafman.com>

    * Merged lp:~mterry/duplicity/ignore-missing to fix patch below.

2013-09-13  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patch from bug 1216921 to fix ignore_missing().

2013-08-17  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~scowcron/duplicity/ftp_password_pexpect
      - Use common backend.Backend get_password() rather than _ssh_pexpect.py specific code.
    * Merged in lp:~mhu-s/duplicity/swiftbackend
      - This branch adds support for Swift, the OpenStack Object Storage service. See
        https://blueprints.launchpad.net/duplicity/+spec/swiftbackend
    * Merged in lp:~verb/duplicity/boto-gcs
      - These patches add support for Google Cloud Storage via the boto backend.
      - boto has supported GCS in interoperability mode for a few years now. This change
        adds support by taking advantage of boto's storage_uri abstraction layer.
    * Merged in lp:~ckornacker/duplicity/megacloud
      - Add support for Mega (mega.co.nz) backend.
    * Applied patch from Eric S Raymond to man page to fix markup problems.
    * Merged in lp:~ed.so/duplicity/man.page
      - update paramiko links
      - add command parameters to synopsis
      - add --compare-data
      - some polishing and several improvements

2013-04-27  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~tblue/duplicity/paramiko-1.10.0
      - This fixes bug #1156746, making the Paramiko backend compatible with
        Paramiko 1.10.0. It keeps compatibility with older Paramiko versions.
    * Merged in lp:~townsend/duplicity/fix-1161599-2
      - The fix in revno. 912 didn't take into account that the parameter "body"
        passed into request() is overloaded, so when it was NULL or of a type other
        than file, it would fail.  This checks if "body" is of type "file" before
        actually seek()'ing back to the beginning of the file.
    * Merged in lp:~tblue/duplicity/paramiko-fix-delete-retry
      - This fixes bug #1115715, which is really annoying. Basically it makes
        using the Paramiko backend with the default settings impossible.
    * Merged in lp:~juan-f/duplicity/progress
      - From time ago, there are people asking for a progress bar estimation in duplicity.
        There is even a script that circumvents the issue, getting info from the log so as
        to estimate the progress status ( https://github.com/quentin/Duplicity-progress )
        but does not give enough feedback and the estimation is rather plain.
      - I have developed a set of heuristics that gather information from the deltas and
        the transfer ratios of the backend so as to forecast % of progress, estimation of
        remaining time and average speed, for both full and incremental backup uploads.
      - The current implementation works for boto backend, but to port the other backends
        to use this feature would be quite easy (we can discuss the details if interested).
      - The algorithm is activated by the --progress command line flag, and will perform a
        first-pass dry-run to collect evidence for all the deltas. Next it will trigger the
        real upload, while a thread statistically estimates the ratio of changes and
        compression for the data in/out, and uses these ratios to forecast time remaining
        and % of completion.
      - The progress data will be logged each 3 seconds, or the --progress-rate flag.
    * Merged in lp:~jnoster/duplicity/dpbx-added
      - The application key was approved as "production" one after some changes to the code
        to suit the requirements of Dropbox team (the keys are now obfuscated, for instance).
    * Applied blocksize.patch from https://bugs.launchpad.net/duplicity/+bug/897423
      - New option --max-blocksize (default 2048) to allow increasing delta blocksize.
    * Applied duplicity-ftps.patch from https://bugs.launchpad.net/duplicity/+bug/1104069
      - Don't try to delete an empty file list.

2013-02-17  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patches from Laszlo Ersek to rdiffdir to "consume a chain of sigtar
      files in rdiffdir delta mode" which supports incremental sigtar files.
    * Merged in lp:~jnoster/duplicity/dpbx-added
      - Add Dropbox backend
      - NB! In order to use the backend one must:
        1. Install Dropbox Python SDK first.
        2. Run the duplicity with Dropbox backend (dpbx://) first time
           *interactively* to catch and follow the oAuth URL.
    * Merged in lp:~ed.so/duplicity/verify.data
      - add switch --compare-data, to selectively enable formerly always disabled
        data comparison on verify runs

2013-01-18  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~duplicity-team/duplicity/po-updates
      - Updated translations
    * Prep for 0.6.21 release

2013-01-18  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/webdav.fix-retry
      - added ssl certificate verification (see man page)
      - more robust retry routine to survive ssl errors, broken pipe errors
      - added http redirect support
    * Merged in lp:~ed.so/duplicity/webdav.manpage
      - explanation of webdav changes above
    * Merged in lp:~mterry/duplicity/pygi
      - Python bindings for the gobject stack (used in the gio backend) have changed
        from static to dynamically-generated bindings. The old static bindings are
        deprecated. So here's a branch to change the gio backend from old to new ones.
    * Merged in lp:~mterry/duplicity/py3rsync
      - This branch lets one build the _librsync module with Python 3. You can't
        really do anything useful with it, but it's a nicely-isolated piece to add
        Python 3 support for.
      - The changes are a mix of modernization and #ifdef logic.
      - All tests still pass in Python 2.7 and 2.4. I tested manually that the module
        worked as expected in Python 3.

2013-01-07  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/static-corruption
      - This branch fixes three possible ways a backup could get data-corrupted.
        Inspired by bug 1091269.
          A) If resuming after a volume that ended in a one-block file, we would
             skip the first block of the next file.
          B) If resuming after a volume that ended in a multi-block file, we would
             skip the first block of the next file.
          C) If resuming after a volume that spanned a multi-block file, we would
             skip some data inside the file.
      - A and B are because when finding the right place in the source files to
        restart the backup, the iteration loop didn't handle None block numbers
        very well (which are used to indicate the end of a file).
      - C is what bug 1091269 talks about. This was because data block sizes would
        get smaller as the difftar file got closer and closer to the volsize.
        Standard block sizes were 64 * 1024.  But say we were close to the end of
        the difftar... When resuming, duplicity doesn't know the custom block sizes
        used by the previous run, so it uses standard block sizes. And it doesn't
        always match up, as you can imagine. So we would leave chunks of data out
        of the backed up file.
      - Tests added for these cases.
      - This branch is called 'static-corruption' because all these issues occur
        even when the source data doesn't change. I still think there are some
        corruption issues when a file changes in between duplicity runs. I haven't
        started looking into that yet, but that's next on my list.
      - C only happened without encryption (because the gpg writer function already
        happened to force a constant data block size). A and B happened with or
        without encryption.

2013-01-02  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed 1091269 Data corruption when resuming with --no-encryption
      - Patches from Pascual Abellan that make block size consistent and
        that add no-encryption option to manual-ctrl-c-test.sh.
      - Modified gpg.py patch to use 64k block size so unit test passes.

2013-01-01  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/u1_and_manpage
      - Manpage
        - document Ubuntu One required python libs
        - added continuous contributors and backend author notes
      - U1backend
        - lazily import non standard python libs, fixes
        http://article.gmane.org/gmane.comp.sysutils.backup.duplicity.general/5753
        - fix "not bytearray" prevents PUT with python 2.6
        - don't hang after putting in credentials (cause it silently retries in background)
          but go through with backup

2012-12-22  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/webdav.fix-retry
      - bugfix: webdav retrying broke on ERRORS like "error: [Errno 32] Broken pipe" in
        socket.pyas reported here https://answers.launchpad.net/duplicity/+question/212966
        added a more generalized 'retry_fatal' decorator which makes retrying backend
        methods even easier
    * Merged in lp:~ed.so/duplicity/manpage
      - Clear up PASSPHRASE reusage as sign passphrase.  Minor fixes.

2012-12-17  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~lenharo-h/duplicity/duplicity
      - Generate encrypted backups without revealing the user's key id
        via option --hidden-encrypt-key
    * Merged in lp:~mterry/duplicity/u1-utf8
      - Make sure u1backend returns filenames as utf8
    * Merged in lp:~carlos-abalde/duplicity/gdocs-backend-gdata-2.0.16.-upgrade
      - Upgrade of GoogleDocs backend to python gdata lib >= 2.0.15:
        Stop using get_everything method.

2012-11-19  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/lftp.netrc
      - Allow .netrc auth for lftp backend
    * Merged in lp:~mterry/duplicity/946988
      - This fixes bug 946988 by not duplicating the checks for when we should ask
        for the password (those same checks are done more correctly inside
        get_passphrase). And add a test to reproduce the bug.

2012-11-10  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~satwell/duplicity/caching
      - Add a cache for password and group lookups. This significantly improves
        runtime with very large password and group configurations.
    * Merged in lp:~ed.so/duplicity/manpage
      - more formatting fixes, clarifications in sections EXAMPLES, FILE SELECTION

2012-11-03  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/u1-oauthlib
      - As the Ubuntu packager for duplicity, I would prefer u1backend.py
        used oauthlib instead of oauth.  oauthlib is well maintained upstream
        (unlike oauth), has a python3 port (for the future), and is in Ubuntu
        main (so is oauth right now, but hopefully in the future we can drop
        it to universe, in which case duplicity can't use it anymore).
    * Merged in lp:~mterry/duplicity/delete-new-sig-in-cache
      - In duplicity 0.6.20, we fixed bug 1031269. This means that we no longer
        leave sig files on the remote location.  Leaving sig files on the remote
        location also caused a bug with deleting cache files. Code used to leave
        remote new-sig but delete the locale cache new-sig; this meant that we would
        keep downloadoing the new-sig all the time from remote. We had worked around
        that by just not deleting the new-sig in the cache, which was sort of the
        wrong side of that problem to tackle.  Now that we handle the remote
        new-sigs better (by deleting them), I don't think we need this code anymore.
        Patch by az@debian.org.
    * Merged in lp:~mterry/duplicity/u1-ascii-error
      - Fix for u1backend unicode error.  Patch by Paul Barker.


2012-10-29  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/24syntaxfix
      - fix python 2.4 vs 2.5 syntax error

2012-10-28  Kenneth Loafman  <kenneth@loafman.com>

    * Remove dist/mkGNUchangelog script.
    * Prep files for 0.6.20 release.

2012-10-27  Kenneth Loafman  <kenneth@loafman.com>

    * Applied patch from az for bug #1066625 u1backend
      - add delay between retries

2012-10-25  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~mterry/duplicity/u1-402
      - Switch the code we check for out-of-space in u1backend.

2012-10-25  Michael Terry  <michael.terry@canonical.com>

    u1backend: interpret http code 402 as no-space-left rather than 507

2012-10-17  Kenneth Loafman  <kenneth@loafman.com>

    Update CHANGELOG and Changelog.GNU

2012-10-17  Kenneth Loafman  <kenneth@loafman.com>

    1039001 --exclude-if-present and --exclude-other-filesystems causes crash with inaccessible other fs

2012-10-17  Kenneth Loafman  <kenneth@loafman.com>

    995851 doc improvement for --encrypt-key, --sign-key

2012-10-17  Kenneth Loafman  <kenneth@loafman.com>

    Update Changelog.GNU

2012-10-17  Kenneth Loafman  <kenneth@loafman.com>

    1066625 ubuntu one backend does not work without gnome/dbus/x11 session

2012-10-16  Kenneth Loafman  <kenneth@loafman.com>

    Updated Changelog.GNU

2012-10-16  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/ssh.manpage
      - added gdocs and rsync REQUIREMENTS
      - added cloudfiles documentation

2012-10-16  ede

    added gdocs, rsync REQUIREMENTS

2012-10-13  ede

    some refinements
    add cloudfiles documentation

2012-10-03  ede

    sort urls alphabetically
    add abs vs. relative file urls

2012-10-03  ede

    typo

2012-10-03  ede

    minor fix

2012-10-03  ede

    some clarifications mostly for ssh pexpect backend

2012-10-16  Kenneth Loafman  <kenneth@loafman.com>

    Update Changelog.GNU

2012-10-16  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/gpginterface
      - refactor GnuPGInterface to gpginterface.py
        reasoning can be found in README

2012-10-15  ede

    some clarifications in README

2012-10-15  ede

    refactor GnuPGInterface to gpginterface.py
    reasoning can be found in README

2012-10-07  Kenneth Loafman  <kenneth@loafman.com>

    Update Changelog.GNU

2012-10-07  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/gpg.tmp
      - place gpg.py tempfiles in duplicity's tmp subfolder which is cleaned
        whatever happens

2012-10-07  ede

    place gpg.py tempfiles in duplicity's tmp subfolder which is cleaned whatever happens

2012-10-02  Michael Terry  <michael.terry@canonical.com>

    tests: apparently on hardy chroots, /bin can be smaller than 3MB compressed, so instead of using /bin in test_multi_volume_failure, use largefiles

2012-10-02  Michael Terry  <michael.terry@canonical.com>

    tests: whoops, I had accidentally disabled one of the new tests for ignoring double entries in a tarball

2012-10-02  Michael Terry  <michael.terry@canonical.com>

    tests: don't use subprocess.check_output, which was only added in Python 2.7

2012-09-30  Michael Terry  <michael.terry@canonical.com>

    don't use unittest.TestCase.assertSetEqual, which isn't supported in older Python versions

2012-09-30  Kenneth Loafman  <kenneth@loafman.com>

    Update Changelog.GNU

2012-09-30  Kenneth Loafman  <kenneth@loafman.com>

    * Merged in lp:~ed.so/duplicity/ssh-pexpect-msgbug
      - Fixes 'UnboundLocalError: local variable 'msg' referenced before assignment'
        in _ssh_pexpect.py

2012-09-30  ede

    probably fix

    File "/usr/local/lib/python2.7/dist-packages/duplicity/backends/_ssh_pexpect.py", line 223, in run_sftp_command
    log.Warn("Running '%s' with commands:\n %s\n failed (attempt #%d): %s" % (commandline, "\n ".join(commands), n, msg))
    UnboundLocalError: local variable 'msg' referenced before assignment

2012-09-29  Kenneth Loafman  <kenneth@loafman.com>

    Wrap CHANGELOG to col 80.

2012-09-29  Kenneth Loafman  <kenneth@loafman.com>

    Update Changelog.GNU

2012-09-29  Kenneth Loafman  <kenneth@loafman.com>

    - Merged in lp:~mterry/duplicity/ropath.index
    + This branch does two main things:
    1) Skips base dir entries when compiling the list of deleted delta iters.
    (this gracefully recovers from the sort of situations that lead to bug
    929067). I'm reasonably confident this is an uninvasive change, but
    please confirm.
    2) Overwrites the sigtar file on backup-restart. This is because AFAICT,
    duplicity will rewrite the entire sigtar each restart. But we were
    opening the sigtar file as "ab", so we'd just dump the contents on top
    of the previous contents. Which was causing some confusion in bug 929067.
    If I'm wrong that we don't always rewrite the entire sigtar each time,
    this needs some rethink. Please also confirm that.
    + In addition, I added two tests for the above two changes and make some
    improvements elsewhere in the restarttest.py file while I was at it.

2012-09-28  Michael Terry  <michael.terry@canonical.com>

    gracefully handle multiple duplicate base dir entries in the sigtar; avoid writing such entries out

2012-09-29  Kenneth Loafman  <kenneth@loafman.com>

    - Merged in lp:~gregretkowski/duplicity/cf-retry-delete
    + This will retry cloudfile delete commands. With large numbers of archive
    files over mediocre links transient network errors will occasionally cause
    deletes to fail and these should be retried.

2012-09-27  Greg Retkowski  <greg@thud.pao.int.nebula.com>

    Retry cloudfiles deletes

    This will retry cloudfile delete commands with large numbers of
    archive files over mediocre links deletes occasionally fail
    and should be retried.

2012-09-29  Kenneth Loafman  <kenneth@loafman.com>

    - Merged in lp:~ed.so/duplicity/duplicity.manpage
    + disabled hyphenation and block justification for better readablility of command line examples.
    + reformatted REQUIREMENTS section for hopefully better online rendering
    + minor clarifications

2012-09-21  ede

    missing space

2012-09-21  ede

    - disabled hyphenation and block justification for better readablility of command line examples.
    - reformatted REQUIREMENTS section for hopefully better online rendering
    - minor clarifications

2012-09-29  Kenneth Loafman  <kenneth@loafman.com>

    - Merged in lp:~mterry/duplicity/leftover-sigtar
    + So currently, duplicity does not delete signature files when doing a remove-all-but-n operation. Seems wrong, since those signature files are now useless and take up space.
    + This branch does several things:
    1) Make remove-all-but-n operate on chains. In practice it did before, since the sets it operated on always came from complete chains (i.e. it never used only some of the sets from a chain)
    2) Add a new method to get all signature chains before a certain time.
    3) Use this new method to also delete signature chains during remove-all-but operations.
    + And it cleans up the cleanuptest.py file:
    1) Removes crufty, unused code
    2) Disallows changing the destination folder for the test, which no one would ever want to do and isn't really supported anyway
    3) Add some additional checks to the existing test
    4) Adds two new methods to test remove-all-but-n and remove-all-inc-of-but-n-full

2012-09-19  Michael Terry  <michael.terry@canonical.com>

    delete signature files when doing remove-all-but

2012-09-29  Kenneth Loafman  <kenneth@loafman.com>

    - Merged in lp:~mterry/duplicity/1031277
    + ssh: actually delete all the requested files, not just the first one

2012-09-19  Michael Terry  <michael.terry@canonical.com>

    ssh: actually delete all the requested files, not just the first one

2012-09-13  Kenneth Loafman  <kenneth@loafman.com>

    Update Changelog.GNU and CHANGELOG.

2012-09-13  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/utf8-po.

2012-09-13  Michael Terry  <michael.terry@canonical.com>

    make sure translations are in utf-8

2012-09-12  Kenneth Loafman  <kenneth@loafman.com>

    Fix dates.

2012-09-12  Kenneth Loafman  <kenneth@loafman.com>

    Update CHANGELOG and Changelog.GNU to reflect recent changes.
    Update location path in mkGNUChangelog.sh.

2012-09-11  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/duplicity.tmpspacefix

2012-09-11  edso

    use tempfile.TemporaryFile() so unused temp files are deleted automagically

2012-09-10  edso

    propbably solve bug 'Out of space error while restoring a file'
    see bug tracker/mailing list
    https://bugs.launchpad.net/duplicity/+bug/1005901
    http://lists.gnu.org/archive/html/duplicity-talk/2012-09/msg00000.html

2012-09-11  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/duplicity.helpfix

2012-09-10  edso

    fix rare 'TypeError: encode() argument 1 must be string, not None'
    read here
    http://lists.nongnu.org/archive/html/duplicity-talk/2012-09/msg00016.html

2012-06-21  Michael Terry  <michael.terry@canonical.com>

    log.py: add a couple comments to reserve error codes 126 and 127 because they conflict with running duplicity under pkexec (very similar to how 255 is reserved because gksu uses it)

2012-05-18  Kenneth Loafman  <kenneth@loafman.com>

    Add note on GnuPGInterface and multiple GPG processes.

2012-05-16  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/backend_fixes

    - fixed ssh/gio backend import warnings
    + ssh paramiko backend imports paramiko lazily now
    + gio backend is not imported automatically but on request when --gio option is used
    - added a warning when --ssh-backend is used with an incorrect value

2012-05-16  edso

    - fixed ssh/gio backend import warnings
    + ssh paramiko backend imports paramiko lazily now
    + gio backend is not imported automatically but on request when --gio option is used
    - added a warning when --ssh-backend is used with an incorrect value

2012-05-15  Kenneth Loafman  <kenneth@loafman.com>

    Update changelogs, remove misleading date.

2012-05-15  Kenneth Loafman  <kenneth@loafman.com>

    Merged  in  lp:~ed.so/duplicity/ssh-fixes

    - ssh paramiko backend respects --num-retries now
    - set retry delay for ssh backends to 10s
    - ssh pexpect backend
    + sftp part does not claim 'Invalid SSH password' although it's only 'Permission denied' now
    + sftp errors are now more talkative
    - gpg.py
    + commented assert which broke otherwise working verify run

2012-05-15  edso

    - ssh paramiko backend respects --num-retries now
    - set retry delay for ssh backends to 10s
    - ssh pexpect backend
    + sftp part does not claim 'Invalid SSH password' although it's only 'Permission denied' now
    + sftp errors are now more talkative
    - gpg.py
    + commented assert which broke otherwise working verify run

2012-05-15  edso

    - ssh paramiko backend respects --num-retries now
    - set retry delay for ssh backends to 10s
    - ssh pexpect backend
    + sftp part does not claim 'Invalid SSH password' although it's only 'Permission denied' now
    + sftp errors are now more talkative
    - gpg.py
    + commented assert which broke otherwise working verify run

2012-03-24  Kenneth Loafman  <kenneth@loafman.com>

    A couple more warning error codes that Deja Dup is interested in noticing.

2012-03-21  Michael Terry  <michael.terry@canonical.com>

    add a couple more warning codes for machine consumption of warnings

2012-03-24  Kenneth Loafman  <kenneth@loafman.com>

    If the gio backend wants to ask a question during its mount phase, it previously just aborted. This branch allows it to continue, though not to make an intelligent answer.

    Only two gvfs daemons ask questions: 'sftp' does for new hosts, and 'afc' does for locked device. In both cases, the 0 choice is the 'just keep going' choice.

2012-03-19  Michael Terry  <michael.terry@canonical.com>

    allow answering gio mount questions (albeit naively)

2012-03-13  edso

    Merged in lp:~ed.so/duplicity/0.6-readd_sshpexpect
    - readd ssh pexpect backend as alternative
    - added --ssh-backend parameter to switch between paramiko,pexpect
    - manpage
    -- update to reflect above changes
    -- added more backend requirements
    - Changelog.GNU removed double entries

2012-03-13  edso

    add missing files

2012-03-13  edso

    - readd ssh pexpect backend as alternative
    - added --ssh-backend parameter to switch between paramiko,pexpect
    - manpage
    -- update to reflect above changes
    -- added more backend requirements
    - Changelog.GNU removed double entries

2012-03-13  Kenneth Loafman  <kenneth@loafman.com>

    Update Changelog.GNU.

2012-03-13  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/0.6-ssh_add_missinghostkey

    add missing_host_key prompt to new sshbackend similar to ssh procedure

2012-03-12  edso

    changelog entry

2012-03-12  edso

    add missing_host_key prompt similar to ssh procedure

2012-03-13  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~carlos-abalde/duplicity/gdocs-backend-gdata-2.0.16.-upgrade.

2012-03-12  Carlos Abalde  <carlos.abalde@gmail.com>

    Fixing most basic stuff. Pending all testing

2012-03-08  edso  <edgar.soldin@web.de>

    Merged in lp:~ed.so/duplicity/0.6-ssh_config

    add ssh_config support (/etc/ssh/ssh_config + ~/.ssh/config) to paramiko sshbackend
    @Ken: would you please announce that sshbackend is paramiko based native python now in the Changelog for the next release?
    this was missing in 0.6.18's Changelog

2012-03-08  edso

    changelog entry

2012-03-08  edso

    add ssh_config support (/etc/ssh/ssh_config + ~/.ssh/config) to paramiko sshbackend

2012-03-08  edso  <edgar.soldin@web.de>

    Merged in lp:~ed.so/duplicity/0.6-webdav_fixes.

2012-03-08  edso

    - empty listbody for enhanced webdav compatibility
    - bugfix: initial folder creation on backend does not result in a ResponseNotReady anymore

2012-03-08  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/0.6-manpage

    - added REQUIREMENTS section

2012-03-08  edso

    - added REQUIREMENTS section
    - restructure SYNOPSIS/ACTIONS to have commands sorted by backup lifecycle
    - added restore and some more hints when --time or --file-to-restore are supported
    - replaced scp:// with sftp:// in examples as this is the suggested protocol anyway
    - added an intro text to ACTIONS section
    - adapted --ssh-askpass description to latest functionality

2012-02-29  kenneth@loafman.com

    Changes for 0.6.18.

2012-02-29  kenneth@loafman.com

    Use correct dir name for cleanup.

2012-02-29  kenneth@loafman.com

    Adjust roottest.py to new test dir structure.

2012-02-29  kenneth@loafman.com

    Changes for 0.6.18.

2012-02-29  kenneth@loafman.com

    Some code/import changes to make the ssh and boto backends compatible with Python 2.4.

2012-02-29  kenneth@loafman.com

    Changes for 0.6.18.

2012-02-29  kenneth@loafman.com

    Changes for 0.6.18.

2012-02-29  kenneth@loafman.com

    Fix for bug 931175 'duplicity crashes when PYTHONOPTIMIZE is set'

2012-02-28  kenneth@loafman.com

    Remove duplicate line.

2012-02-28  kenneth@loafman.com

    File /etc/motd may not exist in test environment.  Use __file__ instead to point to a known plaintext source file.

2012-02-28  kenneth@loafman.com

    Remove tests for 884371.  Can't test that yet.

2012-02-28  kenneth@loafman.com

    Raise log level on backend import failure so it will be visible under default conditions.

2012-02-15  kenneth@loafman.com

    Fix for bug 929465 -- UnsupportedBackendScheme: scheme not supported in url: scp://u123@u123.example.com/foo/

2012-02-12  kenneth@loafman.com

    Applied patch from 930727

    ftpsbackend should respect num_retries for ftp commands

2012-02-07  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/nopexpect

    Just a simple branch that drops the now-unused local copy of pexpect.py. (The ssh backend now uses paramiko)

2012-02-07  Michael Terry  <michael.terry@canonical.com>

    drop unused pexpect.py

2012-02-07  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/testfixes

    Here are two changes that help the test suite pass (it got broken after the recent round of merges).

    1) When file_naming is asked for a name, don't assert if compression AND encryption are turned on.  They are by default now.  But globals.compression is only meant to take effect if encryption is turned off.  So when encryption is on, just turn off gzip suffixes.

    2) Some tests are unit tests that directly import the relevant duplicity code.  So make sure that regular expressions are setup lazily as needed, not once at the start of bin/duplicity.

2012-02-07  Michael Terry  <michael.terry@canonical.com>

    a couple small code fixes to help tests pass

2012-02-05  Kenneth Loafman  <kenneth@loafman.com>

    Applied patch by Alexander Zangerl from bug 909031, "SSH-Backend: Creating dirs separately causes a permissons-problems".

2012-02-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~nguyenqmai/duplicity/file-prefix-option.

    Adding --file-prefix option so different sets of backups can be stored in the same bucket.  See blueprint at https://blueprints.launchpad.net/duplicity/+spec/file-prefix-option

2012-01-19  nguyenqmai

    change the way the file_naming regular expressions are created to support --file-prefix option

2012-02-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/memleak

    Don't cache TarInfo files. Tests still pass, so I don't believe we need the members cache (and in the old tarfile.py, we didn't cache either).

2012-01-20  Michael Terry  <michael.terry@canonical.com>

    Don't have TarFile objects cache member TarInfo objects; it takes too much space

2012-02-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/always-delay

    always delay a little bit when a backend gives us errors

2012-01-09  Michael Terry  <michael.terry@canonical.com>

    always delay a little bit when a backend gives us errors

2012-02-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~tobias-genannt/duplicity/nocompress

    Added option to not compress the backup, when no encryption is selected

2011-12-21  Tobias Genannt  <tobias.genannt@googlemail.com>

    - changelog update
    - fixed comment

2011-12-21  Tobias Genannt  <tobias.genannt@googlemail.com>

    Added option to not compress the backup, when no encryption is selected

2012-02-05  kenneth@loafman.com

    Added patch for testing of bug 884371, 'Globbing patterns fail to include some files if prefix is "**"'

    Note: This patch does not fix the bug, it's just for testing.

2012-02-05  kenneth@loafman.com

    Applied patch from 916689 "multipart upload fails on python 2.7.2"

2012-02-05  kenneth@loafman.com

    Applied patch from 884638 and fixed version check to allow Python 2.5 and above.

2011-12-18  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/resume-inc

2011-12-06  Michael Terry  <michael.terry@canonical.com>

    resuming an incremental results in a 'Restarting backup, but current encryption settings do not match original settings' error because curtime is incorrectly set away from previous incremental value

2011-12-18  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/more-test-fixes

2011-12-05  Michael Terry  <michael.terry@canonical.com>

    tests: make other-filesystem check more robust against certain directories being mounts or not

2011-12-05  Michael Terry  <michael.terry@canonical.com>

    tests: use backup source that is more likely to be larger than 1M compressed

2011-12-05  Michael Terry  <michael.terry@canonical.com>

    tests: add delay between backups to avoid assertion error

2011-12-01  Kenneth Loafman  <kenneth@loafman.com>

    Fix extraneous '.py' that keeps import from working.

2011-11-25  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.17

2011-11-25  Kenneth Loafman  <kenneth@loafman.com>

    Not used.

2011-11-25  Kenneth Loafman  <kenneth@loafman.com>

    Run tests using virtualenv for each.

2011-11-25  Kenneth Loafman  <kenneth@loafman.com>

    - Make adjustments for the new structure.
    - Adjust boto requirements to be 1.6a or higher.
    - Cleanup install scripts.

2011-11-24  Kenneth Loafman  <kenneth@loafman.com>

    Some doc changes including new requirements.

2011-11-23  Kenneth Loafman  <kenneth@loafman.com>

    Don't assume dir location for Python.

2011-11-23  Kenneth Loafman  <kenneth@loafman.com>

    Added --rsync-options flag to allow user to pass options to rsync at will.

2011-11-15  Eliot Moss  <moss@cs.umass.edu>

    Adds --rsync-options to command line
    Allows uer to pass additional options to the rsync backend
    Commit include paragraph in man page, new global variable,
    and the small changes needed to the backend itself

2011-11-23  Kenneth Loafman  <kenneth@loafman.com>

    878964: Resuming a backup with a different password should throw an error

2011-11-23  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-11-22  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-11-19  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-11-08  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-10-30  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-10-22  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-10-17  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-10-16  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-10-20  Michael Terry  <michael.terry@canonical.com>

    check that we have the right passphrase when restarting a backup

2011-11-22  Kenneth Loafman  <kenneth@loafman.com>

    411145  Misleading error message: "Invalid SSH password"

2011-11-21  Kenneth Loafman  <kenneth@loafman.com>

    Split botobackend.py into two parts, _boto_single.py which is the older single-processing version and _boto_multi.py which is the newer multi-processing version.  The default is single processing and can be overridden with --s3-use-multiprocessing.

2011-11-20  Kenneth Loafman  <kenneth@loafman.com>

    The function add_filename was rejecting anything non-encrypted as a legit file.  This fixes that problem and the bug.

2011-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Fix to allow debugging from pydev.  The check for --pydevd must be done after command line is parsed.

2011-11-18  Kenneth Loafman  <kenneth@loafman.com>

    Merged in bzr merge lp:~summer-is-gone/duplicity/tz-incremental-fix.

2011-11-03  Ivan Gromov  <ivan.gromov@redsolution.ru>

    Changed functions working with UTC time file format from localtime() to gmtime() and timegm()

2011-11-03  ivan.gromov  <ivan.gromov@C0011>

    Fixed time_separator global attribute usage in some tests

2011-11-03  Ivan Gromov  <ivan.gromov@redsolution.ru>

    Made proper setUp method for tests in dup_timetest.py.

2011-11-18  Kenneth Loafman  <kenneth@loafman.com>

    Remove random_seed from VCS, adjust .bzrignore.

2011-11-17  ken

    Remove localbackend.testing_in_progress since all it accomplished was to make the local backend test fail.

2011-11-17  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/ship-tests and moved a couple of things around to get manual tests working

2011-11-07  Michael Terry  <michael.terry@canonical.com>

    Make tarball layout match bzr layout much more closely; ship tests in tarballs and adjust things so that they can work

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    rename auto/ to tests/

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    undo accidental changes to run-tests and convert pathtest and rdiffdirtest (for both of which, I uncommented a failing test I didn't understand)

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    move some more custom scripts to manual/

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    move some things around; converge on one script for running any kind of test or list of tests

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert patchdirtest to auto; rip out its root-requiring tests and move them to roottest script; fix roottest script to work now with the new rootfiles.tar.gz, whoops

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert finaltest to auto; workaround an ecryptfs bug with long filenames in the test

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    drop state file random_seed from test gnupg home

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert gpgtest to auto; add testing keys to the suite, so testers don't have to make their own; delete gpgtest2, as it didn't do anything

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    drop unused darwin tarball and util file

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert GnuPGInterfacetest and dup_timetest to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert file_namingtest, parsedurltest, and restarttest to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert manifesttest, selectiontest, and test_tarfile to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert cleanuptest, dup_temptest, and misctest to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert statisticstest to auto; make sure tests are run in English and in US/Central timezone

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert statictest to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert tempdirtest to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert logtest to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    convert lazytest to auto

2011-11-04  Michael Terry  <michael.terry@canonical.com>

    clean up run scripts a little bit, rename testfiles.tgz to rootfiles.tgz

2011-11-03  Michael Terry  <michael.terry@canonical.com>

    make diffdirtest auto

2011-11-03  Michael Terry  <michael.terry@canonical.com>

    make badupload auto

2011-11-03  Michael Terry  <michael.terry@canonical.com>

    make collectionstest auto

2011-11-02  Michael Terry  <michael.terry@canonical.com>

    move all manual tets into their own subdirectory

2011-11-07  ken

    -- Applied patch 0616.diff from bug 881070.
    -- Fixed compile issues in reset_connection.
    -- Changed 'url' to 'parsed_url' to make consistent with backends.

2011-10-16  ken

    Changes for 0.6.16.

2011-10-16  ken

    Changes for 0.6.16.

2011-10-15  Kenneth Loafman  <kenneth@loafman.com>

    Merge in lp:~duplicity-team/duplicity/po-updates

2011-10-15  Kenneth Loafman  <kenneth@loafman.com>

    Merge in lp:~duplicity-team/duplicity/po-updates

2011-10-12  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-10-11  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-09-20  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-29  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-28  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-26  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-25  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-24  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-21  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-10  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-09  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-08  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-08-01  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-07-16  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-06-23  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-06-19  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-10-15  Kenneth Loafman  <kenneth@loafman.com>

    Remove Eclipse stuff from bzr.

2011-10-10  kenneth@loafman.com

    Update .pot and add all languages to LINGUAS list file.

2011-10-10  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/UnicodeDecodeError

2011-10-10  edso

    some links for UnicodeDecodeError

2011-10-10  edso

    fix UnicodeDecodeError: 'ascii' codec can't decode byte on command usage

2011-10-08  kenneth@loafman.com

    Remove evil tab characters causing indent errors.

2011-10-08  kenneth@loafman.com

    838162  Duplicity URL Parser is not parsing IPv6 properly

2011-10-08  kenneth@loafman.com

    676109 Amazon S3 backend multipart upload support

2011-10-08  kenneth@loafman.com

    739438 Local backend should always try renaming instead of copying

2011-10-07  Kenneth Loafman  <kenneth@loafman.com>

    Merge in lp:~ed.so/duplicity/manpage

2011-10-07  edso

    updated
    --verbosity
    symmetric and signing

    minor fixes

2011-10-07  kenneth@loafman.com

    Checkpoint

2011-10-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/rbNoneNone

2011-10-04  Michael Terry  <michael.terry@canonical.com>

    make sure sig_path is a regular file before opening it

2011-10-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ross-ross-williams/duplicity/gpg-agent-fix

2011-09-06  Ross Williams  <ross@ross-williams.net>

    gpg2 will not get the passphrase from gpg-agent if --passphrase-fd is specified. Added tests to disable passphrase FD if use_agent option is true.

2011-10-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/fix-local-backend-validation

2011-09-06  Michael Terry  <michael.terry@canonical.com>

    use cached size of original upload file rather than grabbing it after put() call.  Some backends invalidate the stat information after put (like local backend after a rename)

2011-10-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/partial-encryption

2011-08-31  Michael Terry  <michael.terry@canonical.com>

    allow upgrading partial chain encryption status

2011-10-05  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/tarfile

2011-08-23  Michael Terry  <mike@mterry.name>

    make tarfile.py 2.4-compatible

2011-08-23  Michael Terry  <mike@mterry.name>

    use python2.7's tarfile instead of whichever version comes with user's python

2011-08-20  Michael Terry  <mike@mterry.name>

    use a proper fake TarFile object when reading an empty tar

2011-08-20  Michael Terry  <mike@mterry.name>

    handle empty headers better than passing ignore_zeros -- instead handle ReadErrors

2011-08-20  Michael Terry  <mike@mterry.name>

    and update trailing slashes in test too

2011-08-20  Michael Terry  <mike@mterry.name>

    fix how trailing slashes are used to be cross-python-version compatible

2011-08-20  Michael Terry  <mike@mterry.name>

    whoops, forgot an import

2011-08-20  Michael Terry  <mike@mterry.name>

    handle different versions of tarfile

2011-08-20  Michael Terry  <mike@mterry.name>

    first pass at dropping tarfile

2011-08-29  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~duplicity-team/duplicity/check-volumes

2011-08-28  Michael Terry  <michael.terry@canonical.com>

    make query_info a little easier to use by guaranteeing a well-formated return dictionary

2011-08-28  Michael Terry  <michael.terry@canonical.com>

    add rackspace query support

2011-08-28  Michael Terry  <michael.terry@canonical.com>

    add query support to boto backend

2011-08-28  Michael Terry  <michael.terry@canonical.com>

    make clear the difference between sizes from errors and backends that don't support querying

2011-08-25  Michael Terry  <michael.terry@canonical.com>

    add query_info support to u1 backend

2011-08-25  Michael Terry  <michael.terry@canonical.com>

    first pass at checking volume upload success

2011-08-29  Kenneth Loafman  <kenneth@loafman.com>

    832149: Uploads to Rackspace fail silently

2011-08-28  Michael Terry  <michael.terry@canonical.com>

    cloudfiles: allow listing more than 10k files

2011-08-23  Kenneth Loafman  <kenneth@loafman.com>

    - usability enhancement: sign passphrase prompt has no second
    verification prompt anymore, symmetric passphrases are still verified

2011-08-23  edso

    drop sign passphrase verification prompt

2011-08-23  edso

    bugfix of rev767
    on using sign key duplicity claimed 'PASSPHRASE variable not set'

2011-08-23  Kenneth Loafman  <kenneth@loafman.com>

    Sync with master.

2011-08-20  Michael Terry  <mike@mterry.name>

    remove another non-2.4-ism I introduced

2011-08-19  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.15.

2011-08-19  Kenneth Loafman  <kenneth@loafman.com>

    fixes to unit tests to support SIGN_PASSPHRASE.

2011-08-18  Kenneth Loafman  <kenneth@loafman.com>

    - introduce --numeric-owner parameter
    patch courtesy of Lukas Anzinger <l.anzinger AT gmail.com>
    - duplicity:restore_check_hash
    'Invalid data - *** hash mismatch' lists the offending filename

2011-08-18  edso

    typo fix

2011-08-18  edso

    numowner & hash mismatch verbosity

2011-08-18  Kenneth Loafman  <kenneth@loafman.com>

    Remove use of virtualenv.

2011-08-18  Kenneth Loafman  <kenneth@loafman.com>

    - Ignore ENOENT (file missing) errors where it is safe.
    - Set minimum Python version to 2.4 in README.

2011-08-17  Kenneth Loafman  <kenneth@loafman.com>

    824678     0.6.14 Fails to install on 8.04 LTS (Hardy)

2011-08-17  Kenneth Loafman  <kenneth@loafman.com>

    823556     sftp errors after rev 740 change

2011-08-06  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~carlos-abalde/duplicity/google-docs

2011-08-03  Carlos Abalde  <carlos.abalde@gmail.com>

    Fixed indentation: 2 to 4 spaces

2011-07-31  Carlos Abalde  <carlos.abalde@gmail.com>

    Fetching user password correctly (i.e. not using directly self.parsed_url.password)

2011-07-31  Carlos Abalde  <carlos.abalde@gmail.com>

    Now using backend.retry(fn) decorator to handle API retries

2011-07-30  Carlos Abalde  <carlos.abalde@gmail.com>

    Added subfolders support + several minor improvements and fixes

2011-07-29  Carlos Abalde  <carlos.abalde@gmail.com>

    Added support for captcha challenges

2011-07-29  Carlos Abalde  <carlos.abalde@gmail.com>

    Replacing get_doclist by get_everything in put & delete methods. Raisng BackendException's in constructor

2011-07-29  Carlos Abalde  <carlos.abalde@gmail.com>

    Replaces get_doclist by get_everything when retrieving remote list of files in backup destination folder

2011-07-28  Carlos Abalde  <carlos.abalde@gmail.com>

    Added authentication instruction for accounts with 2-step verification enabled

2011-07-28  Carlos Abalde  <carlos.abalde@gmail.com>

    A couple of assert + missing local_path.setdata on remote file get

2011-07-28  Carlos Abalde  <carlos.abalde@gmail.com>

    Better error logging + retries for each API op

2011-07-28  Carlos Abalde  <carlos.abalde@gmail.com>

    Improved upload: check duplicated file names on destination folder + better error handling

2011-07-28  Carlos Abalde  <carlos.abalde@gmail.com>

    Improved API error handling

2011-07-28  Carlos Abalde  <carlos.abalde@gmail.com>

    Checking Google Data APIs Python libraries are present

2011-07-27  Carlos Abalde  <carlos.abalde@gmail.com>

    Fixed URI format

2011-07-27  Carlos Abalde  <carlos.abalde@gmail.com>

    First usable prototype

2011-08-06  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/u1-fixes

2011-08-03  Michael Terry  <michael.terry@canonical.com>

    some u1 backend fixes: handle errors 507 and 503; add oops-id to message user sees so U1 folks can help

2011-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/encr-sign-key2

2011-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/encr-sign-key2

2011-07-16  ede

    - introduce --encrypt-sign-key parameter
    - duplicity-bin::get_passphrase
    skip passphrase asking and reuse passphrase if
    sign-key is also an encrypt key and
    a passphrase for either one is already set
    - add _() gettext to text in duplicity-bin::get_passphrase
    - document changes and minor additions in manpage

2011-07-29  Kenneth Loafman  <kenneth@loafman.com>

    818178     Shouldn't try to delete files it knows don't exist

2011-07-29  Michael Terry  <michael.terry@canonical.com>

    Don't try to delete partial manifests from backends

2011-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/retry-u1

2011-07-29  Michael Terry  <michael.terry@canonical.com>

    retry operations on u1 backend

2011-07-26  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~mterry/duplicity/815635

2011-07-25  Michael Terry  <michael.terry@canonical.com>

    when copying metadata from remote to local archive, first copy to a temporary file then move over to archive

2011-07-26  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~mterry/duplicity/report-encrypted-chains

2011-07-22  Michael Terry  <michael.terry@canonical.com>

    report whether a chain is encrypted or not

2011-07-26  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~mterry/duplicity/more-accurate-sync

2011-07-22  Michael Terry  <michael.terry@canonical.com>

    be more careful about what we try to synchronize

2011-07-09  Kenneth Loafman  <kenneth@loafman.com>

    703142     AssertionError: assert len(chain_list) == 2

2011-07-08  Michael Terry  <michael.terry@canonical.com>

    pay attention to local partials when sync'ing metadata and make sure we don't end up with three copies of a metadata file

2011-07-09  Kenneth Loafman  <kenneth@loafman.com>

    794576     Transport endpoint is not connected

2011-07-07  Michael Terry  <michael.terry@canonical.com>

    ignore ENOTCONN when scanning files

2011-06-28  Kenneth Loafman  <kenneth@loafman.com>

    Really restore threaded_waitpid().

2011-06-27  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/guard-tarinfo

2011-06-23  Michael Terry  <michael.terry@canonical.com>

    also guard the recursive call

2011-06-23  Michael Terry  <michael.terry@canonical.com>

    guard tarinfo object from being None

2011-06-27  Kenneth Loafman  <kenneth@loafman.com>

    Detabify.  Tabs are evil.

2011-06-24  Kenneth Loafman  <kenneth@loafman.com>

    Restore previous version with threaded_waitpid().

2011-06-22  Kenneth Loafman  <kenneth@loafman.com>

    Ignore 404 errors when we try to delete a file on Ubuntu One.

2011-06-21  Michael Terry  <michael.terry@canonical.com>

    u1backend: ignore file-not-found errors on delete

2011-06-22  Kenneth Loafman  <kenneth@loafman.com>

    Update to duplicity messages.

2011-06-18  Kenneth Loafman  <kenneth@loafman.com>

    Prep for 0.6.14 release.

2011-06-18  Kenneth Loafman  <kenneth@loafman.com>

    Prep for 0.6.14 release.

2011-06-17  Kenneth Loafman  <kenneth@loafman.com>

    777377     collection-status asking for passphrase

    Various fixes to unit tests to comprehend changes made.

2011-06-17  Kenneth Loafman  <kenneth@loafman.com>

    680425     Endless retype passphrase when typo
    793096     Allow to pass different passwords for --sign-key and --encrypt-key

2011-06-17  Lekensteyn  <lekensteyn@gmail.com>

    - duplicity.1: move information about the PASSPHRASE and SIGN_PASSPHRASE
    environment variables to the Environment Variables section
    - duplicity.1: add information about the limitation on using
    symmetric+sign to the bugs section
    - In the passphrase retrieval function get_passphrase, do not switch from
    "ask password without verifying" to ask+verify if the passphrase was
    empty
    - Allow an empty passphrase for signing key
    - Make clear in the verification prompt whether the encryption passphrase
    or the signing passphrase is being confirmed
    - Fix passphrase retrieval for sym+sign (duplicity-bin and gpg.py)
    - Allow sym+sign with limitation (see comments and manual page)

2011-06-11  Lekensteyn  <lekensteyn@gmail.com>

    - invalid function description fixed for get_passphrase in duplicity-bin
    - function get_passphrase in duplicity-bin accepts argument "for_signing"
    which indicates that a passphrase for a signing key is requested
    - introduces the SIGN_PASSPHRASE environment variable for passing a
    different passphrase to the signing key
    - commandline option --encrypt-secret-keyring=path introduced to set a
    custom location for the secret keyring used by the encryption key
    - manual page updated with SIGN_PASSPHRASE and --encrypt-secret-keyring
    - ask for a new passphrase if the passphrase confirmation failed to
    prevent an endless retype
    - improved some comments in the code
    - due to the difference in the handling of the signing and encryption
    passphrase, the passphrase is asked later in the duplicity-bin

2011-06-17  Kenneth Loafman  <kenneth@loafman.com>

    797758     Duplicity ignores some FatalErrors

2011-06-17  Michael Terry  <mike@mterry.name>

    always catch Exceptions, not BaseExceptions

2011-06-17  Kenneth Loafman  <kenneth@loafman.com>

    Checkpoint

2011-06-14  Kenneth Loafman  <kenneth@loafman.com>

    794123     Timeout on sftp command 'ls -1'

2011-06-14  Kenneth Loafman  <kenneth@loafman.com>

    Checkpoint.

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    487720     Restore fails with "Invalid data - SHA1 hash mismatch"

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Fixed boolean swap made when correcting syntax.

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Fix syntax for Python 2.4 and 2.5.

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Fix syntax for Python 2.4 and 2.5.

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Fix CHANGELOG.

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    782337     sftp backend cannot create new subdirs on new backup

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    782294     create tomporary files with sftp

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/retry-decorator

2011-06-12  Michael Terry  <mike@mterry.name>

    move logging code up to retry decorator; fixes use of 'n' variable where it doesn't belong

2011-06-06  Michael Terry  <mike@mterry.name>

    add retry decorator for backend functions; use it for giobackend; add retry to giobackend's list and delete operations

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/u1-status

2011-06-13  Michael Terry  <mike@mterry.name>

    u1: allow any success status, not just 200

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Checkpoint.

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/gio-name

2011-06-06  Michael Terry  <mike@mterry.name>

    giobackend: use name, not display name to list files

2011-06-13  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/levelName

2011-05-31  Michael Terry  <mike@mterry.name>

    fix MachineFilter logic to match new level name code

2011-05-24  Michael Terry  <michael.terry@canonical.com>

    Cautiously avoid using levelname directly in log module.  It can be adjusted by libraries.

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    452342     Provide Ubuntu One integration

2011-05-24  Michael Terry  <michael.terry@canonical.com>

    update man page

2011-05-24  Michael Terry  <michael.terry@canonical.com>

    drop test file

2011-05-24  Michael Terry  <michael.terry@canonical.com>

    further fixups

2011-05-23  Michael Terry  <michael.terry@canonical.com>

    further upload work

2011-05-17  Michael Terry  <michael.terry@canonical.com>

    start of u1 support

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    792704     Webdav(s) url scheme lacks port support

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    782321     duplicity sftp backend should ignore removing a file which is not there

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    778215     ncftpls file delete fails in ftpbackend.py

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    507904     Cygwin: Full Backup fails with "IOError: [Errno 13] Permission denied"

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    761688     Difference found: File X has permissions 666, expected 666

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    739438     [PATCH] Local backend should always try renaming instead of copying

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    705499     "include-filelist-stdin" not implemented on version 0.6.11

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    Sync with repository.

2011-06-07  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-04-26  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-04-25  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-04-17  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-04-04  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-04-03  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-03-22  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2010-12-15  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2010-12-08  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2010-11-21  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2011-05-11  ed  <edgar.soldin@web.de>

    as restoring is non-destructive by default (overideable with --force) there is no need to raie fata errors if not supported in/exclude parameters are given as parameters.
    see also:
    http://lists.gnu.org/archive/html/duplicity-talk/2011-04/msg00010.html

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    512628     --exclude-filelist-stdin and gpg error with/without PASSPHRASE

2011-06-12  Kenneth Loafman  <kenneth@loafman.com>

    512628     --exclude-filelist-stdin and gpg error with/without PASSPHRASE

2011-04-16  Kenneth Loafman  <kenneth@loafman.com>

    Insure Python 2.4 compatible.

2011-04-16  Kenneth Loafman  <kenneth@loafman.com>

    433591  AttributeError: FileobjHooked instance has no attribute 'name'

2011-04-04  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~ed.so/duplicity/0.6-add_sftp.

2011-04-04  ed  <edgar.soldin@web.de>

    link sftp to ssh backend, thus enabling sftp:// urls
    modified explanation in manpage
    minor changes in manpage

2011-04-04  Kenneth Loafman  <kenneth@loafman.com>

    Boto has refactored too many times, so back off and just use Exception rather than searching.

2011-04-03  Kenneth Loafman  <kenneth@loafman.com>

    Boto moved S3ResponseError, so allow for different imports.

2011-04-02  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.13.

2011-04-02  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.13.

2011-04-02  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.13.

2011-04-02  Kenneth Loafman  <kenneth@loafman.com>

    Check for presence of bucket before trying to create.

2011-03-29  Kenneth Loafman  <kenneth@loafman.com>

    579958  Assertion error "time not moving forward at appropriate pace"

2011-03-26  Kenneth Loafman  <kenneth@loafman.com>

    Add in ftpsbackend.py.  Missed it.

2011-03-21  Kenneth Loafman  <kenneth@loafman.com>

    613244     silent data corruption with checkpoint/restore

2011-03-21  Kenneth Loafman  <kenneth@loafman.com>

    Add a manual test for Ctrl-C interrupts.  This could be automated, but I find that the old hairy eyeball works quite well as is.

2011-03-21  Kenneth Loafman  <kenneth@loafman.com>

    Use python-virtualenv to provide a well-defined environment for testing multiple versions of Python.

2011-03-21  Kenneth Loafman  <kenneth@loafman.com>

    Add (undocumented) option --pydevd to allow easier debugging when executing long chains of duplicity executions.

2011-03-21  Kenneth Loafman  <kenneth@loafman.com>

    Remove threaded_waitpid().  We still need GnuPGInterface because of the shift bug in the return code and the ugly mix of tabs and spaces.  All has been reported to the author.

    Note:  With this change people who do long chains of incrementals will need to up the number of file handles.

2011-03-09  Kenneth Loafman  <kenneth@loafman.com>

    Replace 2.5 'except...as' syntax.

2011-03-08  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.12.

2011-03-08  Kenneth Loafman  <kenneth@loafman.com>

    Various fixes for testing.  All tests pass completely.

2011-03-08  Kenneth Loafman  <kenneth@loafman.com>

    Add test for new ftps backend using lftp.

2011-03-07  Kenneth Loafman  <kenneth@loafman.com>

    Some FTP sites return 'total NN' in true ls fashion, so ignore line during listing of files.

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    Fix typo on fix for 700390.

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    Miscellaneous fixes for testing.

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    700390     Backup fails silently when target is full (sftp, verbosity=4)

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    581054     Inverted "Current directory" "Previous directory" in error message

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    626915     ftps support using lftp (ftpsbackend)

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    629984     boto backend uses Python 2.5 conditional

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    670891     Cygwin: TypeError: basis_file must be a (true) file, while restoring inremental backup

2011-03-06  Kenneth Loafman  <kenneth@loafman.com>

    655797     symbolic link ownership not preserved

2011-02-12  Kenneth Loafman  <kenneth@loafman.com>

    lp:~blueyed/duplicity/path-enodev-bugfix

2011-02-12  Kenneth Loafman  <kenneth@loafman.com>

    Merged: lp:~blueyed/duplicity/path-enodev-bugfix

2011-02-12  Kenneth Loafman  <kenneth@loafman.com>

    629136     sslerror: The read operation timed out with cf

2011-01-18  Kenneth Loafman  <kenneth@loafman.com>

    704314     Exception in log module

2010-12-26  Kenneth Loafman  <kenneth@loafman.com>

    486489  Only full backups done on webdav

2010-12-26  Kenneth Loafman  <kenneth@loafman.com>

    620163  OSError: [Errno 2] No such file or directory

2010-12-26  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/backend-log-codes3

2010-12-04  Michael Terry  <mike@mterry.name>

    use log error codes for common backend errors

2010-11-27  Kenneth Loafman  <kenneth@loafman.com>

    681980     Duplicity 0.6.11 aborts if RSYNC_RSH not set

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.11

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.11

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    433970 Add an option to connect to S3 with regular HTTP (and not HTTPS)

2010-10-13  Martin Pool  <mbp@sourcefrog.net>

    Add --s3-unencrypted-connection (bug 433970)

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    631275 missing ssh on rsyncd url - rsync: Failed to exec ssh: ...

2010-11-20  ed  <edgar.soldin@web.de>

    solve bug 631275
    rsync 3.0.7 persists on either rsync:// _or_ :: module notation
    both together and it interpretes it as a dest for rsh

2010-11-13  ed  <edgar.soldin@web.de>

    protect rsync from possibly conflicting remote shell environment setting

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    674506 RsyncBackend instance has no attribute 'subprocess_popen_persist'.

2010-11-12  ed  <edgar.soldin@web.de>

    restored
    backend:subprocess_popen_* methods
    moved ncftpls workaround into ftpbackend
    introduced new backend:popen_persist_breaks setting for such workarounds
    enhanced backend:munge_password
    rsyncbackend: rsync over ssh does not ask for password (only keyauth supported)

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~ed.so/duplicity/survive_spaces.

2010-11-12  ed  <edgar.soldin@web.de>

    survive spaces in path on local copying with encryption enabled

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~ed.so/duplicity/sign_symmetric2.

2010-11-12  ed  <edgar.soldin@web.de>

    allow signing of symmetric encryption

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~duplicity-team/duplicity/po-updates.

2010-10-24  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2010-10-12  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2010-10-08  Launchpad Translations on behalf of duplicity-team

    Launchpad automatic translations update.

2010-09-20  duplicity-team  <duplicity-team@lists.launchpad.net>

    Launchpad automatic translations update.

2010-07-24  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-05-24  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    669225 sftp: Couldnt delete file: Failure only logged on level 9.

2010-11-05  Daniel Hahler  <ubuntu-launchpad@thequod.de>

    Catch "Couldn't delete file" response in sftp commands.

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Fix CHANGELOG.

2010-06-29  Tomaž Muraus  <kami@k5-storitve.net>

    When using listmatch filenames are now unqouted so colons and other special characters don't cause problems.

    Also all the tests now pass.

2010-06-27  Tomaž Muraus  <kami@k5-storitve.net>

    Added test for SpiderOak backend (it should probably just fail in most cases since the API is still very unstable).

2010-06-22  Tomaž Muraus  <kami@k5-storitve.net>

    Add ability to retry failed commands.

2010-06-22  Tomaž Muraus  <kami@k5-storitve.net>

    Handle exceptions when listing files and display coresponding HTTP status code on HTTPError exception

2010-06-22  Tomaž Muraus  <kami@k5-storitve.net>

    First version of SpiderOak DIY backend.

    Still very rough and needs tests.

2010-05-26  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~mterry/duplicity/backend-log-codes2

2010-05-26  Michael Terry  <mike@mterry.name>

    support new backend-error log codes

2010-05-24  Kenneth Loafman  <kenneth@loafman.com>

    Merge changes from 0.6-series.

2010-11-20  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~l2g/duplicity/use-py.test

2009-09-21  Larry Gilbert  <larry+launchpad@l2g.to>

    Adding conftest.py for py.test configuration hooks (right now just setting
    up temporary directories)

2009-09-20  Larry Gilbert  <larry+launchpad@l2g.to>

    Use py.path to simplify a little

2009-09-20  Larry Gilbert  <larry+launchpad@l2g.to>

    Don't try to change dirs in cleanup_test_files for now. Actually, this file probably won't be here much longer.

2009-09-20  Larry Gilbert  <larry+launchpad@l2g.to>

    Criss-cross merge. 'Scuse my mess.

2009-09-19  Larry Gilbert  <larry+launchpad@l2g.to>

    trunk merge

2009-09-20  Larry Gilbert  <larry+launchpad@l2g.to>

    Fix non-root-based test skipping

2009-09-19  Larry Gilbert  <larry+launchpad@l2g.to>

    Expose test files' root directory as config.test_root

2009-09-19  Larry Gilbert  <larry+launchpad@l2g.to>

    New helper module for tests; have backendtest.py make use of it

2009-09-19  Larry Gilbert  <larry+launchpad@l2g.to>

    I think these are all my own changes, not a trunk merge. Sorry for confusion.

2009-09-17  Larry Gilbert  <larry+launchpad@L2G.to>

    Refactored.  Put in py.test.skip to skip tests when tarfile can't be used.

2009-09-17  Larry Gilbert  <larry+launchpad@L2G.to>

    commit.py already adjusts sys.path, so anything that imports commit doesn't
    need to

2009-09-16  Larry Gilbert  <larry+launchpad@L2G.to>

    Allow testing/config.py to find duplicity even when run outside testing/.
    Added a missing import.

2010-10-25  Kenneth Loafman  <kenneth@loafman.com>

    637556     os.execve should get passed program as first argument

2010-10-06  Kenneth Loafman  <kenneth@loafman.com>

    Delete duplicity.spec -- autocreated.

2010-09-19  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.10.

2010-10-06  Kenneth Loafman  <kenneth@loafman.com>

    Replace ternary operator with simple if statement.  Python 2.4 does not support the ternary operator.

2010-10-06  Kenneth Loafman  <kenneth@loafman.com>

    Upgrade setup dependency to Python 2.4 or later.

2010-09-19  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.10.

2010-09-06  Kenneth Loafman  <kenneth@loafman.com>

    612714     NameError: global name 'parsed_url' is not defined

2010-09-06  Kenneth Loafman  <kenneth@loafman.com>

    589495     duplicity --short-filenames crashes with TypeError

2010-09-06  Kenneth Loafman  <kenneth@loafman.com>

    589495     duplicity --short-filenames crashes with TypeError

2010-08-26  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~olivierberger/+junk/dupl-542482

2010-08-26  olivier  <olivier@asustour>

    merge with latest release upstream : 0.6.09

2010-05-16  olivier  <olivier@asustour>

    Fix remove-older-than which would no longer work
    Differentiate the function name from global option name for remove_all_but_n_full

2010-03-29  olivier  <olivier@asustour>

    Added bits of manpage

2010-03-29  olivier  <olivier@asustour>

    Adding the remove-all-inc-of-but-n-full variant to
    remove_all_but_n_full() : remove only incremental sets from a backup
    chain selected as older than the n last full

2010-03-29  olivier  <olivier@asustour>

    Adding the 2 new remove-all-but commands as global markers

2010-03-29  olivier  <olivier@asustour>

    Adding new remove-all-inc-of-but-n-full command as a variant of remove-all-but-n-full

2010-03-29  olivier  <olivier@asustour>

    Fix small typo in comments

2010-08-09  Kenneth Loafman  <kenneth@loafman.com>

    613448     ftpbackend fails if target directory doesn't exist

2010-08-09  Kenneth Loafman  <kenneth@loafman.com>

    615449     Command-line verbosity parsing crash

2010-07-28  Kenneth Loafman  <kenneth@loafman.com>

    Man page improvements and clarification.

2010-07-25  Kenneth Loafman  <kenneth@loafman.com>

    Final changes for 0.6.09.

2010-07-24  Kenneth Loafman  <kenneth@loafman.com>

    582962     Diminishing performance on large files

2010-07-24  Kenneth Loafman  <kenneth@loafman.com>

    Fix to warning message in sshbackend.

2010-07-23  Kenneth Loafman  <kenneth@loafman.com>

    Upgraded tahoebackend to new parse_url.

2010-07-23  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2010-07-23  Kenneth Loafman  <kenneth@loafman.com>

    502609     Unknown error while uploading duplicity-full-signatures

2010-07-22  Kenneth Loafman  <kenneth@loafman.com>

    567738  --ssh-options options passing options to ssh do not work

2010-05-15  Michael Terry  <michael.terry@canonical.com>

    support new backend-error log codes

2010-03-08  Michael Terry  <mike@mterry.name>

    don't crash when asked to encrypt, but not passed any gpg_options.  my bad

2010-03-07  Kenneth Loafman  <kenneth@loafman.com>

    #532051 rdiffdir attempts to reference undefined variables with some command arguments

2010-03-07  Kenneth Loafman  <kenneth@loafman.com>

    #519110 Need accurate man page info on use of scp/sftp usage.

2010-03-02  Kenneth Loafman  <kenneth@loafman.com>

    lp:~mterry/duplicity/use-gpg-options-0.7

2010-03-02  Michael Terry  <mike@mterry.name>

    use global gpg options

2010-03-02  ken

    lp:~mterry/duplicity/fix-gpg-options-crash-0.7

2010-03-01  Michael Terry  <mike@mterry.name>

    fix time command line handling

2010-03-01  Michael Terry  <mike@mterry.name>

    and handle initial, empty value for extend commandline actions

2010-03-01  Michael Terry  <michael.terry@canonical.com>

    fix crash on empty gpg-options argument

2010-02-17  ken

    #520470 - Don't Warn when there's old backup to delete

2010-02-17  ken

    Patch #505739 - "sslerror: The read operation timed out" with S3

2010-02-16  ken

    Patch 522544 -- OSError: [Errno 40] Too many levels of symbolic links

2010-02-08  ken

    Patched #497243 archive dir: cache desynchronization caused by remove*

2010-02-08  ken

    Merge with trunk.

2010-01-18  Michael Terry  <mike@mterry.name>

    logging: fix logging to files by opening them with default of 'a' not 'w'

2010-01-08  Michael Terry  <mike@mterry.name>

    merge lp:~mterry/duplicity/rename

2010-01-08  Michael Terry  <mike@mterry.name>

    make a comment reserving 255 as an error code (used by gksu)

2009-12-15  Michael Terry  <michael.terry@canonical.com>

    merge lp:~mterry/duplicity/optparse

2009-12-14  ken

    Merged in lp:~mterry/duplicity/typos

2009-11-27  ken

    Remove antiquated file.

2009-11-27  ken

    Remove requirement for GnuPGInterface, we have our own.

2010-05-23  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2010-04-23  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-03-21  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-03-12  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-05-23  ken

    576564     username not url decoded in backend (at least rsync)

2010-05-23  Kenneth Loafman  <kenneth@loafman.com>

    579958     Assertion error "time not moving forward at appropriate pace"

    setcurtime() must change with time changes.

2010-05-23  ken

    550455       duplicity doesn't handle with large files well (change librsync.SigGenerator.sig_string to a list)

2010-03-11  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.08b

2010-03-11  Kenneth Loafman  <kenneth@loafman.com>

    Manually apply patch from http://bazaar.launchpad.net/~duplicity-team/duplicity/0.7-series/revision/637 which did not make it into 0.6.

2010-03-11  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.08a

2010-03-09  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-03-01  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-03-11  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.08a

2010-03-07  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.08

2010-03-07  Kenneth Loafman  <kenneth@loafman.com>

    #532051 rdiffdir attempts to reference undefined variables with some command arguments

2010-03-07  Kenneth Loafman  <kenneth@loafman.com>

    #519110 Need accurate man page info on use of scp/sftp usage.

2010-03-02  Kenneth Loafman  <kenneth@loafman.com>

    Merged lp:~mterry/duplicity/use-gpg-options-0.6

2010-03-02  Michael Terry  <mike@mterry.name>

    use global gpg options

2010-03-02  ken

    Merged lp:~mterry/duplicity/fix-gpg-options-crash-0.6

2010-03-01  Michael Terry  <mike@mterry.name>

    fix time command line handling

2010-03-01  Michael Terry  <mike@mterry.name>

    and handle initial, empty value for extend commandline actions

2010-03-01  Michael Terry  <michael.terry@canonical.com>

    fix crash on empty gpg-options argument

2010-02-28  ken

    Changes for 0.6.07.

2010-02-28  ken

    Merged lp:~duplicity-team/duplicity/po-updates.

2010-01-15  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-01-09  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-12-16  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-12-15  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2010-02-17  ken

    #520470 - Don't Warn when there's old backup to delete

2010-02-17  ken

    Patch #505739 - "sslerror: The read operation timed out" with S3

2010-02-16  ken

    Patch 522544 -- OSError: [Errno 40] Too many levels of symbolic links

2010-02-08  ken

    Patched #497243 archive dir: cache desynchronization caused by remove*

2010-02-08  ken

    Merge with trunk.

2010-01-18  Michael Terry  <mike@mterry.name>

    logging: fix logging to files by opening them with default of 'a' not 'w'

2010-01-08  Michael Terry  <mike@mterry.name>

    make a comment reserving 255 as an error code (used by gksu)

2009-12-28  ken

    Patch 501093 SSHBackend doesn't handle spaces in path

2009-12-28  ken

    Try again -- remove Eclipse/PyDev control files from bzr.

2009-12-28  ken

    Eclipse settings should not be in bzr.

2009-12-28  ken

    No longer needed.

2009-12-28  ken

    Fix real errors found by PyLint.  Remove unneeded includes.  Tag spurious errors so they don't annoy.

2009-12-28  ken

    Fix problem in put() where destination filename was not being passed properly.

2009-12-24  ken

    Merged in lp:~mterry/duplicity/rename

2009-12-20  Michael Terry  <mike@mterry.name>

    add --rename argument

2009-12-15  Michael Terry  <michael.terry@canonical.com>

    add back accidentally-dropped --use-scp option from commandline merge

2009-12-14  ken

    Fix CHANGELOG.

2009-12-14  ken

    Merged in lp:~mterry/duplicity/typos

2009-12-14  ken

    Merged in lp:~duplicity-team/duplicity/po-updates

2009-12-13  Michael Terry  <mike@mterry.name>

    whoops, and this typo

2009-12-13  Michael Terry  <mike@mterry.name>

    fix some typos found when using pydev+eclipse

2009-11-26  ken

    459511 --tempdir option doesn't override TMPDIR

2009-11-26  ken

    487686 re-add scp backend and make available via command line option
    Option --use-scp will use scp, not sftp, for get/put operations.

2009-11-26  ken

    Applied patch 467391 to close connection on a 401 and retry
    with authentication credentials.

2009-11-09  ken

    CVS no longer used, so no longer needed.

2009-11-08  Kenneth Loafman  <kenneth@loafman.com>

    Merged in translations.

2009-11-08  Kenneth Loafman  <kenneth@loafman.com>

    Checkpoint.

2009-10-29  Kenneth Loafman  <kenneth@loafman.com>

    lp:~duplicity-team/duplicity/po-updates

2009-10-29  Kenneth Loafman  <kenneth@loafman.com>

    Merge in lp:~duplicity-team/duplicity/i18n-for-0.7

2009-10-02  Larry Gilbert  <larry+launchpad@l2g.to>

    i18nized a few error messages in duplicity.selection

2009-10-02  Larry Gilbert  <larry+launchpad@l2g.to>

    More strings internationalized in asyncscheduler and commandline

2009-10-29  Kenneth Loafman  <kenneth@loafman.com>

    Merge of lp:~mterry/duplicity/list-old-chains

2009-10-23  Michael Terry  <michael.terry@canonical.com>

    warn if we don't have signatures for the given date period

2009-10-22  Michael Terry  <michael.terry@canonical.com>

    allow deleting old signatures with cleanup --extra-clean

2009-10-19  Michael Terry  <michael.terry@canonical.com>

    don't delete signature chains for old backups; allow listing old backup chain files

2009-10-12  Michael Terry  <michael.terry@canonical.com>

    add missing par2_utils.py to dist tarball

2009-10-19  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2009-10-09  Kenneth Loafman  <kenneth@loafman.com>

    Remove unused __future__ imports.

2009-10-06  Kenneth Loafman  <kenneth@loafman.com>

    Add entry for patches from Stéphane Lesimple for par2.

2009-10-06  Kenneth Loafman  <kenneth@loafman.com>

    Applied patch from Stéphane Lesimple found at:
    https://bugs.launchpad.net/duplicity/+bug/426282/comments/5
    patch skips the par2 files when building up the sets and chains of backups

2009-10-06  Kenneth Loafman  <kenneth@loafman.com>

    Applied patch from Stéphane Lesimple found at:
    https://bugs.launchpad.net/duplicity/+bug/426282/comments/4
    patch avoids storing all the par2 files into the local cache

2009-10-03  Kenneth Loafman  <kenneth@loafman.com>

    Fixed 435975 gpg asks for password in 0.6.05, but not in 0.5.18

2009-09-25  Kenneth Loafman  <kenneth@loafman.com>

    Merge with trunk.

2009-04-11  Michael Terry  <mike@mterry.name>

    modify file name test to test short filenames even when not specifically requested to

2009-04-11  Michael Terry  <mike@mterry.name>

    accept short filenames even if not specifically requested

2009-09-20  Michael Terry  <michael.terry@canonical.com>

    ugh, I'm the worst; add missing import

2009-09-20  Michael Terry  <michael.terry@canonical.com>

    add extra information to the 'hostname changed' log message, split it from the 'source dir changed' message

2009-09-25  Kenneth Loafman  <kenneth@loafman.com>

    Fix problems with unittests under Jaunty.  It appears that redirection
    in os.system() has changed for the worse, so a workaround for now.

    Fix problem in restart where there were no manifest entries and no
    remote volumes stored.  We clean out the partial and restart.

2009-09-18  Kenneth Loafman  <kenneth@loafman.com>

    Applied "426282 [PATCH] par2 creating support", corrected some coding format issues and made sure all unit tests passed.

2009-09-15  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/iterate-warnings

2009-09-11  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2009-09-11  Kenneth Loafman  <kenneth@loafman.com>

    Clean up testing run scripts.

2009-09-08  Kenneth Loafman  <kenneth@loafman.com>

    * 422477 [PATCH] IMAP Backend Error in delete()

2009-12-13  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-11-10  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-12-14  ken

    Merged in lp:~mterry/duplicity/optparse

2009-12-13  Michael Terry  <mike@mterry.name>

    whoops, remove debug code

2009-12-13  Michael Terry  <mike@mterry.name>

    don't set xdg dirs in duplicity-bin now that globals.py is restored

2009-12-13  Michael Terry  <mike@mterry.name>

    use defaults from globals.py for commandline options

2009-12-13  Michael Terry  <mike@mterry.name>

    fix an undefined variable usage

2009-12-07  Michael Terry  <mike@mterry.name>

    fix a few typos

2009-12-14  ken

    Merged in lp:~mterry/duplicity/typos-0.6

2009-11-30  Michael Terry  <mike@mterry.name>

    fix typo with log-fd support

2009-11-30  Michael Terry  <michael.terry@canonical.com>

    first pass at getopt->optparse conversion

2009-12-13  Michael Terry  <mike@mterry.name>

    whoops, and this typo

2009-12-13  Michael Terry  <mike@mterry.name>

    fix some typos found when using pydev+eclipse (backported from 0.7 line)

2009-11-27  ken

    Remove antiquated file.

2009-11-27  ken

    Remove requirement for GnuPGInterface, we have our own.

2009-11-26  ken

    459511 --tempdir option doesn't override TMPDIR

2009-11-26  ken

    487686 re-add scp backend and make available via command line option
    Option --use-scp will use scp, not sftp, for get/put operations.

2009-11-26  ken

    Applied patch 467391 to close connection on a 401 and retry
    with authentication credentials.

2009-11-08  Kenneth Loafman  <kenneth@loafman.com>

    Merged in translations.

2009-10-30  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-11-08  Kenneth Loafman  <kenneth@loafman.com>

    Checkpoint.

2009-10-29  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.06

2009-10-29  Kenneth Loafman  <kenneth@loafman.com>

    lp:~duplicity-team/duplicity/po-updates

2009-10-24  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-10-29  Kenneth Loafman  <kenneth@loafman.com>

    Merge of lp:~mterry/duplicity/list-old-chains-0.6

2009-10-23  Michael Terry  <michael.terry@canonical.com>

    merge old-chain signature work from 0.7 branch; keep old sigs around, allow listing them, warn if a too-old listing is requested

2009-10-19  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2009-10-17  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-30  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-10-10  kenneth@loafman.com

    Remove .cvsignore

2009-10-09  Kenneth Loafman  <kenneth@loafman.com>

    Remove unused __future__ imports.

2009-10-03  Kenneth Loafman  <kenneth@loafman.com>

    Fixed 435975 gpg asks for password in 0.6.05, but not in 0.5.18

2009-09-25  Kenneth Loafman  <kenneth@loafman.com>

    Merge with trunk.

2009-09-20  Michael Terry  <michael.terry@canonical.com>

    ugh, I'm the worst; add missing import

2009-09-20  Michael Terry  <michael.terry@canonical.com>

    whoops, use error code 42, not 41 -- that's for par2

2009-09-20  Michael Terry  <michael.terry@canonical.com>

    add extra information to the 'hostname changed' log message, split it from the 'source dir changed' message

2009-09-25  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2009-09-23  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-22  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-21  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-20  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-19  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-18  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-17  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-16  Launchpad Code Hosting  <codehost@crowberry>

    Launchpad automatic translations update.

2009-09-25  Kenneth Loafman  <kenneth@loafman.com>

    Fix problems with unittests under Jaunty.  It appears that redirection
    in os.system() has changed for the worse, so a workaround for now.

    Fix problem in restart where there were no manifest entries and no
    remote volumes stored.  We clean out the partial and restart.

2009-09-15  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~mterry/duplicity/iterate-warnings

2009-09-14  Michael Terry  <michael.terry@canonical.com>

    add some machine codes to various warnings when iterating over source files

2009-09-11  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2009-09-07  Larry Gilbert  <larry+launchpad@l2g.to>

    Additional Portuguese and brand-new Bulgarian translations

2009-09-07  Larry Gilbert  <larry+launchpad@l2g.to>

    merge latest 0.6

2009-09-11  Kenneth Loafman  <kenneth@loafman.com>

    Clean up testing run scripts.

2009-09-08  Kenneth Loafman  <kenneth@loafman.com>

    * 422477  [PATCH] IMAP Backend Error in delete()

2009-09-06  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~l2g/duplicity/bug-411375

2009-09-04  Larry Gilbert  <larry+launchpad@L2G.to>

    Change message "--cleanup option" to "'cleanup' command"

2009-09-06  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~duplicity-team/duplicity/po-updates

2009-09-04  Larry Gilbert  <larry+launchpad@L2G.to>

    Translation of Spanish and Portuguese has begun

2009-09-04  Larry Gilbert  <larry+launchpad@L2G.to>

    Updated existing PO files with Rosetta translations

2009-09-02  Kenneth Loafman  <kenneth@loafman.com>

    Merged in lp:~l2g/duplicity/flag-transl-comments which cleared up how\ntranslation comments should be passed to the translators cleanly now.

2009-08-31  Larry Gilbert  <larry+launchpad@l2g.to>

    When generating PO[T] files, only use code comments starting with "TRANSL:"
    for notes to the translators.  "TRANSL:" is filtered out of the POT file
    with sed after it's generated.

2009-09-02  Kenneth Loafman  <kenneth@loafman.com>

    Applied patches from Kasper Brand that fixed device file handling.
    http://lists.gnu.org/archive/html/duplicity-talk/2009-09/msg00001.html

2009-08-28  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.05.

2009-08-28  Kenneth Loafman  <kenneth@loafman.com>

    Merged in ~l2g/duplicity/test-compat from Larry Gilbert which made
    the testing compatible across more systems.  Also fixed the remaining
    collectionstest bug which was trying to test with no cache present.

2009-08-26  Larry Gilbert  <larry+launchpad@l2g.to>

    Test separate filesystems using /dev instead of /proc (more widely used)

2009-08-23  Larry Gilbert  <larry+launchpad@l2g.to>

    dd on Darwin (and FreeBSD?) doesn't like e.g. "bs=1K", so changed it to "bs=1024"

2009-08-23  Larry Gilbert  <larry+launchpad@l2g.to>

    "cp -pR" seems to be a better analogue to "cp -a".  This may not be perfect
    but it won't hang on a fifo copy like "cp -pr".

2009-08-23  Larry Gilbert  <larry+launchpad@l2g.to>

    Got test_get_extraneous working in collectionstests.py

2009-08-19  Larry Gilbert  <larry+launchpad@l2g.to>

    Unpacked testfiles.tar.gz on Mac OS X file system and repacked as new file

2009-08-14  Larry Gilbert  <larry+launchpad@l2g.to>

    Changed options to 'cp' to be compatible with BSD style yet (hopefully)
    stay compatible with GNU

2009-08-14  Larry Gilbert  <larry+launchpad@l2g.to>

    Took care of some redundancy in tar usage

2009-08-14  Larry Gilbert  <larry+launchpad@l2g.to>

    Use bash "command" command to look for Python binaries beyond /usr/bin

2009-08-25  Kenneth Loafman  <kenneth@loafman.com>

    418170  [PATCH] file names longer then 512 symbols are not supported

2009-08-25  Kenneth Loafman  <kenneth@loafman.com>

    408059  Failure due to _logger.log failure for content with special characters: TypeError decoding Unicode not supported

2009-08-12  Larry Gilbert  <larry+launchpad@L2G.to>

    "remove-older-than" asks for passphrase even though not required; watch for correct internal action name to fix this

2009-08-12  Larry Gilbert  <larry+launchpad@L2G.to>

    "remove-older-than" asks for passphrase even though not required; watch for correct internal action name to fix this

2009-08-11  Larry Gilbert  <larry+launchpad@l2g.to>

    Typo in remove-older-than may have caused unnecessary passphrase prompts?

2009-08-06  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.5.19.

2009-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Fix getrlimit usage for Cygwin, which was returning -1 for the hard limit on max open files

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * ignore unicode() translation errors in log messsages.

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * Make sure 'invalid packet (ctb=14)' from gpg is not a fatal error.

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * On processes that complete before waitpid(), log them and return zero as the process.returned value.  They will have already trapped in the main thread if they returned in error.

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * Copy changes from trunk for duplicity translation.

2009-08-12  Kenneth Loafman  <kenneth@loafman.com>

    Comment out Pydev debug startup code.

2009-08-12  Kenneth Loafman  <kenneth@loafman.com>

    Merge from trunk.

2009-08-11  Larry Gilbert  <larry+launchpad@l2g.to>

    Typo in "remove-older-than" may have caused unnecessary passphrase prompts?

2009-08-12  Kenneth Loafman  <kenneth@loafman.com>

    * Fixed #409593 deja-dup (or duplicity) deletes all signatures

2009-08-05  Kenneth Loafman  <kenneth@loafman.com>

    Merge GIO changes from trunk.

2009-08-02  Michael Terry  <michael.terry@canonical.com>

    allow gio backend to restore by setting correct state.  LP: #407968

2009-08-01  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.04.

2009-08-01  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.04.

2009-08-01  Kenneth Loafman  <kenneth@loafman.com>

    Fixed 405734 duplicity fails to restore files that contain a newline character

2009-07-30  Kenneth Loafman  <kenneth@loafman.com>

    Fixed 403790 Backup error: No such file or directory

2009-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Last changes for 0.6.03.

2009-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.03.

2009-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.03.

2009-07-29  Kenneth Loafman  <kenneth@loafman.com>

    Fixed 402794 duplicity public-key-only incompatible with gnupg 2.0.11.

2009-07-28  Kenneth Loafman  <kenneth@loafman.com>

    Fixed 405975 duplicity.gpg.gpg_failed() breaks and spews on GnuPG error.

2009-07-28  Kenneth Loafman  <kenneth@loafman.com>

    Fixed 398230 Deja-dup backup fails with message: "Unable to locate last file"

2009-07-28  Kenneth Loafman  <kenneth@loafman.com>

    Fix bug 405646 Small i18n error.

2009-07-25  Larry Gilbert  <from-launchpad@l2g.to>

    Oops, one too many things in usage() were dictionarified

2009-07-28  Kenneth Loafman  <kenneth@loafman.com>

    Minor header comment correction.

2009-07-28  Kenneth Loafman  <kenneth@loafman.com>

    Adjust to file renames.

2009-07-27  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~l2g/duplicity/doc-update.

2009-07-21  Larry Gilbert  <from-launchpad@l2g.to>

    Sorry... I missed the point being made here...

2009-07-21  Larry Gilbert  <lgilbert@digium.com>

    Minor capitalization changes in the manpage

2009-07-21  Larry Gilbert  <lgilbert@digium.com>

    CVS-README changed to REPO-README and updated with Launchpad/bzr info

2009-07-27  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~l2g/duplicity/i18n-update-1.

2009-07-25  Larry Gilbert  <from-launchpad@l2g.to>

    Redid dictionary in usage to use a local hash instead of a bunch of local
    variables, to make things a tad more pleasant.

2009-07-25  Larry Gilbert  <from-launchpad@l2g.to>

    Broke up the usage() help info to simplify translation maintenance.
    Imported .po files from Launchpad Translation (not sure how necessary
    they are to have in here, but here they are.)

2009-07-25  Larry Gilbert  <from-launchpad@l2g.to>

    Updated some intltool config info

2009-07-25  Larry Gilbert  <from-launchpad@l2g.to>

    Updated *.po and *.pot files

2009-07-27  Kenneth Loafman  <kenneth@loafman.com>

    Fix restart issues when local manifest does not agree with the contents of the remote system.  In all cases, clean up as needed, and restart the backup at the last known good state.

2009-07-27  Kenneth Loafman  <kenneth@loafman.com>

    Refactor to put loop outside of try/except clause.

2009-07-27  Kenneth Loafman  <kenneth@loafman.com>

    BackupSet.delete() now removes both local and remote files.

2009-07-27  Kenneth Loafman  <kenneth@loafman.com>

    Make testing into a module.

2009-07-25  Kenneth Loafman  <kenneth@loafman.com>

    Capture stderr as well as logger and display stderr with logger only if gpg fails.  Cuts out some of the noise from gpg.

2009-07-25  Kenneth Loafman  <kenneth@loafman.com>

    Split restarttest.py from finaltest.py for ease in debugging.

2009-07-22  Kenneth Loafman  <kenneth@loafman.com>

    * fix test config to import backends (now optional).

2009-07-20  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~scode/duplicity/misc.

2009-07-08  Peter Schuller  <peter.schuller@infidyne.com>

    * s/pair/tuple/ (method doc fix)

2009-07-08  Peter Schuller  <peter.schuller@infidyne.com>

    * when doing the "sleep to make sure we have different current time than last backup":
    - sleep for 2 seconds instead of 1, since it is an expected case that time may be moving
    slightly slower as a result of adjtime() and such
    - assert afterwards that current time really does differ from previous time

2009-07-08  Peter Schuller  <peter.schuller@infidyne.com>

    * merge latest trunk

2009-07-20  Kenneth Loafman  <kenneth@loafman.com>

    Update .bzrignore only.

2009-07-19  Kenneth Loafman  <kenneth@loafman.com>

    * fixed 401303 0.6.2 manpage inconsistent wrt. archive-dir/name

2009-07-19  Kenneth Loafman  <kenneth@loafman.com>

    * fix 377528 --file-to-restore doesn't work with trailing slash

2009-07-15  Kenneth Loafman  <kenneth@loafman.com>

    * First pass at bug 394757 - Optional Backends
    https://bugs.launchpad.net/bugs/394757

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * ignore unicode() translation errors in log messsages.

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * Make sure 'invalid packet (ctb=14)' from gpg is not a fatal error.

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * On processes that complete before waitpid(), log them and return zero as the process.returned value.  They will have already trapped in the main thread if they returned in error.

2009-07-10  Kenneth Loafman  <kenneth@loafman.com>

    * Use correct name of error class ConflictingScheme.

2009-07-08  Kenneth Loafman  <kenneth@loafman.com>

    Make Changelog.GNU close to GNU Changelog format.

2009-07-08  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.02.

2009-07-07  Kenneth Loafman  <kenneth@loafman.com>

    Another attempt at fixing #394629 Hang on first collection-status.

2009-07-07  Kenneth Loafman  <kenneth@loafman.com>

    Fix Bug #395826 "No such file or directory" when backing up second time

2009-07-06  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~scode/duplicity/archive-sync-removelocal and fixes.

2009-07-04  Peter Schuller  <peter.schuller@infidyne.com>

    * optimistically try to resolve final issue by passing ParseResult:s sense of what's what to
    get_suffix() rather than hard-coding based on manifest. not sure if this has other bad side-effects
    though - will discuss on ML.

2009-07-04  Peter Schuller  <peter.schuller@infidyne.com>

    * nuke accidentally added characters in comments - left control is breaking on my keyboard...

2009-07-04  Peter Schuller  <peter.schuller@infidyne.com>

    * initial stab (broken): synch both ways; i.e., remove spurious local files in addition to downloading missing ones
    * problem remaining with determining the correct local name

2009-07-05  Kenneth Loafman  <kenneth@loafman.com>

    Fix bug #394629 Hang on first collection-status

2009-07-04  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~scode/duplicity/ignore-errors

2009-07-04  Peter Schuller  <peter.schuller@infidyne.com>

    * support an --ignore-errors command which is intended to mean "try to continue in the face of" errors
    that might possibly be okay to ignore
    - intended during restoration to avoid bailing out on errors that are not fatal yet would in fact
    produce an "incorrect" restoration
    - for now, only changes behavior on file meta data restoration where I happened to have a problem
    (I had a +t file which was impossible to restore to +t even though it was possible for it to
    exist and for me to read it)
    - be clear in the man page that this is only supposed to be used in case of problems and even then
    to please contact maintainer if use is needed

2009-07-04  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~scode/duplicity/misc

2009-07-04  Peter Schuller  <peter.schuller@infidyne.com>

    * print archive directory in a more readable fashion #394627

2009-07-04  Kenneth Loafman  <kenneth@loafman.com>

    Update ignore list.

2009-07-04  Kenneth Loafman  <kenneth@loafman.com>

    Fixes: [Bug 379386] Fix 'list-current-files' with missing archive dir

2009-07-03  Michael Terry  <michael.terry@canonical.com>

    merge from lp:~mterry/duplicity/po-fixes: reorganize po directory, so that we can start translating in LP

2009-07-02  Michael Terry  <michael.terry@canonical.com>

    fix po dir layout, update POTFILES.in, add pot file to bzr

2009-07-01  Kenneth Loafman  <kenneth@loafman.com>

    Changes for 0.6.01.

2009-07-01  Kenneth Loafman  <kenneth@loafman.com>

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

2009-06-27  Kenneth Loafman  <kenneth@loafman.com>

    Fixes bug 392905.  Allow omission of remote file name if the same as the source file name.

2009-06-25  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~kenneth-loafman/duplicity/smart-archive-v2

2009-06-23  kenneth@loafman.com

    * Change to use XDG_ convention per http://standards.freedesktop.org/basedir-spec/latest/

2009-06-23  kenneth@loafman.com

    * Change handling of smart archive dir so both archive and name can be changed.

2009-06-24  Michael Terry  <michael.terry@canonical.com>

    merge lp:~mterry/duplicity/gio-dist-fix to distribute gio backend

2009-06-24  Michael Terry  <michael.terry@canonical.com>

    merge from trunk

2009-06-24  Michael Terry  <michael.terry@canonical.com>

    actually distribute the gio backend

2009-06-24  kenneth@loafman.com

    Fix "external file not found" to show command and file names.

2009-06-23  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~scode/duplicity/smart-default-archive

2009-06-23  kenneth@loafman.com

    Avoid deprecation warning for md5 in Python 2.6.

2009-06-22  Peter Schuller  <peter.schuller@infidyne.com>

    * --name affects *expansion*, not default value, of --archive-dir

2009-06-22  Peter Schuller  <peter.schuller@infidyne.com>

    * fix a man page mistake from previous merge
    * remove last remnants of DUPLICITY_ARGS_HASH

2009-06-22  Peter Schuller  <peter.schuller@infidyne.com>

    * correct man page to claim hash of backend url rather than has of args

2009-06-22  Peter Schuller  <peter.schuller@infidyne.com>

    * figure out which arg is a backend url without actually instantiating a backend

2009-06-22  Peter Schuller  <peter.schuller@infidyne.com>

    * make default value to --name be the has of the backend URL specifically, rather than
    the has of remaining args
    * outstanding issue: in order to figure out which arg is a backend we call get_backend();
    must either fix this or feel comfortable that instantiating (and not using) a backend
    is side-effect free

2009-06-22  Peter Schuller  <peter.schuller@infidyne.com>

    * introduce --name parameter to specify symbolic name of a backup
    * change --archive-dir expansion to look for %DUPLICITY_BACKUP_NAME%
    * which in turn defaults to the args hash previously used for
    --archive-dir and %DUPLICITY_ARGS_HASH% expansion

2009-06-22  Peter Schuller  <peter.schuller@infidyne.com>

    * merge from trunk

2009-06-15  Peter Schuller  <peter.schuller@infidyne.com>

    * support expansion of %DUPLICITY_ARGS_HASH% in --archive-dir value
    * default to ~/.duplicity/%DUPLICITY_ARGS_HASH$ so that default behavior
    works well even when the user has multiple backup destinations
    * update the manpage accordingly

2009-06-23  kenneth@loafman.com

    Misc project changes.

2009-06-23  kenneth@loafman.com

    If python is run setuid, it's only partway set, so make sure to run with euid/egid of root.

2009-06-23  kenneth@loafman.com

    Create testfiles/output in SetUp routine so it will run standalone.

2009-06-21  kenneth@loafman.com

    Surround --gio option with try/except so user will not see traceback.

2009-06-21  kenneth@loafman.com

    Make GIO tests dependent on presence of gio module.

2009-06-21  kenneth@loafman.com

    Fix 'get' command args.

2009-06-21  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~cjwatson/duplicity/always-sftp

2009-05-06  Colin Watson  <cjwatson@canonical.com>

    initial attempt at using only sftp on the client (https://savannah.nongnu.org/bugs/index.php?26464)

2009-06-21  Kenneth Loafman  <kenneth@loafman.com>

    Add .bzrignore

2009-06-18  Michael Terry  <michael.terry@canonical.com>

    merge with trunk

2009-06-20  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~scode/duplicity/bug-387102

2009-06-18  Peter Schuller  <peter.schuller@infidyne.com>

    * merge lp:~mterry/duplicity/log-upload-events since I created conflicts with my
    changes

2009-06-16  Peter Schuller  <peter.schuller@infidyne.com>

    * s/self.__waiter/self.__failed_waiter/

2009-06-16  Peter Schuller  <peter.schuller@infidyne.com>

    * significantly re-design the asynch scheduler to be much simpler; instead of keeping workers
    and queues, simply launch a thread for each unit of work, blocking when called for by
    a concurrency limit or a barrier. the old design was a result of initially designing for
    keeping a persistent set of workers, only to then drop that idea. when dropping that idea,
    I should have re-done it like this from the start instead of retaining the complexity
    i introduced for the persistent worker design.

2009-06-20  Kenneth Loafman  <kenneth@loafman.com>

    merge of lp:~scode/duplicity/reasonable-io-blocksize

2009-06-16  Peter Schuller  <peter.schuller@infidyne.com>

    * GPGWriteFile: what was previously the minimum block is is now just the block size; meaning
    the maximum block size used for individual I/O operations, but still the minimum in terms
    of when to give up on the iteration
    * GZipWriteFile: similar change, though blocksize handling was a bit different

2009-06-20  kenneth@loafman.com

    Fix regression -- add tahoebackend back in.

2009-06-19  Kenneth Loafman  <kenneth@loafman.com>

    s/src.name/self.src.name/ in exception handling path

2009-06-15  Peter Schuller  <peter.schuller@infidyne.com>

    * s/src.name/self.src.name/ in exception handling path

2009-06-18  Michael Terry  <michael.terry@canonical.com>

    merge log worker event info codes

2009-05-31  Michael Terry  <michael.terry@canonical.com>

    add log codes for upload events

2009-06-18  Michael Terry  <michael.terry@canonical.com>

    Merge GIO branch, supporting the --gio argument

2009-06-04  Michael Terry  <michael.terry@canonical.com>

    don't be so specific about exceptions we catch

2009-06-04  Michael Terry  <michael.terry@canonical.com>

    add GIO backend

2009-05-30  Michael Terry  <michael.terry@canonical.com>

    add info codes for upload events

2009-06-18  kenneth@loafman.com

    Fix omitted changes in duplicity manpage.

2009-06-08  loafman

    Changes for 0.6.0.

2009-06-08  loafman

    Some cleanup on the forced assertion test code to allow
    multiple failures and no traceback for the assert.

2009-06-08  loafman

    Add code for testing of Checkpoint/Restore that I had been doing by hand, both single and multiple failure tests, with verify at the end.

2009-06-07  loafman

    Fix getrlimit usage for Cygwin, which was returning -1 for the hard limit on max open files.

2009-06-06  loafman

    After merge of Checkpoint/Restart.

2009-06-06  loafman

    Checkpoint - Prep for merge of duplicity-cprs.

2009-06-06  loafman

    Allow handling of unicode filenames in log messages.

2009-05-20  loafman

    Changes for 0.5.18.

2009-05-20  loafman

    Changes for 0.5.18.

2009-05-14  loafman

    Correct copyright.

2009-05-13  loafman

    Reset file type preferences.

2009-05-13  loafman

    Changed from using ulimit external command to
    resource.getrlimit to check open files limit.

2009-05-13  loafman

    patch #6743: Tahoe backend for duplicity
    https://savannah.nongnu.org/patch/?6743

2009-05-13  loafman

    Only half of this bug is fixed but it's still useful.
    bug #21792: pipe call fails with an error OSError:
    [Errno 24] Too many open files
    https://savannah.nongnu.org/bugs/?21792

2009-05-07  loafman

    Added support for RackSpace's CloudFiles, cf+http.

2009-05-07  loafman

    Add more detail on connection failure.

2009-05-07  loafman

    Added support for RackSpace's CloudFiles, cf+http.

2009-05-04  loafman

    Changes for 0.5.17.

2009-05-02  loafman

    Checkpoint.

2009-05-02  loafman

    The previous revision got the wrong comment, so
    I cleaned up some code and checked back in.  The
    correct release comment should be:

    patch #6814: Ignore comments in filelists
    https://savannah.nongnu.org/patch/?6814

2009-05-02  loafman

    patch #6813: Making changelist easy to read
    https://savannah.nongnu.org/patch/?6813

2009-05-02  loafman

    Moved from using the df command to get temp space
    availability to Python's os.statvfs() call.  Not all df
    commands work the same way.

2009-04-22  loafman

    I had put in some trial code that I removed incompletely that forced
    a full backup action.  This removes the last line of that code.

2009-04-21  loafman

    Changes for 0.5.16.

2009-04-21  loafman

    Reduce max_open_files limit needed to 1024, was 2048.

2009-04-21  loafman

    Fix argument list in FatalError call re max open files.

2009-04-21  loafman

    bug #24825: duplicity warn on insufficient TMPDIR
    space availability and low max open
    file limits pre-backup.
    https://savannah.nongnu.org/bugs/?24825

    bug #25976: Password requested when not needed.
    https://savannah.nongnu.org/bugs/?25976

2009-04-21  loafman

    Use os.access() check on regular files and dirs only.

2009-04-21  loafman

    Added tilde and variable expansion to the source or
    target argument that is not a URL.

2009-04-21  loafman

    Remove check for only one $version string.

2009-04-21  loafman

    bug #24825: duplicity warn on insufficient TMPDIR
    space availability and low max open
    file limits pre-backup.
    https://savannah.nongnu.org/bugs/?24825

2009-04-21  loafman

    bug #25976: Password requested when not needed.
    https://savannah.nongnu.org/bugs/?25976

2009-04-21  loafman

    Make sure gettext is included first.
    Add variable at top of file for verbosity.

2009-04-21  loafman

    Add some documentation.

2009-04-21  loafman

    Make sure gettext is available by importing first.

2009-04-13  loafman

    Move ssh and imap backend globals to globals.py.

2009-04-12  loafman

    patch #6806: More graceful handling of old
    --short-filename files
    https://savannah.nongnu.org/patch/?6806

2009-04-11  loafman

    bug #25594: wrong backup statistics
    https://savannah.nongnu.org/bugs/?25594

2009-04-10  loafman

    Not needed.

2009-04-09  loafman

    Changes for 0.5.15.

2009-04-09  loafman

    If a file is unreadable due to access rights or other
    non-fatal errors, put out error message and continue
    rather than dying messily with a traceback.

2009-04-09  loafman

    Move SystemExit function back to the top and put
    a large note NOT to move it back down, otherwise,
    Exception gets invoked instead.

2009-04-09  loafman

    Remove "--restore-dir" from options[].
    It's not an option and never has been.

2009-04-09  loafman

    Added tilde '~' expansion and variable expansion in the
    options that require a filename.  You can now have this
    "--archive-dir=~/ArchDir/$SYSNAME" if you need it.  No
    expansion is applied to the source or target URL's.

2009-04-07  loafman

    Unit tests were failing for ftp because of the filtering for
    duplicity-only filenames.  Corrected this and removed
    the check for the filename in the first element.

2009-04-07  loafman

    If a file is unreadable due to access rights or other non-
    fatal errors, put out error message and continue.

2009-04-03  loafman

    FTP backend was failing on PureFTPd when the "-x ''"
    option was removed from the second ncftpls popen, a fix
    that was implemented due to bug #24741.  This fix does
    the ls in one pass by extracting either the first or the
    last entry on the 'ls -l'.  [Standard FTP would be nice!]

2009-04-02  loafman

    Changes for 0.5.14.

2009-04-02  loafman

    Normalized include statements and tried to insure that all
    duplicity includes were from the duplicity module.

2009-04-01  loafman

    After email voting among known duplicity contributors,
    the decision was reached to revert to the GPL Version 2
    license, so with their consensus, duplicity is now under
    GPL Version 2.

2009-03-31  loafman

    The -vN option has not changed.  Verbosity may also be one
    of: character [ewnid], or word ['error', 'warning', 'notice',
    'info', 'debug'].  The default is 4 (Notice).  The options
    -v4, -vn, and -vnotice are functionally equivalent, as are
    the mixed-case versions, -vN, -vNotice, -vNOTICE.

2009-03-31  loafman

    The -vN option has not changed.  Verbosity may also be one
    of: character [ewnid], or word ['error', 'warning', 'notice',
    'info', 'debug'].  The default is 4 (Notice).  The options
    -v4, -vn, and -vnotice are functionally equivalent, as are
    the mixed-case versions, -vN, -vNotice, -vNOTICE.

2009-03-30  loafman

    patch #6790: Add --exclude-if-present
    https://savannah.nongnu.org/patch/?6790

2009-03-30  loafman

    Clarify recent log entries.

2009-03-30  loafman

    Add '../' to Python path so we find our GnuPGInterface and not another.

2009-03-29  loafman

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

2009-03-29  loafman

    Revert to calling NcFTP utilities (ls, get, put) directly
    rather than scripting ncftp via pexpect.  Move fatal error
    regarding version 3.2.0 to a warning message since it has
    been reported that the segfault problem does not occur on
    most distributions.

2009-03-26  loafman

    Add Changelog.GNU to website and distribution to add a bit of detail
    showing the CVS changes via rcs2log.  Added dist/mkGNUChangelog.sh.

2009-03-25  loafman

    bug #22908: Don't block gpg-agent
    https://savannah.nongnu.org/bugs/?22908

    To fix the above, --use-agent was added as a command line option.
    When this is specified and asymetric encryption is enabled, then all
    GnuPG passphrases will come from the gpg-agent or equivalent program
    and no passphrase prompt will be issued.

2009-03-25  loafman

    Add testing/manual dir.

2009-03-23  loafman

    bug #25976: Signed Backups Now Required
    https://savannah.nongnu.org/bugs/?25976

2009-03-21  loafman

    patch #6787: import duplicity.GnuPGInterface explicitly
    https://savannah.nongnu.org/patch/?6787

2009-03-21  loafman

    Project setting changes.

2009-03-21  loafman

    One statement per line.
    Indent text of error message to code level.

2009-03-19  loafman

    Fixed bug where an extra comma caused a traceback during a warning
    about unnecessary sig files.  Plus fixed print so the real filename
    would show up and not a Python object representation.

2009-03-19  loafman

    bug #25787: Usernames with escaped @-sign are not handled properly
    https://savannah.nongnu.org/bugs/?25787

2009-03-18  loafman

    Adjust log levels so errors show up without verbosity.

2009-03-17  loafman

    BackendException does not cause traceback except when
    verbosity is at level 9 (debug).

2009-03-17  loafman

    Fix backends so sleep does not occur after last retry.

2009-03-17  loafman

    Add more error detection to FTP backend.

    Fix backends so sleep does not occur after last retry.

2009-03-15  loafman

    patch #6773: Make user name optional in rsync backend
    https://savannah.nongnu.org/patch/?6773

2009-03-15  loafman

    bug #25853: duplicity fails with boto passwords coming from ~/.boto
    https://savannah.nongnu.org/bugs/?25853

2009-03-15  loafman

    GPG errors will no longer cause tracebacks, but will produce a
    log entry, from gpg, similar to the following:
    ===== Begin GnuPG log =====
    gpg: BAD0BAD0: skipped: public key not found
    gpg: [stdin]: encryption failed: public key not found
    ===== End GnuPG log =====
    This will let the user know what really caused the GPG process
    to fail, and what really caused errors like 'broken pipe'.

2009-03-12  loafman

    bug #25838: Backup fails / ncftp - remote file already exists
    https://savannah.nongnu.org/bugs/?25838

2009-03-11  loafman

    Add / modify / repair Epydoc docstrings and format.

2009-03-11  loafman

    One statement per line.

2009-03-11  loafman

    One statement per line.

2009-03-08  loafman

    Changes for 0.5.11.

2009-03-08  loafman

    Bug #333057: GnuPGInterface prints exit statuses incorrectly
    https://bugs.launchpad.net/bugs/333057

2009-03-08  loafman

    bug #25787: Usernames with @-sign are not handled properly
    https://savannah.nongnu.org/bugs/?25787

2009-03-08  loafman

    Detabify (was tab-width 8).

2009-03-07  loafman

    Bug #333057: GnuPGInterface prints exit statuses incorrectly
    https://bugs.launchpad.net/bugs/333057

2009-03-07  loafman

    Fix issue on return from waitpid where the result was shifted left and not right, producing 131072 instead of 2, as it should.

    Fixed some indent problems that PyDev complained about (Eclipse IDE).

2009-03-07  loafman

    One statement per line.

2009-03-07  loafman

    bug #25696: ncftp error with 0.5.09
    https://savannah.nongnu.org/bugs/?25696

2009-03-06  loafman

    Also log the quit command.

2009-03-02  loafman

    One statement per line.

2009-03-02  loafman

    bug #15664: When restoring backup: "OverflowError:
    long int too large to convert to int"
    https://savannah.nongnu.org/bugs/?15664

2009-03-02  loafman

    One statement per line.

2009-03-02  loafman

    patch #6761: More robust pexpect handling of SSH authentication
    https://savannah.nongnu.org/patch/?6761

2009-03-02  loafman

    patch #6762: Wrong exit() used for 2.3/2.4 Python
    https://savannah.nongnu.org/patch/?6762

2009-03-02  loafman

    One statement per line.

2009-03-01  loafman

    Explain new filenames and --time-separator better.

2009-03-01  loafman

    Changes for 0.5.10.

2009-03-01  loafman

    Add deprecation warnings for options affected by old filenames.

2009-03-01  loafman

    bug #19988: Incompatibility to Samba/SMB share
    https://savannah.nongnu.org/bugs/?19988

2009-02-28  loafman

    One statement per line.

2009-02-28  loafman

    One statement per line.

2009-02-27  loafman

    Module gettext should be imported and installed prior to importing any other modules.  This allows long strings to be translated when put at the module level rather than at the function call level.  See dup_time.py for examples.

2009-02-27  loafman

    One statement per line and other cleanup.

2009-02-24  loafman

    bug #25550: Error codes do not propagate from log to exit status
    https://savannah.nongnu.org/bugs/?25550

2009-02-21  loafman

    bug #25097: Allow listing files from any time, not just current time
    https://savannah.nongnu.org/bugs/?25097

2009-02-20  loafman

    Bug #229826 duplicity crashed with ValueError in port()
    https://bugs.launchpad.net/duplicity/+bug/229826

2009-02-17  loafman

    Changes for 0.5.09.

2009-02-13  loafman

    If tempdir.py is included, but not instantiated, then deleted, it throws an exception,
    as happens during testing when duplicity main is not used to instantiate tempdir.
    The fix is to make sure instantiation has happened before calling cleanup().

2009-02-13  loafman

    These are changes to make debugging easier.
    - Filter ANSI control (bolding) characters from NcFTP responses.
    - Turn off ad for ncftp server at close of each session.

2009-02-10  loafman

    bug #25530: commandline passwd not working
    https://savannah.nongnu.org/bugs/?25530

2009-02-10  loafman

    FTP is now driven with pexpect rather than NcFTP utilities.
    This closes the following bugs:
    bug #24741: ncftpls -x '' causes failure on Yahoo FTP server
    bug #23516: duplicity/ncftpget not closing unlinked files, ...

2009-02-10  loafman

    Merge from pexpect_ftp.

2009-02-09  loafman

    Applied retryImap2.patch from bug 25512.

2009-02-08  loafman

    bug #25509: Logic error in imapbackend.py [IMAP_SERVER]
    https://savannah.nongnu.org/bugs/?25512

    bug #25512: [Patch] Retry on Imap failure
    https://savannah.nongnu.org/bugs/?25509

2009-02-08  loafman

    Replace rdiff-backup with duplicity in strings.

2009-02-07  loafman

    Add copyright for author.

2009-02-07  loafman

    Split parsedurl test from backendtest and add test cases.

2009-02-05  loafman

    Add NcFTP 3.2.0 exception clause to dependencies.

2009-02-02  loafman

    Turns out going backwards in the license is not as easy as
    forwards.  Restoring GPLv3 license until consensus reached.

2009-02-01  loafman

    Add/update copyright statements in all distribution source files
    and revert duplicity to GPL version 2 license.

2009-01-31  loafman

    Changes for 0.5.07.

2009-01-31  loafman

    Python 2.3 unittest.py tried to call to a test-local variable named
    'test_id' and failed.  Changed to 'my_test_id' and all is well.

2009-01-30  loafman

    Original fix to disallow use of ncftpput 3.2.0 mistyped the ErrorCode used.

2009-01-28  loafman

    patch #6733: Improve error handling in imapbackend.py
    https://savannah.nongnu.org/patch/?6733

2009-01-27  loafman

    Add/update copyright statements in all distribution source files
    and revert duplicity to GPL version 2 license.

2009-01-27  loafman

    patch #6729: New imap backend. Replaces current gmail backend
    https://savannah.nongnu.org/patch/?6729

2009-01-25  loafman

    bug #25293: IOError: [Errno 22] Invalid argument
    https://savannah.nongnu.org/bugs/?25293

2009-01-25  loafman

    Modify patch #6730: Fix timing out for SSH backend
    Do not take out the first line from the return buffer (#4).

2009-01-25  loafman

    patch #6730: Fix timing out for SSH backend
    https://savannah.nongnu.org/patch/?6730

2009-01-25  loafman

    patch #6729: New imap backend. Replaces current gmail backend
    https://savannah.nongnu.org/patch/?6729

2009-01-25  loafman

    Removed ref to bug 25331 since the analysis and fix were both wrong.
    The issue was fixed correctly in bug 25403.

2009-01-25  loafman

    bug #25403: 0.5.06 "manifests not equal because different volume numbers"
    https://savannah.nongnu.org/bugs/?25403

2009-01-25  loafman

    bug #25403: 0.5.06 "manifests not equal because different volume numbers"
    https://savannah.nongnu.org/bugs/?25403

2009-01-25  loafman

    One statement per line.

2009-01-24  loafman

    Move alltests list to separate file.

2009-01-24  loafman

    Add coverage output to .cvsignore.

2009-01-24  loafman

    Turn on verbose for unit tests.

2009-01-24  loafman

    Fix backendtest.py so that empty URL's in config.py cause the
    backend test to be skipped rather than erroring.  Added notes
    in config.py.tmpl explaining the change.

2009-01-23  loafman

    Make default Python be system default version.

2009-01-23  loafman

    Add Releases directory.

2009-01-23  loafman

    First pass at coverage analysis, collect the data.

2009-01-23  loafman

    Remove LOG entries.  Not needed.

2009-01-23  loafman

    Change to ASCII (-kkv)

2009-01-23  loafman

    Run a single unit test.

2009-01-22  loafman

    Increase default volume size (--volsize) to 25M from 5M.  This
    reduces the number of volumes to accomodate larger backups.

2009-01-22  loafman

    bug #25379: sys.exit() causes traceback and should not
    https://savannah.nongnu.org/bugs/index.php?25379

2009-01-18  loafman

    Reworked patch 6701 to list collection one at a time rather than
    writing all as one huge list.  Was causing memeory problems when
    the collections got large.

2009-01-15  loafman

    bug #25331: When --archive-dir and --encrypt-key are used together, incremental fails.
    https://savannah.nongnu.org/bugs/index.php?25331

2009-01-15  loafman

    bug #25331: When --archive-dir and --encrypt-key are used together, incremental fails.
    https://savannah.nongnu.org/bugs/index.php?25331

2009-01-09  loafman

    Changes for 0.5.06.

2009-01-08  loafman

    Fix illegal macro .PP. by removing extraneous period on end.

2009-01-07  loafman

    NcFTP version 3.2.0 will not work with duplicity since we require the
    use of both -f and -C options on ncftpput.  3.1.9, 3.2.1+ work fine.
    I put in error checks for this situation in the FTP backend code.

2009-01-06  loafman

    Noah Spurrier has given us permission to distribute pexpect.py along
    with duplicity, so this will no longer be an install requirement.

2009-01-06  loafman

    Added loop to run-all-tests.sh to run all tests against all supported
    versions of Python if available.  Looks for 2.3, 2.4, 2.5, 2.6.

2009-01-06  loafman

    Fix to deprecation warnings about sha and md5 modules.
    Uses hashlib if available, otherwise original module.

2009-01-05  loafman

    Missed the most basic case, no selection functions.  Fixed.

2009-01-05  loafman

    bug #25230: --include-globbing-filelist only including first entry.
    https://savannah.nongnu.org/bugs/?25230

2009-01-04  loafman

    sr #106583: document the need to use the --force option
    https://savannah.nongnu.org/support/?106583

2009-01-03  loafman

    patch #6709: Report correct number of volumes when restoring
    https://savannah.nongnu.org/patch/?6709

2009-01-03  loafman

    bug #25239: Error during clean, wrong case in duplcicity
    https://savannah.nongnu.org/bugs/?25239

2008-12-30  loafman

    Changes for 0.5.05.

2008-12-30  loafman

    Add po files back into distribution.

2008-12-30  loafman

    Cosmetic - reformat FatalError calls at end for readability.

2008-12-29  loafman

    Change "test" to "$version".

2008-12-29  loafman

    Build list of .mo files to be installed from po directory.

2008-12-29  loafman

    bug #25194: Duplicity 5.04 requires python-distutils-extra...
    https://savannah.nongnu.org/bugs/?25194

2008-12-29  loafman

    Use reldate expansion to include release date.

2008-12-29  loafman

    - Use os.path.join() instead of hardcoded strings
    - Make VersionedCopy replace $reldate as well as $version

2008-12-27  loafman

    Adjust RPM spec file for translations.

2008-12-27  loafman

    Changes for 0.5.04.

2008-12-22  loafman

    patch #6702: handle unknown errnos in robust.py
    https://savannah.nongnu.org/patch/?6702

2008-12-22  loafman

    patch #6700: Make duplicity translatable
    https://savannah.nongnu.org/patch/?6700
    [not in patch - added after unit tests]

2008-12-22  loafman

    patch #6701: Make current-list command machine-readable
    https://savannah.nongnu.org/patch/?6701

2008-12-22  loafman

    patch #6700: Make duplicity translatable
    https://savannah.nongnu.org/patch/?6700

2008-12-22  loafman

    GPG was throwing "gpg: [don't know]: invalid packet (ctb=14)" and apparently this is non-fatal.
    There is a fix for this being rolled into GPG 2.x.
    http://lists.gnupg.org/pipermail/gnupg-devel/2006-September/023180.html
    Copied from collections.py.  Fix supplied by Simon Blandford <simon@onepointltd.com>

2008-12-15  loafman

    One statement per line.  No other changes.

2008-12-15  loafman

    One statement per line.  No other changes.

2008-12-15  loafman

    Print backend name for each test started.

2008-12-15  loafman

    Remove test for assert on non-existing delete.  Not all backends will raise an exception when the target of a delete does not exist.

2008-12-15  loafman

    Log correct file name in line 67.  Use diff_ropath, not basis_path.

2008-12-15  loafman

    Fix patch applied during Patch #6696.  Applied fixiter.diff.

2008-12-15  loafman

    patch #6697: Always log at least one progress during dry run
    https://savannah.nongnu.org/patch/?6697

2008-12-15  loafman

    patch #6696: Consolidate get_delta_iter and get_delta_iter_w_sig
    https://savannah.nongnu.org/patch/?6696

2008-12-15  loafman

    patch #6695: Log filenames
    https://savannah.nongnu.org/patch/?6695

2008-12-15  loafman

    patch #6694: Log exceptions
    https://savannah.nongnu.org/patch/?6694

2008-12-15  loafman

    patch #6693: Some FatalError's don't have codes still
    https://savannah.nongnu.org/patch/?6693

2008-12-15  loafman

    patch #6692: Print collection status in a machine-readable way
    https://savannah.nongnu.org/patch/?6692

2008-12-14  loafman

    bug #24889: NCFTP cannot deal with some FTP servers
    https://savannah.nongnu.org/bugs/?24889

2008-12-14  loafman

    bug #25090: Typos and trailing whitespace in duplicity manpage
    https://savannah.nongnu.org/bugs/?25090

2008-12-10  loafman

    patch #6686: Add error codes for all fatal errors
    https://savannah.nongnu.org/patch/?6686

2008-11-18  loafman

    patch #6678: Add progress metering
    https://savannah.nongnu.org/patch/?6678

2008-11-17  loafman

    Changes for 0.5.03.

2008-11-16  loafman

    patch #6676: Raw delta stats aren't right for multivolumes
    https://savannah.nongnu.org/patch/?6676

2008-11-16  loafman

    patch #6675: Add modelines
    https://savannah.nongnu.org/patch/?6675

2008-11-16  loafman

    patch #6674: Add --log-* options to man page
    https://savannah.nongnu.org/patch/?6674

2008-11-16  loafman

    patch #6673: Add --dry-run option
    https://savannah.nongnu.org/patch/?6673

2008-11-15  loafman

    patch #6672: makedist doesn't ship util.py
    https://savannah.nongnu.org/patch/?6672

2008-11-12  loafman

    Add log.setup() call to main() to support new logging.

2008-11-12  loafman

    *** empty log message ***

2008-11-12  loafman

    Add log.setup() to support new logging.

2008-11-12  loafman

    Checkpoint 2 prior to 5.03.

2008-11-12  loafman

    patch #6670: Machine Readable Output
    https://savannah.nongnu.org/patch/?6670

2008-11-12  loafman

    Correct spelling of parsed_url (parsed_urk) in patch #6662.

2008-11-12  loafman

    sr #106534: GMail backups aren't stored in the correct location
    https://savannah.nongnu.org/support/?106534

2008-11-12  loafman

    sr #106496: put install-from-cvs-notes in CVS-README
    https://savannah.nongnu.org/support/?106496

2008-11-12  loafman

    Checkpoint prior to 5.03.

2008-11-12  loafman

    patch #6638: correct typo in reporting lack of sufficiently new boto backend
    https://savannah.nongnu.org/patch/?6638

2008-11-12  loafman

    patch #6642: make ParsedUrl() thread-safe with respect to itself
    https://savannah.nongnu.org/patch/?6642

2008-11-12  loafman

    patch #6652: improve asynch scheduler (including the synchronous case)
    https://savannah.nongnu.org/patch/?6652

2008-11-12  loafman

    patch #6662: improve s3 backend error reporting
    https://savannah.nongnu.org/patch/?6662

2008-11-12  loafman

    patch #6670: Machine Readable Output
    https://savannah.nongnu.org/patch/?6670

2008-11-12  loafman

    bug #24775: Digest Auth for WebDAV backend
    https://savannah.nongnu.org/bugs/?24775

2008-11-12  loafman

    bug #24731: Documentation error: "if... if" in remove-older-than paragraph
    https://savannah.nongnu.org/bugs/?24731

2008-09-21  loafman

    Changes for 0.5.02

2008-09-21  loafman

    patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/index.php?6297

2008-09-16  loafman

    patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/index.php?6297

2008-09-16  loafman

    Change to one statement per line.

2008-09-15  loafman

    Change use of logger so that gpg logs are always collected.
    The log is always printed in the case of gpg IO errors.
    Verbosity level 5 or greater will also print the logs the
    same as previous versions.

2008-09-15  loafman

    Make one statement per line.  No other changes.

2008-09-15  loafman

    - add -h option for help

2008-09-15  loafman

    bug #24274: asyncscheduler.py missing sys import
    https://savannah.nongnu.org/bugs/index.php?24274

2008-09-14  loafman

    bug #24260: backend.py missing re import
    https://savannah.nongnu.org/bugs/index.php?24260

2008-09-11  loafman

    Changes for 0.5.01

2008-09-09  loafman

    Ignore test log file.

2008-09-09  loafman

    Untabify all files.  To compare against previous
    versions use 'cvs diff -w' or 'diff -w'.

2008-09-08  loafman

    Create target dir (collection) if needed.

2008-09-08  loafman

    Ignore testfiles dir.

2008-09-08  loafman

    Add tests for webdav and webdavs.

2008-09-08  loafman

    bug #24223: WebDAV backend broken in 0.5.00
    https://savannah.nongnu.org/bugs/index.php?24223

2008-09-06  loafman

    Changes for 0.5.00

2008-09-06  loafman

    Changes for 0.5.00

2008-09-04  loafman

    temp2.tar was a test-created file that had to be present
    at the beginning of test_tarfile.py.  Removed the need for
    it to be present and removed the file from CVS.

2008-09-03  loafman

    Changes to get unit tests working again:
    - resolve circular imports during unit tests
    - resolve exception error import - now in errors.py

2008-09-03  loafman

    patch #6623: slightly augment tempdir cleanup logging
    https://savannah.nongnu.org/patch/index.php?6623

2008-08-03  loafman

    No longer needed, see backends dir.

2008-08-03  loafman

    no comment

2008-08-03  loafman

    bug #23988: scp destination fails if no username is specified
    https://savannah.nongnu.org/bugs/index.php?23988

2008-08-03  loafman

    bug #23985: --no-encryption option does not work in 0.4.12
    https://savannah.nongnu.org/bugs/index.php?23985

2008-08-02  loafman

    patch #6596: re-organize backend module structure
    https://savannah.nongnu.org/patch/index.php?6596

2008-08-01  loafman

    patch #6353: Concurrency for volume encryption and upload.
    https://savannah.nongnu.org/patch/index.php?6353

2008-08-01  loafman

    patch #6589: S3 european bucket support
    https://savannah.nongnu.org/patch/index.php?6589

2008-07-22  loafman

    Changes for 0.4.12.

2008-07-22  loafman

    bug #23362: Documentation for --version, --time-separator <char>
    https://savannah.nongnu.org/bugs/index.php?23362

2008-07-22  loafman

    Cosmetic only.

2008-07-22  loafman

    bug #23540: doc bug in man page (environment FTP_PASSWORD)
    https://savannah.nongnu.org/bugs/?23540

2008-06-23  loafman

    Dan Muresan created a patch that tries to minimize the number of password
    prompts.  To do so, it sometimes requests a password once without
    confirmation; if later it turns out that a full backup is needed, the
    user is prompted for confirmation.

2008-05-16  loafman

    bug #23066: ssh uris with given portnumbers are not handled correctly
    https://savannah.nongnu.org/bugs/index.php?23066

2008-05-15  loafman

    Fix sort() for Python 2.3

2008-05-07  loafman

    Change back to requiring Python 2.3.

2008-05-05  loafman

    Change requirements back to Python 2.3.

2008-05-05  loafman

    Changes for 0.4.11

2008-05-05  loafman

    Modified to run on Python 2.3.

2008-04-04  loafman

    bug #22826: regressions caused by boto 1.1c
    https://savannah.nongnu.org/bugs/?22826

2008-04-01  loafman

    Reinstate patch #6340 with a detailed explanation.
    http://savannah.nongnu.org/patch/index.php?6340

2008-03-26  loafman

    Changes for 0.4.10.

2008-03-26  loafman

    Remove --sign for now.

2008-03-26  loafman

    bug #22728: FTP backend fails on empty directory
    https://savannah.nongnu.org/bugs/?22728

2008-03-25  loafman

    Fix log.debug to log.Debug

2008-03-25  loafman

    patch #6453: handle absolute urls in webdav backend
    https://savannah.nongnu.org/patch/index.php?6453

2008-03-25  loafman

    patch #6449: add additional debug level logging
    https://savannah.nongnu.org/patch/index.php?6449

2008-02-06  loafman

    patch #6403: Restore by overwriting files/directories by using --force option
    https://savannah.nongnu.org/patch/?6403

2008-02-06  loafman

    Password should be None, not empty string.

2008-02-06  loafman

    Add config for S3 tests.

2008-02-06  loafman

    Reformat to one statement per line.

2008-02-06  loafman

    Fix problem where S3 prefix was appended with 'd'.  This caused
    a failure in the regression tests.  Unsure where it came from.

2008-02-06  loafman

    patch #6389: Possible Fix for pagefile.sys on Win32 systems
    https://savannah.nongnu.org/patch/?6389

2008-02-06  loafman

    patch #6380: add additional named logging levels
    https://savannah.nongnu.org/patch/?6380

2008-02-06  loafman

    patch #6374: Duplicity --tempdir patch documentation.
    https://savannah.nongnu.org/patch/?6374

2008-02-06  loafman

    patch #6375: Duplicity reports the epoch for a nonexistant last full backup date
    https://savannah.nongnu.org/patch/?6375

2008-02-06  loafman

    - remove sleep() from dup_time.py - not used.
    - make one statement per line format change.

2008-02-06  loafman

    Remove testSleeping since sleep() removed from dup_time.py.

2008-02-06  loafman

    Add S3 backend test.

2008-02-03  loafman

    do not store object

2008-01-08  loafman

    Add requirements for source package install.

2008-01-04  loafman

    Changes for 0.4.9.

2008-01-04  loafman

    Add more info on URL formats.

2007-12-31  loafman

    Updated URL Formats in the Help Screen.

2007-12-31  loafman

    Added section URL FORMAT in the duplicity man page.

2007-12-30  loafman

    Make sure to strip extraneous single colon when dealing
    with non-module URLs.  We provide the colon as needed.

2007-12-30  loafman

    bug #21909: Problematic typo in compare_verbose() method
    https://savannah.nongnu.org/bugs/index.php?21909

2007-12-29  loafman

    patch #6357: Explicit restore action is missing from the command list,
    https://savannah.nongnu.org/patch/?6357

2007-12-29  loafman

    patch #6356: Command line option for the temporary directory root.
    https://savannah.nongnu.org/patch/?6356

2007-12-27  loafman

    Added regression tests for absolute, relative, and
    module pathing in the rsync scheme.

2007-12-27  loafman

    Fixed rsync URL description text in --help.

2007-12-27  loafman

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

2007-12-27  loafman

    Fixed so that remove-older-than and remove-all-but-n-full
    will not request a GPG passphrase.

2007-12-26  loafman

    Fixed regression caused by changeover to new urlparse.py.
    bug #21475: FTP Usernames that contain '@' are not recognized
    https://savannah.nongnu.org/bugs/index.php?21475

2007-12-15  loafman

    Changes for 0.4.8.

2007-12-15  loafman

    Format to one statement per line.

2007-12-15  loafman

    Allow pexpect to force the close of the child on sftp
    calls.  We already do that with scp calls.  This cleans
    up that exception.

2007-12-14  loafman

    patch #6344: S3 bad bad key key handling
    http://savannah.nongnu.org/patch/?6344

2007-12-13  loafman

    Replace set_password/phrase with set_environ and
    clarify meaning in config.py.

2007-12-12  loafman

    Complete description of install using --prefix=.

2007-12-12  loafman

    Fix version of boto needed plus formatting.

2007-12-12  loafman

    patch #6340: S3 short filename regression
    https://savannah.nongnu.org/patch/?6340

2007-12-12  loafman

    Make sure config.py not checked in.

2007-12-12  loafman

    Initial release.

2007-12-12  loafman

    This test requires a file that no longer exists.
    Plus, it is unclear what this test is supposed
    to accomplish.  Tar is tested by the other tests.

2007-12-12  loafman

    First pass at getting tests up to date:
    -- isolate config in 'config.py' (see config.py.tmpl)
    -- silence noisy tests as much as possible
    -- fix code on both sides as needed

2007-12-09  loafman

    Initial release.

2007-12-09  loafman

    Remove 2nd call to dup_time.settimestr() since it overrides
    the time that may be set by --current-time (used for testing).

2007-12-09  loafman

    Regen dup_time.curtimestr if time-separator changed.

2007-12-09  loafman

    Fixed previous patch that assumed the presence
    of the user and password in the rsync URL.

2007-12-09  loafman

    Bring tests up to date.

2007-12-08  loafman

    bug #21751: rsync module urls do not work in 0.4.7
    https://savannah.nongnu.org/bugs/index.php?21751

    bug #21752: Boto backend needs version 0.9d or later
    https://savannah.nongnu.org/bugs/index.php?21752

2007-12-07  loafman

    Changes for version 0.4.7.

2007-12-07  loafman

    Change to require Python 2.4 or later.

2007-12-07  loafman

    Formatted list and added tempdir.py and urllib_2_5.py
    to the released files list.

2007-12-06  loafman

    Fix confusion over patches applied to different versions.
    Patch #6300 should now be applied completely.

    Added back munge_password() so entire commandline could
    be logged without the password showing.

2007-12-06  loafman

    Hole imapbackend till next release.

2007-12-06  loafman

    Hold till next release.

2007-12-05  loafman

    patch #6300: Standard library replacement for ParsedUrl class
    https://savannah.nongnu.org/patch/?6300

    I had to fix the ssh/scp scheme to remove the leading '/' in
    parsed_url.path, otherwise it tried to treat the path as absolute.

2007-12-02  loafman

    Backed out the following patch until bugs fixed...
    patch #6300: Standard library replacement for ParsedUrl class
    https://savannah.nongnu.org/patch/?6300

2007-12-02  loafman

    patch #6301: log sftp commands at verbosity 5
    https://savannah.nongnu.org/patch/?6301

2007-12-02  loafman

    patch #6300: Standard library replacement for ParsedUrl class
    https://savannah.nongnu.org/patch/?6300

2007-12-02  loafman

    patch #6299: re-design tempfile handling
    https://savannah.nongnu.org/patch/?6299

2007-12-01  loafman

    Move import of imapbackend to the end of the
    module.  Circular dependency.  Needs fixing.

2007-12-01  loafman

    Undo regression of bug #21508 contained in
    patch #6298: URI unquoting patch for FTP backend
    https://savannah.nongnu.org/patch/?6298

    Some cosmetic cleanup.

2007-12-01  loafman

    patch #6298: URI unquoting patch for FTP backend
    https://savannah.nongnu.org/patch/?6298

2007-12-01  loafman

    patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/?6297

    Added 2nd patch for above.

2007-12-01  loafman

    patch #6297: Add IMAP/s/gmail support
    https://savannah.nongnu.org/patch/?6297

2007-12-01  loafman

    patch #6292: Amazon S3 bucket creation deferral for Duplicity 0.4.6
    https://savannah.nongnu.org/patch/?6292

2007-12-01  loafman

    bug #21686: NcFTPGet 3.2.0 tempfile incompatibility
    https://savannah.nongnu.org/bugs/index.php?21686

2007-12-01  loafman

    Applied patch from Eric Hanchrow to fix logging error in
    botoBackend, and fix delete() in rsyncBackend.

    bug #21686: NcFTPGet 3.2.0 tempfile incompatibility
    https://savannah.nongnu.org/bugs/index.php?21686

2007-11-29  loafman

    bug #21673: remove-all-but-n-full wrong arg usage
    https://savannah.nongnu.org/bugs/index.php?21673

    patch #6293: [patch] left-over patching from
    remove-all-but-n-full patch
    https://savannah.nongnu.org/patch/?6293

2007-11-28  loafman

    more Changes for 0.4.6.

2007-11-28  loafman

    Changes for 0.4.6.

2007-11-28  loafman

    Fixed coding problem where matched_sig_chain could be
    referenced before it was defined.

2007-11-28  loafman

    https://savannah.nongnu.org/patch/index.php?6291
    patch #6291: Alternative WebDAV HTTPS patch

2007-11-28  loafman

    https://savannah.nongnu.org/patch/index.php?6289
    patch #6289: Amazon S3 key prefix patch for Duplicity 0.4.5

2007-11-28  loafman

    https://savannah.nongnu.org/patch/?6284
    patch #6285: security fix: eliminate use of mktemp()

2007-11-28  loafman

    https://savannah.nongnu.org/bugs/index.php?21651
    bug #21651, add https support for webdav.

    https://savannah.nongnu.org/patch/?6284
    patch #6284: document TMPDIR and friends

2007-11-28  loafman

    https://savannah.nongnu.org/bugs/index.php?21657
    bug #21657: ncftpls fails to create dir in ver 0.4.5

2007-11-28  loafman

    https://savannah.nongnu.org/bugs/index.php?21651
    bug #21651, add https support for webdav.

2007-11-28  loafman

    Try, the second.  See comments in the bug tracker.
    https://savannah.nongnu.org/bugs/index.php?21646
    bug #21646: --archive-dir causes delete of remote full
    sigs and orphaned sig files

2007-11-28  loafman

    https://savannah.nongnu.org/bugs/index.php?21651
    bug #21651, add https support for webdav

2007-11-26  loafman

    Fix release date in 0.4.5.

2007-11-26  loafman

    Changes for 0.4.5.

2007-11-26  loafman

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

2007-11-23  loafman

    Changes for version 0.4.4.

2007-11-23  loafman

    Applied a patch from Gregory Hartman to correct handling of DST
    in time calculations.  This affects backups made the night of
    a DST time switch.

2007-11-23  loafman

    Cosmetic - Use True and False, not 1 and None.

2007-11-23  loafman

    Fix version checking code in ftpBackend.

2007-11-19  loafman

    Changes to commandline processing to allow non-ambiguous short
    strings for commands, i.e. 'i', 'inc', 'incr' for 'incremental',
    'f' for 'full', etc..  A warning message is printed if the short
    command is not unique.

2007-11-19  loafman

    Changes to ftpBackend to use the login config file rather than
    putting the username and password on the command line.  This
    requires the use of NcFTP 3.1.9 or later.

    Thanks to a patch from Greg Hewgill the Amazon S3 backend now
    uses --num-retries to retry IO repeatedly if needed.

2007-10-26  loafman

    Changes for 0.4.4.RC4 try 2

2007-10-26  loafman

    Changes for 0.4.4.RC4

2007-10-26  loafman

    Replace with Version 3 GPL text.

2007-10-26  loafman

    Fixed issue in --time-separator where the current time string
    was being set prior to setting the separator, causing errors
    when trying to set the --time-separator for Windows systems.

2007-10-26  loafman

    There is a new command line syntax to separate actions and
    options.  Refer to the new man page for full details.

2007-10-26  loafman

    Correct calling sequence in calls to get_signature_chains().

2007-10-26  loafman

    Fix so that ftpBackend.delete() does not print file list.

2007-10-26  loafman

    Fix so that file mtime is always compared in full seconds.

2007-10-02  loafman

    Changes for 0.4.4.RC3 -- Corrected.

2007-10-02  loafman

    Changes for 0.4.4.RC3.

2007-09-29  loafman

    Add 'patch' dir to ignore list.

2007-09-29  loafman

    Patch from Olivier Croquette to add :port option in FTP.

2007-09-29  loafman

    Patch from Olivier Croquette to add --full-if-older-than=<time>
    option to force a full backup at <time> rather than incremental.

2007-09-28  loafman

    Patch from Olivier Croquette to add :port option in FTP.

    Patch from Mitchell Garnaat to get all keys from S3, rather
    than just the first 1000.

    Fix to sshBackend to version check for python-pexpect 2.1.

    Fix one case in ftpBackend where host string was used instead of
    url_string.  This only affected the creation of the target dir on
    the remote system, if it did not exist, and only if the user or
    port needed to be specified.

2007-09-26  loafman

    Changes for 0.4.4.RC2.

2007-09-26  loafman

    Added --timeout <seconds> (default 30) to allow users to change
    duplicity's network timeout settings.

    Added --time-separator <char> to allow users to change the time
    separator from ':' to another character that will work on their
    system.  HINT: For Windows SMB shares, use --time-separator='_'.
    NOTE: '-' is not valid as it conflicts with date separator.

    Changed usage message to separate options and commands.

2007-09-26  loafman

    Add patch from Olivier Croquette to allow user@domain usernames,
    making ftp://user@domain@domain.com/path a valid URL.

    Added a bit of debug print to sshBackend for --verbosity=9.

2007-09-26  loafman

    Add patch from Alexander Zangerl to suppress the GPG passphrase
    prompt when a passphrase is not needed.
    - full and pubkey enc:  doesn't depend on old encrypted info
    - inc and pubkey enc and archive-dir: need manifest and sigs,
    which the archive dir contains unencrypted
    - with encryption disabled
    - listing files:  needs manifest, but the archive dir has that
    - collection status:  only looks at a repository

2007-09-19  loafman

    Changes for 0.4.4.RC1.

2007-09-19  loafman

    https://savannah.nongnu.org/patch/index.php?6205
    Add option --librsync-dir for when its not found.

2007-09-19  loafman

    Bug #21123: duplicity 0.4.3 does not find any backup chains
    https://savannah.nongnu.org/bugs/?21123

2007-09-19  loafman

    Make tempfiles with useful names.

2007-09-19  loafman

    Fixes manual page and usage msg for rsync url and --remove-older-than.

2007-09-19  loafman

    Fix for Debian bug #228388: old/aborted/offending sig files
    prohibit any further action.

2007-09-19  loafman

    Fixes manual page and usage msg for rsync url and --remove-older-than.

2007-09-19  loafman

    Do not ask for passphrase when none is needed.

2007-09-16  loafman

    Final patch for Peter Schuller's fix to max read size.
    The first one was broken (revision previous to this).

2007-09-10  loafman

    Add patch submitted by Peter Schuller which removes the
    default SSH options that ignored known hosts files and
    disabled strict host checking.  This patch also handles
    the authentication failures from these issues.

2007-09-06  loafman

    Fixed so that max read size is 64k, not the
    volume size which can be quite large.

2007-08-20  loafman

    Fix release date.

2007-08-20  loafman

    Changes for 0.4.3 release.

2007-08-20  loafman

    Removed use of tempfile.TemporaryFile().  This fixes the
    restore problem on Windows that was due to Python bug
    1776696 reported on Sourceforge.

2007-08-20  loafman

    Removed hardwired options to use bzip2 compression.

    Added gpg-options to allow users to add options to
    the gpg process.

2007-08-20  loafman

    Changed ssh-command to ssh-options to allow users
    to add options to the scp and sftp commmands.

    Added gpg-options to allow users to add options to
    the gpg process.

2007-08-20  loafman

    Move get_password() to Backend class to standardize.

    Fix problem with ftpBackend to create target directory if needed.

2007-08-13  loafman

    Upgrade to GPL version 3 license.

2007-08-13  loafman

    Do not pass :port part of URL to scp backend.
    Its taken as the target file and errors out.

2007-08-13  loafman

    Change ssh_command option to be ssh_options.  This adds
    options to the scp and sftp commands that are used by
    the ssh backend.

2007-08-13  loafman

    Fixed bug 20764 - unable to use port in ssh backend.
    https://savannah.nongnu.org/bugs/?20764

    Change ssh backend to send 'quit' instead of EOF when
    using sftp.  This allows it to run under cron as long
    as the password is supplied non-interactively.

2007-08-09  loafman

    Changes for 0.4.3.RC12

2007-08-09  loafman

    Changes for 0.4.3.RC12

2007-08-09  loafman

    Changed the file:, ftp:, and ssh: backends so that
    the target directory will be created at start.

    Changed the ftp: backend so that empty target dirs
    do not error out.

2007-08-09  loafman

    Clean up help list formatting.

2007-08-09  loafman

    Fix index out of range in Bug 20730, triggered when there
    is only one incremental and no previous in list.
    https://savannah.nongnu.org/bugs/?20730

2007-08-09  loafman

    - Print warning if pexpect version is less than 2.1.
    - Fix author and maintainer settings.

2007-08-09  loafman

    Fix environment var name for ssh backend.

2007-07-21  loafman

    Changes for 0.4.3.RC11.

2007-07-21  loafman

    Add --ssh-askpass option.

2007-07-21  loafman

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

2007-07-15  loafman

    patch #6094, Boto Backend Fixes for RC10

2007-07-14  loafman

    Changes for 0.4.3.RC10

2007-07-14  loafman

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

2007-07-14  loafman

    Add support for:
    --ftp-passive,
    --ftp-regular,
    --num-retries

2007-07-14  loafman

    Add descriptions for:
    --ftp-passive,
    --ftp-regular,
    --num-retries

2007-07-10  loafman

    Replace missing comma in argument list.

2007-07-09  loafman

    Changes for 0.4.3.RC9.
    Drop ftplib.py.

2007-07-09  loafman

    No longer needed.

2007-07-09  loafman

    Changes for 0.4.3.RC9.

2007-07-09  loafman

    Added a commandline option, '--num-retries=<int>', to set the number
    of retries.  The default is 5.

2007-07-09  loafman

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

2007-06-29  loafman

    Change to a max block size of 2048 bytes for
    rsync difference buffer.  This may slow things
    down for truly large files, but will give much
    smaller deltas on files with numerous small
    changes, such as database files.

2007-06-28  loafman

    Initial release.

2007-06-27  loafman

    Changes for 0.4.3.RC8

2007-06-27  loafman

    Bug 20039 - Andreas Schildbach: --and--
    Patch 6030 - Alexander Zangerl <az@debian.org>:
    Duplicity now uses bzip2 for compression.  This matches the way
    the Debian distribution handles it.  I'll think about adding an
    option to override later, if its needed.

2007-06-27  loafman

    Bug 20282 - Thomas Tuttle:
    An out of range index when checking past history in the backup
    sets caused a failure when trying to access later.

    Bug 20149 - dAniel hAhler:
    dAniel submitted a second patch for this for further cleanup.
    The new patch prefers the latest intact backup set.

2007-06-19  loafman

    Changes for 0.4.3.RC7

2007-06-19  loafman

    Patch 6029 - Alexander Zangerl <az@debian.org>:
    http://bugs.debian.org/370206
    archive-dir together with incremental backup results in crash. the
    patch is simple, the code in 0.4.2 did attempt to access strings as
    objects.

2007-06-19  loafman

    Patch 6033 - Alexander Zangerl <az@debian.org>:
    let's add a --help terse usage message and don't just direct the user
    to the manual. this should come handy if somebody needs to restore
    stuff without having the manual available.

2007-06-19  loafman

    Patch 6032 - Alexander Zangerl <az@debian.org>:
    a new feature patch: i've recently gotten annoyed with having gazillions of
    5mb files and therefore added a --volsize option to allow the user setting
    the chunk size. the patch is simple and contains a manpage update as well.

2007-06-19  loafman

    Add -u (unbuffered) to shebang line.

2007-06-19  loafman

    Add stderr.flush() in FatalError().

2007-06-19  loafman

    Bug 20179 - dAniel hAhler: When errors cause login to fail in FTP,
    reset and try again.

2007-06-13  loafman

    Not needed.

2007-06-13  loafman

    Cosmetic change to force new log.  The log for revision 1.28
    is not correct.  It should read as follows:

    Patch 5993 - daacyy302@sneakemail.com: Make Amazon S3 backend
    incrementally more robust for recovery.

2007-06-13  loafman

    Changes for 0.4.3.RC6.

2007-06-13  loafman

    Patch 5998 - Kuang-che Wu: Cache uid and gid lookup to speed
    operations.

2007-06-13  loafman

    Bug 20419 - dAniel hAhler: When errors cause an incomplete backup set,
    flag the error with a message, rather than erroring out.  The user
    then knows to run --cleanup.

2007-06-04  loafman

    Changes for 0.4.3.RC5.

2007-06-04  loafman

    dAniel hAhler submitted a patch to change "Error initializing file
    foo" (log level 2), where foo was a socket, to "Skipping socket foo"
    (log level 7).  https://savannah.nongnu.org/patch/?5985

2007-06-04  loafman

    Change logging to flush after every write, unbuffering stdout and
    stderr, thus producing logs that are coherent.

2007-06-04  loafman

    GnuPG fails when trying to access stdin on an empty passphrase.
    Changes allow empty passphrase on public-key encryption and now
    respond gracefully on empty passphrase for symmetric encryption.

2007-06-02  loafman

    Changes for 0.4.3.RC4.

2007-06-02  loafman

    Move catch of NLST errors back to self.error_retry()

2007-06-02  loafman

    More FTP fixes:
    - clean up error handling
    - change initial error delay to zero
    - move catch of NLST errors to self.list()

2007-05-31  loafman

    Changes to release 0.4.3.RC3.

2007-05-30  loafman

    - Fix so that FTP connection/login is closed and
    reopened when errors 221 or 421 are reported.

    - Fix grammer in error message.

2007-05-30  loafman

    Changes to release 0.4.3.RC2.

2007-05-30  loafman

    Remove GnuPGInterface.py

2007-05-30  loafman

    Apply patch for bug 19998, ValueError exception.

2007-05-26  loafman

    Added change notices for FTP password and rsync backend.

2007-05-26  loafman

    Fix request password in ftpBackend if environ not set.

2007-05-26  loafman

    - allow connection after 226 in NLST (ProFTPD)
    - request password in ftpBackend if environ not set
    - rsyncBackend was using the full URL, now uses server:path

2007-05-26  loafman

    Document changes for 0.4.3.

2007-05-25  loafman

    Do not set FTP to active mode at start of session.

2007-05-24  loafman

    1) WebDAV needs a Depth: 1 header otherwise infinite depth
    is assumed and may be restricted due to load.

    2) Used the allprop XML command to get back properties that
    included the filenames.  Refer to RFC 2518.

2007-05-23  loafman

    Fixes bug:
    https://savannah.nongnu.org/bugs/?19940

2007-05-23  loafman

    Applied patches:
    https://savannah.nongnu.org/patch/?5680
    https://savannah.nongnu.org/patch/?5681

2007-05-23  loafman

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

2006-05-09  jinty

    BitBucketBackend:
    * if something goes wrong and we need to re-connect, dump the exception
    on stderr. Be very noisy so that whatever is wrong will be fixed.

2006-05-04  bescoto

    Typo fix for error message

2006-05-02  jinty

    Fix a bug in the bitbucket backend:
    We need to get a new bits from the new bucket if we re-connect.

2006-05-01  jinty

    Changes to the bitbucket backend:
    * Update to work with bitbucket 0.3b.
    * Add some docimentation.
    * Implement a suggestion by Ben Escoto to move the access and secret keys to
    environment variables.
    * Implement a very simplistic error correction mechanisim that will re-connect
    on an operation failure and re-try the operation. Note that this is just a
    band-aid for issues that should be resolved at lower levels.

2006-05-01  bescoto

    Removed time_separator entry from changelog when I backed out patch

2006-05-01  bescoto

    Went back to old time_separator, because I realized new way wouldn't
    handle some cases, and could break backwards compatibility

2006-05-01  bescoto

    Andre Beckedorf's patches for ftp and rsync backends, and time_separator

2006-04-30  bescoto

    Checked in Brian Sutherland's Amazon S3 code

2006-04-30  bescoto

    Added --sftp-command to changelog

2006-04-30  bescoto

    Added --sftp-command option and man page documentation

2006-04-30  bescoto

    Fixed Jiri's name.  Sorry about that :-)

2006-02-03  bescoto

    final changes for version 0.4.2

2006-02-03  bescoto

    Fixes to the scp backend

2006-02-02  bescoto

    Stop --remove-older-than from deleting current chain

2006-02-01  bescoto

    Catch ftp error 450 when listing directory

2006-02-01  bescoto

    cleaned up and documented --collection-status

2006-01-12  bescoto

    asdf's tarfile large uid/gid patch

2006-01-12  bescoto

    Jiri Tyr's scp/sftp patch

2006-01-02  bescoto

    Eric Hanchrow's remove signature patch

2006-01-01  bescoto

    A few minor updates so test pass on my system again

2003-11-21  bescoto

    MDR patch allows signing with different key

2003-08-14  bescoto

    Added note about passphrase confirmation

2003-08-14  bescoto

    When collecting password from user, make type it twice to confirm

2003-08-10  bescoto

    Final changes for 0.4.1

2003-08-10  bescoto

    Updating rpm for Fedora

2003-08-10  bescoto

    Trying to remove...

2003-08-10  bescoto

    Small changes for 0.4.1 and python 2.3

2003-08-09  bescoto

    variable block size, librsync 0.9.6

2003-08-09  bescoto

    Remove large file note now that block size chosen based on file size

2003-08-09  bescoto

    Ported some code from rdiff-backup:  choose sig block based on file
    length, and work with librsync 0.9.6.

2003-08-09  bescoto

    Mention problem with /proc

2003-08-08  bescoto

    Cache pwd and group files

2003-08-08  bescoto

    Added --version switch, small change to man page

2003-08-07  bescoto

    Sebastian Wilhelmi's update for rsync backend

2003-08-07  bescoto

    Applied Stephen Isard's patch for --exclude-globbing-filelist

2003-04-06  bescoto

    Added mention of rsync backend.

2003-04-06  bescoto

    added rsync contributed by Sebastian Wilhelmi

2003-03-14  bescoto

    Added test and fix for long symlink to long file bug

2003-03-09  bescoto

    Raise error (instead of exiting silently) if no files found to restore

2003-03-09  bescoto

    Added long filenames test

2003-03-08  bescoto

    Added man page info on --short-filenames option

2003-02-02  bescoto

    (version of) Helmut Schneider's patch to display mtimes with list files

2002-11-30  bescoto

    Added --no-encryption option, fixed crash on inc when no changed files

2002-11-30  bescoto

    Added --verify option, tweaked some verbosity levels

2002-11-30  bescoto

    Added compare_verbose and test to path module

2002-11-24  bescoto

    Changed restore procedure.  Now all sets integrated simultaneously.

2002-11-19  bescoto

    Fixed typo in get_ropath

2002-11-18  bescoto

    Added a few options for only doing upload/move/checkin/etc

2002-11-18  bescoto

    Changed way difftars are split between volumes to waste less space

2002-11-17  bescoto

    Slight tweak to base36 code

2002-11-17  bescoto

    Added extra tests for base36 conversion

2002-11-17  bescoto

    Shorted short filenames (use base36)

2002-11-17  bescoto

    Swallow GPG logging output if verbosity 3 or less

2002-11-17  bescoto

    Added --remove-older-than option, changed --current-time behavior

2002-11-17  bescoto

    Added --cleanup option

2002-11-17  bescoto

    Added --force option.

2002-11-17  bescoto

    Added code for finding extraneous and old files

2002-11-17  bescoto

    For ssh, deleted in groups of 10 so command line doesn't overflow

2002-11-16  bescoto

    Fixed a few minor collections bugs, added get_extraneous

2002-11-14  bescoto

    Added note on one pass restores/verifies

2002-11-14  bescoto

    Added --restore-time bug fix note

2002-11-12  bescoto

    Better fix for same (current_time) bug

2002-11-12  bescoto

    Fixed minor bug erasing output dir too early

2002-11-12  bescoto

    Restores now default to current time if restore time not specified

2002-11-12  bescoto

    Added undocumended --collection-status option for testing purposes

2002-11-11  bescoto

    More misc updates for 0.3.0

2002-11-10  bescoto

    Few last minute tweaks to prepare for 0.3.0 release

2002-11-10  bescoto

    Added --ssh-command and --scp-command options

2002-11-10  bescoto

    Fixed time-must-be-int bug with --short-filenames, added test

2002-11-10  bescoto

    Various bugfixes so ftp backend passes final test

2002-11-10  bescoto

    Added --short-filenames option

2002-11-10  bescoto

    Added ftp backend support

2002-11-03  bescoto

    Added man page entry for --file-to-restore option

2002-11-03  bescoto

    Added statistics reporting after successful backup

2002-11-02  bescoto

    Added --list-current-files option

2002-11-02  bescoto

    Make CVS more friendly; don't depend on src symlink

2002-11-02  bescoto

    Updated documentation on new globbing options

2002-11-02  bescoto

    Fixed bug & added test when root was reg file, not dir

2002-11-02  bescoto

    Added --include/exclude-globbing-filelist options

2002-11-01  bescoto

    Fixed tar '..' security bug

2002-11-01  bescoto

    Added 2 test cases: neg mtimes, missing u/gnames

    Now check to make sure these files aren't spuriously marked as
    changed.

2002-10-31  bescoto

    Fixed dumb st_time/st_mtime typo

2002-10-29  bescoto

    Updated with new web page/mailing list information.

2002-10-29  bescoto

    Added full GPL statement in source files at request of Jaime Villate
    of the Savannah site.  Also updated address of FSF.

2002-10-29  bescoto

    Initial checkin


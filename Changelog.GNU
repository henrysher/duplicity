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


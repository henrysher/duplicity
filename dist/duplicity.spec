Version: $version
Summary: Untrusted/encrypted backup using rsync algorithm
Name: duplicity
Release: 1
URL: http://rdiff-backup.stanford.edu/duplicity
Source: %{name}-%{version}.tar.gz
Copyright: GPL
Group: Applications/Archiving
BuildRoot: %{_tmppath}/%{name}-root
requires: librsync >= 0.9.5.1, python2 >= 2.2, gnupg >= 1.0.6
BuildPrereq: python2-devel >= 2.2, librsync-devel >= 0.9.5.1

%description
Duplicity incrementally backs up files and directory by encrypting
tar-format volumes with GnuPG and uploading them to a remote (or
local) file server.  In theory many remote backends are possible;
right now only the local or ssh/scp backend is written.  Because
duplicity uses librsync, the incremental archives are space efficient
and only record the parts of files that have changed since the last
backup.  Currently duplicity supports deleted files, full unix
permissions, directories, symbolic links, fifos, etc., but not hard
links.

%prep
%setup

%build
python2 setup.py build

%install
python2 setup.py install --prefix=$RPM_BUILD_ROOT/usr
%clean

%files
%defattr(-,root,root)
/usr/bin/rdiffdir
/usr/bin/duplicity
/usr/share/doc/duplicity-%{version}
/usr/share/man/man1
/usr/lib


%changelog
* Sun Aug 30 2002 Ben Escoto <bescoto@stanford.edu>
- Initial RPM


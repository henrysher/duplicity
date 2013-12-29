#!/bin/bash

help(){
    echo "Usage: ${SCRIPT_NAME} [-n] [-s] [source_dir]"
    echo "Options:"
    echo "  -n   Do not encrypt files (use --no-encryption duplicity option)."
    echo "  -s   Use system duplicity rather than local one."
    exit 1
}

# Check permissions
if [ "`id -ur`" != '0' ]; then
    echo 'Error: you must be root.'
    exit 1
fi

SCRIPT_NAME="$(basename $0)"
SOURCE_DIR="/lib"
NO_ENCRYPTION_OPT=""
DUPLICITY="./bin/duplicity"

while getopts ns opt; do
    case "$opt" in
    n)
        NO_ENCRYPTION_OPT="--no-encryption"
        ;;
    s)
        DUPLICITY="duplicity"
        ;;
    ?)  help
        ;;
    esac
done
shift `expr $OPTIND - 1`

if [ -n "$1" ]; then
    SOURCE_DIR="$1"
fi

if [ "${DUPLICITY}" != "duplicity" ] && [ ! -x "${DUPLICITY}" ]; then
    echo "./bin/duplicity not found!  Maybe try -s to use the system one?"
    exit 1
fi

rm -rf /tmp/backup /tmp/restore

echo "***** Making backup..."

RC=1
FAIL=2
while [ "$RC" != "0" ]; do
    PASSPHRASE=foo ${DUPLICITY} ${NO_ENCRYPTION_OPT} --exclude="**/udev/devices/*" --name=test-backup --fail ${FAIL} ${SOURCE_DIR} file:///tmp/backup
    RC=$?
    FAIL=$(($FAIL + 1))
done

echo "***** Restoring backup..."
PASSPHRASE=foo ${DUPLICITY} --name=test-backup file:///tmp/backup /tmp/restore

echo "***** Diff between ${SOURCE_DIR} and /tmp/restore"
diff -qr ${SOURCE_DIR} /tmp/restore | grep -v "Only in /lib/udev/devices"

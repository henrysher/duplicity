#!/bin/bash

# Check permissions
if [ "`id -ur`" != '0' ]; then
    echo 'Error: you must be root.'
    exit 1
fi

cd /tmp
rm -rf backup* restore*

cd ~/workspace/duplicity-0.6-series
echo "***** Do not disturb the control backup! "
PASSPHRASE=foo ./bin/duplicity --exclude="**/udev/devices/*" --name=test-backup1 /lib file:///tmp/backup1

echo -n "***** Now hit Ctrl-C at random intervals.  Hit any key to continue... "
read -e DUMMY
echo

trap "pkill -INT duplicity" SIGINT

RC=4
while [ "$RC" == "4" ]; do
    PASSPHRASE=foo ./bin/duplicity --exclude="**/udev/devices/*" --name=test-backup2 -v5 /lib file:///tmp/backup2
    RC=$?
    echo "Exit == $RC"
    if [ "$RC" != "4" ] && [ "$RC" != "0" ]; then
        echo "Repeat? "
        read -e REPLY
        if [ "$REPLY" == "Y" ] || [ "$REPLY" == "y" ]; then
            continue
        else
            break
        fi
    fi
done

trap - SIGINT

echo "Restoring backups..."
PASSPHRASE=foo ./bin/duplicity --name=test-backup1 file:///tmp/backup1 /tmp/restore1
PASSPHRASE=foo ./bin/duplicity --name=test-backup2 file:///tmp/backup2 /tmp/restore2

echo "Diff between /lib and /tmp/restore1"
diff -qr /lib /tmp/restore1 | grep -v "Only in /lib/udev/devices"

echo "Diff between /tmp/restore1 and /tmp/restore2"
diff -qr /tmp/restore1 /tmp/restore2

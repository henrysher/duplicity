#!/bin/bash
#
# Simple script for creating backups with Duplicity.
# Full backups are made on the 1st day of each month or with the 'full' option.
# Incremental backups are made on any other days.
#
# USAGE: backup.sh [full]
#

# get day of the month
DATE=`date +%d`

# Set protocol (use scp for sftp and ftp for FTP, see manpage for more)
BPROTO=scp

# set user and hostname of backup account
BUSER='u10000'
BHOST='u10000.your-backup.de'

# Setting the password for the Backup account that the
# backup files will be transferred to.
# for sftp a public key can be used, see:
# http://wiki.hetzner.de/index.php/Backup
#BPASSWORD='yourpass'

# directories to backup (use . for /)
BDIRS="/Users/nils/Documents/bzr/duplicity/testing/testfiles/"
TDIR=`dpbx:///test`
LOGDIR='/var/log/duplicity'
DPBX_APP_KEY="trsyeoi9h23x3rv"
DPBX_APP_SECRET="ayxhen7ojvza1wo"
DPBX_ACCESS_TOKEN="7HslJwV13ZAAAAAAAAAAC_jCBV4ZHyPFx-I4jsRplpJwQ2tMFesgEcndc78A8pyp"


# Setting the pass phrase to encrypt the backup files. Will use symmetrical keys in this case.
PASSPHRASE='yoursecretgpgpassphrase'
export PASSPHRASE
export DPBX_APP_KEY
export DPBX_APP_SECRET
export DPBX_ACCESS_TOKEN

# encryption algorithm for gpg, disable for default (CAST5)
# see available ones via 'gpg --version'
ALGO=AES

##############################

if [ $ALGO ]; then
 GPGOPT="--gpg-options '--cipher-algo $ALGO'"
fi

if [ $BPASSWORD ]; then
 BAC="$BPROTO://$BUSER:$BPASSWORD@$BHOST"
else
 BAC="$BPROTO://$BUSER@$BHOST"
fi

# Check to see if we're at the first of the month.
# If we are on the 1st day of the month, then run
# a full backup. If not, then run an incremental
# backup.

if [ $DATE = 01 ] || [ "$1" = 'full' ]; then
 TYPE='full'
else
 TYPE='incremental'
fi



for DIR in $BDIRS
do
  if [ $DIR = '.' ]; then
    EXCLUDELIST='/usr/local/etc/duplicity-exclude.conf'
  else
    EXCLUDELIST="/usr/local/etc/duplicity-exclude-$DIR.conf"
  fi

  if [ -f $EXCLUDELIST ]; then
    EXCLUDE="--exclude-filelist $EXCLUDELIST"
  else
    EXCLUDE=''
  fi

  # first remove everything older than 2 months
  if [ $DIR = '.' ]; then
   CMD="duplicity remove-older-than 2M -v5 --force $BAC/$TDIR-system >> $LOGDIR/system.log"
  else
   CMD="duplicity remove-older-than 2M -v5 --force $BAC/$TDIR-$DIR >> $LOGDIR/$DIR.log"
  fi
  eval $CMD

  # do a backup
  if [ $DIR = '.' ]; then
    CMD="duplicity $TYPE -v5 $GPGOPT $EXCLUDE / $BAC/$TDIR-system >> $LOGDIR/system.log"
  else
    CMD="duplicity $TYPE -v5 $GPGOPT $EXCLUDE /$DIR $BAC/$TDIR-$DIR >> $LOGDIR/$DIR.log"
  fi

  CMD="duplicity full /Users/nils/Documents/bzr/duplicity/testing/testfiles/ dpbx:///test"
  eval  $CMD

done

# Check the manpage for all available options for Duplicity.
# Unsetting the confidential variables
unset PASSPHRASE
unset FTP_PASSWORD

exit 0
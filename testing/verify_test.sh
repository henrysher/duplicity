#!/bin/sh
# Script to show the current behaviour of duplicity's verify action
# (c) 2014 Aaron Whitehouse <aaron@whitehouse.kiwi.nz>
# GPLv2 or any later version
export PASSPHRASE=test

TESTDIR=/tmp/duplicity_test
mkdir $TESTDIR
SOURCEDIR=$TESTDIR/dup_source
mkdir $SOURCEDIR
TARGETDIR=$TESTDIR/dup_target
mkdir $TARGETDIR

DUPLICITY_CMD="../bin/duplicity"

$DUPLICITY_CMD -V

echo "==========="
echo "FIRST TEST."
echo "==========="
echo "Testing behaviour of verify when the source files change after the backup."
echo "This is a test" > $SOURCEDIR/test.txt
$DUPLICITY_CMD $SOURCEDIR file://$TARGETDIR
echo "-----------"
echo "Normal verify before we've done anything. This should pass and does" 
echo "on 0.6.23."
$DUPLICITY_CMD verify file://$TARGETDIR $SOURCEDIR 
echo "-----------"
echo "Change the source file after sleeping for a second."
# Sleep for a second, as otherwise the mtime can be the same even if it was edited after backup.
sleep 1
echo "This is changing the test file." > $SOURCEDIR/test.txt
echo "-----------"
echo "Verify again. This should pass, but does not on 0.6.23."
$DUPLICITY_CMD verify file://$TARGETDIR $SOURCEDIR
echo "-----------"
echo "Verify again, but with --compare-data. As --compare-data is designed to" 
echo "check against the filesystem, this should fail and does on 0.6.23."
echo "Note that this should flag a difference in the Data as well, but does not"
echo "on 0.6.23, whereas it does so in the Second Test."
$DUPLICITY_CMD verify --compare-data file://$TARGETDIR $SOURCEDIR

rm -r $TESTDIR

echo "============"
echo "SECOND TEST."
echo "============"
echo "Testing behaviour of verify when the source files change after the backup,"
echo "but deliberately change the mtime of the file after editing it so that it"
echo "matches the original file."

mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR

echo "This is a second test that doesn't change mtime" > $SOURCEDIR/test.txt
$DUPLICITY_CMD $SOURCEDIR file://$TARGETDIR
echo "-----------"
echo "Normal verify before we've done anything. This should pass and does on 0.6.23."
$DUPLICITY_CMD verify file://$TARGETDIR $SOURCEDIR 
echo "-----------"
echo "Change the source file after sleeping for a second, but change the mtime to match the original."
# Sleep for a second, as otherwise the mtime can be the same even if it was edited after backup.
sleep 1
cp -p $SOURCEDIR/test.txt $SOURCEDIR/test-temp.txt
echo "This is changing the test file." > $SOURCEDIR/test.txt
touch --reference=$SOURCEDIR/test-temp.txt $SOURCEDIR/test.txt
rm -f $SOURCEDIR/test-temp.txt
touch --reference=$SOURCEDIR/test.txt $SOURCEDIR
echo "-----------"
echo "Verify again. This should pass and does on 0.6.23 (though only because it is 'tricked' by the mtime)."
$DUPLICITY_CMD verify file://$TARGETDIR $SOURCEDIR
echo "-----------"
echo "Verify again, but with --compare-data. As --compare-data is designed to" 
echo "check against the filesystem, this should fail and currently does."
echo "Note that, unlike the First Test, on 0.6.23 this flags a difference in the Data."
$DUPLICITY_CMD verify --compare-data file://$TARGETDIR $SOURCEDIR

rm -r $TESTDIR

echo "==========="
echo "THIRD TEST."
echo "==========="
echo "Testing behaviour of verify when the source files are unchanged after the backup,"
echo "but the archive files are deliberately corrupted."

mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR

echo "This is a third test that just corrupts the archive." > $SOURCEDIR/test.txt
$DUPLICITY_CMD $SOURCEDIR file://$TARGETDIR
echo "-----------"
echo "Normal verify before we've done anything. This should pass and does on 0.6.23."
$DUPLICITY_CMD verify file://$TARGETDIR $SOURCEDIR 
echo "-----------"
echo "Corrupt the archive."
find $TARGETDIR -name 'duplicity-full*.vol*' -exec dd if=/dev/urandom of='{}' bs=1024 seek=$((RANDOM%10+1)) count=1 conv=notrunc \; 
echo "-----------"
echo "Verify again. This should fail, as verify should check the integrity of the archive in either mode, and it does on 0.6.23."
$DUPLICITY_CMD verify file://$TARGETDIR $SOURCEDIR
echo "-----------"
echo "Verify again, but with --compare-data. This should also fail, as verify should check the integrity of the archive"
echo "in either mode, and it does on 0.6.23."
$DUPLICITY_CMD verify --compare-data file://$TARGETDIR $SOURCEDIR

rm -r $TESTDIR

unset PASSPHRASE


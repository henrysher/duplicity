#!/bin/sh
# Script to show the current behaviour of duplicity's --include/exclude-filelist-stdin 
# function. This is currently hard to show in functional tests because the stdin-processing
# logic is in the commandline parser. 
# (c) 2015 Aaron Whitehouse <aaron@whitehouse.kiwi.nz>
# GPLv2 or any later version
export PASSPHRASE=test

TESTDIR=/tmp/duplicity_test
mkdir $TESTDIR
SOURCEDIR=$TESTDIR/dup_source
mkdir $SOURCEDIR
TARGETDIR=$TESTDIR/dup_target
mkdir $TARGETDIR
RESTOREDIR=$TESTDIR/dup_restore
mkdir $RESTOREDIR

tar -C $SOURCEDIR -xvf testfiles.tar.gz testfiles/select 

DUPLICITY_CMD="../bin/duplicity"
export PYTHONPATH=../

$DUPLICITY_CMD -V

echo "==========="
echo "FIRST TEST."
echo "==========="
TEST1="Test with exclude-globbing"
echo "${TEST1}"
echo "+ $SOURCEDIR/testfiles/select/1/1" > $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/1/2" >> $TESTDIR/exclude.txt
echo "+ $SOURCEDIR/testfiles/select/1/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/**" >> $TESTDIR/exclude.txt

$DUPLICITY_CMD --exclude-globbing-filelist $TESTDIR/exclude.txt $SOURCEDIR file://$TARGETDIR
$DUPLICITY_CMD file://$TARGETDIR $RESTOREDIR
echo "Number of files/folders:"
OUTPUT_TEST1="$(find $RESTOREDIR | wc -l)"
echo "${OUTPUT_TEST1}"

rm -r $TESTDIR

echo "==========="
echo "SECOND TEST."
echo "==========="
TEST2="Test with exclude"
echo "${TEST2}"

mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR
mkdir $RESTOREDIR
tar -C $SOURCEDIR -xvf testfiles.tar.gz testfiles/select 

echo "+ $SOURCEDIR/testfiles/select/1/1" > $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/1/2" >> $TESTDIR/exclude.txt
echo "+ $SOURCEDIR/testfiles/select/1/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/**" >> $TESTDIR/exclude.txt

$DUPLICITY_CMD --exclude-filelist $TESTDIR/exclude.txt $SOURCEDIR file://$TARGETDIR
$DUPLICITY_CMD file://$TARGETDIR $RESTOREDIR
echo "Number of files/folders:"
find $RESTOREDIR | wc -l
OUTPUT_TEST2="$(find $RESTOREDIR | wc -l)"
echo "${OUTPUT_TEST2}"

rm -r $TESTDIR

echo "==========="
echo "THIRD TEST."
echo "==========="
TEST3="Test with stdin with exclude"
echo "${TEST3}"
mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR
mkdir $RESTOREDIR
tar -C $SOURCEDIR -xvf testfiles.tar.gz testfiles/select 

echo "+ $SOURCEDIR/testfiles/select/1/1" > $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/1/2" >> $TESTDIR/exclude.txt
echo "+ $SOURCEDIR/testfiles/select/1/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/**" >> $TESTDIR/exclude.txt

cat $TESTDIR/exclude.txt | $DUPLICITY_CMD --exclude-filelist-stdin $SOURCEDIR file://$TARGETDIR
$DUPLICITY_CMD file://$TARGETDIR $RESTOREDIR
echo "Number of files/folders:"
OUTPUT_TEST3="$(find $RESTOREDIR | wc -l)"
echo "${OUTPUT_TEST3}"

rm -r $TESTDIR

echo "==========="
echo "FOURTH TEST."
echo "==========="
TEST4="Test with nothing"
echo "${TEST4}"
mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR
mkdir $RESTOREDIR
tar -C $SOURCEDIR -xvf testfiles.tar.gz testfiles/select 

echo "+ $SOURCEDIR/testfiles/select/1/1" > $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/1/2" >> $TESTDIR/exclude.txt
echo "+ $SOURCEDIR/testfiles/select/1/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/**" >> $TESTDIR/exclude.txt

$DUPLICITY_CMD $SOURCEDIR file://$TARGETDIR
$DUPLICITY_CMD file://$TARGETDIR $RESTOREDIR
echo "Number of files/folders:"
OUTPUT_TEST4="$(find $RESTOREDIR | wc -l)"
echo "${OUTPUT_TEST4}"

rm -r $TESTDIR

echo "==========="
echo "FIFTH TEST."
echo "==========="
TEST5="Test using /dev/stdin as a substitute for --exclude-filelist-stdin"
echo "${TEST5}"
mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR
mkdir $RESTOREDIR
tar -C $SOURCEDIR -xvf testfiles.tar.gz testfiles/select 

echo "+ $SOURCEDIR/testfiles/select/1/1" > $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/1/2" >> $TESTDIR/exclude.txt
echo "+ $SOURCEDIR/testfiles/select/1/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/testfiles/select/3" >> $TESTDIR/exclude.txt
echo "- $SOURCEDIR/**" >> $TESTDIR/exclude.txt

cat $TESTDIR/exclude.txt | $DUPLICITY_CMD --exclude-filelist /dev/stdin $SOURCEDIR file://$TARGETDIR
$DUPLICITY_CMD file://$TARGETDIR $RESTOREDIR
echo "Number of files/folders:"
OUTPUT_TEST5="$(find $RESTOREDIR | wc -l)"
echo "${OUTPUT_TEST5}"

rm -r $TESTDIR

echo "==========="
echo "SIXTH TEST."
echo "==========="
TEST6="Test with stdin with include"
echo "${TEST6}"
mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR
mkdir $RESTOREDIR
tar -C $SOURCEDIR -xvf testfiles.tar.gz testfiles/select 

echo "+ $SOURCEDIR/testfiles/select/1/1" > $TESTDIR/include.txt
echo "- $SOURCEDIR/testfiles/select/1/2" >> $TESTDIR/include.txt
echo "+ $SOURCEDIR/testfiles/select/1/3" >> $TESTDIR/include.txt
echo "- $SOURCEDIR/testfiles/select/3" >> $TESTDIR/include.txt
echo "- $SOURCEDIR/**" >> $TESTDIR/include.txt

cat $TESTDIR/include.txt | $DUPLICITY_CMD --include-filelist-stdin $SOURCEDIR file://$TARGETDIR
$DUPLICITY_CMD file://$TARGETDIR $RESTOREDIR
echo "Number of files/folders:"
OUTPUT_TEST6="$(find $RESTOREDIR | wc -l)"
echo "${OUTPUT_TEST6}"

rm -r $TESTDIR

echo "============"
echo "SEVENTH TEST."
echo "============"
TEST7="Test using /dev/stdin as a substitute for --include-filelist-stdin"
echo "${TEST7}"
mkdir $TESTDIR
mkdir $SOURCEDIR
mkdir $TARGETDIR
mkdir $RESTOREDIR
tar -C $SOURCEDIR -xvf testfiles.tar.gz testfiles/select 

echo "+ $SOURCEDIR/testfiles/select/1/1" > $TESTDIR/include.txt
echo "- $SOURCEDIR/testfiles/select/1/2" >> $TESTDIR/include.txt
echo "+ $SOURCEDIR/testfiles/select/1/3" >> $TESTDIR/include.txt
echo "- $SOURCEDIR/testfiles/select/3" >> $TESTDIR/include.txt
echo "- $SOURCEDIR/**" >> $TESTDIR/include.txt

cat $TESTDIR/include.txt | $DUPLICITY_CMD --include-filelist /dev/stdin $SOURCEDIR file://$TARGETDIR
$DUPLICITY_CMD file://$TARGETDIR $RESTOREDIR
echo "Number of files/folders:"
OUTPUT_TEST7="$(find $RESTOREDIR | wc -l)"
echo "${OUTPUT_TEST7}"

rm -r $TESTDIR

unset PASSPHRASE
echo "1.""${TEST1}" "${OUTPUT_TEST1}"
echo "2.""${TEST2}" "${OUTPUT_TEST2}"
echo "3.""${TEST3}" "${OUTPUT_TEST3}"
echo "4.""${TEST4}" "${OUTPUT_TEST4}"
echo "5.""${TEST5}" "${OUTPUT_TEST5}"
echo "6.""${TEST6}" "${OUTPUT_TEST6}"
echo "7.""${TEST7}" "${OUTPUT_TEST7}"

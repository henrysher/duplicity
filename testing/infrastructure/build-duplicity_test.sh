#!/bin/bash

cd duplicity_test
cp -p ../../../requirements.txt .
cp -p ../id_rsa .
cp -p ../id_rsa.pub .

docker build --tag dernils/duplicitytest:latest .
rm requirements.txt
rm id_rsa
rm id_rsa.pub 

cd ..
cd ftp_server
docker build --tag dernils/duplicity_testinfrastructure_ftp:latest .

cd ..
cd ssh_server
cp -p ../id_rsa.pub .
docker build --tag dernils/duplicity_testinfrastructure_ssh:latest .
rm id_rsa.pub 

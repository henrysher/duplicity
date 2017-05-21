#!/bin/bash

cd duplicity_test
cp -p ../../../requirements.txt .
cp -p ../id_rsa .
cp -p ../id_rsa.pub .
docker build --tag firstprime/duplicity_test:latest .
rm requirements.txt
rm id_rsa
rm id_rsa.pub
cd ..

cd ftp_server
docker build --tag firstprime/duplicity_ftp:latest .
cd ..

cd ssh_server
cp -p ../id_rsa.pub .
docker build --tag firstprime/duplicity_ssh:latest .
rm id_rsa.pub
cd ..

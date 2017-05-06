#!/bin/bash

cd duplicity_test
cp -p ../../../requirements.txt .
docker build --tag dernils/duplicitytest:latest .
rm requirements.txt

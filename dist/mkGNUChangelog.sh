#!/bin/bash

# must be in root of BZR project
cd /home/ken/workspace/duplicity-0.6-series

# make changelog
bzr log --gnu-changelog > Changelog.GNU

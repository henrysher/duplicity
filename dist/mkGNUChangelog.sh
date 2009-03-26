#!/bin/bash

# must be in root of CVS project
cd /home/ken/workspace/duplicity-src

# make changelog with full email addresses
rcs2log -i 4 -l 79 \
-u $'loafman\tKenneth Loafman\tkenneth@loafman.com' \
-u $'bescoto\tBen Escoto\tben@emrose.org' \
-u $'jinty\tBrian Sutherland\tjinty@lentejasverdes.ath.cx' > Changelog.GNU

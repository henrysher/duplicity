#!/bin/bash

for t in *test.py test_tarfile.py; do
    echo "========== Starting $t =========="
    sudo python -u $t 2>&1 | grep -v "unsafe ownership"
    echo "========== Finished $t =========="
    echo
    echo
done

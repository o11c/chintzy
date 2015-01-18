#!/bin/sh
set -e
rm -rf .coverage/
python ./coverage.py
! rgrep -n '^>' .coverage
rv=$?
make -k -j`nproc` -f graphs.make
if [ $rv = 0 ]; then
echo 'Everything is Ok.'
else
echo 'Something is wrong!'
fi

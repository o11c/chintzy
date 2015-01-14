#!/bin/sh -e
rm -rf .coverage/
python ./coverage.py
! rgrep -n '^>' .coverage
rv=$?
if [ $rv = 0 ]; then
echo 'Everything is Ok.'
else
echo 'Something is wrong!'
fi

#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


CACHE_DIR=$SCRIPT_DIR/../tmp/.mypy_cache


cd $SCRIPT_DIR/../src


echo "running mypy"
echo "ignore line warning using: # type: ignore"

MYPY_ERR_PATH="/tmp/mypy.err.txt"
FAILED=0
mypy --cache-dir $CACHE_DIR --no-strict-optional --ignore-missing-imports -p clevokeyboardcontrol -p testclevokeyboardcontrol \
     2> "$MYPY_ERR_PATH" || FAILED=1

if [ $FAILED -ne 0 ]; then
	cat "$MYPY_ERR_PATH"
	# shellcheck disable=SC2002
	ASSERTION=$(cat $MYPY_ERR_PATH | grep "AssertionError:")
	if [ "$ASSERTION" == "" ]; then
		exit 1
	else
		# mypy internal error
		echo "detected mypy internal error"
	fi
else
	echo "mypy finished"
fi

#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


CACHE_DIR=$SCRIPT_DIR/../tmp/.mypy_cache


cd $SCRIPT_DIR/../src


mypy --cache-dir $CACHE_DIR --no-strict-optional --ignore-missing-imports -p clevokeyboardcontrol -p testclevokeyboardcontrol

echo "mypy finished"

#!/bin/bash

set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"


cd $SCRIPT_DIR

python3 -m testclevokeyboardcontrol


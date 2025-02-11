#!/bin/bash

set -eu

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


## ensure required version of pip3
pip3 install --upgrade 'pip>=18.0' --break-system-packages


## install requirements
pip3 install -r $SCRIPT_DIR/requirements.txt --break-system-packages


echo -e "\ninstallation done\n"

#!/bin/bash

set -e


while :; do
    echo $(date) "idle time[ms]:" $(xprintidle)
    sleep 1
done

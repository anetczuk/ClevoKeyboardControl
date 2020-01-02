#!/bin/bash

set -e


while :; do
    echo $(xset q | grep Monitor) \
        "brightness:" $(cat /sys/class/backlight/intel_backlight/brightness) \
        "actual_brightness:" $(cat /sys/class/backlight/intel_backlight/actual_brightness) \
        "bl_power:" $(cat /sys/class/backlight/intel_backlight/bl_power)
    sleep 1
done


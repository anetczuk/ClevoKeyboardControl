#!/bin/bash


if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit
fi


#### listing groups
## cut -d: -f1 /etc/group | sort


KBD_GROUP=clevo-keyboard
DRIVER_ROOT=/sys/devices/platform/tuxedo_keyboard


## add group

groupadd "$KBD_GROUP"


## set files attributes

files=( "$DRIVER_ROOT/brightness" 
        "$DRIVER_ROOT/color_center" 
        "$DRIVER_ROOT/color_left" 
        "$DRIVER_ROOT/color_right" 
        "$DRIVER_ROOT/mode" 
        "$DRIVER_ROOT/state"
)


for i in "${files[@]}"; do
    echo "setting attriutes for file: $i"
    chgrp "$KBD_GROUP" "$i"
    chmod g+w "$i"
done

echo -e "call:\n\tsudo usermod -a -G $KBD_GROUP userName\nto add user to $KBD_GROUP group"

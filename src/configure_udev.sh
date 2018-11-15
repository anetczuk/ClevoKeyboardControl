#!/bin/bash


if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit
fi


## add group
KBD_GROUP=clevo-keyboard

groupadd "$KBD_GROUP"

echo -e "call:\n\tsudo usermod -a -G $KBD_GROUP userName\nto add user to $KBD_GROUP group"


## add udev rule
RULE_FILE=/etc/udev/rules.d/30-tuxedo_keyboard.rules 

cat > $RULE_FILE << EOL
##
## change group and permissions of driver sysfs files
##
SUBSYSTEM=="platform", DRIVER=="tuxedo_keyboard", PROGRAM="/bin/sh -c 'chgrp $KBD_GROUP /sys%p/*'"
SUBSYSTEM=="platform", DRIVER=="tuxedo_keyboard", PROGRAM="/bin/sh -c 'chmod g=u /sys%p/*'"
EOL


#### test rules, so rules will apply
udevadm test /sys/devices/platform/tuxedo_keyboard/

## reload udev configuration
udevadm control --reload

## run rules
udevadm trigger


#!/bin/bash

set -eu


if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi


##
## Parse arguments
##
USER=""
for i in "$@"; do
    case $i in
        -u=*|--user=*)
            USER="${i#*=}"
            shift # past argument=value
            ;;
        *)
            ## unknown option
            ;;
    esac
done


## add group
KBD_GROUP=clevo-keyboard

groupadd "$KBD_GROUP" || true


if [ ! -z "$USER" ]; then
    echo "adding user $USER to group $KBD_GROUP"
    usermod -a -G "$KBD_GROUP" "$USER"
else
    echo "pass --user={user} parameter to allow given user to access the driver"
    #echo -e "call:\n\tsudo usermod -a -G $KBD_GROUP userName\nto add user to $KBD_GROUP group"
    exit 1
fi


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


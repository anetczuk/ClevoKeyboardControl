#!/bin/bash

set -e


sleep 1


##
## start screen saver
##
dbus-send --session --dest=org.freedesktop.ScreenSaver --type=method_call --print-reply /ScreenSaver org.freedesktop.ScreenSaver.SetActive boolean:true

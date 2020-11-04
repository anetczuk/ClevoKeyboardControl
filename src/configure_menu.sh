#!/bin/bash


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


## add udev rule
AUTOSTART_FILE=~/.local/share/applications/menulibre-clevo-keyboard.desktop


cat > $AUTOSTART_FILE << EOL
[Desktop Entry]
Version=1.1
Type=Application
Name=Clevo Keyboard
Comment=A small descriptive blurb about this application.
Icon=$SCRIPT_DIR/clevokeyboardcontrol/gui/img/keyboard-source.png
Exec=$SCRIPT_DIR/clevokbdctl
Path=$SCRIPT_DIR
Actions=
Categories=Office;X-XFCE;X-Xfce-Toplevel;
StartupNotify=true

EOL


echo "File created in: $AUTOSTART_FILE"

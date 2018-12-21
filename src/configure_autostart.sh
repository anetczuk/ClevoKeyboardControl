#!/bin/bash


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


## add udev rule
AUTOSTART_FILE=~/.config/autostart/ClevoKeyboardControl.desktop


cat > $AUTOSTART_FILE << EOL
[Desktop Entry]
Type=Application
Categories=Office;
Name=ClevoKeyboardControl
GenericName=Clevo keyboard backlight control
Comment=Control Your Clevo keyboard backlight through GUI application
Exec=$SCRIPT_DIR/clevokbdctl --minimized
Icon=$SCRIPT_DIR/clevokeyboardcontrol/gui/img/keyboard-source.png
Terminal=false
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOL


echo "File created in: $AUTOSTART_FILE"

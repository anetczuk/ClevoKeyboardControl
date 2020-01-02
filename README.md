# Clevo Keyboard GUI

Application allows convenient control of Clevo keyboard LED backlight. In addition it 
restores lights settings after startup and returning from suspend state.


## Features
- system tray icon
- persisting application settings
- restoring LED seetings after suspension / hibernation
- turning LED off durning screen saver
- detection of LED settings changed externally


## Screens

![Keyboard settings](doc/app-screen-device.png "Keyboard settings")
![Application settings](doc/app-screen-settings.png "Application settings")


## Requirements
- *Clevo* based device
- *tuxedo-keyboard* driver
- *PyQt5*
- *watchdog*

It's recommended to install *PyQt5* by ```apt install python3-pyqt5```

For more info about installing *tuxedo-keyboard* driver visit:
https://github.com/tuxedocomputers/tuxedo-keyboard


## Permissions

Application requires that user have permission to write to driver's sysfs files.
To do so run *configure_udev.sh* to add udev rule permitting *clevo-keyboard* group to modify the files.
Then add Your user to the group. It might require rebooting the system.


## Running application

To run application try one of:
- run *src/clevokbdctl*
- run *src/clevokeyboardcontrol/main.py* 
- execute ```cd src; python3 -m clevokeyboardcontrol```

Application can be run in profiler mode passing *--profile* as command line parameter. 


## Running tests

To run tests execute *src/runtests.py*. It can be run with code profiling 
and code coverage options.

In addition there is demo application not requiring installed drivers. It 
can be run by *testclevokeyboardcontrol/gui/main_window_example.py*.


## Autostrart

You can easily add application to autostart by running *configure_autostart.sh*. 
No special proviledges required.


## Modules
- clevokeyboardcontrol.main -- entry point for the application
- testclevokeyboardcontrol -- unit tests for the application


## Examples of use of not obvious Python mechanisms
- properly killing (Ctrl+C) PyQt (*sigint.py*)
- loading of UI files and inheriting from it
- code profiling (*cProfile*)
- code coverage (*coverage*)


## ToDo
- add support for old *clevo-wmi* driver
- add keyboard sleep option (after certain inactivity)


## References
- https://github.com/tuxedocomputers/tuxedo-keyboard



# Clevo Keyboard GUI

Application allows convenient control of Clevo keyboard LED backlight.


## Features
- system tray icon
- persisting application settings


## Screenshots
TODO: add screenshots


## Requirements
- Clevo based device
- PyQt5
- tuxedo-keyboard

For more info about installing *tuxedo-keyboard* driver visit:
https://github.com/tuxedocomputers/tuxedo-keyboard


## Running application

To run application try one of:
- run *src/startApp.sh*
- run *src/clevokeyboardgui/main.py* 
- execute *cd src; python3 -m clevokeyboardgui*
Application can be run in profiler mode passing *--profile* as command line parameter. 


## Running tests

To run tests execute *src/runtests.py*. It can be run with code profiling 
and code coverage options.

In addition there is demo application not requiring installed drivers. It 
can be run by *testclevokeyboardgui/gui/main_window_example.py*.


## Modules
- clevokeyboardgui.main -- entry point for the application
- testclevokeyboardgui -- unit tests for the application


## Examples of use of not obvious Python mechanisms:
- properly killing (Ctrl+C) PyQt (*sigint.py*)
- loading of UI files and inheriting from it
- code profiling (*cProfile*)
- code coverage (*coverage*)


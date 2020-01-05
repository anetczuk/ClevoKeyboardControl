#!/usr/bin/env python3


import sys
import os

### append clevo library
script_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath( os.path.join(script_dir, "..") ))

import logging
import clevokeyboardcontrol.logger as logger

from gi.repository import GObject
from clevokeyboardcontrol.screensaverwatcher import ScreenSaverWatcher


logFile = logger.getLoggingOutputFile()
logger.configure( logFile )

_LOGGER = logging.getLogger(__name__)


class ScreenSaverActivity():

    def __init__(self):
        self.detector = ScreenSaverWatcher()
        self.detector.setCallback( self._screenSaverActivationCallback )

    def _screenSaverActivationCallback(self, activated):
        _LOGGER.info( "screen saver active: %s", activated )


if __name__ == '__main__':
    #from .main import main

    _LOGGER.debug("Logger log file: %s" % logger.log_file)

    activity = ScreenSaverActivity()

    # Start the loop and wait for the signal
    GObject.MainLoop().run()


#!/usr/bin/python3
#
#     ClevoKeyboardControl. Control of keyboard backlights.
#
#     Copyright (C) 2018  Arkadiusz Netczuk <dev.arnet@gmail.com>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#


import sys
import os


#### append local library
sys.path.append(os.path.abspath( os.path.join(os.path.dirname(__file__), "../..") ))


import argparse
import logging

import clevokeyboardcontrol.logger as logger

from testclevokeyboardcontrol.clevodrivermock import ClevoDriverMock

from clevokeyboardcontrol.gui.qt import QApplication
from clevokeyboardcontrol.gui.sigint import setup_interrupt_handling
from clevokeyboardcontrol.gui.main_window import MainWindow



## ============================= main section ===================================



if __name__ != '__main__':
    sys.exit(0)

parser = argparse.ArgumentParser(description='Clevo Keyboard Control')
parser.add_argument('--minimized', action='store_const', const=True, default=False, help='Start minimized' )
parser.add_argument('--profile', action='store_const', const=True, default=False, help='Profile the code' )
parser.add_argument('--pfile', action='store', default=None, help='Profile the code and output data to file' )


args = parser.parse_args()


logFile = logger.getLoggingOutputFile()
logger.configure( logFile )


_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("\n\n")
_LOGGER.debug("Starting the test application")

_LOGGER.debug("Logger log file: %s" % logFile)


exitCode = 0

try:

    driver = ClevoDriverMock()

    app = QApplication(sys.argv)
    app.setApplicationName("ClevoKeyboardControl")
    app.setOrganizationName("arnet")
    ### app.setOrganizationDomain("www.my-org.com")

    window = MainWindow(driver)
    window.loadSettings()

    if args.minimized == False:
        window.show()

    setup_interrupt_handling()

    exitCode = app.exec_()

    if exitCode == 0:
        window.saveSettings()

    _LOGGER.info("Done with exit code: %s", exitCode)

except:
    exitCode = 1
    _LOGGER.exception("Exception occured")
    raise

sys.exit(exitCode)

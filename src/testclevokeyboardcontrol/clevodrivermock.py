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


import logging

from clevokeyboardcontrol.clevoio import ClevoDriver, FilePath



_LOGGER = logging.getLogger(__name__)



class ClevoDriverMock(ClevoDriver):

    def __init__(self):
        self.data = dict()
        self.data[ FilePath.STATE_PATH ]         = 0
        self.data[ FilePath.BRIGHTNESS_PATH ]    = 0
        self.data[ FilePath.MODE_PATH ]          = 0
        self.data[ FilePath.COLOR_LEFT_PATH ]    = "0"
        self.data[ FilePath.COLOR_CENTER_PATH ]  = "0"
        self.data[ FilePath.COLOR_RIGHT_PATH ]   = "0"

    def getDriverRootDirectory(self):
        return None

    def _read(self, fileType: FilePath):
        _LOGGER.debug("reading mock from file: %s", fileType)
        retVal = self.data[ fileType ]
        _LOGGER.debug("returning mock value: %s", retVal)
        return retVal

    def _store(self, fileType: FilePath, value: str):
        _LOGGER.debug("writing to mock file: %s %r",  fileType, value)
        self.data[ fileType ] = value

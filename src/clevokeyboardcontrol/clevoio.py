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


import os
import logging

from enum import Enum, unique, auto



_LOGGER = logging.getLogger(__name__)



@unique
class Mode(Enum):

    ## contains two accessors: 'name' and 'value'

    Custom      = 0
    Breathe     = 1
    Cycle       = 2
    Dance       = 3
    Flash       = 4
    RandomColor = 5
    Tempo       = 6
    Wave        = 7


    def __str__(self):
        return "%s.%s[%s]" % (self.__class__.__name__, self.name, self.value )

    @classmethod
    def find(cls, value):
        for item in cls:
            if item.value == value:
                return item
        return None


@unique
class Panel(Enum):
    Left    = auto()
    Center  = auto()
    Right   = auto()


@unique
class FilePath(Enum):
    STATE_PATH          = auto()
    BRIGHTNESS_PATH     = auto()
    MODE_PATH           = auto()
    COLOR_LEFT_PATH     = auto()
    COLOR_CENTER_PATH   = auto()
    COLOR_RIGHT_PATH    = auto()

    @classmethod
    def findByName(cls, name):
        for item in cls:
            if item.name == name:
                return item
        return None



class ClevoDriver():

    def __init__(self):
        pass

    def getDriverRootDirectory(self):
        raise NotImplementedError('You need to define this method in derived class!')

    def getState(self):
        value = int( self.readString(FilePath.STATE_PATH) )
        _LOGGER.debug("got state: %r",  value)
        if value == 0:
            return False
        else:
            return True

    def setState(self, enabled: bool):
        _LOGGER.debug("setting led state: %i",  enabled)
        if enabled == True:
            self.storeString( FilePath.STATE_PATH, 1 )
        else:
            self.storeString( FilePath.STATE_PATH, 0 )

    def getBrightness(self):
        value = int( self.readString(FilePath.BRIGHTNESS_PATH) )
        _LOGGER.debug("got brightness: %r",  value)
        return value

    def setBrightness(self, value: int):
        _LOGGER.debug("setting brightness: %i",  value)
        value = max(value, 0)
        value = min(value, 255)
        self.storeString( FilePath.BRIGHTNESS_PATH, value )

    def getMode(self):
        value = int( self.readString(FilePath.MODE_PATH) )
        enumVal = Mode( value )
        _LOGGER.debug("got mode: %r",  enumVal)
        return enumVal

    def setMode(self, mode: Mode):
        _LOGGER.debug("setting mode: %s",  mode)
        self.storeString( FilePath.MODE_PATH, mode.value )

    def getColorLeft(self):
        return self.getColor(Panel.Left)

    def getColorCenter(self):
        return self.getColor(Panel.Center)

    def getColorRight(self):
        return self.getColor(Panel.Right)

    def getColor(self, panel):
        fileType = self._getPanelFile( panel )
        hexString = self.readString( fileType )
        value = int(hexString, 16)
        red = (value >> 16) & 255
        green = (value >> 8) & 255
        blue = value & 255
        retColor = [red, green, blue]
        _LOGGER.debug("got color for %s: %r", panel, retColor)
        return retColor

    def setColorLeft(self, red, green, blue):
        self.setColor( Panel.Left, red, green, blue )

    def setColorCenter(self, red, green, blue):
        self.setColor( Panel.Center, red, green, blue )

    def setColorRight(self, red, green, blue):
        self.setColor( Panel.Right, red, green, blue )

    def setColor(self, panel: Panel, red, green, blue):
        colorValue = (red << 16) + (green << 8) + blue
        hexValue = hex(colorValue)
        _LOGGER.debug("setting color for %s: %s", panel.name, hexValue)
        file = self._getPanelFile( panel )
        self.storeString( file, hexValue )

    def _getPanelFile(self, panel: Panel):
        if panel == Panel.Left:
            return FilePath.COLOR_LEFT_PATH
        elif panel == Panel.Center:
            return FilePath.COLOR_CENTER_PATH
        elif panel == Panel.Right:
            return FilePath.COLOR_RIGHT_PATH
        else:
            raise ValueError("unhandled value: " + str(panel))

    def readDriverState(self):
        _LOGGER.debug("reading driver's state")
        ret = dict()
        for key in FilePath:
            val = self.readString( key )
            keyStr = key.name
            ret[ keyStr ] = val
        return ret

    def setDriverState(self, stateDict: dict):
        _LOGGER.debug("setting driver's state")
        for key in stateDict:
            val = stateDict[ key ]
            keyEnum = FilePath.findByName( key )
            self.storeString( keyEnum, val )

    def readString(self, fileType: FilePath):
        val = self._read( fileType )
        if fileType == fileType.COLOR_LEFT_PATH:
            return self._filterColor( val )
        if fileType == fileType.COLOR_CENTER_PATH:
            return self._filterColor( val )
        if fileType == fileType.COLOR_RIGHT_PATH:
            return self._filterColor( val )
        return val

    def _filterColor(self, value: str):
        if value.startswith("0x") == True:
            return value
        return "0x" + value

    def storeString(self, fileType: FilePath, value: str):
        self._store( fileType, value )

    def _read(self, fileType: FilePath):
        raise NotImplementedError('You need to define this method in derived class!')

    def _store(self, fileType: FilePath, value: str):
        raise NotImplementedError('You need to define this method in derived class!')



class TuxedoDriver( ClevoDriver ):

    DRIVERFS_PATH       = '/sys/devices/platform/tuxedo_keyboard'

    STATE_PATH          = DRIVERFS_PATH + '/state'
    BRIGHTNESS_PATH     = DRIVERFS_PATH + '/brightness'
    MODE_PATH           = DRIVERFS_PATH + '/mode'
    COLOR_LEFT_PATH     = DRIVERFS_PATH + '/color_left'
    COLOR_CENTER_PATH   = DRIVERFS_PATH + '/color_center'
    COLOR_RIGHT_PATH    = DRIVERFS_PATH + '/color_right'

    filePaths = {
        FilePath.STATE_PATH:        STATE_PATH,
        FilePath.BRIGHTNESS_PATH:   BRIGHTNESS_PATH,
        FilePath.MODE_PATH:         MODE_PATH,
        FilePath.COLOR_LEFT_PATH:   COLOR_LEFT_PATH,
        FilePath.COLOR_CENTER_PATH: COLOR_CENTER_PATH,
        FilePath.COLOR_RIGHT_PATH:  COLOR_RIGHT_PATH
    }


    def __init__(self):
        super().__init__()

    def getDriverRootDirectory(self):
        return self.DRIVERFS_PATH

    def _read(self, fileType: FilePath):
        _LOGGER.debug("reading from file: %s", fileType)
        filePath = self._getFile( fileType )
        file = None
        try:
            file = open( filePath, "r")
            dataStr = str(file.readline())
            dataStr = dataStr.rstrip()
            _LOGGER.debug("returning value: %s", dataStr)
            return dataStr
        except PermissionError:
#           sys.exit("needs to be run as root!")
            _LOGGER.exception("exception occurred")
            return None
        finally:
            if file != None:
                file.close()

    def _store(self, fileType: FilePath, value: str):
        filePath = self._getFile( fileType )
        fd = None
        try:
            fd = os.open( filePath, os.O_WRONLY)
            dataStr = str(value)
            dataStr = dataStr.rstrip()
            data = bytes( dataStr+"\n", 'UTF-8')
            os.write(fd, data )
        except OSError:
            _LOGGER.exception("unable to store data[%s] for file[%s]", value, fileType)
        except PermissionError:
            _LOGGER.exception("exception occurred")
        finally:
            if fd != None:
                os.close(fd)

    def _getFile(self, fileType: FilePath):
        return self.filePaths[ fileType ]

# MIT License
# 
# Copyright (c) 2017 Arkadiusz Netczuk <dev.arnet@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
    ROOT_PATH           = auto()
    STATE_PATH          = auto()
    BRIGHTNESS_PATH     = auto()
    MODE_PATH           = auto()
    COLOR_LEFT_PATH     = auto()
    COLOR_CENTER_PATH   = auto()
    COLOR_RIGHT_PATH    = auto()



class ClevoDriver():
    
    def __init__(self):
        pass
    
    def getState(self):
        value = int( self._read(FilePath.STATE_PATH) )
        _LOGGER.debug("got state: %r",  value)
        if value == 0:
            return False
        else:
            return True
    
    def setState(self, enabled: bool):
        _LOGGER.debug("setting led state: %i",  enabled)
        if enabled == True:
            self._store( FilePath.STATE_PATH, 1 )
        else:
            self._store( FilePath.STATE_PATH, 0 )
    
    def getBrightness(self):
        value = int( self._read(FilePath.BRIGHTNESS_PATH) )
        _LOGGER.debug("got brightness: %r",  value)
        return value   
    
    def setBrightness(self, value: int):
        _LOGGER.debug("setting brightness: %i",  value)
        value = max(value, 0)
        value = min(value, 255)
        self._store( FilePath.BRIGHTNESS_PATH, value )
        
    def getMode(self):
        value = int( self._read(FilePath.MODE_PATH) )
        enumVal = Mode( value )
        _LOGGER.debug("got mode: %r",  enumVal)
        return enumVal   
        
    def setMode(self, mode: Mode):
        _LOGGER.debug("setting mode: %s",  mode)
        self._store( FilePath.MODE_PATH, mode.value )
    
    def getColorLeft(self):
        return self.getColor(Panel.Left)
        
    def getColorCenter(self):
        return self.getColor(Panel.Center)
        
    def getColorRight(self):
        return self.getColor(Panel.Right)
    
    def getColor(self, panel):
        fileType = self._getPanelFile( panel )
        hexString = self._read( fileType )
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
        self._store( file, hexValue )
    
    def _getPanelFile(self, panel: Panel):
        if panel == Panel.Left:
            return FilePath.COLOR_LEFT_PATH
        elif panel == Panel.Center:
            return FilePath.COLOR_CENTER_PATH
        elif panel == Panel.Right:
            return FilePath.COLOR_RIGHT_PATH
        else:
            raise ValueError("unhandled value: " + str(panel))
        
    
    def _read(self, fileType: FilePath):
        filePath = self._getFile( fileType )
        file = None
        try:
            file = open( filePath, "r")
            data = str(file.readline())
            return data
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
            data = bytes( str(value)+"\n", 'UTF-8')
            os.write(fd, data )
        except PermissionError:
            _LOGGER.exception("exception occurred")
        finally:
            if fd != None:
                os.close(fd)
                
    def _getFile(self, fileType: FilePath):
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
        FilePath.ROOT_PATH:         DRIVERFS_PATH,
        FilePath.STATE_PATH:        STATE_PATH,
        FilePath.BRIGHTNESS_PATH:   BRIGHTNESS_PATH,
        FilePath.MODE_PATH:         MODE_PATH,
        FilePath.COLOR_LEFT_PATH:   COLOR_LEFT_PATH,
        FilePath.COLOR_CENTER_PATH: COLOR_CENTER_PATH,
        FilePath.COLOR_RIGHT_PATH:  COLOR_RIGHT_PATH
    }
    
    
    def __init__(self):
        super().__init__()
    
    def _getFile(self, fileType: FilePath):
        return self.filePaths[ fileType ]
    
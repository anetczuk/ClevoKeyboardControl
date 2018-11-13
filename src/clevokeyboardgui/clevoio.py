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

from enum import Enum, unique



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
    Left    = 0
    Center  = 1
    Right   = 2



class ClevoDriver():

    DRIVERFS_PATH       = '/sys/devices/platform/tuxedo_keyboard'
    STATE_PATH          = DRIVERFS_PATH + '/state'
    BRIGHTNESS_PATH     = DRIVERFS_PATH + '/brightness'
    MODE_PATH           = DRIVERFS_PATH + '/mode'
    COLOR_LEFT_PATH     = DRIVERFS_PATH + '/color_left'
    COLOR_CENTER_PATH   = DRIVERFS_PATH + '/color_center'
    COLOR_RIGHT_PATH    = DRIVERFS_PATH + '/color_right'
    
    
    def __init__(self):
        pass
    
    def getState(self):
        value = int( self.read(self.STATE_PATH) )
        _LOGGER.debug("got state: %r",  value)
        if value == 0:
            return False
        else:
            return True
    
    def setState(self, enabled: bool):
        _LOGGER.debug("setting led state: %i",  enabled)
        if enabled == True:
            self.store( self.STATE_PATH, 1 )
        else:
            self.store( self.STATE_PATH, 0 )
    
    def getBrightness(self):
        value = int( self.read(self.BRIGHTNESS_PATH) )
        _LOGGER.debug("got brightness: %r",  value)
        return value   
    
    def setBrightness(self, value: int):
        _LOGGER.debug("setting brightness: %i",  value)
        value = max(value, 0)
        value = min(value, 255)
        self.store( self.BRIGHTNESS_PATH, value )
        
    def getMode(self):
        value = int( self.read(self.MODE_PATH) )
        enumVal = Mode( value )
        _LOGGER.debug("got mode: %r",  enumVal)
        return enumVal   
        
    def setMode(self, mode: Mode):
        _LOGGER.debug("setting mode: %s",  mode)
        self.store( self.MODE_PATH, mode.value )
    
    def getColorLeft(self):
        return self.getColor(Panel.Left)
        
    def getColorCenter(self):
        return self.getColor(Panel.Center)
        
    def getColorRight(self):
        return self.getColor(Panel.Right)
    
    def getColor(self, panel):
        file = self._getPanelFile( panel )
        hexString = self.read(file)
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
        self.store( file, hexValue )
    
    def _getPanelFile(self, panel: Panel):
        if panel == Panel.Left:
            return self.COLOR_LEFT_PATH
        elif panel == Panel.Center:
            return self.COLOR_CENTER_PATH
        elif panel == Panel.Right:
            return self.COLOR_RIGHT_PATH
        else:
            raise ValueError("unhandled value: " + str(panel))
    
    def read(self, filePath: str):
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
    
    def store(self, filePath: str, value: str):
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
    
    
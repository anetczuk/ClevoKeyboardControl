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
import os

from .sysfswatchdog import SysFSWatcher


_LOGGER = logging.getLogger(__name__)


def readFile( file_path ):
    file = None
    try:
        file = open( file_path, "r")
        dataStr = str(file.readline())
        dataStr = dataStr.rstrip()
        return dataStr
    except Exception:
        _LOGGER.error("unable to read data for file[%s]", file_path)
        raise
    finally:
        if file is not None:
            file.close()


class DeviceWatcher():

    logger = None

    def __init__(self, driver_path, index):
        self.watcherIndex = index
        self.stateCallback = None
        self.driverPath = driver_path
#         self.brightnessFile = self.driverPath + "/actual_brightness"
        self.powerFile = self.driverPath + "/bl_power"

#         self.actualBrightness = self._readActualBrightness()
        self.blPower = self._readPower()

#         self.brightnessWatcher = SysFSWatcher()
#         self.brightnessWatcher.setCallback( self._sysfsBrightnessChanged )
#         self.brightnessWatcher.watch( self.brightnessFile, False )

        self.watcher = SysFSWatcher("SSaverThread")
        self.watcher.setCallback( self._sysfsPowerChanged )
        self.watcher.watch( self.driverPath, False )

    def setCallback(self, callback):
        self.stateCallback = callback

#     def _sysfsBrightnessChanged(self):
#         newValue = self._readActualBrightness()
#         if newValue == self.actualBrightness:
#             return
#         self.actualBrightness = newValue
#         if self.stateCallback is None:
#             self.logger.debug( "brightness file changed to: %s" % newValue )
#             return
#         self.stateCallback( self.watcherIndex )

    def _sysfsPowerChanged(self):
        newValue = self._readPower()
        if newValue == self.blPower:
            self.logger.debug( "power file not changed" )
            return
        self.blPower = newValue
        if self.stateCallback is None:
            self.logger.debug( "power file changed to: %s" % newValue )
            return
        self.logger.debug( "power file changed to: %s" % newValue )
        self.stateCallback( self.watcherIndex )

#     def _readActualBrightness(self):
#         return int( readFile(self.brightnessFile) )

    def _readPower(self):
        """
        Read power state of backlight.

        Returns True if backlight is powered, otherwise False.
        """
        ## 0 -- power on
        ## 4 -- power off
        currVal = int( readFile(self.powerFile) )
        if currVal == 0:
            return True
        return False


DeviceWatcher.logger = _LOGGER.getChild(DeviceWatcher.__name__)


class ScreenSaverWatcher():
    """
    Watch for changes in backlight driver.

    Note: Xfce blocks Qt event loop when session is locked, so it cannot be
    wrapped around QtObject if backlight needs to be monitored even when user's
    session is locked.
    """

    logger = None

    def __init__(self):
        self.watchers = []
        self.isLEDOn = True
        self.callbackEnabled = None
        self.stateCallback = None

        backlight_dir = "/sys/class/backlight/"
        for f in os.listdir(backlight_dir):
            item_path = os.path.join(backlight_dir, f)
            if os.path.isdir(item_path):
                self.logger.debug( "registering device watcher: {0}".format( item_path ) )
                watcher = DeviceWatcher( item_path, len(self.watchers) )
                watcher.setCallback( self._sysfsChanged )
                self.watchers.append( watcher )
        self.isLEDOn = self._isBacklightOn()

    def setEnabled(self, newState):
        self.callbackEnabled = newState

    def setCallback(self, callback):
        self.stateCallback = callback

    def _sysfsChanged( self, deviceIndex ):
        deviceWatcher = self.watchers[ deviceIndex ]
        newPower = deviceWatcher.blPower
        if newPower:
            if self.isLEDOn:
                ## screen power state not changed
                self.logger.debug( "device's power file changed to %s" % newPower )
                return
        else:
            if not self.isLEDOn:
                ## screen power state not changed
                self.logger.debug( "device's power file changed to %s" % newPower )
                return
        newPowerState = self._isBacklightOn()
        if newPowerState == self.isLEDOn:
            ## screen power state not changed
            self.logger.debug( "device's power file changed to %s" % newPower )
            return
        if self.stateCallback is None or self.callbackEnabled is False:
            self.logger.debug( "device's power file changed to %s" % newPower )
            return
        self.isLEDOn = newPowerState
        self.stateCallback( not self.isLEDOn )

    def _isBacklightOn(self):
        for w in self.watchers:
            if w.blPower:
                return True
        return False


ScreenSaverWatcher.logger = _LOGGER.getChild(ScreenSaverWatcher.__name__)

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

from . import uiloader
from .qt import pyqtSignal
from .tray_icon import TrayIconTheme


UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)


class SettingsWidget(QtBaseClass):

    restoreDriver            = pyqtSignal( dict )
    iconThemeChanged         = pyqtSignal( TrayIconTheme )
    handleSuspendChanged     = pyqtSignal( bool )
    handleScreenSaverChanged = pyqtSignal( bool )

    def __init__(self, parentWidget=None):
        super().__init__(parentWidget)

        self.driverState = dict()

        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.ui.restoreSuspendCB.stateChanged.connect( self._toggleResumeSuspend )
        self.ui.screenSaverLEDOffCB.stateChanged.connect( self._toggleScreenSaverLED )

        self.ui.restoreStartCB.setChecked( True )
        self.ui.restoreSuspendCB.setChecked( True )
        self.ui.screenSaverLEDOffCB.setChecked( True )

        ## tray combo box
        self.ui.trayThemeCB.currentIndexChanged.connect( self._trayThemeChanged )
        for item in TrayIconTheme:
            itemName = item.name
            self.ui.trayThemeCB.addItem( itemName, item )

    def readDriverState(self, driver):
        self.driverState = driver.readDriverState()
        ##_LOGGER.info("driver state: %r", self.driverState)

    def requestDriverRestore(self):
        self._emitDriverRestore( True )

    ## =====================================================

    def _trayThemeChanged(self):
        selectedTheme = self.ui.trayThemeCB.currentData()
        self.iconThemeChanged.emit( selectedTheme )

    def _toggleResumeSuspend(self, state):
        ## state: 0 -- unchecked
        ## state: 2 -- checked
        enabled = (state != 0)
        self.handleSuspendChanged.emit( enabled )

    def _toggleScreenSaverLED(self, state):
        ##_LOGGER.info("toggling screen saver LED")
        ## state: 0 -- unchecked
        ## state: 2 -- checked
        enabled = (state != 0)
        self.handleScreenSaverChanged.emit( enabled )

    ## =====================================================

    def loadSettings(self, settings):
        self._loadDriverState(settings)

        settings.beginGroup( self.objectName() )

        restoreStartValue = settings.value("restoreStart", True, type=bool)
        self.ui.restoreStartCB.setChecked( restoreStartValue )

        restoreSuspendValue = settings.value("restoreSuspend", True, type=bool)
        self.ui.restoreSuspendCB.setChecked( restoreSuspendValue )

        handleScreenSaverLEDValue = settings.value("turnLEDOffOnScreenSaver", True, type=bool)
        self.ui.screenSaverLEDOffCB.setChecked( handleScreenSaverLEDValue )

        trayTheme = settings.value("trayIcon", None, type=str)
        self._setCurrentTrayTheme( trayTheme )

        settings.endGroup()

        self._emitDriverRestore( restoreStartValue )

    def saveSettings(self, settings):
        self._saveDriverState(settings)

        settings.beginGroup( self.objectName() )

        restoreStartValue = self.ui.restoreStartCB.isChecked()
        settings.setValue("restoreStart", restoreStartValue)

        restoreSuspendValue = self.ui.restoreSuspendCB.isChecked()
        settings.setValue("restoreSuspend", restoreSuspendValue)

        handleScreenSaverLEDValue = self.ui.screenSaverLEDOffCB.isChecked()
        settings.setValue("turnLEDOffOnScreenSaver", handleScreenSaverLEDValue)

        selectedTheme = self.ui.trayThemeCB.currentData()
        settings.setValue("trayIcon", selectedTheme.name)

        settings.endGroup()

    def _loadDriverState(self, settings):
        settings.beginGroup( "DriverState" )
        state = loadKeysToDict( settings )
        settings.endGroup()
        if bool(state) is False:
            ## state dictionary is empty
            return
        self.driverState = state
        _LOGGER.debug( "loaded driver state: %r", self.driverState )

    def _saveDriverState(self, settings):
        if bool(self.driverState) is False:
            ## state dictionary is empty
            return
        _LOGGER.debug( "Saving driver state: %r", self.driverState )
        settings.beginGroup( "DriverState" )
        for key in self.driverState:
            val = self.driverState[ key ]
            settings.setValue( key, val)
        settings.endGroup()

    def _setCurrentTrayTheme( self, trayTheme: str ):
        themeIndex = TrayIconTheme.indexOf( trayTheme )
        if themeIndex < 0:
            _LOGGER.debug("could not find index for theme: %r", trayTheme)
            return
        self.ui.trayThemeCB.setCurrentIndex( themeIndex )

    def _emitDriverRestore(self, emitState=True):
        if emitState is True:
            self.restoreDriver.emit( self.driverState )
        else:
            self.restoreDriver.emit( dict() )


def loadKeysToDict(settings):
    state = dict()
    for key in settings.childKeys():
        value = settings.value(key, "", type=str)
        if len(value) > 0:
            state[ key ] = value
    return state


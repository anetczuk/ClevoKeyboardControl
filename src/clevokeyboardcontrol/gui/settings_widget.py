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
from . import suspenddetector
from .tray_icon import TrayIconTheme



UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)



class SettingsWidget(QtBaseClass):
    
    restoreDriver       = pyqtSignal( dict )
    iconThemeChanged    = pyqtSignal( TrayIconTheme )
    
    
    def __init__(self, parentWidget = None):
        super().__init__(parentWidget)
        
        self.driverState = None
        
        self.ui = UiTargetClass()
        self.ui.setupUi(self)
        
        self.suspendDetector = suspenddetector.QSuspendDetector(self)
        self.suspendDetector.resumed.connect( self._suspensionRestored )
        
        self.ui.restoreSuspendCB.stateChanged.connect( self._toggleResumeSuspend )
        
        ## tray combo box
        self.ui.trayThemeCB.currentIndexChanged.connect( self._trayThemeChanged )
        for item in TrayIconTheme:
            itemName = item.name
            self.ui.trayThemeCB.addItem( itemName, item )


    def driverChanged(self, driver):
        self.driverState = driver.readDriverState()
        ##_LOGGER.info("driver state: %r", self.driverState)

    
    ## =====================================================

    
    def _suspensionRestored(self):
        self._emitDriverRestore()
            
    def _toggleResumeSuspend(self, state):
        ## state: 0 -- unchecked
        ## state: 2 -- checked
        enabled = (state != 0)
        if enabled == True:
            self.suspendDetector.start()
        else:
            self.suspendDetector.stop()
    
    def _trayThemeChanged(self):
        selectedTheme = self.ui.trayThemeCB.currentData()
        self.iconThemeChanged.emit( selectedTheme )
    
    
    ## =====================================================
    
    
    def loadSettings(self, settings):
        self._loadDriverState(settings)
        
        settings.beginGroup( self.objectName() )
        restoreStartValue = settings.value("restoreStart", True, type=bool)
        self.ui.restoreStartCB.setChecked( restoreStartValue )
        restoreSuspendValue = settings.value("restoreSuspend", True, type=bool)
        self.ui.restoreSuspendCB.setChecked( restoreSuspendValue )
        trayTheme = settings.value("trayIcon", None, type=str)
        self._setCurrentTrayTheme( trayTheme )
        settings.endGroup()
        
        if restoreStartValue == True:
            self._emitDriverRestore()
    
    def _loadDriverState(self, settings):
        state = dict()
        settings.beginGroup( "DriverState" )
        for key in settings.childKeys():
            value = settings.value(key, "", type=str)
            if len(value) > 0:
                state[ key ] = value
        settings.endGroup()
        if bool(state) == False:
            ## state dictionary is empty
            return
        self.driverState = state
        _LOGGER.debug( "loaded driver state: %r", self.driverState )
    
    def saveSettings(self, settings):
        self._saveDriverState(settings)
        
        settings.beginGroup( self.objectName() )
        restoreStartValue = self.ui.restoreStartCB.isChecked()
        settings.setValue("restoreStart", restoreStartValue)
        restoreSuspendValue = self.ui.restoreSuspendCB.isChecked()
        settings.setValue("restoreSuspend", restoreSuspendValue)
        selectedTheme = self.ui.trayThemeCB.currentData()
        settings.setValue("trayIcon", selectedTheme.name)
        settings.endGroup()
        
    def _saveDriverState(self, settings):
        _LOGGER.debug( "Saving driver state: %r", self.driverState )
        if self.driverState == None:
            return
        settings.beginGroup( "DriverState" )
        for key in self.driverState:
            val = self.driverState[ key ]
            settings.setValue( key, val)
        settings.endGroup()
    
    def _setCurrentTrayTheme( self, trayTheme: str ):
        themeIndex = TrayIconTheme.indexOf( trayTheme )
        if themeIndex < 0:
            _LOGGER.warn("could not find index for theme: %r", trayTheme)
            return
        self.ui.trayThemeCB.setCurrentIndex( themeIndex )
    
    def _emitDriverRestore(self):
        if self.driverState == None:
            return
        self.restoreDriver.emit( self.driverState )
    
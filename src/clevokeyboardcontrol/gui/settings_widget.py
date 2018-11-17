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


import logging

from . import uiloader
from .qt import pyqtSignal
from . import suspenddetector



UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)



class SettingsWidget(QtBaseClass):
    
    restoreDriver = pyqtSignal( dict )
    
    
    def __init__(self, parentWidget = None):
        super().__init__(parentWidget)
        
        self.driverState = None
        
        self.ui = UiTargetClass()
        self.ui.setupUi(self)
        
        self.suspendDetector = suspenddetector.QSuspendDetector(self)
        self.suspendDetector.resumed.connect( self._suspensionRestored )
        
        self.ui.restoreSuspendCB.stateChanged.connect( self._toggleResumeSuspend )

    def driverChanged(self, driver):
        self.driverState = driver.readDriverState()
        ##_LOGGER.info("driver state: %r", self.driverState)
    
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
    
    
    ## =====================================================
    
    
    def loadSettings(self, settings):
        self._loadDriverState(settings)
        
        settings.beginGroup( self.objectName() )
        restoreStartValue = settings.value("restoreStart", True, type=bool)
        self.ui.restoreStartCB.setChecked( restoreStartValue )
        restoreSuspendValue = settings.value("restoreSuspend", True, type=bool)
        self.ui.restoreSuspendCB.setChecked( restoreSuspendValue )
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
    
    def _emitDriverRestore(self):
        if self.driverState == None:
            return
        self.restoreDriver.emit( self.driverState )
    
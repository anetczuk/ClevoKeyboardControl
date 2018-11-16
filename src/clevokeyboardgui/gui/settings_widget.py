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



UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)



class SettingsWidget(QtBaseClass):
    
    restoreDriver   = pyqtSignal( dict )
    
    
    def __init__(self, parentWidget = None):
        super().__init__(parentWidget)
        
        self.driverState = None
        
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

    def driverChanged(self, driver):
        self.driverState = driver.readDriverState()
        ##_LOGGER.info("driver state: %r", self.driverState)
    
    
    ## =====================================================
    
    
    def loadSettings(self, settings):
        self._loadDriverState(settings)
        
        settings.beginGroup( self.objectName() )
        restoreValue = settings.value("restore", True, type=bool)
        self.ui.restoreCB.setChecked( restoreValue )
        settings.endGroup()
        
        if restoreValue == True and self.driverState != None:
            self.restoreDriver.emit( self.driverState )
    
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
        _LOGGER.debug( "Loaded driver state: %r", self.driverState )
    
    def saveSettings(self, settings):
        self._saveDriverState(settings)
        
        settings.beginGroup( self.objectName() )
        restoreValue = self.ui.restoreCB.isChecked()
        settings.setValue("restore", restoreValue)
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
    
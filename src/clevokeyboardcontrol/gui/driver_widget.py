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
from .qt import QtGui
from ..clevoio import Mode as ClevoMode, ClevoDriver
from ..sysfswatchdog import SysFSWatcher



UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)



class DriverWidget(QtBaseClass):
    
    driverChanged   = pyqtSignal( ClevoDriver )
    
    
    def __init__(self, parentWidget = None):
        super().__init__(parentWidget)
        
        self.ui = UiTargetClass()
        self.ui.setupUi(self)
        
        self.driver = None
        self.watcher = None
        
        self._initModeCB()

        ## connect signals
        self.ui.refreshWidgetPB.clicked.connect( self.refreshWidgets )
        self.ui.refreshDriverPB.clicked.connect( self.refreshDriver )
        
        self.ui.stateCB.stateChanged.connect( self._toggleLED )
        
        self.ui.brightnessSlider.valueChanged.connect( self._brightnessChanged )
        self._setBrightnessLabel( self.ui.brightnessSlider.value() )
        
        self.ui.modeCB.currentIndexChanged.connect( self._modeChanged )
        
        self.ui.leftColor.colorChanged.connect( self._leftColorChanged )
        self.ui.centerColor.colorChanged.connect( self._centerColorChanged )
        self.ui.rightColor.colorChanged.connect( self._rightColorChanged )

        self.ui.setToAllLeftPB.clicked.connect( self._setLeftToAll )
        self.ui.setToAllCenterPB.clicked.connect( self._setCenterToAll )
        self.ui.setToAllRightPB.clicked.connect( self._setRightToAll )

    def _initModeCB(self):
        for item in ClevoMode:
            self.ui.modeCB.addItem( item.name, item )

    def attachDriver(self, driver):
        _LOGGER.debug("attaching driver")
        self.driver = driver
        
        if self.watcher != None:
            self.watcher.stop()
        self.watcher = SysFSWatcher()
        self.watcher.setCallback( self._sysfsChanged )
        driverDir = self.driver.getDriverRootDirectory()
        self.watcher.watch(driverDir, False)
        
        ## self.refreshWidgets()               ## read driver state

    def refreshWidgets(self):
        self._refreshView()
        self.driverChanged.emit( self.driver )
    
    def _refreshView(self):
        _LOGGER.debug("refreshing widget")
        
        self.ui.stateCB.blockSignals( True )
        ledOn = self.driver.getState()
        self.ui.stateCB.setChecked( ledOn )
        self.ui.stateCB.blockSignals( False )
        
        self.ui.brightnessSlider.blockSignals( True )
        brightness = self.driver.getBrightness()
        self.ui.brightnessSlider.setValue( brightness )
        self._setBrightnessLabel( brightness )
        self.ui.brightnessSlider.blockSignals( False )
        
        self.ui.modeCB.blockSignals( True )
        mode = self.driver.getMode()
        self.ui.modeCB.setCurrentIndex( mode.value )
        self.ui.modeCB.blockSignals( False )
        
        self.ui.leftColor.blockSignals( True )
        leftPanelColor = self.driver.getColorLeft()
        leftColor = self.toQColor( leftPanelColor )
        self.ui.leftColor.updateWidget( leftColor )
        self.ui.leftColor.blockSignals( False )
        
        self.ui.centerColor.blockSignals( True )
        centerPanelColor = self.driver.getColorCenter()
        centerColor = self.toQColor( centerPanelColor )
        self.ui.centerColor.updateWidget( centerColor )
        self.ui.centerColor.blockSignals( False )
        
        self.ui.rightColor.blockSignals( True )
        rightPanelColor = self.driver.getColorRight()
        rightColor = self.toQColor( rightPanelColor )
        self.ui.rightColor.updateWidget( rightColor )
        self.ui.rightColor.blockSignals( False )

    def refreshDriver(self):
        enabled = self.ui.stateCB.isChecked()
        self.driver.setState( enabled )
        
        value = self.ui.brightnessSlider.value()
        self.driver.setBrightness( value )
        
        self._modeChanged()
        
        self.ui.leftColor.emitColor()
        self.ui.centerColor.emitColor()
        self.ui.rightColor.emitColor()

    def restoreDriver(self, driverState: dict):
        _LOGGER.debug( "restoring driver state" )
        self.driver.setDriverState( driverState )
        self._refreshView()


    ### ==============================================
    
    
    def _sysfsChanged(self):
        _LOGGER.debug("detected driver external change")
        self.refreshWidgets()
        
    
    ### ==============================================
    

    def _toggleLED(self, state):
        ## state: 0 -- unchecked
        ## state: 2 -- checked
        enabled = (state != 0)
        self.driver.setState( enabled )
        self._emitDriverChange()

    def _brightnessChanged(self, value: int):
        self.driver.setBrightness( value )
        self._setBrightnessLabel( value )
        self._emitDriverChange()

    def _setBrightnessLabel(self, value: int):
        valueString = str(value)
        if len(valueString) == 1:
            valueString = "00" + valueString
        elif len(valueString) == 2:
            valueString = "0" + valueString
        self.ui.brightnessValue.setText( valueString )
        
    def _modeChanged(self):
        selectedMode = self.ui.modeCB.currentData()
        self.driver.setMode( selectedMode )
        self._emitDriverChange()
        
    def _leftColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorLeft( red, green, blue )
        self._emitDriverChange()
        
    def _centerColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorCenter( red, green, blue )
        self._emitDriverChange()
        
    def _rightColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorRight( red, green, blue )
        self._emitDriverChange()

    def _setLeftToAll(self):
        color = self.ui.leftColor.getColor()
        self.ui.centerColor.setColor(color)
        self.ui.rightColor.setColor(color)
    
    def _setCenterToAll(self):
        color = self.ui.centerColor.getColor()
        self.ui.leftColor.setColor(color)
        self.ui.rightColor.setColor(color)
    
    def _setRightToAll(self):
        color = self.ui.rightColor.getColor()
        self.ui.leftColor.setColor(color)
        self.ui.centerColor.setColor(color)
        
    def _emitDriverChange(self):
        ##self.watcher.ignoreNextEvent()
        self.driverChanged.emit( self.driver )

    @staticmethod
    def toQColor(driverColor):
        red = driverColor[0]
        green = driverColor[1]
        blue = driverColor[2]
        return QtGui.QColor( red, green, blue )

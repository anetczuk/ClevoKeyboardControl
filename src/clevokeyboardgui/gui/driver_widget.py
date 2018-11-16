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
from .qt import QtGui
from ..clevoio import Mode as ClevoMode, ClevoDriver



UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)



class DriverWidget(QtBaseClass):
    
    driverChanged   = pyqtSignal( ClevoDriver )
    
    
    def __init__(self, parentWidget = None):
        super().__init__(parentWidget)
        
        self.ui = UiTargetClass()
        self.ui.setupUi(self)
        
        self.driver = None
        
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
        self.driver = driver
        
        ## read driver state
        self.refreshWidgets()

    def refreshWidgets(self):
        self._refreshView()
        self.driverChanged.emit( self.driver )
    
    def _refreshView(self):
        _LOGGER.debug("refreshing widget")
        ledOn = self.driver.getState()
        self.ui.stateCB.setChecked( ledOn )
        
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
        self.driver.setDriverState( driverState )
        self._refreshView()


    ### ==============================================
    

    def _toggleLED(self, state):
        ## state: 0 -- unchecked
        ## state: 2 -- checked
        enabled = (state != 0)
        self.driver.setState( enabled )
        self.driverChanged.emit( self.driver )

    def _brightnessChanged(self, value: int):
        self.driver.setBrightness( value )
        self._setBrightnessLabel( value )
        self.driverChanged.emit( self.driver )

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
        self.driverChanged.emit( self.driver )
        
    def _leftColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorLeft( red, green, blue )
        self.driverChanged.emit( self.driver )
        
    def _centerColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorCenter( red, green, blue )
        self.driverChanged.emit( self.driver )
        
    def _rightColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorRight( red, green, blue )
        self.driverChanged.emit( self.driver )

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

    @staticmethod
    def toQColor(driverColor):
        red = driverColor[0]
        green = driverColor[1]
        blue = driverColor[2]
        return QtGui.QColor( red, green, blue )

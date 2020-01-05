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
from .qt import QtCore, QtGui
from ..clevoio import Mode as ClevoMode, ClevoDriver
from ..sysfswatchdog import SysFSWatcher
from ..sysfswatchdog import WatcherBlocker


_LOGGER = logging.getLogger(__name__)


class QSysFSWatcher( QtCore.QObject ):

    sysfsChanged  = pyqtSignal()

    def __init__(self, parent):
        super().__init__( parent )
        self.detector = SysFSWatcher("DriverThread")
        self.detector.setCallback( self._sysfsCallback )

    def setEnabled(self, newState):
        self.detector.setEnabled(newState)

    def ignoreNextEvent(self):
        self.detector.ignoreNextEvent()

    def stop(self):
        self.detector.stop()

    def watch(self, directoryPath, recursiveMode: bool):
        self.detector.watch(directoryPath, recursiveMode)

    def _sysfsCallback(self):
        self.sysfsChanged.emit()


UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


class DriverWidget(QtBaseClass):

    driverChanged    = pyqtSignal( ClevoDriver )
    permissionDenied = pyqtSignal( )

    def __init__(self, parentWidget=None):
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

        if self.watcher is not None:
            self.watcher.stop()
        self.watcher = QSysFSWatcher(self)
        self.watcher.sysfsChanged.connect( self._sysfsChanged )
        driverDir = self.driver.getDriverRootDirectory()
        self.watcher.watch(driverDir, False)

        ## self.refreshWidgets()               ## read driver state

    def refreshWidgets(self):
        self._refreshView()
        self._emitDriverChange()

    def _refreshView(self):
        _LOGGER.debug("reading widget state from driver")

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
        """Set drivers values from GUI controls."""
        enabled = self.ui.stateCB.isChecked()
        self.driver.setState( enabled )

        value = self.ui.brightnessSlider.value()
        self.driver.setBrightness( value )

        selectedMode = self.ui.modeCB.currentData()
        self.driver.setMode( selectedMode )

        leftColor = self.ui.leftColor.getColor()
        self.driver.setColorLeft( leftColor.red(), leftColor.green(), leftColor.blue() )

        centerColor = self.ui.centerColor.getColor()
        self.driver.setColorCenter( centerColor.red(), centerColor.green(), centerColor.blue() )

        rightColor = self.ui.rightColor.getColor()
        self.driver.setColorRight( rightColor.red(), rightColor.green(), rightColor.blue() )

        self._emitDriverChange()

    def restoreDriver(self, driverState: dict):
        _LOGGER.debug( "restoring driver state" )
        try:
            self.driver.setDriverState( driverState )
            self._refreshView()
        except PermissionError:
            _LOGGER.exception("unable to restore driver state")
            self.permissionDenied.emit()

    def turnLED(self, newState):
        ## Xfce4 stops Qt main loop, so turning LED when screen saver changes during session lock is impossible.
        ## Workaround is to change LED state without use of signals/slots.
        self.ui.stateCB.blockSignals( True )
        self.ui.stateCB.setChecked( newState )
        self.ui.stateCB.blockSignals( False )
        self._toggleLED( newState )

    ### ==============================================

    def _sysfsChanged(self):
        ## call method from Qt's thread instead of watchdog's thread
        QtCore.QTimer.singleShot(0, self.refreshWidgets)

    ### ==============================================

    def _toggleLED(self, state):
        ## state: 0 -- unchecked
        ## state: 2 -- checked
        with WatcherBlocker(self.watcher):
            enabled = (state != 0)
            self.driver.setState( enabled )
            self._emitDriverChange()

    def _brightnessChanged(self, value: int):
        with WatcherBlocker(self.watcher):
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
        with WatcherBlocker(self.watcher):
            selectedMode = self.ui.modeCB.currentData()
            self.driver.setMode( selectedMode )
            self._emitDriverChange()

    def _leftColorChanged(self, color):
        with WatcherBlocker(self.watcher):
            self._setDeviceLeftColor(color)
            self._emitDriverChange()

    def _setDeviceLeftColor(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorLeft( red, green, blue )

    def _centerColorChanged(self, color):
        with WatcherBlocker(self.watcher):
            self._setDeviceCenterColor(color)
            self._emitDriverChange()

    def _setDeviceCenterColor(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorCenter( red, green, blue )

    def _rightColorChanged(self, color):
        with WatcherBlocker(self.watcher):
            self._setDeviceRightColor(color)
            self._emitDriverChange()

    def _setDeviceRightColor(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorRight( red, green, blue )

    def _setLeftToAll(self):
        color = self.ui.leftColor.getColor()
        self.ui.centerColor.setColor(color)
        self.ui.rightColor.setColor(color)

    def _setCenterToAll(self):
        color = self.ui.centerColor.getColor()
        with WatcherBlocker(self.watcher):
            self.ui.leftColor.updateWidget(color)
            self.ui.rightColor.updateWidget(color)
            self._setDeviceLeftColor(color)
            self._setDeviceRightColor(color)

    def _setRightToAll(self):
        color = self.ui.rightColor.getColor()
        with WatcherBlocker(self.watcher):
            self.ui.leftColor.updateWidget(color)
            self.ui.centerColor.updateWidget(color)
            self.ui.leftColor.updateWidget(color)
            self._setDeviceCenterColor(color)

    def _emitDriverChange(self):
        self.driverChanged.emit( self.driver )

    @staticmethod
    def toQColor(driverColor):
        red = driverColor[0]
        green = driverColor[1]
        blue = driverColor[2]
        return QtGui.QColor( red, green, blue )

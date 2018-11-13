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


import sys
import logging

from . import uiloader
from . import tray_icon
from . import resources
from .qt import qApp, QApplication, QIcon, QtCore

from ..clevoio import Mode as ClevoMode


_LOGGER = logging.getLogger(__name__)


UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )



class MainWindow(QtBaseClass):
    
    def __init__(self, driver):
        super().__init__()
        self.ui = UiTargetClass()
        self.ui.setupUi(self)
    
        self.driver = driver
        
        imgDir = resources.getImagePath('keyboard-white.png')
        appIcon = QIcon( imgDir )
        self.setWindowIcon( appIcon )
        
        self.statusBar().showMessage("Ready")
        
        self.trayIcon = tray_icon.TrayIcon(self)
        self.trayIcon.setToolTip("Clevo Keyboard")
        ##self.ui.appSettings.showMessage.connect( self.trayIcon.displayMessage )
        ##self.ui.appSettings.stateInfoChanged.connect( self.trayIcon.setInfo )
        self.trayIcon.show()
        
        
        ## ============ controls ====================
        
        self.ui.stateCB.stateChanged.connect( self._toggleLED )
        
        self.ui.brightnessSlider.valueChanged.connect( self._brightnessChanged )
        self._setBrightnessLabel( self.ui.brightnessSlider.value() )
        
        self._initModeCB()
        
        self.ui.leftColor.colorChanged.connect( self._leftColorChanged )
        self.ui.centerColor.colorChanged.connect( self._centerColorChanged )
        self.ui.rightColor.colorChanged.connect( self._rightColorChanged )

        self.ui.setToAllLeftPB.clicked.connect( self._setLeftToAll )
        self.ui.setToAllCenterPB.clicked.connect( self._setCenterToAll )
        self.ui.setToAllRightPB.clicked.connect( self._setRightToAll )


    def _toggleLED(self, state):
        ## state: 0 -- unchecked
        ## state: 2 -- checked
        enabled = (state != 0)
        self.driver.setState( enabled )

    def _brightnessChanged(self, value: int):
        self.driver.setBrightness( value )
        self._setBrightnessLabel( value )

    def _setBrightnessLabel(self, value: int):
        valueString = str(value)
        if len(valueString) == 1:
            valueString = "00" + valueString
        elif len(valueString) == 2:
            valueString = "0" + valueString
        self.ui.brightnessValue.setText( valueString )

    def _initModeCB(self):
        for item in ClevoMode:
            self.ui.modeCB.addItem( item.name, item )
        self.ui.modeCB.currentIndexChanged.connect( self._modeChanged )
        
    def _modeChanged(self):
        selectedMode = self.ui.modeCB.currentData()
        self.driver.setMode( selectedMode )
        
        
    def _leftColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorLeft( red, green, blue )
        
    def _centerColorChanged(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()
        self.driver.setColorCenter( red, green, blue )
        
    def _rightColorChanged(self, color):
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
        self.ui.leftColor.setColor(color)
        self.ui.rightColor.setColor(color)
    
    def _setRightToAll(self):
        color = self.ui.rightColor.getColor()
        self.ui.leftColor.setColor(color)
        self.ui.centerColor.setColor(color)
    

    def loadSettings(self):
        settings = self.getSettings()
        _LOGGER.debug( "loading app state from %s", settings.fileName() )
        ##self.ui.appSettings.loadSettings( settings )
        
        ## restore widget state and geometry
        settings.beginGroup( self.objectName() )
        geometry = settings.value("geometry")
        state = settings.value("windowState")
        if geometry != None:
            self.restoreGeometry( geometry );
        if state != None:
            self.restoreState( state );
        settings.endGroup()
        
#         ## store geometry of all widgets        
#         widgets = self.findChildren(QWidget)
#         for w in widgets:
#             wKey = getWidgetKey(w)
#             settings.beginGroup( wKey )
#             geometry = settings.value("geometry")
#             if geometry != None:
#                 w.restoreGeometry( geometry );            
#             settings.endGroup()
    
    def saveSettings(self):
        settings = self.getSettings()
        _LOGGER.debug( "saving app state to %s", settings.fileName() )
        ##self.ui.appSettings.saveSettings( settings )
        
        ## store widget state and geometry
        settings.beginGroup( self.objectName() )
        settings.setValue("geometry", self.saveGeometry() );
        settings.setValue("windowState", self.saveState() );
        settings.endGroup()

#         ## store geometry of all widgets        
#         widgets = self.findChildren(QWidget)
#         for w in widgets:
#             wKey = getWidgetKey(w)
#             settings.beginGroup( wKey )
#             settings.setValue("geometry", w.saveGeometry() );
#             settings.endGroup()
        
        ## force save to file
        settings.sync()        

    def getSettings(self):
        ## store in home directory
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "arnet", "ClevoKeyboardGui", self)
        return settings
        

    # ================================================================


    ## slot
    def closeApplication(self):
        ##self.close()
        qApp.quit()

        
    # =======================================


    # Override closeEvent, to intercept the window closing event
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.trayIcon.show()
    
    def showEvent(self, event):
        self.trayIcon.updateLabel()
    
    def hideEvent(self, event):
        self.trayIcon.updateLabel()
    

def getWidgetKey(widget):
    if widget == None:
        return None
    retKey = widget.objectName()
    widget = widget.parent()
    while widget != None:
        retKey = widget.objectName() + "-"+ retKey
        widget = widget.parent()
    return retKey

def execApp():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())


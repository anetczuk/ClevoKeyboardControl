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


import sys
import logging

from . import uiloader
from . import tray_icon
from . import resources
from .qt import qApp, QApplication, QIcon, QtCore



_LOGGER = logging.getLogger(__name__)


UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )



class MainWindow(QtBaseClass):
    
    def __init__(self, driver):
        super().__init__()
        self.ui = UiTargetClass()
        self.ui.setupUi(self)
    
        self.ui.driverWidget.attachDriver( driver )
        
        self.ui.actionExit.triggered.connect( qApp.quit )
        
        imgDir = resources.getImagePath('keyboard-white.png')
        appIcon = QIcon( imgDir )
        self.setWindowIcon( appIcon )
        
        self.statusBar().showMessage("Ready")
        
        self.trayIcon = tray_icon.TrayIcon(self)
        self.trayIcon.setToolTip("Clevo Keyboard")
        ##self.ui.appSettings.showMessage.connect( self.trayIcon.displayMessage )
        ##self.ui.appSettings.stateInfoChanged.connect( self.trayIcon.setInfo )
        self.trayIcon.show()
    
        self.ui.driverWidget.driverChanged.connect( self.ui.settingsWidget.driverChanged )
        self.ui.settingsWidget.restoreDriver.connect( self.ui.driverWidget.restoreDriver )

    def loadSettings(self):
        settings = self.getSettings()
        _LOGGER.debug( "loading app state from %s", settings.fileName() )
        self.ui.settingsWidget.loadSettings( settings )
        
        ## restore widget state and geometry
        settings.beginGroup( self.objectName() )
        geometry = settings.value("geometry")
        state = settings.value("windowState")
        if geometry != None:
            self.restoreGeometry( geometry );
        if state != None:
            self.restoreState( state );
        settings.endGroup()
    
    def saveSettings(self):
        settings = self.getSettings()
        _LOGGER.debug( "saving app state to %s", settings.fileName() )
        self.ui.settingsWidget.saveSettings( settings )
        
        ## store widget state and geometry
        settings.beginGroup( self.objectName() )
        settings.setValue("geometry", self.saveGeometry() );
        settings.setValue("windowState", self.saveState() );
        settings.endGroup()
        
        ## force save to file
        settings.sync()

    def getSettings(self):
        ## store in home directory
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "arnet", "ClevoKeyboardControl", self)
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


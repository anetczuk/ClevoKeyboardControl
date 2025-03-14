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
import subprocess
import os
import getpass

from .qt import qApp, QIcon, QtCore, QMessageBox
# from .qt import pyqtSignal
from . import uiloader
from . import tray_icon
from . import resources

from . import suspenddetector
from .. import screensaverwatcher


_LOGGER = logging.getLogger(__name__)


# class QScreenSaverDetector( QtCore.QObject ):
#
#     ssaverChanged  = pyqtSignal( bool )
#
#     def __init__(self, parent):
#         super().__init__( parent )
#         self.detector = screensaverwatcher.ScreenSaverWatcher()
#         self.detector.setCallback( self._screenSaverActivationCallback )
#
#     def setEnabled(self, newState):
#         self.detector.setEnabled( newState )
#
#     def _screenSaverActivationCallback(self, newState):
#         self.ssaverChanged.emit( newState )


UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


class MainWindow(QtBaseClass):      # type: ignore

    def __init__(self, driver):
        super().__init__()
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        ## configure objects
        self.suspendDetector = suspenddetector.QSuspendDetector(self)
        self.suspendDetector.systemResumed.connect( self.ui.settingsWidget.requestDriverRestore )
        self.suspendDetector.setEnabled( self.ui.settingsWidget.isRestoreFromSuspendEnabled() )

        self.screenSaverDetector = screensaverwatcher.ScreenSaverWatcher()
        self.screenSaverDetector.setCallback( self._screenSaverActivationCallback )
        self.screenSaverDetector.setEnabled( self.ui.settingsWidget.isScreenSaverLEDEnabled() )

        ## connect widgets
        self.ui.actionExit.triggered.connect( qApp.quit )

        self.ui.driverWidget.driverChanged.connect( self.ui.settingsWidget.readDriverState )
        self.ui.driverWidget.permissionDenied.connect( self.noDriverPermission )

        self.ui.settingsWidget.restoreDriver.connect( self.ui.driverWidget.restoreDriver )
        self.ui.settingsWidget.iconThemeChanged.connect( self.setIconTheme )
        self.ui.settingsWidget.handleSuspendChanged.connect( self.suspendDetector.setEnabled )
        self.ui.settingsWidget.handleScreenSaverChanged.connect( self.screenSaverDetector.setEnabled )

        self.ui.fixPermissionsPB.clicked.connect( self.fixPermissions )

        ## other operations
        self.ui.driverWidget.attachDriver( driver )

        self.trayIcon = tray_icon.TrayIcon(self)
        self.trayIcon.setToolTip("Clevo Keyboard")

        self.setIconTheme( tray_icon.TrayIconTheme.WHITE )

        self.trayIcon.show()

        self.statusBar().showMessage("Ready")

    def noDriverPermission(self):
        _LOGGER.debug( "received no permission signal" )
        self.ui.stackedWidget.setCurrentWidget( self.ui.errorPage )

    def fixPermissions(self):
        _LOGGER.debug( "fixing permissions" )

        ##configure_udev
        appDir = os.getcwd()
        username = getpass.getuser()
        ret = subprocess.call( ["pkexec", appDir + "/configure_udev.sh", "--user=" + username] )
        errorCode = int(ret)
        if errorCode != 0:
            _LOGGER.debug( "returned subprocess exit code: %s", errorCode )
            QMessageBox.critical(self, 'Error', "Could not fix driver permissions.")
            return

        QMessageBox.information(self, 'Info', "Fixed driver permissions. Reboot the system.")

        ## refresh view
        self.ui.stackedWidget.setCurrentWidget( self.ui.tabPage )
        self.loadSettings()

    def _screenSaverActivationCallback(self, newState):
        _LOGGER.info( "screen saver activation: %s", newState )
        if newState:
            ## turn off
            self.ui.driverWidget.turnLED( False )
        else:
            ## turn on
            self.ui.driverWidget.turnLED( True )

    # ================================================================

    def loadSettings(self):
        settings = self.getSettings()
        _LOGGER.debug( "loading app state from %s", settings.fileName() )
        self.ui.settingsWidget.loadSettings( settings )

        ## restore widget state and geometry
        settings.beginGroup( self.objectName() )
        geometry = settings.value("geometry")
        state = settings.value("windowState")
        if geometry is not None:
            self.restoreGeometry( geometry )
        if state is not None:
            self.restoreState( state )
        settings.endGroup()

    def saveSettings(self):
        settings = self.getSettings()
        _LOGGER.debug( "saving app state to %s", settings.fileName() )
        self.ui.settingsWidget.saveSettings( settings )

        ## store widget state and geometry
        settings.beginGroup( self.objectName() )
        settings.setValue("geometry", self.saveGeometry() )
        settings.setValue("windowState", self.saveState() )
        settings.endGroup()

        ## force save to file
        settings.sync()

    def getSettings(self):
        ## store in home directory
        orgName = qApp.organizationName()
        appName = qApp.applicationName()
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, orgName, appName, self)
        return settings

    # ================================================================

    def setIconTheme(self, theme: tray_icon.TrayIconTheme):
        _LOGGER.debug("setting tray theme: %r", theme)

        fileName = theme.value
        iconPath = resources.getImagePath( fileName )
        appIcon = QIcon( iconPath )

        self.setWindowIcon( appIcon )
        self.trayIcon.setIcon( appIcon )

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
    if widget is None:
        return None
    retKey = widget.objectName()
    widget = widget.parent()
    while widget is not None:
        retKey = widget.objectName() + "-" + retKey
        widget = widget.parent()
    return retKey


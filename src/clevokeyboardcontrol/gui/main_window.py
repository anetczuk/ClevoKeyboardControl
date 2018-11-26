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

from .qt import qApp, QIcon, QtCore
from . import uiloader
from . import tray_icon
from . import resources


_LOGGER = logging.getLogger(__name__)


UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


class MainWindow(QtBaseClass):

    def __init__(self, driver):
        super().__init__()
        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.ui.actionExit.triggered.connect( qApp.quit )

        self.statusBar().showMessage("Ready")

        self.trayIcon = tray_icon.TrayIcon(self)
        self.trayIcon.setToolTip("Clevo Keyboard")

        self.setIconTheme( tray_icon.TrayIconTheme.WHITE )

        self.ui.driverWidget.driverChanged.connect( self.ui.settingsWidget.driverChanged )
        self.ui.settingsWidget.restoreDriver.connect( self.ui.driverWidget.restoreDriver )

        self.ui.settingsWidget.iconThemeChanged.connect( self.setIconTheme )

        self.ui.driverWidget.attachDriver( driver )

        self.trayIcon.show()

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


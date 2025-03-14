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
import unittest
import logging

# from testclevokeyboardcontrol.clevodrivermock import ClevoDriverMock

from clevokeyboardcontrol.gui.qt import QApplication, QtCore

from clevokeyboardcontrol.gui.settings_widget import SettingsWidget as TestWidget


_LOGGER = logging.getLogger(__name__)
app = QApplication(sys.argv)


class SettingsWidgetTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        self.widget = TestWidget()
        self.receiver = SettingsReceiver()
        self.widget.restoreDriver.connect( self.receiver.driverChanged )
        self.widget.iconThemeChanged.connect( self.receiver.themeChanged )

    def tearDown(self):
        ## Called after testfunction was executed
        self.receiver = None
        self.widget = None

    def test_loadSettings_empty(self):
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "test-org", "test-app", None)

        self.widget.loadSettings(settings)
        self.assertEqual(self.receiver.driverCounter, 1)        ## receives empty dict
        self.assertEqual(self.receiver.themeCounter, 0)

    def test_saveSettings_default(self):
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "test-org", "test-app", None)

        self.widget.saveSettings(settings)

        allKeys = settings.allKeys()
        self.assertEqual( len(allKeys), 4 )
        self.assertIn("settingsWidget/restoreStart", settings.allKeys())
        self.assertIn("settingsWidget/restoreSuspend", settings.allKeys())
        self.assertIn("settingsWidget/trayIcon", settings.allKeys())
        self.assertIn("settingsWidget/turnLEDOffOnScreenSaver", settings.allKeys())

        restoreStartValue = settings.value("settingsWidget/restoreStart", None, type=bool)
        restoreSuspendValue = settings.value("settingsWidget/restoreSuspend", None, type=bool)
        trayTheme = settings.value("settingsWidget/trayIcon", None, type=str)
        turnLEDValue = settings.value("settingsWidget/turnLEDOffOnScreenSaver", None, type=bool)

        self.assertEqual( restoreStartValue, True )
        self.assertEqual( restoreSuspendValue, True )
        self.assertEqual( trayTheme, 'WHITE' )
        self.assertEqual( turnLEDValue, True )


class SettingsReceiver():

    def __init__(self):
        self.driverCounter = 0
        self.themeCounter = 0

    def driverChanged(self, driverState: dict):
        self.driverCounter += 1

    def themeChanged(self):
        self.themeCounter += 1

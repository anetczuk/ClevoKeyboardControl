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

# from testclevokeyboardcontrol.clevodrivermock import ClevoDriverMock

from clevokeyboardcontrol.gui.qt import QApplication, QtCore

from clevokeyboardcontrol.gui.settings_widget import SettingsWidget as TestWidget


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


class SettingsReceiver():

    def __init__(self):
        self.driverCounter = 0
        self.themeCounter = 0

    def driverChanged(self, driverState: dict):
        self.driverCounter += 1

    def themeChanged(self):
        self.themeCounter += 1

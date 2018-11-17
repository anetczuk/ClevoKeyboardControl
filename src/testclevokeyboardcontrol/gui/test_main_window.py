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

from testclevokeyboardcontrol.clevodrivermock import ClevoDriverMock

from clevokeyboardcontrol.gui.qt import QApplication

from clevokeyboardcontrol.gui.main_window import MainWindow as TestWidget



app = QApplication(sys.argv)



class MainWindowTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        self.driver = ClevoDriverMock()
        self.widget = TestWidget( self.driver )
  
    def tearDown(self):
        ## Called after testfunction was executed
        self.widget = None
        self.driver = None
       
    def test_test(self):
        self.assertTrue(True)



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


import unittest
import logging

from clevokeyboardcontrol.gui.suspenddetector import QSuspendSingleton


_LOGGER = logging.getLogger(__name__)


class QSuspendSingletonTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_constructor_singleton(self):
        detector1 = QSuspendSingleton()
        detector2 = QSuspendSingleton()
        self.assertEqual(detector1, detector2)

    def test_instance(self):
        detector1 = QSuspendSingleton.instance()
        detector2 = QSuspendSingleton.instance()
        self.assertEqual(detector1, detector2)


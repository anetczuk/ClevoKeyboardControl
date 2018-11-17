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

import clevokeyboardcontrol.logger as logger

import logging
import io



class LoggerTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        self.logger = logging.Logger(__name__)
        self.logger.propagate = False
        self.logger.setLevel( logging.DEBUG )
        self.buffer = io.StringIO()
        handler = logging.StreamHandler( self.buffer )
        formatter = logger.createFormatter()
        handler.setFormatter( formatter )
        self.logger.addHandler( handler )
  
    def tearDown(self):
        ## Called after testfunction was executed
        self.logger = None
        self.buffer.close()
        self.buffer = None
       
    def test_emptyMessage(self):
        self.logger.info("")
        msg = self.buffer.getvalue()
        self.assertEqual(msg, "\n")
         
    def test_newLines_Linux(self):
        self.logger.info("\n\n\n")
        msg = self.buffer.getvalue()
        self.assertEqual(msg, "\n\n\n\n")
        
    def test_newLines_Windows(self):
        self.logger.info("\r\n\r\n\r\n")
        msg = self.buffer.getvalue()
        self.assertEqual(msg, "\r\n\r\n\r\n\n")
    
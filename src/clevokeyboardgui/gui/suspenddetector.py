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

import logging

import datetime
from .qt import QtCore
from .qt import pyqtSignal



_LOGGER = logging.getLogger(__name__)



class QSuspendDetector( QtCore.QObject ):
    
    resumed   = pyqtSignal()
    
    
    def __init__(self, parent):
        super().__init__(parent)
        self.lastTime = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect( self._suspend_check )

    def start(self):
        _LOGGER.debug("starting suspension detector")
        self.lastTime = None
        self.timer.start( 1000 );                            ## triggered every second

    def stop(self):
        _LOGGER.debug("stopping suspension detector")
        self.timer.stop()

    def _suspend_check(self):
        if self.lastTime == None:
            self.lastTime = datetime.datetime.now()
            return
        currTime = datetime.datetime.now()
        timeDiff = currTime - self.lastTime
        secDiff = timeDiff.total_seconds()
        if secDiff > 3.5:
            _LOGGER.debug("resumed from suspend / hibernation after %s[s]", secDiff)
            self.resumed.emit()
        self.lastTime = currTime


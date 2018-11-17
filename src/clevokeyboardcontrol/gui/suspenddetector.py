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


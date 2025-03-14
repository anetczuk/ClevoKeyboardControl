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
from typing import Dict, Any
import datetime

from .qt import QtCore
from .qt import qApp
from .qt import pyqtSignal


_LOGGER = logging.getLogger(__name__)


class QSuspendTimer( QtCore.QObject ):

    resumed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.lastTime = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect( self.checkResumed )

    def start(self):
        _LOGGER.debug("starting suspension timer")
        self.lastTime = None
        self.timer.start( 1000 )                            ## triggered every second

    def stop(self):
        _LOGGER.debug("stopping suspension timer")
        self.timer.stop()

    def checkResumed(self):
        if self.lastTime is None:
            self.lastTime = datetime.datetime.now()
            return False
        currTime = datetime.datetime.now()
        timeDiff = currTime - self.lastTime
        secDiff = timeDiff.total_seconds()
        self.lastTime = currTime
        if secDiff < 3.5:
            return False
        _LOGGER.debug("resumed from suspend / hibernation after %s[s]", secDiff)
        self.resumed.emit()
        return True


class SingletonMeta(type):
    _instances: Dict[Any, Any] = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(SingletonMeta, self).__call__(*args, **kwargs)
        return self._instances[self]


QObjectMeta = type(QtCore.QObject)


class QSingletonMeta(QObjectMeta, SingletonMeta):       # type: ignore
    """
    Shared meta class of QObject's meta and Singleton.

    This is workaround of metaclass conflict:
    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
    """

    pass


class QSuspendSingleton( QtCore.QObject, metaclass=QSingletonMeta ):
    """Singleton."""

    resumed = pyqtSignal()
    _instance = None

    def __init__(self):
        super().__init__( qApp )
        self.timer = QSuspendTimer( self )
        self.timer.resumed.connect( self.resumed )

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    @classmethod
    def checkResumed(cls):
        timer = QSuspendSingleton().timer
        return timer.checkResumed()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = QSuspendSingleton()
        return cls._instance


class QSuspendDetector( QtCore.QObject ):

    systemResumed = pyqtSignal()

    def __init__(self, parent):
        super().__init__( parent )
        self.detector = QSuspendSingleton()             ## currently not used as singleton
        self.detector.resumed.connect( self.systemResumed )

    def setEnabled(self, enable=True):
        _LOGGER.debug("changing suspend detector state to %s" % enable)
        if enable:
            self.start()
        else:
            self.stop()

    def start(self):
        _LOGGER.debug("starting suspension detector")
        #self.detector.resumed.connect( self.systemResumed )
        self.detector.start()

    def stop(self):
        _LOGGER.debug("stopping suspension detector")
        #self.detector.resumed.disconnect( self.systemResumed )
        self.detector.stop()

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

from . import uiloader

from .qt import pyqtSignal
from .qt import QtWidgets, QtGui


UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)


class ColorWidget(QtBaseClass):     # type: ignore

    colorChanged = pyqtSignal( QtGui.QColor )      ## passes RGB value

    def __init__(self, parentWidget=None):
        super().__init__(parentWidget)

        self.ui = UiTargetClass()
        self.ui.setupUi(self)

        self.ui.redSB.valueChanged.connect( self.emitColor )
        self.ui.greenSB.valueChanged.connect( self.emitColor )
        self.ui.blueSB.valueChanged.connect( self.emitColor )

        self.ui.pickColorPB.clicked.connect(self._pickColor)

    def getColor(self):
        red = self.ui.redSB.value()
        green = self.ui.greenSB.value()
        blue = self.ui.blueSB.value()
        color = QtGui.QColor(red, green, blue)
        return color

    def setColor(self, color):
        self.updateWidget( color )
        self.colorChanged.emit( color )

    def updateWidget(self, color):
        self._updateSpinColor( color )
        self._updatePreviewColor(color)

    def emitColor(self):
        color = self.getColor()
        self._updatePreviewColor(color)
        self.colorChanged.emit( color )

    def _pickColor(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid() is False:
            _LOGGER.info("picked color is invalid")
            return
        self.setColor( color )

    def _updateSpinColor(self, color):
        red = color.red()
        green = color.green()
        blue = color.blue()

        self.blockSignals( True )
        self.ui.redSB.setValue( red )
        self.ui.greenSB.setValue( green )
        self.ui.blueSB.setValue( blue )
        self.blockSignals( False )

    def _updatePreviewColor(self, color):
        pal = self.ui.colorPreview.palette()
        pal.setColor(QtGui.QPalette.Background, color)
        self.ui.colorPreview.setAutoFillBackground(True)
        self.ui.colorPreview.setPalette(pal)


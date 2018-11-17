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

from . import uiloader

from .qt import pyqtSignal
from .qt import QtWidgets, QtGui



UiTargetClass, QtBaseClass = uiloader.loadUiFromClassName( __file__ )


_LOGGER = logging.getLogger(__name__)



class ColorWidget(QtBaseClass):
    
    colorChanged   = pyqtSignal( QtGui.QColor )      ## passes RGB value
    
    
    def __init__(self, parentWidget = None):
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
        if color.isValid() == False:
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
        pal = self.ui.colorPreview.palette();
        pal.setColor(QtGui.QPalette.Background, color);
        self.ui.colorPreview.setAutoFillBackground(True);
        self.ui.colorPreview.setPalette(pal);


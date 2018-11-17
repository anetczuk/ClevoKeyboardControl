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

#from .qt import QtCore
from .qt import qApp, QSystemTrayIcon, QMenu, QAction
from .qt import QIcon

from . import resources



_LOGGER = logging.getLogger(__name__)



class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__(parent)

        self.neutralIcon = None
        self.indicatorIcon = None
        self.currIconState = 0

        iconPath = resources.getImagePath('keyboard-white.png')
        self.setIcon( QIcon( iconPath ) )

        self.activated.connect( self._icon_activated )

        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        self.toggle_window_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        self.toggle_window_action.triggered.connect( self._toggleParent )
        quit_action.triggered.connect( qApp.quit )
        
        tray_menu = QMenu()
        tray_menu.addAction( self.toggle_window_action )
        tray_menu.addAction( quit_action )
        self.setContextMenu( tray_menu )
    
    def displayMessage(self, message):
        timeout = 10000
        ## under xfce4 there is problem with balloon icon -- it changes tray icon, so
        ## it cannot be changed back to proper one. Workaround is to use NoIcon parameter
        self.showMessage("Keyboard", message, QSystemTrayIcon.NoIcon, timeout)
        
    def setInfo(self, message):
        self.setToolTip("Keyboard: " + message)
    
    def _icon_activated(self, reason):
#         print("tray clicked, reason:", reason)
        if reason == 3:
            ## clicked
            self._toggleParent()
    
    def _toggleParent(self):
        parent = self.parent()
        if parent.isHidden():
            parent.show()
        else:
            parent.hide()
        self.updateLabel()
        
    def updateLabel(self):
        parent = self.parent()
        if parent.isHidden():
            self.toggle_window_action.setText("Show")
        else:
            self.toggle_window_action.setText("Hide")
    
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


import os

import logging


try:
    from PyQt5 import uic
except ImportError as e:
    ### No module named <name>
    logging.exception("Exception while importing")
    exit(1)

import clevokeyboardcontrol.defs as defs


def generateUIFileNameFromClassName(classFileName):
    baseName = os.path.basename(classFileName)
    nameTuple = os.path.splitext(baseName)
    return nameTuple[0] + ".ui"

def loadUi(uiFilename):
    try:
        return uic.loadUiType( os.path.join( defs.ROOT_DIR, "ui", uiFilename ) )
    except Exception as e:
        print("Exception while loading UI file:", uiFilename, e)
        raise

def loadUiFromClassName(uiFilename):
    ui_file = generateUIFileNameFromClassName(uiFilename)
    return loadUi( ui_file )


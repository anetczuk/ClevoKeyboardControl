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
import sys
import logging



script_dir = os.path.dirname(__file__)
log_file = None


def getLoggingOutputFile():
    logDir = os.path.join(script_dir, "../../tmp")
    if os.path.isdir( logDir ) == False:
        logDir = os.getcwd()

    logFile = os.path.join(logDir, "log.txt")
    return logFile


def configure( logFile = None ):
    global log_file

    log_file = logFile
    if log_file == None:
        log_file = getLoggingOutputFile()

    fileHandler    = logging.FileHandler( filename = log_file, mode = "a+" )
    consoleHandler = logging.StreamHandler( stream = sys.stdout )

    formatter = createFormatter()

    fileHandler.setFormatter( formatter )
    consoleHandler.setFormatter( formatter )

    logging.root.addHandler( consoleHandler )
    logging.root.addHandler( fileHandler )
    logging.root.setLevel( logging.DEBUG )

##     loggerFormat   = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s [%(filename)s:%(lineno)d] %(message)s'
##     dateFormat     = '%Y-%m-%d %H:%M:%S'
##     logging.basicConfig( format   = loggerFormat,
##                          datefmt  = dateFormat,
##                          level    = logging.DEBUG,
##                          handlers = [ fileHandler, consoleHandler ]
##                        )

def createFormatter():
    loggerFormat   = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s [%(filename)s:%(lineno)d] %(message)s'
    dateFormat     = '%Y-%m-%d %H:%M:%S'
    return EmptyLineFormatter( loggerFormat, dateFormat )
    ## return logging.Formatter( loggerFormat, dateFormat )



class EmptyLineFormatter(logging.Formatter):
    """
    Special formatter storing empty lines without formatting.
    """

    ## override base class method
    def format(self, record):
        msg = record.getMessage()
        clearMsg = msg.replace('\n', '')
        clearMsg = clearMsg.replace('\r', '')
        if len(clearMsg) == 0:
            return msg
        return super().format( record )


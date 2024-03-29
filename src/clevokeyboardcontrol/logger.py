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
import logging.handlers as handlers


script_dir = os.path.dirname(__file__)
log_file = None


def getLoggingOutputFile():
    logDir = os.path.join(script_dir, "../../tmp/log")
    logDir = os.path.abspath( logDir )
    os.makedirs( logDir, exist_ok=True )
    if os.path.isdir( logDir ) is False:
        ## something bad happened (or unable to create directory)
        logDir = os.getcwd()

    logFile = os.path.join(logDir, "log.txt")
    return logFile


def configure( logFile=None, logLevel=None ):
    global log_file

    log_file = logFile
    if log_file is None:
        log_file = getLoggingOutputFile()

    if logLevel is None:
        logLevel = logging.DEBUG

    ## rotation of log files, 1048576 equals to 1MB
    fileHandler    = handlers.RotatingFileHandler( filename=log_file, mode="a+", maxBytes=1048576, backupCount=100 )
    ## fileHandler    = logging.FileHandler( filename=log_file, mode="a+" )
    consoleHandler = logging.StreamHandler( stream=sys.stdout )

    formatter = createFormatter()

    fileHandler.setFormatter( formatter )
    consoleHandler.setFormatter( formatter )

    logging.root.addHandler( consoleHandler )
    logging.root.addHandler( fileHandler )
    logging.root.setLevel( logLevel )

##     loggerFormat   = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s [%(filename)s:%(lineno)d] %(message)s'
##     dateFormat     = '%Y-%m-%d %H:%M:%S'
##     logging.basicConfig( format   = loggerFormat,
##                          datefmt  = dateFormat,
##                          level    = logging.DEBUG,
##                          handlers = [ fileHandler, consoleHandler ]
##                        )


def createStdOutHandler():
    formatter = createFormatter()
    consoleHandler = logging.StreamHandler( stream=sys.stdout )
    consoleHandler.setFormatter( formatter )
    return consoleHandler


def createFormatter(loggerFormat=None):
    if loggerFormat is None:
        ## loggerFormat = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s [%(filename)s:%(lineno)d] %(message)s'
        loggerFormat = ('%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(name)s:%(funcName)s '
                        '[%(filename)s:%(lineno)d] %(message)s')
    dateFormat = '%Y-%m-%d %H:%M:%S'
    return EmptyLineFormatter( loggerFormat, dateFormat )
    ## return logging.Formatter( loggerFormat, dateFormat )


class EmptyLineFormatter(logging.Formatter):
    """Special formatter storing empty lines without formatting."""

    ## override base class method
    def format(self, record):
        msg = record.getMessage()
        clearMsg = msg.replace('\n', '')
        clearMsg = clearMsg.replace('\r', '')
        if not clearMsg:
            # empty
            return msg
        return super().format( record )

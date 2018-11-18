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
import os
import time

import hashlib

from watchdog.observers import polling
from watchdog.events import FileSystemEventHandler



_LOGGER = logging.getLogger(__name__)



class SysFSWatcher:

    def __init__(self):
        self.observer = FileContentObserver()
        self.event_handler = Handler()

    def setCallback(self, callback):
        self.event_handler.callback = callback

    def ignoreNextEvent(self):
        self.event_handler.ignoreNextEvent = True

    def watch(self, directoryPath, recursiveMode: bool):
        if directoryPath == None:
            return
        self.observer.schedule(self.event_handler, directoryPath, recursive=recursiveMode)
        self.observer.start()
        
    def stop(self):
        self.observer.stop()

    def runLoop(self):
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            _LOGGER.error("Error")

        self.observer.join()
        

class Handler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.callback = None
        self.ignoreNextEvent = False

    def on_any_event(self, event):
        ##_LOGGER.info( "Directory content modified - %s, %r", event.src_path, event )
        
        if self.ignoreNextEvent == True:
            _LOGGER.debug("detected driver external change -- ignored")
            self.ignoreNextEvent = False
            return
        
        if self.callback == None:
            _LOGGER.debug("detected driver external change -- no callback")
            return
        
        _LOGGER.debug("detected driver external change")
        self.callback()


class FileContentObserver(polling.PollingObserverVFS):
    
    def __init__(self, listdir=os.listdir):
        super().__init__(self.stat, listdir)

    def stat(self, path):
        if os.path.isdir( path ):
            ## _LOGGER.debug("performing stat on directory %r", path)
            return polling.default_stat(path)
        ## file case
        defStat = polling.default_stat(path)
        ret = StatResult(defStat, path)
        return ret


class StatResult():
    
    def __init__(self, osResult, path):
        self.osResult = osResult
        self.filePath = path
        self.mtimeField = None

    @property
    def st_ino(self):
        return self.osResult.st_ino
    
    @property
    def st_dev(self):
        return self.osResult.st_dev
    
    @property
    def st_mode(self):
        return self.osResult.st_mode
    
    @property
    def st_mtime(self):
        """
        Watchdog does not support checking for file content, so workaround is 
        to incorporate information about content (hash) into 'mtime' field.
        """
        if self.mtimeField == None:
            hashValue = self.calculateHash()
            ## st_mtime allows to detect case, when file was modified with the same content
            self.mtimeField = str(self.osResult.st_mtime) + "_" + str(self.osResult.st_size) + "_" + hashValue
            ##_LOGGER.debug("calculated field %r", self.mtimeField)
        return self.mtimeField
    

    def calculateHash(self): 
        hasher = hashlib.md5()
        with open(self.filePath, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()
    

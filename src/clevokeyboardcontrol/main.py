#!/usr/bin/python3
#
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


import sys
import os
# import signal
# from time import sleep

#### append local library
script_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath( os.path.join(script_dir, "..") ))

import time
import argparse
import logging
import cProfile

import clevokeyboardcontrol.logger as logger

from clevokeyboardcontrol.clevoio import TuxedoDriver

from clevokeyboardcontrol.gui.main_window import MainWindow
from clevokeyboardcontrol.gui.qt import QApplication
from clevokeyboardcontrol.gui.sigint import setup_interrupt_handling 



logger.configure()
_LOGGER = logging.getLogger(__name__)



def runApp(args):
    
    ## GUI
    app = QApplication(sys.argv)
    
    driver = TuxedoDriver()
                  
    window = MainWindow( driver )
    
    window.loadSettings()     
         
    window.show()
     
    setup_interrupt_handling()
     
    exitCode = app.exec_()

    if exitCode == 0:
        window.saveSettings()
    
    return exitCode


def main():
    parser = argparse.ArgumentParser(description='Clevo Keyboard Application')
    parser.add_argument('--profile', action='store_const', const=True, default=False, help='Profile the code' )
    parser.add_argument('--pfile', action='store', default=None, help='Profile the code and output data to file' )
     
          
    args = parser.parse_args()

    
    _LOGGER.debug("\n\n")
    _LOGGER.debug("Starting the application")
    
    _LOGGER.debug("Logger log file: %s" % logger.log_file)
    
    
    
    starttime = time.time()
    profiler = None
    
    exitCode = 0
    
    
    try:
     
        profiler_outfile = args.pfile
        if args.profile == True or profiler_outfile != None:
            print( "Starting profiler" )
            profiler = cProfile.Profile()
            profiler.enable()
    
    
        exitCode = runApp(args)
        
    
    except:
        exitCode = 1
        _LOGGER.exception("Exception occured")
        raise
    
    finally:
        _LOGGER.info( "" )                    ## print new line
        if profiler != None:
            profiler.disable()
            if profiler_outfile == None:
                _LOGGER.info( "Generating profiler data" )
                profiler.print_stats(1)
            else:
                _LOGGER.info( "Storing profiler data to", profiler_outfile )
                profiler.dump_stats( profiler_outfile )
                _LOGGER.info( "pyprof2calltree -k -i", profiler_outfile )
             
        timeDiff = (time.time()-starttime)*1000.0
        _LOGGER.info( "Execution time: {:13.8f}ms".format(timeDiff) )
        
        sys.exit(exitCode)


if __name__ == '__main__':
    main()

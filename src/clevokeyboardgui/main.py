#!/usr/bin/python3
#
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

import clevokeyboardgui.logger as logger

from clevokeyboardgui.clevoio import ClevoDriver

from clevokeyboardgui.gui.main_window import MainWindow
from clevokeyboardgui.gui.qt import QApplication
from clevokeyboardgui.gui.sigint import setup_interrupt_handling 



logger.configure()
_LOGGER = logging.getLogger(__name__)



def runApp(args):
    
    driver = ClevoDriver()
    
    ## GUI
    app = QApplication(sys.argv)
                  
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
        _LOGGER.info( "Calculation time: {:13.8f}ms".format(timeDiff) )
        
        sys.exit(exitCode)


if __name__ == '__main__':
    main()

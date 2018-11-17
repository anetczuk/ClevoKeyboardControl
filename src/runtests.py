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

script_dir = os.path.dirname(os.path.abspath(__file__))

## do not have to add 'src' dir to path until script is in separate directory
# src_dir = os.path.abspath(os.path.join(script_dir, "../src"))
# sys.path.insert(0, src_dir)

import unittest
import argparse
import cProfile
import subprocess

import tempfile


## ============================= main section ===================================


if __name__ == '__main__':    
    parser = argparse.ArgumentParser(description='Test runner')
    parser.add_argument('-rt', '--runtest', action='store', required=False, default="", help='Module with tests, e.g. test.test_class' )
    parser.add_argument('-r', '--repeat', action='store', type=int, default=0, help='Repeat tests given number of times' )
    parser.add_argument('-ut', '--untilfailure', action="store_true", help='Run tests in loop until failure' )
    parser.add_argument('-cov', '--coverage', action="store_true", help='Measure code coverage' )
    parser.add_argument('--profile', action="store_true", help='Profile the code' )
    parser.add_argument('--pfile', action='store', default=None, help='Profile the code and output data to file' )
    
    args = parser.parse_args()
    
    
    coverageData = None
    ## start code coverage
    if args.coverage == True:
        try:
            import coverage
        except ImportError:
            print( "Missing coverage module. Try running 'pip install coverage'" )
            print( "Python info:", sys.version )
            raise

        print( "Executing code coverage" )
        currScript = os.path.realpath(__file__)
        coverageData = coverage.Coverage(branch=True, omit=currScript)
        ##coverageData.load()
        coverageData.start()
        
        
    if len(args.runtest) > 0:
        suite = unittest.TestLoader().loadTestsFromName( args.runtest )
    else:
        suite = unittest.TestLoader().discover( script_dir )
        

    testsRepeats = int(args.repeat)

    profiler = None

    try:
        ## start code profiler
        profiler_outfile = args.pfile
        if args.profile == True or profiler_outfile != None:
            print( "Starting profiler" )
            profiler = cProfile.Profile()
            profiler.enable()
            
        ## run proper tests
        if args.untilfailure == True:
            counter = 1
            while True:
                print( "Tests iteration:", counter )
                counter += 1
                testResult = unittest.TextTestRunner().run(suite)
                if testResult.wasSuccessful() == False:
                    break;
                print( "\n" )
        elif testsRepeats > 0:
            for counter in range(1, testsRepeats+1):
                print( "Tests iteration:", counter )
                testResult = unittest.TextTestRunner().run(suite)
                if testResult.wasSuccessful() == False:
                    break;
                print( "\n" )
        else:
            unittest.TextTestRunner().run(suite)
    
    finally:
        ## stop profiler            
        if profiler != None:
            profiler.disable()
            if profiler_outfile == None:
                print( "Generating profiler data" )
                profiler.print_stats(1)
            else:
                print( "Storing profiler data to", profiler_outfile )
                profiler.dump_stats( profiler_outfile )

            if profiler_outfile != None:
                ##pyprof2calltree -i $PROF_FILE -k
                print( "Launching: pyprof2calltree -i {} -k".format(profiler_outfile) )
                subprocess.call(["pyprof2calltree", "-i", profiler_outfile, "-k"])
        
        ## prepare coverage results
        if coverageData != None:
            ## convert results to html
            tmprootdir=tempfile.gettempdir()
            revCrcTmpDir=tmprootdir+"/revcrc"
            if not os.path.exists(revCrcTmpDir):
                os.makedirs(revCrcTmpDir)
            htmlcovdir=revCrcTmpDir+"/htmlcov"
            
            coverageData.stop()
            coverageData.save()
            coverageData.html_report(directory=htmlcovdir)
            print( "\nCoverage HTML output:", (htmlcovdir+"/index.html") )

        
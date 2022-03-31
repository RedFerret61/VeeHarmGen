#!/usr/bin/env python
# -*- coding: utf-8 -*-
# run_tests.py which runs the VeeHarmGen tests with parameters in the line_parameters variable and searches the output for errors
# free and open-source software, Paul Wardley Davies, see license.txt

# usage: run_tests.py [-h]
#   This runs the VeeHarmGen program appending the line_parameters variables and searches the output for errors.


# usage examples:
# 1. run top level
# cd <installation directory>
# python run_tests.py


# standard libraries
import argparse
import glob
import os
import platform
import subprocess
from time import strftime
import time
# from datetime import datetime


line_parameters = ['-m input/music/God_Save_The_Queen.xml',
                    '-m input/music/JingleBells-2_2.mxl -i Harmonica',
                    '-m input/music/JingleBells-2_4.mxl -o 0.5 1.0 1.5 2.0 3.0',
                    '-m input/music/SorcererApprentice-3_8.mxl -t -12',
                    '-m input/music/music.mxl '
                   ]

def main():

    # get platform
    os_name = os.name
    platform_system = platform.system()
    platform_release = platform.release()
    # print('os_name', os_name,'platform_system',platform_system,'platform_release',platform_release)
    # e.g. nt Windows 10
    # e.g. Linux platform_release 5.4.0-26-generic
    
    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    # print("Current working directory: {0}".format(cwd))

    parser = argparse.ArgumentParser()

    # Specify command line arguments.

    # Parse command line arguments.
    args = parser.parse_args()


    program_arguments = ' '


    program_fully_qualified = "python VeeHarmGen.py" + program_arguments
    if platform.system() == 'Linux':
        # print('Linux')
        program_fully_qualified = "python3 VeeHarmGen.py" + program_arguments
        
    # print('program_fully_qualified', program_fully_qualified)

    # os.curdir is a string representing the current directory (always '.')   -
    # os.pardir is a string representing the parent directory (always '..')   -
    # os.sep is the (or a most common) pathname separator ('/' or '\\')

    # rel_config_path = os.curdir + os.sep
    # # print('rel_config_path', rel_config_path)
    #
    # # os.chdir(os.curdir + os.sep + args_config)
    # os.chdir(rel_config_path)

    print('run_tests.py')
    print('This runs the VeeHarmGen program appending the line_parameters variables and searches the output for errors.')
    print('\nline_parameters:', line_parameters, '\n')
    # input('Press Enter to continue...')
    print('wait for 10 seconds... ^C to exit.')
    time.sleep(10)

    # Change to original current working directory
    os.chdir(cwd)
    # print("Current working directory: {0}".format(cwd))

    redirection_base_str = ' > '
    redirection_end_str = ' 2>&1'

    for line_parameter in line_parameters:

        dt_string = strftime("%Y%m%d-%H_%M_%S")
        # print("date and time =", dt_string)
        log_path_file = 'output' + os.sep + 'run_tests-' + dt_string + '.log'
        redirection_str = redirection_base_str + log_path_file + redirection_end_str
        # print('redirection_str', redirection_str)

        call_str = program_fully_qualified + line_parameter + redirection_str
        # print('Next Command line to run: ', call_str)
        # input('Press Enter to continue...')
        # run
        print(dt_string,'Running: ', call_str,'...')
        subprocess.call(call_str, shell=True)

        # look for failures in log
        logfile_list = open(log_path_file)
        search_words = ['Traceback', 'VeeHarmGen.py', 'Error', 'Warning']
        print('Search log for', search_words, '...blank if nothing found...')
        for line in logfile_list:
            if any(word in line for word in search_words):
                print(line)

    print('\nrun_tests.py line_parameters:', line_parameters, '\n')


if __name__ == '__main__':

    main()

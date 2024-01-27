#!/bin/bash

echo USAGE: ./run_demo.sh mxlfile
echo        where mxlfile.mxl is in input/music e.g. ./run_demo.sh music
echo        Output is in output
echo Produces demonstration chord type files for each harmonic rhythm.

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else   
 python3 VeeHarmGen.py -m input/music/$1.mxl -d DEMO
fi

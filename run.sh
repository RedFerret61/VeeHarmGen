#!/bin/bash

echo USAGE: ./run.sh mxlfile
echo        where mxfile.mxl is in input/music e.g. ./run.sh music
echo        Output is in output
echo Produces harmonic rhythm placeholders and styles for the one measure harmonic rhythm.

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else  
  python3 VeeHarmGen.py -m input/music/$1.mxl
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl
fi

#!/bin/bash

echo USAGE: run_no_pc mxlfile
echo        where mxlfile.mxl is in input/music and has no placeholder chords e.g. run music
echo        Output is in output
echo Produces harmonic rhythm placeholders

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else 
  python3 VeeHarmGen.py -m input/music/$1.mxl
fi

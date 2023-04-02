#!/bin/bash

echo USAGE: ./run_BAR2_folk.sh mxlfile
echo        where mxfile.mxl is in input/music e.g. ./run_BAR2_folk.sh music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR2" as input for a "folk" style subset 

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else
  python3 VeeHarmGen.py -m input/music/$1.mxl
  python3 VeeHarmGen.py -m output/$1-BAR2.mxl -s folk -i Harp
fi

#!/bin/bash

echo USAGE: ./run_BAR1_rock.sh mxlfile
echo        where mxlfile.mxl is in input/music e.g. ./run_BAR1_rock.sh music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR1" as input for a "rock" style subset 

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else
  python3 VeeHarmGen.py -m input/music/$1.mxl
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s rock -i Kalimba
fi

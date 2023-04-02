#!/bin/bash

echo USAGE: ./run_BEAT2_jazz.sh mxlfile
echo        where mxfile.mxl is in input/music e.g. ./run_BEAT2_jazz.sh music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BEAT2" as input for a "jazz" style subset 

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else
  python3 VeeHarmGen.py -m input/music/$1.mxl
  python3 VeeHarmGen.py -m output/$1-BEAT2.mxl -s jazz -i Trombone
fi

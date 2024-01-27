#!/bin/bash

echo USAGE: ./run_placeholder.sh mxlfile
echo        where mxlfile.mxl is in input/music/placeholder_chords e.g. ./run_placeholder.sh music
echo        Output is in output
echo Uses the input file placeholder chords to output files for "all" styles.

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else 
  python3 VeeHarmGen.py -m input/music/placeholder_chords/$1.mxl -s all -i Soprano
fi

#!/bin/bash

echo USAGE: ./run_rank.sh mxlfile
echo        where mxlfile.mxl is in input/music e.g. ./run_rank.sh music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR1" as input for the "all" style superset for a range of chord popularity ranks -r

if [ $# -eq 0 ];
then
  echo "$0: Missing argument"
  exit 1
else 
  python3 VeeHarmGen.py -m input/music/$1.mxl
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 90 -i Clarinet
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 80 -i Flute
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 70 -i Guitar
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 60 -i Harmonica
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 50 -i Oboe
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 40 -i Saxophone
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 30 -i Trumpet
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 20 -i Violin
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 10 -i Violoncello
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s all-_-ptc -c rank -n 1  -i Voice
fi

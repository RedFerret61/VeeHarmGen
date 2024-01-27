#!/bin/bash

echo USAGE: ./run_nth_outcome.sh mxlfile style
echo        where mxlfile.mxl is in input/music e.g. ./run_nth_outcome.sh music all-
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR1" as input for the style superset for a range of chord outcomes

if [ $# -lt 2 ]; 
then
  echo "$0: Missing argument. See USAGE"
  exit 1
else 
  python3 VeeHarmGen.py -m input/music/$1.mxl
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 0 -i Clarinet
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 1 -i Flute
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 2 -i Guitar
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 3 -i Harmonica
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 4 -i Oboe
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 5 -i Saxophone
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 6 -i Trumpet
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 7 -i Violin
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 8 -i Violoncello
  python3 VeeHarmGen.py -m output/$1-BAR1.mxl -s $2 -c nth_outcome -n 9 -i Voice
fi

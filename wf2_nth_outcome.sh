#!/bin/bash

echo USAGE: wf2_nth_outcome mxlfile style
echo        where mxlfile has placeholder chords and includes path e.g. 
echo		      style is a style filter string on files in input/style directory
echo        Output for the first 10 chord outcomes is in written to the output directory
echo		e.g. wf2_nth_outcome input/music/placeholder_chords/Cairo-PC.mxl all-

if [ $# -lt 2 ]; 
then
  echo "$0: Missing argument. See USAGE"
  exit 1
else 
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 0 -i Clarinet
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 1 -i Flute
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 2 -i Guitar
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 3 -i Harmonica
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 4 -i Oboe
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 5 -i Saxophone
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 6 -i Trumpet
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 7 -i Violin
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 8 -i Violoncello
  python3 VeeHarmGen.py -m $1 -s $2 -c nth_outcome -n 9 -i Voice
fi

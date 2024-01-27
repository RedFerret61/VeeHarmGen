#!/bin/bash

echo run_out 
echo        USAGE: run_out n style instrument mxlfile 
echo        where n is the last outcome. Outcomes start at 0.
echo              style is a style filter string on files in input/style directory
echo              instrument is used by the output melody, chords are on Piano, for instruments, see python VeeHarmGen.py -h 
echo              mxlfile has placeholder chords and includes path  
echo        Output for chord outcomes is in written to the output directory
echo        Examples:
echo		run_out 1 _pop_ Harmonica input/music/placeholder_chords/Cairo-PC.mxl
echo		run_out 2 pop_country_1 Violin input/music/placeholder_chords/Cairo-PC.mxl
echo		run_out 3 all_contemporary Piano input/music/placeholder_chords/Cairo-PC.mxl

if [ $# -lt 4 ];
then
  echo "$0: Missing argument.  See USAGE"
  exit 1
else
  integer_value=$1
  for i in $(seq 0 1 $integer_value); do
    python3 VeeHarmGen.py -m $4 -s $2 -c nth_outcome -n $i -i $3
done
fi


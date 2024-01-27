@echo off
echo USAGE: wf2_nth_outcome mxlfile style
echo        where mxlfile has placeholder chords and includes path e.g. 
echo		      style is a style filter string on files in input/style directory
echo        Output for the first 10 chord outcomes is in written to the output directory
echo		e.g. wf2_nth_outcome input/music/placeholder_chords/Cairo-PC.mxl all-
if "%~2"=="" goto :eof

python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 0 -i Clarinet
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 1 -i Flute
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 2 -i Guitar
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 3 -i Harmonica
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 4 -i Oboe
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 5 -i Saxophone
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 6 -i Trumpet
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 7 -i Violin
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 8 -i Violoncello
python VeeHarmGen.py -m %1 -s %2 -c nth_outcome -n 9  -i Voice

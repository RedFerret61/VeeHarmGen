@echo off
echo USAGE: run_nth_outcome mxlfile style
echo        where mxlfile.mxl is in input/music e.g. run_nth_outcome music all-
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR1" as input for the style superset for a range of chord outcomes 
if "%~2"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 0 -i Clarinet
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 1 -i Flute
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 2 -i Guitar
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 3 -i Harmonica
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 4 -i Oboe
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 5 -i Saxophone
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 6 -i Trumpet
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 7 -i Violin
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 8 -i Violoncello
python VeeHarmGen.py -m output/%1-BAR1.mxl -s %2 -c nth_outcome -n 9  -i Voice

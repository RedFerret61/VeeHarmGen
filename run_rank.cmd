@echo off
echo USAGE: run_rank mxlfile
echo        where mxfile.mxl is in input/music e.g. run_rank music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR1" as input for the "all" style superset for a range of chord popularity ranks (-r)
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 90 -i Clarinet
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 80 -i Flute
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 70 -i Guitar
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 60 -i Harmonica
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 50 -i Oboe
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 40 -i Saxophone
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 30 -i Trumpet
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 20 -i Violin
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 10 -i Violoncello
python VeeHarmGen.py -m output/%1-BAR1.mxl -s all-_-ptc -r 1  -i Voice

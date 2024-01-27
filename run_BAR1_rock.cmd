@echo off
echo USAGE: run_BAR1_rock mxlfile
echo        where mxlfile.mxl is in input/music e.g. run_BAR1_rock music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR1" as input for a "rock" style subset 
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl
python VeeHarmGen.py -m output/%1-BAR1.mxl -s rock -i Kalimba

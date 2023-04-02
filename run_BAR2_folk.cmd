@echo off
echo USAGE: run_BAR2_folk mxlfile
echo        where mxfile.mxl is in input/music e.g. run_BAR2_folk music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BAR2" as input for a "folk" style subset 
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl
python VeeHarmGen.py -m output/%1-BAR2.mxl -s folk -i Harp

@echo off
echo USAGE: run_BEAT2_jazz mxlfile
echo        where mxfile.mxl is in input/music e.g. run_BEAT2_jazz music
echo        Output is in output
echo Produces harmonic rhythm placeholders and then  
echo uses "BEAT2" as input for a "jazz" style subset 
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl
python VeeHarmGen.py -m output/%1-BEAT2.mxl -s jazz -i Trombone

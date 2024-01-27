@echo off
echo USAGE: run mxlfile
echo        where mxlfile.mxl is in input/music e.g. run music
echo        Output is in output
echo Produces harmonic rhythm placeholders and styles for the one measure harmonic rhythm.
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl
python VeeHarmGen.py -m output/%1-BAR1.mxl

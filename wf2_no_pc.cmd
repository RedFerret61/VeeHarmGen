@echo off
echo USAGE: run_no_pc mxlfile
echo        where mxlfile.mxl is in input/music and has no placeholder chords e.g. run music
echo        Output is in output
echo Produces harmonic rhythm placeholders
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl

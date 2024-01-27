@echo off
echo USAGE: run_demo mxlfile
echo        where mxlfile.mxl is in input/music e.g. run_demo music
echo        Output is in output
echo Produces demonstration chord type files for each harmonic rhythm.
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/%1.mxl -d DEMO
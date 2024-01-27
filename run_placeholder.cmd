@echo off
echo USAGE: run_placeholder mxlfile
echo        where mxlfile.mxl is in input/music/placeholder_chords e.g. run_placeholder music
echo        Output is in output
echo Uses the input file placeholder chords to output files for "all" styles.
if "%~1"=="" goto :eof

python VeeHarmGen.py -m input/music/placeholder_chords/%1.mxl -s all -i Soprano


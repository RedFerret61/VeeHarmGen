@echo off
echo run_out 
echo        USAGE: run_out n style instrument mxlfile 
echo        where n is the last outcome (outcomes start at 0)
echo              style is a style filter string on files in input/style directory
echo              instrument is used by the output melody (chords are Piano), for instruments, see python VeeHarmGen.py -h 
echo              mxlfile has placeholder chords and includes path  
echo        Output for chord outcomes is in written to the output directory
echo        Examples:
echo		run_out 1 _pop_ Harmonica input/music/placeholder_chords/Cairo-PC.mxl
echo		run_out 2 pop_country_1 Violin input/music/placeholder_chords/Cairo-PC.mxl
echo		run_out 3 all_contemporary Piano input/music/placeholder_chords/Cairo-PC.mxl

if "%~4"=="" goto :eof

for /L %%v in (0,1,%1) do (
python VeeHarmGen.py -m %4 -s %2 -c nth_outcome -n %%v -i %3
)

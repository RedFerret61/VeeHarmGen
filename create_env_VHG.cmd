@echo off
set CurrDir=%CD%
echo The current working directory is %CurrDir%
echo The current working directory should be the VeeHarmGen install directory
echo Ctrl-C if not
pause 

setx VHG "%CurrDir%"
echo In a new command window, to change to the VeeHarmGen install directory type: 
echo cd %%VHG%%
echo ... that is ...
echo cd [percent]VHG[percent]
echo 	where percent is %%


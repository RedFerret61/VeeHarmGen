@echo off
echo USAGE: run_tests

::run
call run music
call run Cairo
call run Love_Stand_Strong
call run Perambulate

::run_BAR1_rock
call run_BAR1_rock music
call run_BAR1_rock Cairo
call run_BAR1_rock Love_Stand_Strong
call run_BAR1_rock Perambulate

::run_BAR2_folk.cmd
call run_BAR2_folk music
call run_BAR2_folk Cairo
call run_BAR2_folk Love_Stand_Strong
call run_BAR2_folk Perambulate

::run_BEAT2_jazz.cmd
call run_BEAT2_jazz music
call run_BEAT2_jazz Cairo
call run_BEAT2_jazz Love_Stand_Strong
call run_BEAT2_jazz Perambulate

::run_demo.cmd
call run_demo music
call run_demo Cairo
call run_demo Love_Stand_Strong
call run_demo Perambulate

:: run_nth_outcome.cmd
call run_nth_outcome music
call run_nth_outcome Cairo
call run_nth_outcome Love_Stand_Strong
call run_nth_outcome Perambulate

::run_placeholder.cmd
call run_placeholder music
call run_placeholder Cairo
call run_placeholder Love_Stand_Strong
call run_placeholder Perambulate

::run_rank.cmd
call run_rank music
call run_rank Cairo
call run_rank Love_Stand_Strong
call run_rank Perambulate

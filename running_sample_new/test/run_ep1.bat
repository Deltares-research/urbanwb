@ECHO OFF
ECHO Getting started...
ECHO Example for Function "save-to-csv": Single run and csv all (selected results)

:: Water balance for entire model at small q, short time series need checks

ECHO Save all results of single run to a file
::        module name               function    forcing.csv config1.ini        config2.ini    output.csv
python -m urbanwb.main save_to_csv ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep1_results.csv


ECHO Save selected results of single run to a file
::        module name               function    forcing.csv config1.ini        config2.ini    output.csv               variable to save       save_all is False meaning save selected 
python -m urbanwb.main save_to_csv ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep1_results_selected.csv owl r_pr_swds theta_uz --save_all=False 

ECHO Ended!
pause

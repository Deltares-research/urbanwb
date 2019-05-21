@ECHO OFF
ECHO Getting started...
ECHO Example for Function "batch_run_measure"

::          module                    function          ts.csv    config1.ini          config2.ini    output.csv      var to change               value to update var   corresp var        value for corresp var  baseline runoff               measure runoff to save
python -m urbanwb.main batch_run_measure ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep3_results.csv --varkey="storcap_btm_meas" --vararrlist1=[1050,1200] --correspvarkey=None --vararrlist2=None --baseline_variable="r_cp_swds" --variable_to_save="q_meas_swds"


python -m urbanwb.main batch_run_measure ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep3_results.csv --varkey="storcap_btm_meas" --vararrlist1=[1050,1200] --correspvarkey="runoffcap_btm_meas" --vararrlist2=[30,40] --baseline_variable="r_cp_swds" --variable_to_save="q_meas_swds"


python -m urbanwb.getconstants ep3_results.csv --num_year=30
ECHO Ended!
pause

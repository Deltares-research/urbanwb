@ECHO OFF
ECHO Getting started...
ECHO Example for Function "batch_run_sdf": First run baseline (q = default mean daily rainfall or predefined value)
ECHO then batch run different q (random number [a,b,c,d,...] or [min,max,steps])

::        module name                  function      ts.csv    config1.ini          config2.ini    output.csv      random number     baseline q default
python -m urbanwb.main batch_run_sdf ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep2_results.csv --q_list=[4,5]

::        module name                  function      ts.csv    config1.ini          config2.ini    output.csv      random number     baseline q predefined
python -m urbanwb.main batch_run_sdf ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep2_results1.csv --q_list=[10,20] --baseline_q=4

::        module name                  function      ts.csv    config1.ini          config2.ini    output.csv      [min,max,steps]   baseline q:predefined AP:True to enable [min,max,steps]. if False, then q_list random numbers
python -m urbanwb.main batch_run_sdf ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep2_results2.csv --q_list=[4,8,3] --baseline_q=3 --arithmetic_progression=True

ECHO Ended!
pause

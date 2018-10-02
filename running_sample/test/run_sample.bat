@ECHO OFF


:: this is the function you need to do single runs. you can run the model either through cmd or through run.bat, latter recommended
:: run function: savecsv
:: sequence of input: -1.DYN.INP -2. STAT1.INP -3.STAT2.INP -4 DYN.OUT
python -m urbanwb.main savecsv timeseries.csv sample_stat1.ini sample_stat2.ini sample_result.csv


:: this is the function to produce sdf-curve which you don't need, but I have include it for you.
:: run function: batch-run-sdf
:: sequence of input: -1.DYN.INP -2. STAT1.INP -3.STAT2.INP -4 DYN.OUT  -5.vararr 
:: python -m urbanwb.main batch-run-sdf timeseries.csv sample_stat1.ini sample_stat2.ini sample_outcome.csv 0.05787037 0.115740741 0.173611111

pause

ECHO ON
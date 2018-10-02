@ECHO OFF

:: run function: savecsv
:: sequence of input: 1. DYN.INP 2. STAT1.INP 3. STAT2.INP 4. DYN.OUT
python -m urbanwb.main_with_measure savecsv timeseries_measure.csv sample_measure_stat1.ini sample_measure_stat2.ini sample_measure_result.csv
	
ECHO ON
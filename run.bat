:: run function: savecsv
:: sequence of input: 1. DYN.INP 2. STAT1.INP 3. STAT2.INP 4. DYN.OUT
python -m urbanwb.main savecsv input_csv.csv static_form.ini static_form_measure.ini results123.csv
	

: run function: batch-run
: sequence of input: -1.DYN.INP -2. STAT1.INP -3.STAT2.INP -4 DYN.OUT -5. Num of years -6.varkey -7.vararr 
python -m urbanwb.main batch-run input_csv.csv static_form.ini static_form_measure.ini results12345.csv 5 pump_cap 1

pause
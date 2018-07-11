python -m urbanwb.main savecsv input_csv.csv static_form.ini static_form_measure.ini results123.csv
* run function: savecsv
* sequence of input: 1. DYN.INP 2. STAT1.INP 3. STAT2.INP 4. OUTPUT.CSV	


python -m urbanwb.main batch-run input_csv.csv static_form.ini static_form_measure.ini pump_cap [2,3,4] 5 1.5 results1234.csv
* run function: batch-run
* sequence of input: -1.DYN.INP -2. STAT1.INP -3.STAT2.INP -4.varkey -5.vararr -6.Num of years -7.target_owl level -8 OUTPUT.csv
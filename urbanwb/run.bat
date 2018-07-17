@ECHO OFF

:: run function: savecsv
:: sequence of input: 1. DYN.INP 2. STAT1.INP 3. STAT2.INP 4. DYN.OUT
python -m urbanwb.main savecsv input_csv.csv static_form.ini static_form_measure.ini results123.csv
	

:: run function: batch-run-sdf
:: sequence of input: -1.DYN.INP -2. STAT1.INP -3.STAT2.INP -4. DYN.OUT -5. vararr 
python -m urbanwb.main batch-run-sdf input_csv.csv static_form.ini static_form_measure.ini results12345.csv 1 1.2 1.3


:: run function: save-run
:: sequence of input: -1.DYN.INP -2. STAT1.INP -3.STAT2.INP -4 DYN.OUT [optional] selected output variable + saveall=False
python -m urbanwb.main saverun input_csv.csv static_form.ini static_form_measure.ini resultstest.csv int_pr int_cp --saveall=False


:: run function: batch-run
:: sequence of input: -1.DYN.INP -2. STAT1.INP -3.STAT2.INP -4 DYN.OUT -5. varkey -6. vararr
python -m urbanwb.main batch-run input_csv.csv static_form.ini static_form_measure.ini test.csv infilcap_up 10 20 30 40
pause

ECHO ON
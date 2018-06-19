import numpy as np
import pandas as pd
import ast

# read output csv file.
data = pd.read_csv('pysol/test.csv')
iters = np.shape(data)[0]

OWL = []
for i in range(iters):
    OWL.append(ast.literal_eval(data['openwater'][i])['owl'])


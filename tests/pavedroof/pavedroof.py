import numpy as np
import pandas as pd
from pathlib import Path


indir = Path('input')
outdir = Path('pysol')
outdir.mkdir(parents=True, exist_ok=True)
InputData = pd.read_csv(indir / 'input_csv.csv')  # input the precipitation, potential evaporation

date = InputData['date']
P_atm = InputData['P_atm']
Ref_grass = InputData['Ref.grass']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]

# 1. GENERAL TEST

# 1.1 General test settings
# tot_area --- total area of study domain
# pr_frac --- paved roof percentage
# tot_pr_area --- total paved roof area
# pr_meas_area --- area of paved roof (with a measure)
# pr_no_meas_area --- area of paved roof (without a measure)
# measure_inflow_area --- runoff inflow area to measure, inflow area >= measure area, predefined as 0.
tot_area = 10000
pr_frac = 0.156
tot_pr_area = tot_area * pr_frac
pr_meas_area = 0
pr_no_meas_area = tot_pr_area - pr_meas_area
pr_meas_inflow_area = 0


# 1.2 PavedRoof class.
class PavedRoof:
    """
    creates an instance of PavedRoof class with given states and properties, iterates sol function at each time step.
    """
    def __init__(self, init_intstor_pr_t0, pr_no_meas_area, pr_meas_area, pr_meas_inflow_area, intstorcap_pr=1.6,
                 stormfrac_pr=1.0, discfrac_pr=0.0):

        # state
        # init_intstor_pr --- initial interception storage on paved roof area [mm].
        self.init_intstor_pr = init_intstor_pr_t0

        # properties
        # pr_no_meas_area --- paved roof area (without a measure) [m^2].
        # pr_meas_area --- paved roof area (with a measure) [m^2].
        # pr_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # intstorcap_pr --- predefined storage capacity on paved roof area [mm].
        # stormfrac_pr --- part of urban area with storm water drainage system [-].
        # self.mxdfrac--- part of urban area with mixed sewer system [-].
        # discfrac_pr --- part of paved roof area that is disconnected [-].

        self.pr_no_meas_area = pr_no_meas_area
        self.pr_meas_area = pr_meas_area
        self.pr_meas_inflow_area = pr_meas_inflow_area
        self.intstorcap = intstorcap_pr
        self.stormfrac = stormfrac_pr
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_pr

    def inflowfac(self):
        return (self.pr_meas_inflow_area - self.pr_meas_area) / self.pr_no_meas_area

    def sol(self, p_atm, e_pot_ow):

        # parameters
        # int_pr --- Interception on paved roof after rainfall during current time step [mm].
        # e_atm_pr --- Evaporation from interception storage on paved roof during current time step [mm].
        # intstor_pr --- Remaining interception storage on paved roof at the end of the current time step [mm].
        # r_pr_meas --- Runoff from paved roof to an area with a drainage measure
        # (not necessarily on the roof itself) [mm].
        # r_pr_swds --- Runoff from paved roof to the storm water drainage system [mm].
        # r_pr_mss --- Runoff from paved roof to the mixed sewer system [mm].
        # r_pr_up --- Runoff from paved roof to unpaved area [mm].

        if self.pr_no_meas_area == 0:
            int_pr = e_atm_pr = intstor_pr = r_pr_meas = r_pr_swds = r_pr_mss = r_pr_up = 0

        else:
            int_pr = min(self.intstorcap, max(0, self.init_intstor_pr + p_atm))

            e_atm_pr = min(e_pot_ow, int_pr)

            intstor_pr = int_pr - e_atm_pr

            r_pr_meas = self.inflowfac() * max(0, p_atm - e_atm_pr - (intstor_pr - self.init_intstor_pr))

            r_pr_swds = self.stormfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_pr - (
                        intstor_pr - self.init_intstor_pr) - r_pr_meas)

            r_pr_mss = self.mxdfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_pr - (
                        intstor_pr - self.init_intstor_pr) - r_pr_meas)

            r_pr_up = self.discfrac * max(0, p_atm - e_atm_pr - (intstor_pr - self.init_intstor_pr) - r_pr_meas)

            # update state
            self.init_intstor_pr = intstor_pr

        return int_pr, e_atm_pr, intstor_pr, r_pr_meas, r_pr_swds, r_pr_mss, r_pr_up


# 1.3 Get python solutions and save in csv file.
Int_pr = [0]
E_atm_pr = [0]
init_intstor_pr_t0 = 0  # Set initial interception storage as 0.
Intstor_pr = [init_intstor_pr_t0]
R_pr_meas = [0]
R_pr_swds = [0]
R_pr_mss = [0]
R_pr_up = [0]

m = PavedRoof(init_intstor_pr_t0, pr_no_meas_area, pr_meas_area, pr_meas_inflow_area, intstorcap_pr=1.6,
              stormfrac_pr=1.0, discfrac_pr=0.0)

t = 1

while t <= iters - 1:

    sol = m.sol(P_atm[t], E_pot_OW[t])

    Int_pr.append(sol[0])
    E_atm_pr.append(sol[1])
    Intstor_pr.append(sol[2])
    R_pr_meas.append(sol[3])
    R_pr_swds.append(sol[4])
    R_pr_mss.append(sol[5])
    R_pr_up.append(sol[6])
    #if t % 200 == 0:
        #print(f'timestep {t} / {iters}')
    t += 1

filename = 'PR_general_test_pysol.csv'
np.savetxt('pysol/' + filename, np.c_[Int_pr, E_atm_pr, Intstor_pr, R_pr_meas, R_pr_swds, R_pr_mss, R_pr_up],
           fmt="%.8f", delimiter=',',
           header='Int_pr, E_atm_pr, Intstor_pr, R_pr_meas, R_pr_swds, R_pr_mss, R_pr_up')
# Insert the Date column for locating purposes.
df = pd.read_csv('pysol/' + filename)
df.insert(0, 'Date', date)
df.to_csv('pysol/' + filename)

# 1.4 Validate with excel solutions.
data_py = pd.read_csv('pysol/' + filename)
data_ex = pd.read_csv('exsol/PR_general_test_exsol.csv')

# Examine through the dataframe column by column
A = np.zeros((43825, 7))
for c in range(7):
    for r in range(1, 43825):  # from row 1 to the last row (row 43824), excluding first row(t=0).
        A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
for c in range(7):
    print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))


# 2. EXTENDED TESTS
# 2.0 Validate function. Built for easily manipulating comparisons between python and excel solutions.
def validate(a, b, c, d, A1, A2, A3):
    """Validates python solution with excel solutions based on given parameter sets"""
    # a --- interception storage capacity on paved roof.
    # b --- part of paved roof area with storm water drainage system.
    # c --- part of paved roof area that is disconnected.
    # d --- Set No., used to name the output file.
    # A1 --- paved roof area (without a measure)
    # A2 --- paved roof area (with a measure)
    # A3 --- paved roof measure inflow area.
    Int_pr = [0]
    E_atm_pr = [0]
    init_intstor_pr_t0 = 0
    Intstor_pr = [init_intstor_pr_t0]
    R_pr_meas = [0]
    R_pr_swds = [0]
    R_pr_mss = [0]
    R_pr_up = [0]

    m = PavedRoof(init_intstor_pr_t0, pr_no_meas_area=A1, pr_meas_area=A2, pr_meas_inflow_area=A3,
                  intstorcap_pr=a, stormfrac_pr=b, discfrac_pr=c)
    t = 1

    while t <= iters - 1:

        sol = m.sol(P_atm[t], E_pot_OW[t])

        Int_pr.append(sol[0])
        E_atm_pr.append(sol[1])
        Intstor_pr.append(sol[2])
        R_pr_meas.append(sol[3])
        R_pr_swds.append(sol[4])
        R_pr_mss.append(sol[5])
        R_pr_up.append(sol[6])
        # print('time step', t)
        t += 1
    # save python results
    filename = 'PR_extended_test_pysol_set'+str(d)+'.csv'
    np.savetxt('pysol/' + filename, np.c_[Int_pr, E_atm_pr, Intstor_pr, R_pr_meas, R_pr_swds, R_pr_mss, R_pr_up],
               fmt = "%.8f", delimiter=',',
               header = 'Int_pr, E_atm_pr, Intstor_pr, R_pr_meas, R_pr_swds, R_pr_mss, R_pr_up')
    df = pd.read_csv('pysol/' + filename)
    df.insert(0, 'Date', date)
    df.to_csv('pysol/' + filename)
    # validate with excel
    data_py = pd.read_csv('pysol/' + filename)
    data_ex = pd.read_csv('exsol/PR_extended_test_exsol_set'+str(d)+'.csv')
    A = np.zeros((43825, 7))
    for c in range(7):
        for r in range(1,43825):
            A[r,c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
    for c in range(7):
        print('col ' + str(c), 'max', max(A[:,c]), 'min', min(A[:,c]))
        #print(np.where(max(A[:,c]) != 0 and A[:,c] == max(A[:,c])), # np.where(min(A[:,c]) != 0 and A[:,c] == min(A[:,c])))


# 2.1 Set 1: pr_no_meas_area = 0
i = 1
print(i)
validate(1.6, 1.0, 0.0, i, 0, 1560, 0)

# 2.2 Set 2: intstorcap_pr = 0
i = 2
print(i)
validate(0, 1, 0, i, 1560, 0, 0)

# 2.3 Set 3: intstorcap_pr = 1600
i = 3
print(i)
validate(1600, 1, 0, i, 1560, 0, 0)

# 2.4 Set 4: stormfrac = 0.0
i = 4
print(i)
validate(1.6, 0, 0, i, 1560, 0, 0)

# 2.5 Set 5: stormfrac = 0.37
i = 5
print(i)
validate(1.6, 0.37, 0, i, 1560, 0, 0)

# 2.6 Set 6: discfrac = 1.0
i = 6
print(i)
validate(1.6, 1, 1, i, 1560, 0, 0)

# 2.7 Set 7: discfrac = 0.37
i = 7
print(i)
validate(1.6, 1, 0.37, i, 1560, 0, 0)


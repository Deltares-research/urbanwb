import numpy as np
import pandas as pd
from pathlib import Path
import time

indir = Path('input')
outdir = Path('pysol')
outdir.mkdir(parents=True, exist_ok=True)
InputData = pd.read_csv(indir / 'input_csv.csv')  # input the precipitation, potential evaporation

date = InputData['date']
P_atm = InputData['P_atm']
Ref_grass = InputData['Ref.grass']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]

# 1.GENERAL TEST
# 1.1 Input data from other modules.
# a. results of r_pr_swds, r_cp_swds, r_op_swds, r_pr_mss, r_cp_mss, r_op_mss
# from paved roof, closed paved, open paved module.
r_pr_swds = pd.read_csv(indir / 'r_swds.csv')['r_pr_swds_0']
r_cp_swds = pd.read_csv(indir / 'r_swds.csv')['r_cp_swds_0']
r_op_swds = pd.read_csv(indir / 'r_swds.csv')['r_op_swds_0']
r_pr_mss = pd.read_csv(indir / 'r_mss.csv')['r_pr_mss_0']
r_cp_mss = pd.read_csv(indir / 'r_mss.csv')['r_cp_mss_0']
r_op_mss = pd.read_csv(indir / 'r_mss.csv')['r_op_mss_0']
# b. flow from measure to swds/mss
meas_swds = meas_mss = np.zeros(iters)


# 1.2 General test settings
tot_pr_area = 1560
tot_cp_area = 803.3906406
tot_op_area = 481.6093594
pr_discfrac = 0.0
cp_discfrac, op_discfrac = 0, 0
swds_frac = 1
mss_frac = 1 - swds_frac
tot_disc_area = tot_pr_area * pr_discfrac + tot_cp_area * cp_discfrac + tot_op_area * op_discfrac
tot_sdws_area = (tot_pr_area + tot_cp_area + tot_op_area - tot_disc_area) * swds_frac
# 1 is the storm drainage fraction 100%
tot_mss_area = (tot_pr_area + tot_cp_area + tot_op_area - tot_disc_area) * mss_frac
# 0 is the mss drainage fraction 0 %
pr_meas_area = 0
pr_no_meas_area = tot_pr_area - pr_meas_area
cp_meas_area = 0
cp_no_meas_area = tot_cp_area - cp_meas_area
op_meas_area = 0
op_no_meas_area = tot_op_area - op_meas_area
swds_meas_area = 0
swds_no_meas_area = tot_sdws_area - swds_meas_area
mss_meas_area = 0
mss_no_meas_area = tot_mss_area - mss_meas_area
ow_no_meas_area = 300
tot_meas_area = 0  # for the time being, it equals to swds_meas_area 0.


class SewerSystem:
    """
    creates an instance of sewer system class with given states and properties,
    iterates sol function at each time step.
    """

    def __init__(self, swds_no_meas_area, mss_no_meas_area, prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0,
                 prev_so_mss_t0, q_swds_ow_cap=55.1, q_mss_out_cap=26.3, q_mss_ow_cap=48.1, stor_swds_cap=2,
                 stor_mss_cap=9):
        # state
        # prev_stor_swds --- Storage in the storm water drainage system at the end of the previous time step [mm].
        # prev_so_swds --- Overflow of storm water drainage system during the previous time step [mm].
        # prev_stor_mss --- Storage in the mixed sewer system at the end of the previous time step [mm].
        # prev_so_mss --- Overflow of mixed sewer system during the previous time step [mm].

        self.prev_stor_swds = prev_stor_swds_t0
        self.prev_so_swds = prev_so_swds_t0
        self.prev_stor_mss = prev_stor_mss_t0
        self.prev_so_mss = prev_so_mss_t0

        # properties
        # swds_no_meas_area --- area of storm water drainage system (without a measure) [m^2].
        # mss_no_meas_area --- area of mixed sewer system (without a measure) [m^2].
        # q_swds_ow_cap --- predefined discharge capacity of storm water drainage system [mm/hr].
        # q_mss_out_cap --- predefined discharge capacity of mixed sewer system to WWTP [mm/hr].
        # q_mss_ow_cap --- predefined discharge capacity of mixed sewer system to open water [mm/hr].
        # stor_swds_cap --- predefined storage capacity of storm water drainage system [mm].
        # stor_mss_cap --- predefined storage capacity of mixed sewer system [mm].
        # Note the relationship between q_swds_ow_cap, stor_swds_cap, cp_intstor_cap, rainfall intensity.

        self.swds_no_meas_area = swds_no_meas_area
        self.mss_no_meas_area = mss_no_meas_area
        self.q_swds_ow_cap = q_swds_ow_cap
        self.q_mss_out_cap = q_mss_out_cap
        self.q_mss_ow_cap = q_mss_ow_cap
        self.stor_swds_cap = stor_swds_cap
        self.stor_mss_cap = stor_mss_cap

    def sol(self, pr_no_meas_area, cp_no_meas_area, op_no_meas_area, r_pr_swds, r_cp_swds,
            r_op_swds, r_pr_mss, r_cp_mss, r_op_mss, meas_swds, meas_mss, ow_no_meas_area, tot_meas_area):
        # parameters
        # sum_r_swds --- Total runoff to storm water drainage system during the current time step [mm].
        # r_meas_swds --- Inflow from measure area (if applicable) during current time step [mm]
        # sum_r_mss --- Total runoff to mixed sewer system during the current time step [mm].
        # r_meas_mss --- Inflow from measure area (if applicable) during current time step [mm].
        # q_swds_ow --- Outflow from storm water drainage system to open water [mm]
        # q_mss_out --- Discharge from mixed sewer system to Waste Water Treatment Plant (WWTP)
        # during the current time step [mm]
        # q_mss_ow --- Outflow from mixed sewer system to open water during the current time step [mm]
        # so_sdws --- Overflow of storm water drainage system during the current time step [mm]
        # so_mss --- Overflow of mixed sewer system during the current time step [mm]
        # stor_swds --- Storage in the storm water drainage system at the end of the current time step [mm]
        # stor_mss --- Storage in the mixed sewer system at the end of the current time step [mm]

        if self.swds_no_meas_area == 0:

            sum_r_swds = r_meas_swds = q_swds_ow = so_swds = stor_swds = 0

        else:

            sum_r_swds = (pr_no_meas_area * r_pr_swds + cp_no_meas_area * r_cp_swds + op_no_meas_area * r_op_swds) \
                         / self.swds_no_meas_area
            r_meas_swds = meas_swds * tot_meas_area / self.swds_no_meas_area

            if ow_no_meas_area == 0:
                q_swds_ow = min(self.prev_stor_swds + sum_r_swds + r_meas_swds + self.prev_so_swds, self.q_swds_ow_cap)

                so_swds = max(0,
                              self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - self.stor_swds_cap +
                              self.prev_so_swds)

                stor_swds = max(0, self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - (
                        so_swds - self.prev_so_swds))

            else:
                q_swds_ow = min(self.prev_stor_swds + sum_r_swds + r_meas_swds + 0, self.q_swds_ow_cap)

                so_swds = max(0, self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - self.stor_swds_cap + 0)

                stor_swds = max(0, self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - so_swds)

            # update state
            self.prev_stor_swds = stor_swds
            self.prev_so_swds = so_swds

        if self.mss_no_meas_area == 0:

            sum_r_mss = r_meas_mss = q_mss_out = q_mss_ow = so_mss = stor_mss = 0

        else:
            sum_r_mss = (pr_no_meas_area * r_pr_mss + cp_no_meas_area * r_cp_mss + op_no_meas_area * r_op_mss) \
                        / self.mss_no_meas_area
            r_meas_mss = meas_mss * tot_meas_area / self.mss_no_meas_area

            if ow_no_meas_area == 0:
                q_mss_out = min(self.prev_stor_mss + sum_r_mss + r_meas_mss + self.prev_so_mss, self.q_mss_out_cap)

                q_mss_ow = max(0, min(self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out + self.prev_so_mss,
                                      self.q_mss_ow_cap - self.q_mss_out_cap))

                so_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow - self.stor_mss_cap
                             + self.prev_so_mss)

                stor_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow -
                               (so_mss - self.prev_so_mss))

            else:
                q_mss_out = min(self.prev_stor_mss + sum_r_mss + r_meas_mss + 0, self.q_mss_out_cap)

                q_mss_ow = max(0, min(self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out + 0,
                                      self.q_mss_ow_cap - self.q_mss_out_cap))

                so_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow - self.stor_mss_cap
                             + 0)

                stor_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow - so_mss)

            # update state
            self.prev_stor_mss = stor_mss
            self.prev_so_mss = so_mss
        return sum_r_swds, r_meas_swds, sum_r_mss, r_meas_mss, q_swds_ow, q_mss_out, q_mss_ow, so_swds, so_mss, \
               stor_swds, stor_mss


# 1.4 Get python solutions and save in csv file
start = time.time()
Sum_r_swds =[0]
R_meas_swds = [0]
Sum_r_mss = [0]
R_meas_mss = [0]
Q_swds_ow = [0]
Q_mss_out = [0]
Q_mss_ow = [0]
prev_so_swds_t0, prev_so_mss_t0, prev_stor_swds_t0, prev_stor_mss_t0 = 0, 0, 0, 0
So_swds = [prev_so_swds_t0]
So_mss = [prev_so_mss_t0]
Stor_swds = [prev_stor_swds_t0]
Stor_mss = [prev_stor_mss_t0]


m = SewerSystem(swds_no_meas_area, mss_no_meas_area, prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0,
                prev_so_mss_t0,
                q_swds_ow_cap=55.1, q_mss_out_cap=26.3, q_mss_ow_cap=48.1, stor_swds_cap=2, stor_mss_cap=9)

t = 1

while t <= iters - 1:
    sol = m.sol(pr_no_meas_area, cp_no_meas_area, op_no_meas_area, r_pr_swds[t], r_cp_swds[t], r_op_swds[t], r_pr_mss[t]
                , r_cp_mss[t], r_op_mss[t], meas_swds[t], meas_mss[t], ow_no_meas_area, tot_meas_area)

    Sum_r_swds.append(sol[0])
    R_meas_swds.append(sol[1])
    Sum_r_mss.append(sol[2])
    R_meas_mss.append(sol[3])
    Q_swds_ow.append(sol[4])
    Q_mss_out.append(sol[5])
    Q_mss_ow.append(sol[6])
    So_swds.append(sol[7])
    So_mss.append(sol[8])
    Stor_swds.append(sol[9])
    Stor_mss.append(sol[10])

    t += 1

filename = 'SS_general_test_pysol.csv'
np.savetxt('pysol/' + filename, np.c_[Sum_r_swds, R_meas_swds, Sum_r_mss, R_meas_mss, Q_swds_ow, Q_mss_out, Q_mss_ow,
                                      So_swds, So_mss, Stor_swds, Stor_mss],
           fmt="%.8f", delimiter=',',
           header='Sum_r_swds, R_meas_swds, Sum_r_mss, R_meas_mss, Q_swds_ow, Q_mss_out, Q_mss_ow, So_swds, '
                  'So_mss, Stor_swds, Stor_mss')
# Insert the Date column for locating purposes.
df = pd.read_csv('pysol/' + filename)
df.insert(0, 'Date', date)
df.to_csv('pysol/' + filename)
end = time.time()
print(end - start)

# 1.5 Validate with excel solutions.
data_py = pd.read_csv('pysol/' + filename)
data_ex = pd.read_csv('exsol/SS_general_test_exsol.csv')

# Examine through the dataframe column by column
A = np.zeros((43825, 11))
for c in range(11):
    for r in range(1, 43825):  # from row 1 to the last row (row 43824), excluding first row(t=0).
        A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
for c in range(11):
    print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))


# 2. EXTENDED TESTS
# 2.0 Validate function. Built for easily manipulating comparisons between python and excel solutions.
def validate(a, b, c, d, e, f, A1, A2):
    """Validates python solution with excel solution based on given parameter sets"""
    # a ---  q_swds_ow_cap (default: 55.1)
    # b ---  q_mss_out_cap (default: 26.3)
    # c --- q_mss_ow_cap (default: 48.1)
    # d --- stor_swds_cap (default: 2)
    # e --- stor_mss_cap (default: 9)
    # f --- Set No., used to name the output file.
    # A1 --- swds_no_meas_area
    # A2 --- mss_no_meas_area

    Sum_r_swds = [0]
    R_meas_swds = [0]
    Sum_r_mss = [0]
    R_meas_mss = [0]
    Q_swds_ow = [0]
    Q_mss_out = [0]
    Q_mss_ow = [0]
    prev_so_swds_t0, prev_so_mss_t0, prev_stor_swds_t0, prev_stor_mss_t0 = 0, 0, 0, 0
    So_swds = [prev_so_swds_t0]
    So_mss = [prev_so_mss_t0]
    Stor_swds = [prev_stor_swds_t0]
    Stor_mss = [prev_stor_mss_t0]

    m = SewerSystem(A1, A2, prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0,
                    prev_so_mss_t0,
                    q_swds_ow_cap=a, q_mss_out_cap=b, q_mss_ow_cap=c, stor_swds_cap=d, stor_mss_cap=e)

    t = 1

    while t <= iters - 1:
        sol = m.sol(pr_no_meas_area, cp_no_meas_area, op_no_meas_area, r_pr_swds[t], r_cp_swds[t], r_op_swds[t],
                    r_pr_mss[t], r_cp_mss[t], r_op_mss[t], meas_swds[t], meas_mss[t], ow_no_meas_area, tot_meas_area)

        Sum_r_swds.append(sol[0])
        R_meas_swds.append(sol[1])
        Sum_r_mss.append(sol[2])
        R_meas_mss.append(sol[3])
        Q_swds_ow.append(sol[4])
        Q_mss_out.append(sol[5])
        Q_mss_ow.append(sol[6])
        So_swds.append(sol[7])
        So_mss.append(sol[8])
        Stor_swds.append(sol[9])
        Stor_mss.append(sol[10])

        t += 1

    filename = 'SS_extended_test_pysol' + str(f) + '.csv'
    np.savetxt('pysol/' + filename,
               np.c_[Sum_r_swds, R_meas_swds, Sum_r_mss, R_meas_mss, Q_swds_ow, Q_mss_out, Q_mss_ow,
                     So_swds, So_mss, Stor_swds, Stor_mss],
               fmt="%.8f", delimiter=',',
               header='Sum_r_swds, R_meas_swds, Sum_r_mss, R_meas_mss, Q_swds_ow, Q_mss_out, Q_mss_ow, So_swds, '
                      'So_mss, Stor_swds, Stor_mss')
    df = pd.read_csv('pysol/' + filename)
    df.insert(0, 'Date', date)
    df.to_csv('pysol/' + filename)

    data_py = pd.read_csv('pysol/' + filename)
    data_ex = pd.read_csv('exsol/SS_extended_test_exsol_set' + str(f) + '.csv')
    A = np.zeros((43825, 11))
    for c in range(11):
        for r in range(1, 43825):  # from row 1 to the last row (row 43824), excluding first row(t=0).
            A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c + 2]][r]
    for c in range(11):
        print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))
        #print(np.where(max(A[:,c]) != 0 and A[:,c] == max(A[:,c])), np.where(min(A[:,c]) != 0 and A[:,c] == min(A[:,c])))


R_swds_all = pd.read_csv(indir / 'r_swds.csv')
R_mss_all = pd.read_csv(indir / 'r_mss.csv')

# 2.1 Set 1: q_swds_ow_cap  = 551
f = 1
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(551, 26.3, 48.1, 2, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.2 Set 2: q_swds_ow_cap  = 0
f = 2
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(0, 26.3, 48.1, 2, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.3 Set 3: q_mss_out_cap = 263
f = 3
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(55.1, 263, 48.1, 2, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.4 Set 4: q_mss_out_cap = 0
f = 4
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(55.1, 0, 48.1, 2, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.5 Set 5: q_mss_ow_cap = 481
f = 5
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(55.1, 26.3, 481, 2, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.6 Set 6: q_mss_ow_cap = 0
f = 6
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(55.1, 26.3, 0, 2, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.7 Set 7: stor_swds_cap = 20
f = 7
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(37.1, 26.3, 48.1, 20, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.8 Set 8: stor_swds_cap = 0
f = 8
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(57.1, 26.3, 48.1, 0, 9, f, swds_no_meas_area, mss_no_meas_area)

# 2.9 Set 9: stor_mss_cap = 90
f = 9
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(55.1, 26.3, 48.1, 2, 90, f, swds_no_meas_area, mss_no_meas_area)

# 2.10 Set 10: stor_mss_cap = 0
f = 10
print(str(f))
r_pr_swds = R_swds_all['r_pr_swds_'+str(f)]
r_cp_swds = R_swds_all['r_cp_swds_'+str(f)]
r_op_swds = R_swds_all['r_op_swds_'+str(f)]
r_pr_mss = R_mss_all['r_pr_mss_'+str(f)]
r_cp_mss = R_mss_all['r_cp_mss_'+str(f)]
r_op_mss = R_mss_all['r_op_mss_'+str(f)]
validate(55.1, 26.3, 48.1, 2, 0, f, swds_no_meas_area, mss_no_meas_area)






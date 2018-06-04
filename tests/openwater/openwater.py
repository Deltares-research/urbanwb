import numpy as np
import pandas as pd
import time
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
# 1.1 Input data from other modules.
# a. results of r_up_ow, d_gw_ow, q_swds_ow, q_mss_ow, so_swds_ow, so_mss_ow
# from ..... modules
r_up_ow = pd.read_csv(indir / 'r_up_ow.csv')['r_up_ow_0']
d_gw_ow = pd.read_csv(indir / 'd_gw_ow.csv')['d_gw_ow_0']
q_swds_ow = pd.read_csv(indir / 'q_swds_ow.csv')['q_swds_ow_0']
q_mss_ow = pd.read_csv(indir / 'q_mss_ow.csv')['q_mss_ow_0']
so_swds_ow = pd.read_csv(indir / 'so_swds_ow.csv')['so_swds_ow_0']
so_mss_ow = pd.read_csv(indir / 'so_mss_ow.csv')['so_mss_ow_0']
# b. flow from measure to open water
meas_ow = np.zeros(iters)

# 1.2 General test settings
# ow_level --- target open water level. A calculated value.
total_area = 10000
total_meas_area = 0
ow_no_meas_area = 300
ow_level = 1.5
up_no_meas_area = 6855
gw_no_meas_area = 8140
swds_no_meas_area = 2845
mss_no_meas_area = 0


class OpenWater:
    def __init__(self, init_owl_t0, ow_no_meas_area, ow_level, q_ow_out_cap=200):
        """
        creates an instance of open water class with given states and properties,
        iterates sol function at each time step.
        """

        # state
        # prev_owl --- open water level at previous time step [m-SL].
        self.prev_owl = init_owl_t0

        # properties
        # ow_no_meas_area --- area of open water (without a measure) [m^2].
        # q_ow_out_cap --- predefined discharge capacity from open water to outside water [mm/d]
        # ow_level --- predefined target open water level [m-SL].
        self.ow_no_meas_area = ow_no_meas_area
        self.q_ow_out_cap = q_ow_out_cap
        self.ow_level = ow_level

    def sol(self, p_atm, e_pot_ow, r_up_ow, d_gw_ow, q_swds_ow, q_mss_ow, so_swds_ow, so_mss_ow, meas_ow,
            up_no_meas_area, gw_no_meas_area, swds_no_meas_area, mss_no_meas_area,
            tot_meas_area, total_area, delta_t=1/24):

        # parameters
        # prec_ow --- Direct rainfall on open water during the current time step [mm].
        # e_atm_ow --- Evarporation from open water during current time step [mm]
        # sum_r_ow --- Total runoff (from unpaved area) to open water during current time step [mm]
        # sum_d_ow --- Drainage from groundwater to open water during current time step [mm]
        # sum_q_ow --- Total outflow from sewer systems to open water during current time step [mm]
        # sum_so_ow --- Total sewer overflow from sewer systems to open water during current time step [mm]
        # r_meas_ow --- Inflow from measure area (if applicable) during current time step [mm]
        # q_ow_out --- Discharge from open water to outside water during current time step [mm]

        if self.ow_no_meas_area == 0:
            prec_ow = e_atm_ow = sum_r_ow = sum_d_ow = sum_q_ow = sum_so_ow = r_meas_ow = q_ow_out = 0

            owl = self.ow_level

        else:
            prec_ow = p_atm

            e_atm_ow = e_pot_ow

            sum_r_ow = r_up_ow * up_no_meas_area / self.ow_no_meas_area

            sum_d_ow = d_gw_ow * gw_no_meas_area / self.ow_no_meas_area

            sum_q_ow = (q_swds_ow * swds_no_meas_area + q_mss_ow * mss_no_meas_area) / self.ow_no_meas_area

            sum_so_ow = (so_swds_ow * swds_no_meas_area + so_mss_ow * mss_no_meas_area) / self.ow_no_meas_area

            r_meas_ow = meas_ow * tot_meas_area / self.ow_no_meas_area

            q_ow_out = (self.ow_no_meas_area / total_area) * min(delta_t * self.q_ow_out_cap *
                                                                 (total_area / self.ow_no_meas_area),
                                                               1000 * (self.ow_level - self.prev_owl) + prec_ow -
                                                               e_atm_ow + sum_r_ow + sum_d_ow + sum_q_ow + sum_so_ow +
                                                               r_meas_ow)

            owl = self.prev_owl - (prec_ow - e_atm_ow + sum_r_ow + sum_d_ow + sum_q_ow + sum_so_ow + r_meas_ow -
                                   (total_area / self.ow_no_meas_area) * q_ow_out) / 1000

            # update state
            self.prev_owl = owl

        return prec_ow, e_atm_ow, sum_r_ow, sum_d_ow, sum_q_ow, sum_so_ow, r_meas_ow, q_ow_out, owl

# 1.4 Get python solutions and save in csv file
start = time.time()
Prec_ow = [0]
E_atm_ow = [0]
Sum_r_ow = [0]
Sum_d_ow = [0]
Sum_q_ow = [0]
Sum_so_ow = [0]
R_meas_ow = [0]
Q_ow_out = [0]
init_owl_t0 = 1.5
Owl = [init_owl_t0]

m = OpenWater(init_owl_t0, ow_no_meas_area, ow_level, q_ow_out_cap=200)

t = 1

while t <= iters - 1:
    sol = m.sol(P_atm[t], E_pot_OW[t], r_up_ow[t], d_gw_ow[t], q_swds_ow[t], q_mss_ow[t], so_swds_ow[t], so_mss_ow[t], meas_ow[t],
            up_no_meas_area, gw_no_meas_area, swds_no_meas_area, mss_no_meas_area,
            total_meas_area, total_area, delta_t = 1/24)

    Prec_ow.append(sol[0])
    E_atm_ow.append(sol[1])
    Sum_r_ow.append(sol[2])
    Sum_d_ow.append(sol[3])
    Sum_q_ow.append(sol[4])
    Sum_so_ow.append(sol[5])
    R_meas_ow.append(sol[6])
    Q_ow_out.append(sol[7])
    Owl.append(sol[8])

    t += 1

filename = 'OW_general_test_pysol.csv'
np.savetxt('pysol/' + filename, np.c_[Prec_ow, E_atm_ow, Sum_r_ow, Sum_d_ow, Sum_q_ow, Sum_so_ow,
                                      R_meas_ow, Q_ow_out, Owl],
           fmt="%.8f", delimiter=',',
           header='Prec_ow, E_atm_ow, Sum_r_ow, Sum_d_ow, Sum_q_ow, Sum_so_ow, R_meas_ow, Q_ow_out, Owl')
# Insert the Date column for locating purposes.
df = pd.read_csv('pysol/' + filename)
df.insert(0, 'Date', date)
df.to_csv('pysol/' + filename)
end = time.time()
print(end - start)

# 1.5 Validate with excel solutions.
data_py = pd.read_csv('pysol/' + filename)
data_ex = pd.read_csv('exsol/OW_general_test_exsol.csv')

# Examine through the dataframe column by column
A = np.zeros((43825, 9))
for c in range(9):
    for r in range(1, 43825):  # from row 1 to the last row (row 43824), excluding first row(t=0).
        A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
for c in range(9):
    print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))









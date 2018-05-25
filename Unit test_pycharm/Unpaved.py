import numpy as np
import pandas as pd

# Load csv file.
path = "C:/Users/ZWX/PycharmProjects/UWM/Unit_test/Unpaved/"
InputData = pd.read_csv(path + 'input_csv.csv')  # input the precipitation, potential evaporation

date = InputData['date']
P_atm = InputData['P_atm']
Ref_grass = InputData['Ref.grass']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]

# 1. GENERAL TEST

# 1.1 Input data from other modules.
# a. results of r_up from paved roof, closed paved and open paved module.
r_pr_up = pd.read_csv(path + 'inputdata/r_up.csv')['r_pr_up_0']
r_cp_up = pd.read_csv(path + 'inputdata/r_up.csv')['r_cp_up_0']
r_op_up = pd.read_csv(path + 'inputdata/r_up.csv')['r_op_up_0']
# b. results of theta_rz from unsaturated zone module.
theta_rz = pd.read_csv(path + 'inputdata/theta_rz.csv')['theta_rz_0']


# 1.2 General test settings
# tot_area --- total area of study domain.
# xx_frac --- xx percentage.
# xx_discfrac --- part of xx that is disconnected.
# xx_meas_area --- area of xx (with a measure)
# xx_no_meas_area --- area of xx (without a measure)
# up_meas_inflow_area --- runoff inflow area to measure, inflow area >= measure area, predefined as 0.
tot_area = 10000
pr_frac = 0.156
tot_pr_area = tot_area * pr_frac
pr_discfrac = 0
pr_meas_area = 0
pr_no_meas_area = tot_pr_area - pr_meas_area

cp_frac = 0.1285 - 5184*0.3048**2/10000
tot_cp_area = tot_area * cp_frac
cp_discfrac = 0
cp_meas_area = 0
cp_no_meas_area = tot_cp_area - cp_meas_area

op_frac = 5184*0.3048**2/10000
tot_op_area = tot_area * op_frac
op_discfrac = 0
op_meas_area = 0
op_no_meas_area = tot_op_area - op_meas_area

up_frac = 0.6855
tot_up_area = tot_area * up_frac
up_meas_area = 0
up_no_meas_area = tot_up_area - up_meas_area
up_meas_inflow_area = 0

ow_frac = 0.03
tot_ow_area = tot_area * ow_frac
ow_meas_area = 0
ow_no_meas_area = tot_ow_area - op_meas_area

# 1.3 Class Unpaved.
class Unpaved:
    def __init__(self, fin_stor_up_t0, up_no_meas_area, up_meas_area, up_meas_inflow_area, infilcap_up=48,
                 mois_uz_max=249.2, k_sat_uz=67.9, intstorcap_up=20):

        # state
        # prev_fin_stor_up --- final storage on the surface of the unpaved area at previous time step [mm].
        self.prev_fin_stor_up = fin_stor_up_t0

        # properties
        # up_no_meas_area --- unpaved area (without a measure) [m^2].
        # up_meas_area --- unpaved area (with a measure) [m^2].
        # up_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # infilcap_up --- predefined infiltration capacity of unpaved area [mm/d].
        # mois_uz_max --- maximum water volume in root zone [mm].
        # k_sat_uz --- predefined saturated permeability of unsaturated zone [mm/d].
        # intstorcap_up --- predefined storage capacity on unpaved area [mm].
        self.up_no_meas_area = up_no_meas_area
        self.up_meas_area = up_meas_area
        self.up_meas_inflow_area = up_meas_inflow_area
        self.infilcap_up = infilcap_up
        self.mois_uz_max = mois_uz_max
        self.k_sat_uz = k_sat_uz
        self.intstorcap_up = intstorcap_up

    def inflowfac(self):
        return (self.up_meas_inflow_area - self.up_meas_area) / self.up_no_meas_area

    def sol(self, p_atm, e_pot_ow, r_pr_up, r_cp_up, r_op_up, prev_mois_uz, pr_no_meas_area, cp_no_meas_area,
            op_no_meas_area, ow_no_meas_area, delta_t=1 / 24):

        # parameters
        # sum_r_up --- Runoff from all paved areas to unpaved area [mm].
        # init_stor_up --- Initial storage on the surface of the unpaved area
        # after rainfall during current time step [mm]
        # act_infilcap_up --- Actual infiltration capacity during the current time step [mm].
        # prev_mois_uz --- water volume in root zone at the previous time step [mm].
        # tfac_up --- Time factor [-]. Part of the current time step that storage on the surface of the unpaved area
        # is available for infiltration and evaporation.
        # e_atm_up --- Evaporation from storage on the surface of the unpaved area during the current time step [mm]
        # i_up_uz --- Infiltration from storage on the surface of the unpaved area
        # to the unsaturated zone during the current time step [mm].
        # fin_stor_up --- Final storage on the surface of the unpaved area at the end of the current time step [mm].
        # r_up_meas --- Runoff from unpaved to an area with a drainage measure during the current time step
        # (not necessarily on the unpaved area itself) [mm].
        # r_up_ow --- Runoff from unpaved to open water area during the current time step [mm].

        if self.up_no_meas_area == 0:
            sum_r_up = init_stor_up = act_infilcap_up = tfac_up = e_atm_up = i_up_uz = fin_stor_up \
                     = r_up_meas = r_up_ow = 0

        else:
            sum_r_up = (r_pr_up * pr_no_meas_area + r_cp_up * cp_no_meas_area + r_op_up * op_no_meas_area) / (
                self.up_no_meas_area)

            init_stor_up = self.prev_fin_stor_up + p_atm + sum_r_up

            act_infilcap_up = min(delta_t * self.infilcap_up,
                                  self.mois_uz_max - prev_mois_uz + min(self.mois_uz_max - prev_mois_uz,
                                                                        delta_t * self.k_sat_uz))

            if e_pot_ow + act_infilcap_up <= 0:
                tfac_up = 0
            else:
                tfac_up = min(1, init_stor_up / (e_pot_ow + act_infilcap_up))

            e_atm_up = tfac_up * e_pot_ow

            i_up_uz = tfac_up * act_infilcap_up

            if ow_no_meas_area == 0:
                fin_stor_up = max(0, min(self.intstorcap_up + (self.up_no_meas_area - (
                            self.up_meas_inflow_area - self.up_meas_area)) / self.up_no_meas_area * (
                                                     init_stor_up - e_atm_up - i_up_uz - self.intstorcap_up),
                                         init_stor_up - e_atm_up - i_up_uz))

            else:
                fin_stor_up = max(0, min(self.intstorcap_up, init_stor_up - e_atm_up - i_up_uz))

            r_up_meas = self.inflowfac() * max(0, init_stor_up - e_atm_up - i_up_uz - self.intstorcap_up)

            if ow_no_meas_area == 0:
                r_up_ow = 0
            else:
                r_up_ow = max(0, init_stor_up - e_atm_up - i_up_uz - self.intstorcap_up - r_up_meas)

            # update state
            self.prev_fin_stor_up = fin_stor_up

        return sum_r_up, init_stor_up, act_infilcap_up, tfac_up, e_atm_up, i_up_uz, fin_stor_up, r_up_meas, r_up_ow


# 1.4 Get python solutions and save in csv file.
delta_t = 1 / 24

Sum_r_up = [0]
Init_stor_up = [0]
Act_infilcap_up = [0]
Tfac_up = [0]
E_atm_up = [0]
I_up_uz = [0]
fin_stor_up_t0 = 0  # Set initial final storage on the surface of the unpaved area as 0.
Fin_stor_up = [fin_stor_up_t0]
R_up_meas = [0]
R_up_ow = [0]


m = Unpaved(fin_stor_up_t0, up_no_meas_area, up_meas_area, up_meas_inflow_area, infilcap_up=48, mois_uz_max=249.2,
            k_sat_uz=67.9, intstorcap_up=20)

t = 1

while t <= iters - 1:
    sol = m.sol(P_atm[t], E_pot_OW[t], r_pr_up[t], r_cp_up[t], r_op_up[t], theta_rz[t - 1], pr_no_meas_area,
                cp_no_meas_area, op_no_meas_area, ow_no_meas_area, delta_t=1 / 24)

    Sum_r_up.append(sol[0])
    Init_stor_up.append(sol[1])
    Act_infilcap_up.append(sol[2])
    Tfac_up.append(sol[3])
    E_atm_up.append(sol[4])
    I_up_uz.append(sol[5])
    Fin_stor_up.append(sol[6])
    R_up_meas.append(sol[7])
    R_up_ow.append(sol[8])

    t += 1

filename = 'UP_general_test_pysol.csv'
np.savetxt('pysol/' + filename,
           np.c_[Sum_r_up, Init_stor_up, Act_infilcap_up, Tfac_up, E_atm_up, I_up_uz, Fin_stor_up, R_up_meas, R_up_ow],
           fmt="%.8f", delimiter=',',
           header='Sum_r_up, Init_stor_up, Act_infilcap_up, Tfac_up, E_atm_up, '
                  'I_up_uz, Fin_stor_up, R_up_meas, R_up_ow')
df = pd.read_csv('pysol/' + filename)
df.insert(0, 'Date', date)
df.to_csv('pysol/' + filename)


# 1.5 Validate with excel solutions.
data_py = pd.read_csv('pysol/' + filename)
data_ex = pd.read_csv('exsol/UP_general_test_exsol.csv')

# Examine through the dataframe column by column
A = np.zeros((43825, 9))
for c in range(9):
    for r in range(1, 43825):  # from row 1 to the last row (row 43824), excluding first row(t=0).
        A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
for c in range(9):
    print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))

# 2. EXTENDED TESTS
# 2.0 Validate function. Built for easily manipulating comparisons between python and excel solutions.
def validate(a, b, c, d, e, A1, A2, A3):
    """Validates python solution with excel solution based on given parameter sets"""
    # a --- predefined infiltration capacity of unpaved area [mm/d].
    # b --- maximum water volume in root zone[mm].
    # c --- predefined saturated permeability of unsaturated zone [mm/d].
    # d --- predefined storage capacity on unpaved area [mm].
    # e --- Set No., used to name the output file.
    # A1 --- unpaved area (without a measure)
    # A2 --- unpaved area (with a measure)
    # A3 --- unpaved measure inflow area.
    Sum_r_up = [0]
    Init_stor_up = [0]
    Act_infilcap_up = [0]
    Tfac_up = [0]
    E_atm_up = [0]
    I_up_uz = [0]
    fin_stor_up_t0 = 0
    Fin_stor_up = [fin_stor_up_t0]
    R_up_meas = [0]
    R_up_ow = [0]

    m = Unpaved(fin_stor_up_t0, up_no_meas_area=A1, up_meas_area=A2, up_meas_inflow_area=A3,
                infilcap_up=a, mois_uz_max=b, k_sat_uz=c, intstorcap_up=d)

    t = 1

    while t <= iters - 1:
        sol = m.sol(P_atm[t], E_pot_OW[t], r_pr_up[t], r_cp_up[t], r_op_up[t], theta_rz[t - 1], pr_no_meas_area,
                cp_no_meas_area, op_no_meas_area, ow_no_meas_area, delta_t=1 / 24)

        Sum_r_up.append(sol[0])
        Init_stor_up.append(sol[1])
        Act_infilcap_up.append(sol[2])
        Tfac_up.append(sol[3])
        E_atm_up.append(sol[4])
        I_up_uz.append(sol[5])
        Fin_stor_up.append(sol[6])
        R_up_meas.append(sol[7])
        R_up_ow.append(sol[8])

        t += 1

    filename = 'UP_General_test_pysol' + str(e) + '.csv'
    np.savetxt('pysol/' + filename,
           np.c_[Sum_r_up, Init_stor_up, Act_infilcap_up, Tfac_up, E_atm_up, I_up_uz, Fin_stor_up, R_up_meas, R_up_ow],
           fmt="%.8f", delimiter=',',
           header='Sum_r_up, Init_stor_up, Act_infilcap_up, Tfac_up, E_atm_up, '
                  'I_up_uz, Fin_stor_up, R_up_meas, R_up_ow')
    df = pd.read_csv('pysol/' + filename)
    df.insert(0, 'Date', date)
    df.to_csv('pysol/' + filename)

    data_py = pd.read_csv('pysol/' + filename)
    data_ex = pd.read_csv('exsol/UP_extended_test_exsol_set' + str(e) + '.csv')
    A = np.zeros((43825, 9))
    for c in range(9):
        for r in range(1, 43825):
            A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c + 2]][r]
    for c in range(9):
        print('COL ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))
        # print(np.where(max(A[:,c]) != 0 and A[:,c] == max(A[:,c])), np.where(min(A[:,c]) != 0 and A[:,c] == min(A[:,c])))


r_up = pd.read_csv(path + 'inputdata/r_up.csv')
theta_rz_all = pd.read_csv(path + 'inputdata/theta_rz.csv')

# 2.1 Set 1: intstorcap_up = 0
e = 1
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(48, 249.2, 67.9, 0, e, 6855, 0, 0)

# 2.2 Set 2: intstorcap_up = 2000
e = 2
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(48, 249.2, 67.9, 2000, e, 6855, 0, 0)

# 2.3 Set 3: infilcap_up = 0
e = 3
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(0, 249.2, 67.9, 20, e, 6855, 0, 0)

# 2.4 Set 4: infilcap_up = 4800
e = 4
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(4800, 249.2, 67.9, 20, e, 6855, 0, 0)

# 2.5 Set 5: soiltype = 3, croptype = 1 (mois_uz_max = 202.4, k_sat_uz = 45.3)
e = 5
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(48, 202.4, 45.3, 20, e, 6855, 0, 0)

# 2.6 Set 6: soiltype = 4, croptype = 1 (mois_uz_max = 91.2, k_sat_uz = 152.2)
e = 6
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(48, 91.2, 152.2, 20, e, 6855, 0, 0)

# 2.7 Set 7: disfrac = 0.37 for all three paved areas
e = 7
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(48, 249.2, 67.9, 20, e, 6855, 0, 0)

# 2.8 Set 8: up_no_meas_area = 0
e = 8
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
validate(48, 249.2, 67.9, 20, e, 0, 6855, 0)

# 2.9 Set 9: ow_no_meas_area = 0
e = 9
r_pr_up = r_up['r_pr_up_'+str(e)]
r_cp_up = r_up['r_cp_up_'+str(e)]
r_op_up = r_up['r_op_up_'+str(e)]
theta_rz = theta_rz_all['theta_rz_'+str(e)]
ow_no_meas_area = 0
validate(48, 249.2, 67.9, 20, e, 6855, 0, 0)

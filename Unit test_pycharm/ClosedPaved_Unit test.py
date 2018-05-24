import numpy as np
import pandas as pd

# Load csv file.
path = "C:/Users/ZWX/PycharmProjects/UWM/Unit_test/ClosedPaved/"
InputData = pd.read_csv(path + 'input_csv.csv')  # input the precipitation, potential evaporation

date = InputData['date']
P_atm = InputData['P_atm']
Ref_grass = InputData['Ref.grass']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]

# 1. GENERAL TEST

# 1.1 General test settings
# tot_area --- total area of study domain
# cp_frac --- closed paved percentage
# tot_cp_area --- total closed paved area
# cp_meas_area --- area of closed paved (with a measure)
# cp_no_meas_area --- area of closed paved (without a measure)
# measure_inflow_area --- runoff inflow area to measure, inflow area >= measure area, predefined as 0.
tot_area = 10000
cp_frac = 0.1285 - (5184*0.3048**2/10000)
tot_cp_area = tot_area * cp_frac
cp_meas_area = 0
cp_no_meas_area = tot_cp_area - cp_meas_area
cp_meas_inflow_area = 0


# 1.2 Class ClosedPaved.
class ClosedPaved:
    def __init__(self, init_intstor_cp_t0, cp_no_meas_area, cp_meas_area, cp_meas_inflow_area, intstorcap_cp=1.6,
                 stormfrac_cp=1.0, discfrac_cp=0.0):

        # state
        # init_intstor_cp --- initial interception storage on closed paved
        self.init_intstor_cp = init_intstor_cp_t0

        # properties
        # cp_no_meas_area --- closed paved area (without a measure) [m^2].
        # cp_meas_area --- closed paved area (with a measure) [m^2].
        # cp_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # intstorcap_cp --- predefined storage capacity on closed paved
        # stormfrac_cp --- part of urban area with storm water drainage system
        # mxdfrac --- part of urban area with mixed sewer system
        # discfrac_cp --- part of closed paved area that is disconnected
        self.cp_no_meas_area = cp_no_meas_area
        self.cp_meas_area = cp_meas_area
        self.cp_meas_inflow_area = cp_meas_inflow_area
        self.intstorcap = intstorcap_cp
        self.stormfrac = stormfrac_cp
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_cp

    def inflowfac(self):
        return (self.cp_meas_inflow_area - self.cp_meas_area) / self.cp_no_meas_area

    def sol(self, p_atm, e_pot_ow):

        # parameters
        # int_cp --- Interception on closed paved after rainfall during current time step [mm]
        # e_atm_cp --- Evaporation from interception storage on closed paved during current time step [mm]
        # intstor_cp --- Remaining interception storage on closed paved at the end of the current time step [mm]
        # r_cp_meas --- Runoff from closed paved to an area with a drainage measure
        # (not necessarily on the closed paved area itself) [mm].
        # r_cp_swds --- Runoff from closed paved to the storm water drainage system [mm]
        # r_cp_mss --- Runoff from closed paved to the mixed sewer system [mm]
        # r_cp_up --- Runoff from closed paved to unpaved area [mm].

        if self.cp_no_meas_area == 0:
            int_cp = e_atm_cp = intstor_cp = r_cp_meas = r_cp_swds = r_cp_mss = r_cp_up = 0

        else:
            int_cp = min(self.intstorcap, max(0, self.init_intstor_cp + p_atm))

            e_atm_cp = min(e_pot_ow, int_cp)

            intstor_cp = int_cp - e_atm_cp

            r_cp_meas = self.inflowfac() * max(0, (p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp)))

            r_cp_swds = self.stormfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_cp - (
                        intstor_cp - self.init_intstor_cp) - r_cp_meas)

            r_cp_mss = self.mxdfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_cp - (
                        intstor_cp - self.init_intstor_cp) - r_cp_meas)

            r_cp_up = self.discfrac * max(0, p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp) - r_cp_meas)

            # update state
            self.init_intstor_cp = intstor_cp

        return int_cp, e_atm_cp, intstor_cp, r_cp_meas, r_cp_swds, r_cp_mss, r_cp_up


# 1.3 Get python solutions and save in csv file.
E_atm = [0]
Intcp = [0]
init_intstor_cp_t0 = 0  # Set initial interception storage as 0.
Intstor = [init_intstor_cp_t0]
R_meas = [0]
R_swds = [0]
R_mss = [0]
R_up = [0]

m = ClosedPaved(init_intstor_cp_t0, cp_no_meas_area, cp_meas_area, cp_meas_inflow_area
                , intstorcap_cp=1.6, stormfrac_cp=1.0, discfrac_cp=0.0)

t = 1

while t <= iters - 1:
    sol = m.sol(P_atm[t], E_pot_OW[t])

    Intcp.append(sol[0])
    E_atm.append(sol[1])
    Intstor.append(sol[2])
    R_meas.append(sol[3])
    R_swds.append(sol[4])
    R_mss.append(sol[5])
    R_up.append(sol[6])
    # print('time step', t)
    t += 1

filename = 'CP_general_test_pysol.csv'
np.savetxt('pysol/' + filename, np.c_[Intcp, E_atm, Intstor, R_meas, R_swds, R_mss, R_up], fmt="%.8f", delimiter=',',
           header='Intcp_cp, E_atm_cp, Intstor_cp, R_cp_meas, R_cp_swds, R_cp_mss, R_cp_up')
df = pd.read_csv('pysol/' + filename)
df.insert(0, 'Date', date)
df.to_csv('pysol/' + filename)


# 1.4 Validate with excel solutions.
data_py = pd.read_csv('pysol/' + filename)
data_ex = pd.read_csv('exsol/CP_general_test_exsol.csv')

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
    # a --- interception storage capacity on closed paved.
    # b --- part of closed paved area with storm water drainage system.
    # c --- part of closed paved area that is disconnected.
    # d --- Set No., used to name the output file.
    # A1 --- closed paved area (without a measure)
    # A2 --- closed paved area (with a measure)
    # A3 --- closed paved measure inflow area.
    E_atm = [0]
    Intcp = [0]
    Intstor = [0]
    R_meas = [0]
    R_swds = [0]
    R_mss = [0]
    R_up = [0]

    m = ClosedPaved(init_intstor_cp_t0=0, cp_no_meas_area=A1, cp_meas_area=A2, cp_meas_inflow_area=A3,
                    intstorcap_cp=a, stormfrac_cp=b, discfrac_cp=c)

    t = 1

    while t <= iters - 1:
        sol = m.sol(P_atm[t], E_pot_OW[t])

        Intcp.append(sol[0])
        E_atm.append(sol[1])
        Intstor.append(sol[2])
        R_meas.append(sol[3])
        R_swds.append(sol[4])
        R_mss.append(sol[5])
        R_up.append(sol[6])

        t += 1

    filename = 'CP_extended_test_pysol_set' + str(d) + '.csv'
    np.savetxt('pysol/' + filename, np.c_[Intcp, E_atm, Intstor, R_meas, R_swds, R_mss, R_up], fmt="%.8f", delimiter=','
               , header='Intcp_cp, E_atm_cp, Intstor_cp, R_cp_meas, R_cp_swds, R_cp_mss, R_cp_up')
    df = pd.read_csv('pysol/' + filename)
    df.insert(0, 'Date', date)
    df.to_csv('pysol/' + filename)
    data_py = pd.read_csv('pysol/' + filename)
    data_ex = pd.read_csv('exsol/CP_extended_test_exsol_set' + str(d) + '.csv')
    A = np.zeros((43825, 7))
    for c in range(7):
        for r in range(1, 43825):
            A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c + 2]][r]
    for c in range(7):
        print('COL ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))
        # print(np.where(max(A[:,c]) != 0 and A[:,c] == max(A[:,c])), np.where(min(A[:,c]) != 0 and A[:,c] == min(A[:,c])))


# 2.1 Set 1: cp_no_meas_area = 0
validate(1.6, 1.0, 0.0, 1, 0, 803.39, 0)

# 2.2 Set 2: intstorcap_cp = 0
validate(0, 1, 0, 2, 803.39, 0, 0)

# 2.3 Set 3: intstorcap_cp = 1600
validate(1600, 1, 0, 3, 803.39, 0, 0)

# 2.4 Set 4: stormfrac = 0.0
validate(1.6, 0, 0, 4, 803.39, 0, 0)

# 2.5 Set 5: stormfrac = 0.37
validate(1.6, 0.37, 0, 5, 803.39, 0, 0)

# 2.6 Set 6: discfrac = 1.0
validate(1.6, 1, 1, 6, 803.39, 0, 0)

# 2.7 Set 7: discfrac = 0.37
validate(1.6, 1, 0.37, 7, 803.39, 0, 0)


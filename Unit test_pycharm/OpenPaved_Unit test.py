import numpy as np
import pandas as pd

# Load csv file
path = "C:/Users/ZWX/PycharmProjects/UWM/Unit_test/OpenPaved/"
InputData = pd.read_csv(path + 'input_csv.csv')  # input the precipitation, potential evaporation

date = InputData['date']
P_atm = InputData['P_atm']
Ref_grass = InputData['Ref.grass']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]

# 1. GENERAL TEST

# 1.1 General test settings
# tot_area --- total area of study domain
# op_frac --- open paved percentage
# tot_op_area --- total open paved area
# op_meas_area --- area of open paved (with a measure)
# op_no_meas_area --- area of open paved (without a measure)
# op_meas_inflow_area --- runoff inflow area to measure, inflow area >= measure area, predefined as 0.
tot_area = 10000
op_frac = 5184*0.3048**2/10000
tot_op_area = tot_area * op_frac
op_meas_area = 0
op_no_meas_area = tot_op_area - op_meas_area
op_meas_inflow_area = 0


# 1.2 Class OpenPaved.
class OpenPaved:
    def __init__(self, init_intstor_op_t0, op_no_meas_area, op_meas_area, op_meas_inflow_area,
                 intstorcap_op=1.6, stormfrac_op=1.0, discfrac_op=0.0, infilcap_op=1.0):

        # state
        # init_intstor_op --- initial interception storage on open paved.
        self.init_intstor_op = init_intstor_op_t0

        # properties
        # op_no_meas_area --- open paved area (without a measure) [m^2].
        # op_meas_area --- open paved area (with a measure) [m^2].
        # op_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # intstorcap_op --- predefined storage capacity on open paved
        # stormfrac_op --- part of urban area with storm water drainage system
        # mxdfrac--- part of urban area with mixed sewer system
        # discfrac_op --- part of open paved area that is disconnected
        # infilcap_op --- predefined infiltration capacity [mm/d] on open paved area
        self.op_no_meas_area = op_no_meas_area
        self.op_meas_area = op_meas_area
        self.op_meas_inflow_area = op_meas_inflow_area
        self.intstorcap = intstorcap_op
        self.stormfrac = stormfrac_op
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_op
        self.infilcap = infilcap_op

    def inflowfac(self):
        return (self.op_meas_inflow_area - self.op_meas_area) / self.op_no_meas_area

    def sol(self, p_atm, e_pot_ow):

        # parameters
        # int_op --- Interception on open paved after rainfall during current time step [mm]
        # e_atm_op --- Evaporation from interception storage on open paved during current time step [mm]
        # intstor_op --- Remaining interception storage on open paved at the end of the current time step [mm]
        # p_op_gw --- Percolation of interception storage on open paved to groundwater during current time step [mm].
        # r_op_meas --- Runoff from open paved to an area with a drainage measure
        # (not necessarily on the open paved area itself) [mm].
        # r_op_swds --- Runoff from open paved to the storm water drainage system [mm]
        # r_op_mss --- Runoff from open paved to the mixed sewer system [mm]
        # r_op_up --- Runoff from open paved to unpaved area [mm].

        if self.op_no_meas_area == 0:
            int_op = e_atm_op = intstor_op = p_op_gw = r_op_meas = r_op_swds = r_op_mss = r_op_up = 0

        else:
            int_op = min(self.intstorcap, max(0, p_atm + self.init_intstor_op))

            e_atm_op = min(e_pot_ow, int_op)

            intstor_op = int_op - e_atm_op

            p_op_gw = max(0, min(p_atm - (self.intstorcap - self.init_intstor_op),
                                 self.infilcap * delta_t))  # infiltration capacity (mm/d) * time step size (hr to d)

            r_op_meas = self.inflowfac() * max(0, p_atm - e_atm_op - (intstor_op - self.init_intstor_op) - p_op_gw)

            r_op_swds = self.stormfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_op - (
                        intstor_op - self.init_intstor_op) - p_op_gw - r_op_meas)

            r_op_mss = self.mxdfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_op - (
                        intstor_op - self.init_intstor_op) - p_op_gw - r_op_meas)

            r_op_up = self.discfrac * max(0,
                                          p_atm - e_atm_op - (intstor_op - self.init_intstor_op) - p_op_gw - r_op_meas)

            # update state
            self.init_intstor_op = intstor_op

        return int_op, e_atm_op, intstor_op, p_op_gw, r_op_meas, r_op_swds, r_op_mss, r_op_up


# 1.3 Get python solutions and save in csv file.
delta_t = 1 / 24

E_atm = [0]
Intcp = [0]
init_intstor_op_t0 = 0
Intstor = [init_intstor_op_t0]
P_gw = [0]
R_meas = [0]
R_swds = [0]
R_mss = [0]
R_up = [0]

m = OpenPaved(init_intstor_op_t0, op_no_meas_area, op_meas_area, op_meas_inflow_area,
              intstorcap_op=1.6, stormfrac_op=1.0, discfrac_op=0.0, infilcap_op=1.0)

t = 1

while t <= iters -1:
    sol = m.sol(P_atm[t], E_pot_OW[t])

    Intcp.append(sol[0])
    E_atm.append(sol[1])
    Intstor.append(sol[2])
    P_gw.append(sol[3])
    R_meas.append(sol[4])
    R_swds.append(sol[5])
    R_mss.append(sol[6])
    R_up.append(sol[7])

    t += 1

filename = 'OP_general_test_pysol.csv'
np.savetxt('pysol/' + filename, np.c_[Intcp, E_atm, Intstor, P_gw, R_meas, R_swds, R_mss, R_up], fmt="%.8f",
           delimiter=',', header='Intcp, E_atm, Intstor, P_gw, R_meas, R_swds, R_mss, R_up')
df = pd.read_csv('pysol/' + filename)
df.insert(0, 'Date', date)
df.to_csv('pysol/' + filename)


# 1.4 Validate with excel solutions.
data_py = pd.read_csv('pysol/' + filename)
data_ex = pd.read_csv('exsol/OP_general_test_exsol.csv')

# Examine through the dataframe column by column
A = np.zeros((43825, 8))
for c in range(8):
    for r in range(1,43825): # do not include the initial row.
        A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
for c in range(8):
    print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))


# 2. EXTENDED TESTS
# 2.0 Validate function. Built for easily manipulating comparisons between python and excel solutions.
def validate(a, b, c, d, e, A1, A2, A3):
    """Validates python solutions with excel solutions based on given parameter sets"""
    # a --- interception storage capacity on open paved.
    # b --- part of open paved area with storm water drainage system.
    # c --- part of open paved area that is disconnected.
    # d --- predefined infiltration capacity [mm/d] on open paved area.
    # e --- Set No., used to name the output file.
    # A1 --- closed paved area (without a measure)
    # A2 --- closed paved area (with a measure)
    # A3 --- closed paved measure inflow area.
    E_atm = [0]
    Intcp = [0]
    init_intstor_op_t0 = 0
    Intstor = [init_intstor_op_t0]
    P_gw = [0]
    R_meas = [0]
    R_swds = [0]
    R_mss = [0]
    R_up = [0]

    m = OpenPaved(init_intstor_op_t0, op_no_meas_area=A1, op_meas_area=A2, op_meas_inflow_area=A3,
                  intstorcap_op=a, stormfrac_op=b, discfrac_op=c, infilcap_op=d)

    t = 1

    while t <= iters - 1:
        sol = m.sol(P_atm[t], E_pot_OW[t])

        Intcp.append(sol[0])
        E_atm.append(sol[1])
        Intstor.append(sol[2])
        P_gw.append(sol[3])
        R_meas.append(sol[4])
        R_swds.append(sol[5])
        R_mss.append(sol[6])
        R_up.append(sol[7])

        t += 1

    filename = 'OP_extended_test_pysol_set' + str(e) + '.csv'
    np.savetxt('pysol/' + filename, np.c_[Intcp, E_atm, Intstor, P_gw, R_meas, R_swds, R_mss, R_up], fmt="%.8f",
               delimiter=',', header='Intcp, E_atm, Intstor, P_gw, R_meas, R_swds, R_mss, R_up')
    df = pd.read_csv('pysol/' + filename)
    df.insert(0, 'Date', date)
    df.to_csv('pysol/' + filename)

    data_py = pd.read_csv('pysol/' + filename)
    data_ex = pd.read_csv('exsol/OP_extended_test_exsol_set' + str(e) + '.csv')
    A = np.zeros((43825, 8))
    for c in range(8):
        for r in range(1, 43825):
            A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c + 2]][r]
    for c in range(8):
        print('COL ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))
        # print(np.where(max(A[:,c]) != 0 and A[:,c] == max(A[:,c])), np.where(min(A[:,c]) != 0 and A[:,c] == min(A[:,c])))


# 2.1 Set 1: intstorcap_op = 0
validate(0, 1, 0, 1, 1, 481.61, 0, 0)

# 2.2 Set 2: intstorcap_op = 1600
validate(1600, 1, 0, 1, 2, 481.61, 0, 0)

# 2.3 Set 3: stormfrac = 0.0
validate(1.6, 0, 0, 1, 3, 481.61, 0, 0)

# 2.4 Set 4: stormfrac = 0.37
validate(1.6, 0.37, 0, 1, 4, 481.61, 0, 0)

# 2.5 Set 5: discfrac = 1.0
validate(1.6, 1, 1, 1, 5, 481.61, 0, 0)

# 2.6 Set 6: discfrac = 0.37
validate(1.6, 1, 0.37, 1, 6, 481.61, 0, 0)

# 2.7 Set 7: infilcap_op = 0
validate(1.6, 1, 0, 0, 7, 481.61, 0, 0)

# 2.8 Set 8: infilcap_op = 100
validate(1.6, 1, 0, 100, 8, 481.61, 0, 0)

# 2.9 Set 9: infilcap_op = 0
validate(1.6, 1, 0, 1, 9, 0, 481.61, 481.61)


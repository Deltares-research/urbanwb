import numpy as np
import pandas as pd
from selector import et_selector, soil_selector
from gwlcalculator import gwlcal
from pathlib import Path
import time


class UnsaturatedZone:
    """
    creates an instance of unsaturated zone class with given states and properties,
    iterates sol function at each time step.
    """
    def __init__(self, theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=2, croptype=1):

        # state
        # init_theta_uz --- moisture content at previous time step [mm].
        self.init_theta_uz = theta_uz_t0

        # properties
        # uz_no_meas_area --- unsaturated zone area (without a measure) [m^2].
        # uz_meas_area --- unsaturated zone area (with a measure) [m^2].
        # soiltype --- Soil type
        # croptype --- Crop type
        # theta_h3l --- Equilibrium moisture content in rootzone, at which transpiration(Epot≤ 1 mm/d) reduction starts.
        # theta_h3h --- Equilibrium moisture content in rootzone, at which transpiration(Epot≥ 5 mm/d) reduction starts.
        # theta_h1 --- Equilibrium moisture content in rootzone with groundwater level at surface level
        # i.e. top root zone (complete saturation).
        # theta_h2 --- Equilibrium moisture content in rootzone with groundwater level at bottom root zone
        # (field capacity).
        # theta_h4 --- Equilibrium moisture content in rootzone, at which transpiration = 0 (wilting point).
        # soil_prm --- soil parameter database determined by soil type and crop type.
        # k_sat_uz --- Predefined saturated permeability of unsaturated zone.

        self.uz_no_meas_area = uz_no_meas_area
        self.uz_meas_area = uz_meas_area
        self.soiltype = soiltype
        self.croptype = croptype
        et = et_selector(self.soiltype, self.croptype)
        self.theta_h3l = et['theta_h3l_mm'].values
        self.theta_h3h = et['theta_h3h_mm'].values
        self.theta_h1 = et['theta_h1_mm'].values
        self.theta_h2 = et['theta_h2_mm'].values
        self.theta_h4 = et['theta_h4_mm'].values
        self.soil_prm = soil_selector(self.soiltype, self.croptype)
        self.k_sat_uz = 10 * self.soil_prm[0]['k_sat']
        # Note here the predefined index 0 does not affect K_sat_uz, which is only dependent on soiltype.

    def sol(self, i_up_uz, meas_uz, tot_meas_area, e_ref, prev_gwl, delta_t=1 / 24):

        # parameters
        # i_up_uz --- Infiltration from storage on the surface of the unpaved area
        # to the unsaturated zone during the current time step [mm].
        # r_meas_uz --- Inflow from measure area (if applicable) during current time step [mm]
        # theta_h3_uz --- Equilibrium moisture content in the root zone
        # at which reduction of transpiration starts [mm] for the current time step.
        # t_alpha_uz --- Transpiration factor [-] for the current time step.
        # t_atm_uz --- Transpiration from unsaturated zone to atmosphere during the current time step [mm].
        # gwl_up_uz --- First value in predefined table above groundwater level at the end of previous time step [m-SL].
        # gwl_low_uz --- First value in predefined table below groundwater level at the end of previous time step[m-SL].
        # theta_eq_uz --- Equilibrium soil moisture content in the root zone for the current time step [mm].
        # capris_max_uz --- Maximum capillary rise for the current time step [mm/d].
        # theta_uz --- Soil moisture content in the root zone at the end of the current time step [mm].

        if self.uz_no_meas_area == 0:
            i_up_uz = r_meas_uz = theta_h3_uz = t_alpha_uz = t_atm_uz = gwl_up = gwl_low = theta_eq_uz = \
                      capris_max_uz = p_uz_gw = theta_uz = 0

        else:
            i_up_uz = i_up_uz  # It is assumed that UP and UZ areas area equal.

            r_meas_uz = meas_uz * tot_meas_area / self.uz_no_meas_area

            if e_ref / (2 * delta_t) < 1:
                theta_h3_uz = self.theta_h3l
            elif e_ref / (2 * delta_t) > 5:
                theta_h3_uz = self.theta_h3h
            else:
                theta_h3_uz = self.theta_h3l + (e_ref / (2 * delta_t) - 1) / 4 * (self.theta_h3h - self.theta_h3l)

            if self.init_theta_uz + i_up_uz + r_meas_uz > self.theta_h1:
                t_alpha_uz = 0
            elif self.init_theta_uz + i_up_uz + r_meas_uz > self.theta_h2:
                t_alpha_uz = 1 - ((self.init_theta_uz + i_up_uz + r_meas_uz) - self.theta_h2) / (
                            self.theta_h1 - self.theta_h2)
            elif self.init_theta_uz + i_up_uz + r_meas_uz > theta_h3_uz:
                t_alpha_uz = 1
            elif self.init_theta_uz + i_up_uz + r_meas_uz > self.theta_h4:
                t_alpha_uz = ((self.init_theta_uz + i_up_uz + r_meas_uz) - self.theta_h4) / (
                            theta_h3_uz - self.theta_h4)
            else:
                t_alpha_uz = 0

            t_atm_uz = e_ref * t_alpha_uz

            gwl_sol = gwlcal(prev_gwl)
            gwl_up = gwl_sol[0]
            gwl_low = gwl_sol[1]
            id1 = gwl_sol[2]
            id2 = gwl_sol[3]

            if prev_gwl < 10:
                theta_eq_uz = self.soil_prm[id2]['moist_cont_eq_rz[mm]'] + (
                            gwl_low - prev_gwl) / (gwl_low - gwl_up) * (
                            self.soil_prm[id1][
                                              'moist_cont_eq_rz[mm]'] -
                            self.soil_prm[id2][
                                              'moist_cont_eq_rz[mm]'])
                capris_max_uz = self.soil_prm[id2]['capris_max[mm/d]'] + (
                            gwl_low - prev_gwl) / (gwl_low - gwl_up) * (
                        self.soil_prm[id1][
                                                'capris_max[mm/d]'] -
                        self.soil_prm[id2][
                                                'capris_max[mm/d]'])
            else:
                theta_eq_uz = self.soil_prm[29]['moist_cont_eq_rz[mm]']
                capris_max_uz = self.soil_prm[29]['capris_max[mm/d]']

            if self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz > theta_eq_uz:
                p_uz_gw = min(self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz - theta_eq_uz,
                              delta_t * self.k_sat_uz)
            else:
                p_uz_gw = -1 * min(theta_eq_uz - (self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz),
                                   delta_t * capris_max_uz)

            theta_uz = self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz - p_uz_gw

            # update state
            self.init_theta_uz = theta_uz

        return i_up_uz, r_meas_uz, theta_h3_uz, t_alpha_uz, t_atm_uz, gwl_up, gwl_low, theta_eq_uz, \
            capris_max_uz, p_uz_gw, theta_uz


if __name__ == '__main__':
    start = time.time()

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
    # a. results of i_up_uz from unpaved module.
    i_up_uz = pd.read_csv(indir / 'i_up_uz.csv')['i_up_uz_0']
    # b. gwl from Groundwater module.
    gwl = pd.read_csv(indir / 'gwl.csv')['gwl_0']
    # c. meas_uz flow from measure to unsaturated zone
    meas_uz = np.zeros(iters)

    # 1.2. General test settings
    # tot_uz_area --- total unsaturated zone area
    # uz_meas_area --- area of unsaturated zone (with a measure)
    # uz_no_meas_area --- area of unsaturated zone (without a measure)
    # tot_meas_area --- total measure area.
    tot_uz_area = 6855
    uz_meas_area = 0
    uz_no_meas_area = tot_uz_area - uz_meas_area
    tot_meas_area = 0

    # 1.4 Get python solutions and save in csv file.
    I_up_uz = [0]
    R_meas_uz = [0]
    Theta_h3_uz = [0]
    T_alpha_uz = [0]
    T_atm_uz = [0]
    Gwl_up_uz = [0]
    Gwl_low_uz = [0]
    Theta_eq_uz = [0]
    Capris_max_uz = [0]
    P_uz_gw = [0]
    init_GWL = 1.5
    theta_uz_t0 = soil_selector(2, 1)[15]['moist_cont_eq_rz[mm]']  # 1.5m is initial gwl.
    Theta_uz = [theta_uz_t0]

    m = UnsaturatedZone(theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=2, croptype=1)

    t = 1

    while t <= iters - 1:
        sol = m.sol(i_up_uz[t], meas_uz[t], tot_meas_area, Ref_grass[t], prev_gwl=gwl[t - 1], delta_t=1 / 24)

        I_up_uz.append(sol[0])
        R_meas_uz.append(sol[1])
        Theta_h3_uz.append(sol[2])
        T_alpha_uz.append(sol[3])
        T_atm_uz.append(sol[4])
        Gwl_up_uz.append(sol[5])
        Gwl_low_uz.append(sol[6])
        Theta_eq_uz.append(sol[7])
        Capris_max_uz.append(sol[8])
        P_uz_gw.append(sol[9])
        Theta_uz.append(sol[10])

        t += 1

    filename = 'UZ_general_test_pysol.csv'
    np.savetxt('pysol/' + filename, np.c_[
        I_up_uz, R_meas_uz, Theta_h3_uz, T_alpha_uz, T_atm_uz, Gwl_up_uz, Gwl_low_uz, Theta_eq_uz, Capris_max_uz,
        P_uz_gw, Theta_uz],
        fmt="%.8f", delimiter=',',
        header='I_up_uz, R_meas_uz, Theta_h3_uz, T_alpha_uz, T_atm_uz, Gwl_up_uz, Gwl_low_uz, Theta_eq_uz, Capris_max_uz, '
               'P_uz_gw, Theta_uz')
    # Insert the Date column for locating purposes.
    df = pd.read_csv('pysol/' + filename)
    df.insert(0, 'Date', date)
    df.to_csv('pysol/' + filename)
    end = time.time()
    print(end - start)

    # 1.5 Validate with excel solutions.
    data_py = pd.read_csv('pysol/' + filename)
    data_ex = pd.read_csv('exsol/UZ_general_test_exsol.csv')

    # Examine through the dataframe column by column
    A = np.zeros((43825, 11))
    for c in range(11):
        for r in range(1, 43825):  # from row 1 to the last row (row 43824), excluding first row(t=0).
            A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
    for c in range(11):
        print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))

    # 2. EXTENDED TESTS
    # 2.0 Validate function. Built for easily manipulating comparisons between python and excel solutions.
    def validate(a, b, c, e, A1, A2):
        """Validates python solution with excel solution based on given parameter sets"""
        # a --- soil type.
        # b --- crop type.
        # c --- initial GWL index.
        # e --- Set No., used to name the output file.
        # A1 --- area of unsaturated zone without a measure.
        # A2 --- area of unsaturated zone with a measure.
        t = 1

        I_up_uz = [0]
        R_meas_uz = [0]
        Theta_h3_uz = [0]
        T_alpha_uz = [0]
        T_atm_uz = [0]
        Gwl_up_uz = [0]
        Gwl_low_uz = [0]
        Theta_eq_uz = [0]
        Capris_max_uz = [0]
        P_uz_gw = [0]
        theta_uz_t0 = soil_selector(a, b)[c]['moist_cont_eq_rz[mm]']  # c is initial gwl [m].
        Theta_uz = [theta_uz_t0]

        m = UnsaturatedZone(theta_uz_t0, uz_no_meas_area=A1, uz_meas_area=A2, soiltype=a, croptype=b)

        while t <= iters - 1:

            sol = m.sol(i_up_uz[t], meas_uz[t], tot_meas_area, Ref_grass[t], prev_gwl=gwl[t - 1], delta_t=1 / 24)

            I_up_uz.append(sol[0])
            R_meas_uz.append(sol[1])
            Theta_h3_uz.append(sol[2])
            T_alpha_uz.append(sol[3])
            T_atm_uz.append(sol[4])
            Gwl_up_uz.append(sol[5])
            Gwl_low_uz.append(sol[6])
            Theta_eq_uz.append(sol[7])
            Capris_max_uz.append(sol[8])
            P_uz_gw.append(sol[9])
            Theta_uz.append(sol[10])
            # print('time step', t)
            t += 1
        filename = 'UZ_extended_test_pysol' + str(e) + '.csv'
        np.savetxt('pysol/' + filename, np.c_[
            I_up_uz, R_meas_uz, Theta_h3_uz, T_alpha_uz, T_atm_uz, Gwl_up_uz, Gwl_low_uz, Theta_eq_uz, Capris_max_uz,
            P_uz_gw, Theta_uz],
            fmt="%.8f", delimiter=',',
            header='I_up_uz, R_meas_uz, Theta_h3_uz, T_alpha_uz, T_atm_uz, Gwl_up_uz, Gwl_low_uz, '
                   'Theta_eq_uz, Capris_max_uz, P_uz_gw, Theta_uz')
        # Insert the Date column for locating purposes.
        df = pd.read_csv('pysol/' + filename)
        df.insert(0, 'Date', date)
        df.to_csv('pysol/' + filename)

        data_py = pd.read_csv('pysol/' + filename)
        data_ex = pd.read_csv('exsol/UZ_extended_test_exsol_set' + str(e) + '.csv')
        A = np.zeros((43825, 11))
        for c in range(11):
            for r in range(1, 43825):
                A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c + 2]][r]
        for c in range(11):
            print('COL ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))
            # print(np.where(max(A[:,c]) != 0 and A[:,c] == max(A[:,c])), np.where(min(A[:,c]) != 0 and A[:,c] == min(A[:,c])))


    i_up = pd.read_csv(indir / 'i_up_uz.csv')
    gwl_all = pd.read_csv(indir / 'gwl.csv')

    # 2.1 Set 1: soil type = 3, crop type = 1
    print("1")
    e = 1
    i_up_uz = i_up['i_up_uz_'+str(e)]
    gwl = gwl_all['gwl_'+str(e)]
    validate(3, 1, 15, 1, 6855, 0)

    # 2.2 Set 2: soil type = 7, crop type = 1
    print("2")
    e = 2
    i_up_uz = i_up['i_up_uz_'+str(e)]
    gwl = gwl_all['gwl_'+str(e)]
    validate(7, 1, 15, 2, 6855, 0)

    # 2.3 Set 3: initial gwl = 3.0
    print("3")
    e = 3
    i_up_uz = i_up['i_up_uz_'+str(e)]
    gwl = gwl_all['gwl_'+str(e)]
    validate(2, 1, 26, 3, 6855, 0)

    # 2.4 Set 4: initial gwl = 0  # there is -0.00042564999999999964 difference in col 9
    # which comes from copy paste excel
    print("4")
    e = 4
    i_up_uz = i_up['i_up_uz_'+str(e)]
    gwl = gwl_all['gwl_'+str(e)]
    validate(2, 1, 0, 4, 6855, 0)

    # 2.5 Set 5: uz_no_meas_area = 0
    print("5")
    e = 5
    i_up_uz = i_up['i_up_uz_'+str(e)]
    gwl = gwl_all['gwl_'+str(e)]
    validate(2, 1, 15, 5, 0, 6855)

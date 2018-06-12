import numpy as np
import pandas as pd
from selector import et_selector, soil_selector
from gwlcalculator import gwlcal
import time
from pathlib import Path


class Groundwater:
    """
    creates an instance of groundwater class with given states and properties, iterates sol function at each time step.
    """
    def __init__(self, init_gwl_t0, gw_no_meas_area, gw_meas_area, seep_def=0, w=100, vc=20000, h_deepgw=21.5,
                 flux=1, soiltype=2, croptype=1):

        # state
        # prev_gwl --- groundwater level at previous time step [m-SL].
        # prev_gwl_sl --- groundwater level above surface level at previous time step [m-SL].

        self.prev_gwl = init_gwl_t0
        self.prev_gwl_sl = 0

        # properties
        # gw_no_meas_area --- groundwater area (without a measure) [m^2].
        # gw_meas_area --- groundwater area (with a measure) [m^2].
        # seep_def --- seepage defined by deep groundwater level and flow resistance [0=flux; 1=level].
        # w --- groundwater drainage resistance [d].
        # vc --- flow resistance between deep and shallow groundwater [d].
        # h_deepgw --- defined hydraulic head of deep groundwater [m-SL].
        # flux --- defined constant downward seepage flux [mm/d]
        # soiltype --- soil type
        # croptype --- crop type
        # soil_prm --- soil parameter database determined by soil type and crop type.

        self.gw_no_meas_area = gw_no_meas_area
        self.gw_meas_area = gw_meas_area
        self.seep_def = seep_def
        self.w = w
        self.vc = vc
        self.h_deepgw = h_deepgw
        self.flux = flux
        self.soiltype = soiltype
        self.croptype = croptype
        self.soil_prm = soil_selector(self.soiltype, self.croptype)

    def sol(self, p_uz_gw, uz_no_meas_area, p_op_gw, op_no_meas_area, tot_meas_area, meas_gw,
            prev_owl,  delta_t=1 / 24):

        # parameter
        # sum_p_gw --- Total percolation from unsaturated zone and from open paved area to groundwater
        # during the current time step [mm].
        # r_meas_gw --- Inflow from measure area (if applicable) during current time step [mm]
        # sc_gw --- Storage coefficient of the groundwater for the current time step [-].
        # h_gw --- Groundwater level at the end of the current time step [m-SL].
        # prev_owl --- Open water level at the previous time step [m-SL].
        # s_gw_out --- downward seepage flux to deep groundwater during current time step [mm].
        # d_gw_ow  --- Groundwater drainage to the open water for the current time step [mm].
        # gwl --- Groundwater level below surface level at the end of the current time step [m-SL].
        # gwl_sl --- Groundwater level above surface level at the end of the current time step [m-SL].

        if self.gw_no_meas_area == 0:
            sum_p_gw = r_meas_gw = gwl_up = gwl_low = sc_gw = h_gw = s_gw_out = d_gw_ow = gwl = gwl_sl = 0
        else:
            sum_p_gw = (p_uz_gw * uz_no_meas_area + p_op_gw * op_no_meas_area) / self.gw_no_meas_area

            r_meas_gw = meas_gw * tot_meas_area / self.gw_no_meas_area

            gwl_sol = gwlcal(self.prev_gwl)
            gwl_up = gwl_sol[0]
            gwl_low = gwl_sol[1]
            id1 = gwl_sol[2]
            id2 = gwl_sol[3]

            if self.prev_gwl < 10:
                sc_gw = self.soil_prm[id2]['stor_coef'] + \
                    (gwl_low - self.prev_gwl) / (gwl_low - gwl_up) * (
                        self.soil_prm[id1]['stor_coef'] -
                        self.soil_prm[id2]['stor_coef'])
            else:
                sc_gw = self.soil_prm[29]['stor_coef']

            if self.seep_def > 0.5:
                h_gw = -(((sum_p_gw + r_meas_gw) / 1000 * self.w * self.vc - self.h_deepgw * self.w - prev_owl *
                          self.vc) / (self.w + self.vc) + (-(self.prev_gwl + self.prev_gwl_sl) -
                         ((sum_p_gw + r_meas_gw) / 1000 * self.w * self.vc - self.h_deepgw * self.w - prev_owl *
                             self.vc) / (self.w + self.vc)) * np.exp(- delta_t * (self.w + self.vc) /
                                                                                 (sc_gw * self.w * self.vc)))

                s_gw_out = 1000 * (
                            self.h_deepgw - 0.5 * (h_gw + (self.prev_gwl + self.prev_gwl_sl))) / self.vc * delta_t

            else:
                h_gw = - (self.w * (((sum_p_gw + r_meas_gw) - self.flux) / 1000) - prev_owl + (
                        -(self.prev_gwl + self.prev_gwl_sl) - (
                            self.w * (((sum_p_gw + r_meas_gw) - self.flux) / 1000) - prev_owl)) * np.exp(
                    - delta_t / (sc_gw * self.w)))

                s_gw_out = delta_t * self.flux

            d_gw_ow = sum_p_gw + r_meas_gw - s_gw_out - sc_gw * (self.prev_gwl + self.prev_gwl_sl - h_gw) * 1000

            gwl = max(0, self.prev_gwl - (sum_p_gw + r_meas_gw - s_gw_out - d_gw_ow) / (1000 * sc_gw))

            gwl_sl = -1 * max(0, (0 - (self.prev_gwl - (sum_p_gw + r_meas_gw - s_gw_out - d_gw_ow) / (1000 * sc_gw)))
                              * sc_gw)

            # update state
            self.prev_gwl = gwl
            self.prev_gwl_sl = gwl_sl

        return sum_p_gw, r_meas_gw, gwl_up, gwl_low, sc_gw, h_gw, s_gw_out, d_gw_ow, gwl, gwl_sl


if __name__ == '__main__':
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
    # a. results of percolation from unsaturated zone and from open paved area to groundwater.
    p_uz_gw = pd.read_csv(indir / 'p_uz_gw.csv')['p_uz_gw_0']
    p_op_gw = pd.read_csv(indir / 'p_op_gw.csv')['p_op_gw_0']
    # b. results of open water level.
    owl = pd.read_csv(indir / 'owl.csv')['owl_0']
    # c. meas_gw -- flow from measure to groundwater
    meas_gw = np.zeros(iters)  # set as all zeros for the time being as there is no meas.

    # 1.2 General test settings
    # tot_pr_area --- total paved roof area.
    # pr_part_aboveGW --- part of buildings above Groundwater.
    # tot_cp_area --- total closed paved area.
    # tot_op_area --- total open paved area.
    # tot_up_area --- total unpaved area.
    # tot_uz_area --- total unsaturated zone area.
    # tot_ow_area --- total open water area.
    # ow_part_aboveGW --- part of open water above Groundwater.
    # tot_gw_area  --- total groundwater area.
    # tot_meas_area --- total measure area.
    tot_pr_area = 1560
    pr_part_aboveGW = 0.0
    tot_cp_area = 803.3906406
    tot_op_area = 481.6093594
    op_meas_area = 0
    op_no_meas_area =  tot_op_area - op_meas_area
    tot_up_area = 6855
    tot_uz_area = tot_up_area
    uz_meas_area = 0
    uz_no_meas_area = tot_uz_area - uz_meas_area
    tot_ow_area = 300
    ow_part_aboveGW = 0.0
    tot_gw_area = tot_pr_area * pr_part_aboveGW + tot_cp_area + tot_op_area + tot_up_area + tot_ow_area * ow_part_aboveGW
    gw_meas_area = 0
    gw_no_meas_area = tot_gw_area - gw_meas_area
    tot_meas_area = 0

    # 1.4 Get python solutions and save in csv file.
    start = time.time()
    Sum_p_gw = [0]
    R_meas_gw = [0]
    Gwl_up = [0]
    Gwl_low = [0]
    init_gwl_t0 = 1.5
    Sc_gw = [soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['stor_coef']]
    H_gw = [0]
    S_gw_out = [0]
    D_gw_ow = [0]
    Gwl = [init_gwl_t0]
    Gwl_sl = [0]

    # Specify the parameter or use the default setting.
    m = Groundwater(init_gwl_t0, gw_no_meas_area, gw_meas_area, seep_def=0, w=100, vc=20000, h_deepgw=21.5,
                    flux=1, soiltype=2, croptype=1)
    t = 1

    while t <= iters - 1:

        sol = m.sol(p_uz_gw[t], uz_no_meas_area, p_op_gw[t], op_no_meas_area, tot_meas_area, meas_gw=meas_gw[t],
                    prev_owl=owl[t-1], delta_t=1 / 24)

        Sum_p_gw.append(sol[0])
        R_meas_gw.append(sol[1])
        Gwl_up.append(sol[2])
        Gwl_low.append(sol[3])
        Sc_gw.append(sol[4])
        H_gw.append(sol[5])
        S_gw_out.append(sol[6])
        D_gw_ow.append(sol[7])
        Gwl.append(sol[8])
        Gwl_sl.append(sol[9])
        # print('time step', t)
        t += 1

    filename = 'GW_general_test_pysol.csv'
    np.savetxt('pysol/' + filename, np.c_[Sum_p_gw, R_meas_gw, Sc_gw, H_gw, S_gw_out, D_gw_ow, Gwl, Gwl_sl],
               fmt="%.8f", delimiter=',',
               header='Sum_p_gw, R_meas_gw, Sc_gw, H_gw, S_gw_out, D_gw_ow, Gwl, Gwl_sl')
    # Insert the Date column for locating purposes.
    df = pd.read_csv('pysol/' + filename)
    df.insert(0, 'Date', date)
    df.to_csv('pysol/' + filename)
    end = time.time()
    print(end - start)

    # 1.5 Validate with excel solutions.
    data_py = pd.read_csv('pysol/' + filename)
    data_ex = pd.read_csv('exsol/GW_general_test_exsol.csv')
    A = np.zeros((43825, 8))
    for c in range(8):
        for r in range(1, 43825):  # from row 1 to the last row (row 43824), excluding first row(t=0).
            A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c+2]][r]
    for c in range(8):
        print('col ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))

    # 2. EXTENDED TESTS
    # 2.0 Validate function. Built for easily manipulating comparisons between python and excel solutions.


    def validate(a, b, c, d, e, f, g, h, i, A1, A2):
        # a --- seep_def
        # b --- w
        # c --- vc
        # d --- h_deepgw
        # e --- flux
        # f --- soiltype
        # g --- croptype
        # h --- init GWL index
        # i --- Set No., used to name the output file.

        Sum_p_gw = [0]
        R_meas_gw = [0]
        Gwl_up = [0]
        Gwl_low = [0]
        init_gwl_t0 = h
        Sc_gw = [soil_selector(f, g)[gwlcal(h)[2]]['stor_coef']]
        H_gw = [0]
        S_gw_out = [0]
        D_gw_ow = [0]
        Gwl = [init_gwl_t0]
        Gwl_sl = [0]

        m = Groundwater(init_gwl_t0=h, gw_no_meas_area=A1, gw_meas_area=A2, seep_def=a, w=b, vc=c, h_deepgw=d,
                        flux=e, soiltype=f, croptype=g)

        t = 1

        while t <= iters - 1:
            sol = m.sol(p_uz_gw[t], uz_no_meas_area, p_op_gw[t], op_no_meas_area, tot_meas_area, meas_gw=meas_gw[t],
                        prev_owl=owl[t - 1], delta_t=1 / 24)

            Sum_p_gw.append(sol[0])
            R_meas_gw.append(sol[1])
            Gwl_up.append(sol[2])
            Gwl_low.append(sol[3])
            Sc_gw.append(sol[4])
            H_gw.append(sol[5])
            S_gw_out.append(sol[6])
            D_gw_ow.append(sol[7])
            Gwl.append(sol[8])
            Gwl_sl.append(sol[9])
            #print('time step', t)
            t += 1

        filename = 'GW_extended_test_pysol' + str(i) + '.csv'
        np.savetxt('pysol/' + filename, np.c_[Sum_p_gw, R_meas_gw, Sc_gw, H_gw, S_gw_out, D_gw_ow, Gwl, Gwl_sl],
                   fmt="%.8f", delimiter=',',
                   header='Sum_p_gw, R_meas_gw, Sc_gw, H_gw, S_gw_out, D_gw_ow, Gwl, Gwl_sl')
        # Insert the Date column for locating purposes.
        df = pd.read_csv('pysol/' + filename)
        df.insert(0, 'Date', date)
        df.to_csv('pysol/' + filename)

        data_py = pd.read_csv('pysol/' + filename)
        data_ex = pd.read_csv('exsol/GW_extended_test_exsol_set' + str(i) + '.csv')
        A = np.zeros((43825, 8))
        for c in range(8):
            for r in range(1, 43825):
                A[r, c] = data_ex[list(data_ex)[c]][r] - data_py[list(data_py)[c + 2]][r]
        for c in range(8):
            print('COL ' + str(c), 'max', max(A[:, c]), 'min', min(A[:, c]))
            # print(np.where(max(A[:, c]) != 0 and A[:, c] == max(A[:, c])),
            # np.where(min(A[:, c]) != 0 and A[:, c] == min(A[:, c])))


    P_uz_gw = pd.read_csv(indir / 'p_uz_gw.csv')
    P_op_gw = pd.read_csv(indir / 'p_op_gw.csv')
    Owl = pd.read_csv(indir / 'owl.csv')

    #  2.1 Set 1: soil type  = 3, crop type = 1
    print('1')
    i = 1
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(0, 100, 20000, 21.5, 1, 3, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.2 Set 2: soil type = 7, crop type = 1
    print('2')
    i = 2
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(0, 100, 20000, 21.5, 1, 7, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.3 Set 3: seep_def = 1
    print('3')
    i = 3
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(1, 100, 20000, 21.5, 1, 2, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.4 Set 4: w = 10000. More modifications on digits
    print('4')
    i = 4
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(0, 10000, 20000, 21.5, 1, 2, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.5 Set 5: w = 0.1  (w cannot be 0, otherwise #div 0 error.
    # And be aware of the digits of owl input, as it influence the final results)
    i = 5
    print(str(i))
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(0, 0.1, 20000, 21.5, 1, 2, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.6 Set 6: vc = 2000000
    i = 6
    print(str(i))
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(0, 100, 2000000, 21.5, 1, 2, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.7 Set 7: vc = 0
    i = 7
    print(str(i))
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(0, 100, 0, 21.5, 1, 2, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.8 Set 8: h_deepgw = 215, seep_def = 1
    i = 8
    print(str(i))
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(1, 100, 20000, 215, 1, 2, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.9 Set 9: h_deepgw = 0, seep_def = 1
    i = 9
    print(str(i))
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(1, 100, 20000, 0, 1, 2, 1, 1.5, i, gw_no_meas_area, gw_meas_area)

    # 2.10 Set 10: gw_no_meas_area = 0
    i = 10
    print(str(i))
    p_uz_gw = P_uz_gw['p_uz_gw_'+str(i)]
    p_op_gw = P_op_gw['p_op_gw_'+str(i)]
    owl = Owl['owl_'+str(i)]
    validate(0, 100, 20000, 21.5, 1, 2, 1, 1.5, i, 0, gw_meas_area)

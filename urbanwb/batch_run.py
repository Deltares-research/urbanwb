from pathlib import Path
import pandas as pd
import numpy as np
import urbanwb
from urbanwb.read_parameter_no_section import read_parameter
from urbanwb.gwlcalculator import gwlcal
from urbanwb.selector import soil_selector
from urbanwb.main import Model


def batch_run(Q):
    # Load csv file
    path = urbanwb.urbanwbdir / ".." / "input"
    InputData = pd.read_csv(path / 'input_csv.csv')  # input the precipitation, potential evaporation
    date = InputData['date']
    P_atm = InputData['P_atm']
    Ref_grass = InputData['Ref.grass']
    E_pot_OW = InputData['E_pot_OW']
    iters = np.shape(date)[0]
    # read toml
    para = read_parameter()
    # general parameters
    delta_t = para['delta_t']
    total_area = para['tot_area']
    soiltype, croptype = para['soiltype'], para['croptype']
    # paved roof
    tot_pr_area, pr_meas_area = para['tot_pr_area'], 0
    pr_no_meas_area, pr_meas_inflow_area, init_intstor_pr_t0 = tot_pr_area - pr_meas_area, 0, 0
    # closed paved
    tot_cp_area, cp_meas_area = para['tot_cp_area'], 0
    cp_no_meas_area, cp_meas_inflow_area, init_intstor_cp_t0 = tot_cp_area - cp_meas_area, 0, 0
    # open paved
    tot_op_area, op_meas_area = para['tot_op_area'], 0
    op_no_meas_area, op_meas_inflow_area, init_intstor_op_t0 = tot_op_area - op_meas_area, 0, 0
    # unpaved
    tot_up_area, up_meas_area = para['tot_up_area'], 0
    up_no_meas_area, up_meas_inflow_area, fin_stor_up_t0 = tot_up_area - up_meas_area, 0, 0
    # openwater
    tot_ow_area, ow_meas_area = para['tot_ow_area'], 0
    ow_no_meas_area, ow_level = tot_ow_area - ow_meas_area, para['ow_level']
    # unsaturated zone
    init_gwl_t0 = 1.5
    theta_uz_t0 = soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['moist_cont_eq_rz[mm]']
    tot_uz_area, uz_meas_area = para['tot_uz_area'], 0
    uz_no_meas_area = tot_uz_area - uz_meas_area
    # groundwater
    tot_gw_area, gw_meas_area = para['tot_gw_area'], 0
    gw_no_meas_area = tot_gw_area - gw_meas_area
    # swds
    tot_swds_area, swds_meas_area, tot_mss_area, mss_meas_area = para['tot_swds_area'], 0, para['tot_mss_area'], 0
    swds_no_meas_area, mss_no_meas_area = tot_swds_area - swds_meas_area, tot_mss_area - mss_meas_area
    prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0, prev_so_mss_t0 = 0, 0, 0, 0
    # measure inflow:
    tot_meas_area = 0
    meas_uz, meas_gw, meas_swds, meas_mss = np.zeros(iters), np.zeros(iters), np.zeros(iters), np.zeros(iters)
    meas_ow = np.zeros(iters)
    owl_database = []
    for q in Q:
        q_ow_out_cap = q * 8.64
        lst = [{'int_pr': 0, 'e_atm_pr': 0, 'intstor_pr': init_intstor_pr_t0, 'r_pr_meas': 0, 'r_pr_swds': 0,
                'r_pr_mss': 0, 'r_pr_up': 0,

                'int_cp': 0, 'e_atm_cp': 0, 'intstor_cp': init_intstor_cp_t0, 'r_cp_meas': 0, 'r_cp_swds': 0,
                'r_cp_mss': 0, 'r_cp_up': 0,

                'int_op': 0, 'e_atm_op': 0, 'intstor_op': init_intstor_op_t0, 'p_op_gw': 0, 'r_op_meas': 0,
                'r_op_swds': 00, 'r_op_mss': 0.0, 'r_op_up': 0.0,
                'sum_r_up': 0, 'init_stor_up': 0, 'act_infilcap_up': 0,
                'tfac_up': 0, 'e_atm_up': 0, 'i_up_uz': 0, 'fin_stor_up': fin_stor_up_t0,
                'r_up_meas': 0, 'r_up_ow': 0,
                # theta_uz_t0 could be written as soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['moist_cont_eq_rz[mm]']
                'sum_i_uz': 0, 'r_meas_uz': 0, 'theta_h3_uz': 0, 't_alpha_uz': 0,
                't_atm_uz': 0, 'gwl_up': 0, 'gwl_low': 0, 'theta_eq_uz': 0,
                'capris_max_uz': 0, 'p_uz_gw': 0, 'theta_uz': theta_uz_t0,

                'sum_p_gw': 0, 'r_meas_gw': 0, 'gwl_up_1': 0, 'gwl_low_1': 0,
                'sc_gw': soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['stor_coef'],
                'h_gw': 0, 's_gw_out': 0, 'd_gw_ow': 0, 'gwl': init_gwl_t0, 'gwl_sl': 0,

                'sum_r_swds': 0, 'r_meas_swds': 0, 'sum_r_mss': 0, 'r_meas_mss': 0,
                'q_swds_ow': 0, 'q_mss_out': 0, 'q_mss_ow': 0, 'so_swds': prev_so_swds_t0,
                'so_mss': prev_so_mss_t0, 'stor_swds': prev_stor_swds_t0, 'stor_mss': prev_stor_mss_t0,

                'prec_ow': P_atm[0], 'e_atm_ow': E_pot_OW[0], 'sum_r_ow': 0, 'sum_d_ow': 0,
                'sum_q_ow': 0, 'sum_so_ow': 0, 'r_meas_ow': 0, 'q_ow_out': 0, 'owl': ow_level
                }]
        k = Model
        t = 1
        while t <= iters - 1:
            lst.append(k.__next__(P_atm[t], E_pot_OW[t], Ref_grass[t], lst[t - 1], meas_uz[t], meas_gw[t], meas_swds[t], meas_mss[t], meas_ow[t]))
            if t % 200 == 0:
                print(f'timestep {t} / {iters}')
            t += 1
        df = pd.DataFrame(lst)
        df.insert(0, 'Date', date)
        owl_database.append(df['owl'])
    return owl_database



if __name__ == '__main__':
    # batch_run([3, 4, 5, 6])
    print(batch_run([3, 4, 5, 6]))



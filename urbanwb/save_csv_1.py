#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from urbanwb.pavedroof import PavedRoof
from urbanwb.closedpaved import ClosedPaved
from urbanwb.openpaved import OpenPaved
from urbanwb.unpaved import Unpaved
from urbanwb.groundwater import Groundwater
from urbanwb.unsaturatedzone import UnsaturatedZone
from urbanwb.sewersystem import SewerSystem
from urbanwb.openwater import OpenWater
from urbanwb.selector import soil_selector
from urbanwb.gwlcalculator import gwlcal
import time
from pathlib import Path

start = time.time()
# Load csv file

indir = Path('input')
outdir = Path('pysol')
outdir.mkdir(parents=True, exist_ok=True)

InputData = pd.read_csv(indir / 'input_csv.csv')  # input the precipitation, potential evaporation

date = InputData['date']
P_atm = InputData['P_atm']
Ref_grass = InputData['Ref.grass']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]

filename = 'save_csv_1.csv'  # name the output file

# Parameter settings.
delta_t = 1/24
# paved roof
pr_no_meas_area = 1560
pr_meas_area = 0
pr_meas_inflow_area = 0
init_intstor_pr_t0 = 0
# closed paved
cp_no_meas_area = 803.39064064
cp_meas_area = 0
cp_meas_inflow_area = 0
init_intstor_cp_t0 = 0
# open paved
op_no_meas_area = 481.60935936000004
op_meas_area = 0
op_meas_inflow_area = 0
init_intstor_op_t0 = 0
# unpaved
up_no_meas_area = 6855
up_meas_area = 0
up_meas_inflow_area = 0
fin_stor_up_t0 = 0
ow_no_meas_area = 300
# unsaturated zone
init_gwl_t0 = 1.5
theta_uz_t0 = soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['moist_cont_eq_rz[mm]']
uz_no_meas_area = 6855
uz_meas_area = 0
# groundwater
gw_no_meas_area = 8140
gw_meas_area = 0
# swds
swds_no_meas_area = 2845
mss_no_meas_area = 0
prev_stor_swds_t0 = 0
prev_so_swds_t0 = 0
prev_stor_mss_t0 = 0
prev_so_mss_t0 = 0
ow_level = 1.5
# measure inflow:
total_area = 10000
tot_meas_area = total_meas_area = 0  # reduplicated.
meas_uz = np.zeros(iters)
meas_gw = np.zeros(iters)
meas_swds = np.zeros(iters)
meas_mss = np.zeros(iters)
meas_ow = np.zeros(iters)


class Model(object):
    def __init__(self):
        self.pavedroof = PavedRoof(init_intstor_pr_t0, pr_no_meas_area, pr_meas_area, pr_meas_inflow_area,
                                   intstorcap_pr=1.6, stormfrac_pr=1.0, discfrac_pr=0.0)
        self.closedpaved = ClosedPaved(init_intstor_cp_t0, cp_no_meas_area, cp_meas_area, cp_meas_inflow_area,
                                       intstorcap_cp=1.6, stormfrac_cp=1.0, discfrac_cp=0.0)
        self.openpaved = OpenPaved(init_intstor_op_t0, op_no_meas_area, op_meas_area, op_meas_inflow_area,
                                   intstorcap_op=1.6, stormfrac_op=1.0, discfrac_op=0.0, infilcap_op=1.0)

        self.unpaved = Unpaved(fin_stor_up_t0, up_no_meas_area, up_meas_area, up_meas_inflow_area, infilcap_up=48,
                               intstorcap_up=20, soiltype=2, croptype=1)
        self.unsaturatedzone = UnsaturatedZone(theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=2, croptype=1)

        self.groundwater = Groundwater(init_gwl_t0, gw_no_meas_area, gw_meas_area, seep_def=0, w=100, vc=20000,
                                       h_deepgw=21.5, flux=1, soiltype=2, croptype=1)

        self.sewersystem = SewerSystem(swds_no_meas_area, mss_no_meas_area, prev_stor_swds_t0, prev_so_swds_t0,
                                       prev_stor_mss_t0, prev_so_mss_t0, q_swds_ow_cap=55.1, q_mss_out_cap=26.3,
                                       q_mss_ow_cap=48.1, stor_swds_cap=2, stor_mss_cap=9)

        self.openwater = OpenWater(ow_no_meas_area, ow_level, q_ow_out_cap=200)

    def __iter__(self):
        return self

    def __next__(self, p_atm, e_pot_ow, ref_grass, prev_lst, meas_uz, meas_gw, meas_swds, meas_mss, meas_ow):
        try:
            # empty dictionary
            a = self.pavedroof.sol(p_atm, e_pot_ow)
            b = self.closedpaved.sol(p_atm, e_pot_ow)
            c = self.openpaved.sol(p_atm, e_pot_ow, delta_t=1/24)
            d1 = self.unpaved.sol(p_atm, e_pot_ow, a['r_pr_up'],
                                  b['r_cp_up'], c['r_op_up'],
                                  prev_lst['theta_uz'],
                                  pr_no_meas_area, cp_no_meas_area,
                                  op_no_meas_area, ow_no_meas_area, delta_t=1/24)
            e = self.unsaturatedzone.sol(d1['i_up_uz'], meas_uz, tot_meas_area,
                                         ref_grass, prev_lst['gwl'],
                                         delta_t=1/24)
            f = self.groundwater.sol(e['p_uz_gw'], uz_no_meas_area,
                                     c['p_op_gw'], op_no_meas_area, tot_meas_area,
                                     meas_gw, prev_lst['owl'],  delta_t=1 / 24)  # prev_lst['owl']
            g = self.sewersystem.sol(pr_no_meas_area, cp_no_meas_area, op_no_meas_area,
                                     a['r_pr_swds'], b['r_cp_swds'],
                                     c['r_op_swds'], a['r_pr_mss'],
                                     b['r_cp_mss'], c['r_op_mss'],
                                     meas_swds, meas_mss, ow_no_meas_area, tot_meas_area)
            h = self.openwater.sol(p_atm, e_pot_ow, d1['r_up_ow'], f['d_gw_ow'],
                                   g['q_swds_ow'], g['q_mss_ow'],
                                   g['so_swds_ow'], g['so_mss_ow'],
                                   meas_ow, up_no_meas_area, gw_no_meas_area, swds_no_meas_area,
                                   mss_no_meas_area, tot_meas_area, total_area, delta_t=1/24)
            dictmerged = dict(a, **b, **c, **d1, **e, **f, **g, **h)

        except IndexError:
            raise StopIteration
        return dictmerged


def run():
    start = time.time()

    lst2 = [{'int_pr': 0, 'e_atm_pr': 0, 'intstor_pr': init_intstor_pr_t0, 'r_pr_meas': 0, 'r_pr_swds': 0,
             'r_pr_mss': 0, 'r_pr_up': 0,

             'int_cp': 0, 'e_atm_cp': 0, 'intstor_cp': init_intstor_cp_t0, 'r_cp_meas': 0, 'r_cp_swds': 0,
             'r_cp_mss': 0, 'r_cp_up': 0,

             'int_op': 0, 'e_atm_op': 0, 'intstor_op': init_intstor_op_t0, 'p_op_gw': 0, 'r_op_meas': 0,
             'r_op_swds': 00, 'r_op_mss': 0.0, 'r_op_up': 0.0,
             'sum_r_up': 0, 'init_stor_up': 0, 'act_infilcap_up': 0,
             'tfac_up': 0, 'e_atm_up': 0, 'i_up_uz': 0, 'fin_stor_up': fin_stor_up_t0,
             'r_up_meas': 0, 'r_up_ow': 0,

             'sum_i_up_uz': 0, 'r_meas_uz': 0, 'theta_h3_uz': 0, 't_alpha_uz': 0,
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

    k = Model()

    t = 1
    while t <= iters - 1:

        lst2.append(k.__next__(P_atm[t], E_pot_OW[t], Ref_grass[t], lst2[t - 1], meas_uz[t], meas_gw[t], meas_swds[t],
                               meas_mss[t], meas_ow[t]))
        if t % 200 == 0:
            print(f'timestep {t} / {iters}')
        t += 1

    # print(lst[3]['paved_roof']['e_atm_pr'])
    # print(lst[4]['closed_paved']['intstor_cp'])
    # print(lst[100])

    df = pd.DataFrame(lst2)
    df.insert(0, 'Date', date)
    df.to_csv(outdir / filename, index=True)
    end = time.time()
    print(f'Model runtime: {end - start:.1f}s')


run()

if __name__ == '__main__':
    # filename = '.csv'
    # run()

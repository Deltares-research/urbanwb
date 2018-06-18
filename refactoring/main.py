#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pavedroof import PavedRoof
from closedpaved import ClosedPaved
from openpaved import OpenPaved
from unpaved import Unpaved
from groundwater import Groundwater
from unsaturatedzone import UnsaturatedZone
from sewersystem import SewerSystem
from openwater import OpenWater
from gwlcalculator import gwlcal
from selector import soil_selector

import time
from pathlib import Path

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

filename = 'test.csv'  # name the output file

# Parameter settings.
delta_t = 1/24
pr_no_meas_area = 1560
pr_meas_area = 0
pr_meas_inflow_area = 0
init_intstor_pr_t0 = 0

cp_no_meas_area = 803.39064064
cp_meas_area = 0
cp_meas_inflow_area = 0
init_intstor_cp_t0 = 0

op_no_meas_area = 481.60935936000004
op_meas_area = 0
op_meas_inflow_area = 0
init_intstor_op_t0 = 0

up_no_meas_area = 6855
up_meas_area = 0
up_meas_inflow_area = 0
fin_stor_up_t0 = 0
ow_no_meas_area = 300

init_gwl_t0 = 1.5
theta_uz_t0 = soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['moist_cont_eq_rz[mm]']
uz_no_meas_area = 6855
uz_meas_area = 0

gw_no_meas_area = 8140
gw_meas_area = 0

swds_no_meas_area = 2845
mss_no_meas_area = 0
prev_stor_swds_t0 = 0
prev_so_swds_t0 = 0
prev_stor_mss_t0 = 0
prev_so_mss_t0 = 0
ow_level = 1.5


total_area = 10000
tot_meas_area = 0
meas_uz = np.zeros(iters)
meas_gw = np.zeros(iters)
meas_swds = np.zeros(iters)
meas_mss = np.zeros(iters)
meas_ow = np.zeros(iters)


class Model:
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
            d = dict()
            d['paved_roof'] = self.pavedroof.sol(p_atm, e_pot_ow)
            d['closed_paved'] = self.closedpaved.sol(p_atm, e_pot_ow)
            d['open_paved'] = self.openpaved.sol(p_atm, e_pot_ow, delta_t=1/24)
            d['unpaved'] = self.unpaved.sol(p_atm, e_pot_ow, d['paved_roof']['r_pr_up'],
                                            d['closed_paved']['r_cp_up'], d['open_paved']['r_op_up'],
                                            prev_lst['unsaturatedzone']['theta_uz'],
                                            pr_no_meas_area, cp_no_meas_area,
                                            op_no_meas_area, ow_no_meas_area, delta_t=1/24)
            d['unsaturatedzone'] = self.unsaturatedzone.sol(d['unpaved']['i_up_uz'], meas_uz, tot_meas_area,
                                                            ref_grass, prev_lst['groundwater']['gwl'],
                                                            delta_t=1/24)
            d['groundwater'] = self.groundwater.sol(d['unsaturatedzone']['p_uz_gw'], uz_no_meas_area,
                                                    d['open_paved']['p_op_gw'], op_no_meas_area, tot_meas_area,
                                                    meas_gw, prev_lst['openwater']['owl'],  delta_t=1 / 24)
            d['sewersystem'] = self.sewersystem.sol(pr_no_meas_area, cp_no_meas_area, op_no_meas_area,
                                                    d['paved_roof']['r_pr_swds'], d['closed_paved']['r_cp_swds'],
                                                    d['open_paved']['r_op_swds'], d['paved_roof']['r_pr_mss'],
                                                    d['closed_paved']['r_cp_mss'], d['open_paved']['r_op_mss'],
                                                    meas_swds, meas_mss, ow_no_meas_area, tot_meas_area)

            d['openwater'] = self.openwater.sol(p_atm, e_pot_ow, d['unpaved']['r_up_ow'], d['groundwater']['d_gw_ow'],
                                                d['sewersystem']['q_swds_ow'], d['sewersystem']['q_mss_ow'],
                                                d['sewersystem']['so_swds_ow'],
                                                d['sewersystem']['so_mss_ow'], meas_ow,
                                                up_no_meas_area, gw_no_meas_area, swds_no_meas_area, mss_no_meas_area,
                                                tot_meas_area, total_area, delta_t=1/24)

        except IndexError:
            raise StopIteration
        return d


def run():
    start = time.time()

    lst = [{'paved_roof': {'int_pr': 0, 'e_atm_pr': 0, 'intstor_pr': 0, 'r_pr_meas': 0, 'r_pr_swds': 0, 'r_pr_mss': 0, 'r_pr_up': 0},
            'closed_paved': {'int_cp': 0, 'e_atm_cp': 0, 'intstor_cp': 0, 'r_cp_meas': 0, 'r_cp_swds': 0, 'r_cp_mss': 0, 'r_cp_up': 0},
            'open_paved': {'int_op': 0, 'e_atm_op': 0, 'intstor_op': 0, 'p_op_gw': 0, 'r_op_meas': 0, 'r_op_swds': 00, 'r_op_mss': 0.0, 'r_op_up': 0.0},
            'unpaved': {'sum_r_up': 0, 'init_stor_up': 0, 'act_infilcap_up': 0,
                        'tfac_up': 0, 'e_atm_up': 0, 'i_up_uz': 0, 'fin_stor_up': 0,
                        'r_up_meas': 0, 'r_up_ow': 0},
            'unsaturatedzone': {'i_up_uz': 0, 'r_meas_uz': 0, 'theta_h3_uz': 0, 't_alpha_uz': 0,
                                't_atm_uz': 0, 'gwl_up': 0, 'gwl_low': 0, 'theta_eq_uz': 0,
                                'capris_max_uz': 0, 'p_uz_gw': 0, 'theta_uz': 194.1},
            'groundwater': {'sum_p_gw': 0, 'r_meas_gw': 0, 'gwl_up': 0, 'gwl_low': 0, 'sc_gw': soil_selector(2, 1)[gwlcal(1.5)[2]]['stor_coef'],
                            'h_gw': 0, 's_gw_out': 0, 'd_gw_ow': 0, 'gwl': 1.5, 'gwl_sl': 0},

            'sewersystem': {'sum_r_swds': 0, 'r_meas_swds': 0, 'sum_r_mss': 0, 'r_meas_mss': 0,
                            'q_swds_ow': 0, 'q_mss_out': 0, 'q_mss_ow': 0, 'so_swds': 0,
                            'so_mss': 0, 'stor_swds': 0, 'stor_mss': 0},

            'openwater': {'prec_ow': P_atm[0], 'e_atm_ow': E_pot_OW[0], 'sum_r_ow': 0, 'sum_d_ow': 0,
                          'sum_q_ow': 0, 'sum_so_ow': 0, 'r_meas_ow': 0, 'q_ow_out': 0, 'owl': 1.5}
            }]
    k = Model()

    t = 1
    while t <= iters - 1:

        lst.append(k.__next__(P_atm[t], E_pot_OW[t], Ref_grass[t], lst[t-1], meas_uz[t], meas_gw[t], meas_swds[t],
                              meas_mss[t], meas_ow[t]))
        if t % 200 == 0:
            print(f'timestep {t} / {iters}')
        t += 1

    # print(lst[3]['paved_roof']['e_atm_pr'])
    # print(lst[4]['closed_paved']['intstor_cp'])
    # print(lst[100])

    df = pd.DataFrame(lst)
    df.insert(0, 'Date', date)
    df.to_csv(outdir/ 'list.csv', index=True)
    end = time.time()
    print(f'Model runtime: {end - start:.1f}s')

    a = 0
    for i in range(iters):
        a += lst[i]['unsaturatedzone']['capris_max_uz']

    print(a)


run()
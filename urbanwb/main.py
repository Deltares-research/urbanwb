#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import time
import urbanwb
from pathlib import Path
from collections import OrderedDict
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
from urbanwb.read_parameter_no_section import read_parameter
<<<<<<< HEAD
import matplotlib.pyplot as plt


class Model(object):
    def __init__(self, q_ow_out_cap):
        self.pavedroof = PavedRoof(init_intstor_pr_t0, pr_no_meas_area, pr_meas_area, pr_meas_inflow_area,
                                   intstorcap_pr=para['intstorcap_pr'], stormfrac_pr=para['swds_frac'],
                                   discfrac_pr=para['discfrac_pr'])
        self.closedpaved = ClosedPaved(init_intstor_cp_t0, cp_no_meas_area, cp_meas_area, cp_meas_inflow_area,
                                       intstorcap_cp=para['intstorcap_cp'], stormfrac_cp=para['swds_frac'],
                                       discfrac_cp=para['discfrac_cp'])
        self.openpaved = OpenPaved(init_intstor_op_t0, op_no_meas_area, op_meas_area, op_meas_inflow_area,
                                   intstorcap_op=para['intstorcap_op'], stormfrac_op=para['swds_frac'],
                                   discfrac_op=para['discfrac_op'], infilcap_op=para['infilcap_op'])
        self.unpaved = Unpaved(fin_stor_up_t0, up_no_meas_area, up_meas_area, up_meas_inflow_area,
                               infilcap_up=para['infilcap_up'], intstorcap_up=para['intstorcap_up'],
                               soiltype=soiltype, croptype=croptype)
        self.unsaturatedzone = UnsaturatedZone(theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=soiltype,
                                               croptype=croptype)
        self.groundwater = Groundwater(init_gwl_t0, gw_no_meas_area, gw_meas_area, seep_def=para['seep_def'],
                                       w=para['w'], vc=para['vc'], h_deepgw=para['h_deepgw'], flux=para['flux'],
                                       soiltype=soiltype, croptype=croptype)
        self.sewersystem = SewerSystem(swds_no_meas_area, mss_no_meas_area, prev_stor_swds_t0, prev_so_swds_t0,
                                       prev_stor_mss_t0, prev_so_mss_t0, q_swds_ow_cap=para['q_swds_ow_cap'],
                                       q_mss_out_cap=para['q_mss_out_cap'], q_mss_ow_cap=para['q_mss_ow_cap'],
                                       stor_swds_cap=para['storcap_swds'], stor_mss_cap=para['storcap_mss'])
        self.openwater = OpenWater(ow_no_meas_area, para['ow_level'], q_ow_out_cap=q_ow_out_cap)  # 8.64*para['pump_cap']
        # batch run (different pump capacity i.e. different q_ow_out_cap)
=======

# Load csv file
indir = Path("input")
outdir = Path("pysol")
outdir.mkdir(parents=True, exist_ok=True)
InputData = pd.read_csv(
    indir / "input_csv.csv"
)  # input the precipitation, potential evaporation
date = InputData["date"]
P_atm = InputData["P_atm"]
Ref_grass = InputData["Ref.grass"]
E_pot_OW = InputData["E_pot_OW"]
iters = np.shape(date)[0]

# Parameter settings.
para = read_parameter("input/static_form.ini")
# general parameters
delta_t = para["delta_t"]
total_area = para["tot_area"]
soiltype, croptype = para["soiltype"], para["croptype"]
# paved roof
tot_pr_area, pr_meas_area = para["tot_pr_area"], 0
pr_no_meas_area, pr_meas_inflow_area, init_intstor_pr_t0 = (
    tot_pr_area - pr_meas_area,
    0,
    0,
)
# closed paved
tot_cp_area, cp_meas_area = para["tot_cp_area"], 0
cp_no_meas_area, cp_meas_inflow_area, init_intstor_cp_t0 = (
    tot_cp_area - cp_meas_area,
    0,
    0,
)
# open paved
tot_op_area, op_meas_area = para["tot_op_area"], 0
op_no_meas_area, op_meas_inflow_area, init_intstor_op_t0 = (
    tot_op_area - op_meas_area,
    0,
    0,
)
# unpaved
tot_up_area, up_meas_area = para["tot_up_area"], 0
up_no_meas_area, up_meas_inflow_area, fin_stor_up_t0 = tot_up_area - up_meas_area, 0, 0
# openwater
tot_ow_area, ow_meas_area = para["tot_ow_area"], 0
ow_no_meas_area, ow_level = tot_ow_area - ow_meas_area, para["ow_level"]
# unsaturated zone
init_gwl_t0 = 1.5
theta_uz_t0 = soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]["moist_cont_eq_rz[mm]"]
tot_uz_area, uz_meas_area = para["tot_uz_area"], 0
uz_no_meas_area = tot_uz_area - uz_meas_area
# groundwater
tot_gw_area, gw_meas_area = para["tot_gw_area"], 0
gw_no_meas_area = tot_gw_area - gw_meas_area
# swds
tot_swds_area, swds_meas_area, tot_mss_area, mss_meas_area = (
    para["tot_swds_area"],
    0,
    para["tot_mss_area"],
    0,
)
swds_no_meas_area, mss_no_meas_area = (
    tot_swds_area - swds_meas_area,
    tot_mss_area - mss_meas_area,
)
prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0, prev_so_mss_t0 = 0, 0, 0, 0

# measure inflow:
tot_meas_area = 0
meas_uz, meas_gw, meas_swds, meas_mss, meas_ow = (
    np.zeros(iters),
    np.zeros(iters),
    np.zeros(iters),
    np.zeros(iters),
    np.zeros(iters),
)


class Model(object):
    def __init__(self):
        self.pavedroof = PavedRoof(
            init_intstor_pr_t0,
            pr_no_meas_area,
            pr_meas_area,
            pr_meas_inflow_area,
            intstorcap_pr=para["intstorcap_pr"],
            stormfrac_pr=para["swds_frac"],
            discfrac_pr=para["discfrac_pr"],
        )
        self.closedpaved = ClosedPaved(
            init_intstor_cp_t0,
            cp_no_meas_area,
            cp_meas_area,
            cp_meas_inflow_area,
            intstorcap_cp=para["intstorcap_cp"],
            stormfrac_cp=para["swds_frac"],
            discfrac_cp=para["discfrac_cp"],
        )
        self.openpaved = OpenPaved(
            init_intstor_op_t0,
            op_no_meas_area,
            op_meas_area,
            op_meas_inflow_area,
            intstorcap_op=para["intstorcap_op"],
            stormfrac_op=para["swds_frac"],
            discfrac_op=para["discfrac_op"],
            infilcap_op=para["infilcap_op"],
        )
        self.unpaved = Unpaved(
            fin_stor_up_t0,
            up_no_meas_area,
            up_meas_area,
            up_meas_inflow_area,
            infilcap_up=para["infilcap_up"],
            intstorcap_up=para["intstorcap_up"],
            soiltype=soiltype,
            croptype=croptype,
        )
        self.unsaturatedzone = UnsaturatedZone(
            theta_uz_t0,
            uz_no_meas_area,
            uz_meas_area,
            soiltype=soiltype,
            croptype=croptype,
        )
        self.groundwater = Groundwater(
            init_gwl_t0,
            gw_no_meas_area,
            gw_meas_area,
            seep_def=para["seep_def"],
            w=para["w"],
            vc=para["vc"],
            h_deepgw=para["h_deepgw"],
            flux=para["flux"],
            soiltype=soiltype,
            croptype=croptype,
        )
        self.sewersystem = SewerSystem(
            swds_no_meas_area,
            mss_no_meas_area,
            prev_stor_swds_t0,
            prev_so_swds_t0,
            prev_stor_mss_t0,
            prev_so_mss_t0,
            q_swds_ow_cap=para["q_swds_ow_cap"],
            q_mss_out_cap=para["q_mss_out_cap"],
            q_mss_ow_cap=para["q_mss_ow_cap"],
            stor_swds_cap=para["storcap_swds"],
            stor_mss_cap=para["storcap_mss"],
        )
        self.openwater = OpenWater(ow_no_meas_area, para["ow_level"], q_ow_out_cap=200)
        # batch run (different pump capacity, different q_ow_out_cap)
>>>>>>> 55d77f455be2621db16d1a5f9cca37019ae5a4c0

    def __iter__(self):
        return self

    def __next__(
        self,
        p_atm,
        e_pot_ow,
        ref_grass,
        prev_lst,
        meas_uz,
        meas_gw,
        meas_swds,
        meas_mss,
        meas_ow,
    ):
        try:
            # empty dictionary
            a = self.pavedroof.sol(p_atm, e_pot_ow)
            b = self.closedpaved.sol(p_atm, e_pot_ow)
            c = self.openpaved.sol(p_atm, e_pot_ow, delta_t=1 / 24)
            d = self.unpaved.sol(
                p_atm,
                e_pot_ow,
                a["r_pr_up"],
                b["r_cp_up"],
                c["r_op_up"],
                prev_lst["theta_uz"],
                pr_no_meas_area,
                cp_no_meas_area,
                op_no_meas_area,
                ow_no_meas_area,
                delta_t=1 / 24,
            )
            e = self.unsaturatedzone.sol(
                d["i_up_uz"],
                meas_uz,
                tot_meas_area,
                ref_grass,
                prev_lst["gwl"],
                delta_t=1 / 24,
            )
            f = self.groundwater.sol(
                e["p_uz_gw"],
                uz_no_meas_area,
                c["p_op_gw"],
                op_no_meas_area,
                tot_meas_area,
                meas_gw,
                prev_lst["owl"],
                delta_t=1 / 24,
            )
            g = self.sewersystem.sol(
                pr_no_meas_area,
                cp_no_meas_area,
                op_no_meas_area,
                a["r_pr_swds"],
                b["r_cp_swds"],
                c["r_op_swds"],
                a["r_pr_mss"],
                b["r_cp_mss"],
                c["r_op_mss"],
                meas_swds,
                meas_mss,
                ow_no_meas_area,
                tot_meas_area,
            )
            h = self.openwater.sol(
                p_atm,
                e_pot_ow,
                d["r_up_ow"],
                f["d_gw_ow"],
                g["q_swds_ow"],
                g["q_mss_ow"],
                g["so_swds_ow"],
                g["so_mss_ow"],
                meas_ow,
                up_no_meas_area,
                gw_no_meas_area,
                swds_no_meas_area,
                mss_no_meas_area,
                tot_meas_area,
                total_area,
                delta_t=1 / 24,
            )
            dictmerged = OrderedDict(dict(a, **b, **c, **d, **e, **f, **g, **h))
        except IndexError:
            raise StopIteration
        return dictmerged


def running(para):
    start = time.time()
    lst = [
        {
            "int_pr": 0,
            "e_atm_pr": 0,
            "intstor_pr": init_intstor_pr_t0,
            "r_pr_meas": 0,
            "r_pr_swds": 0,
            "r_pr_mss": 0,
            "r_pr_up": 0,
            "int_cp": 0,
            "e_atm_cp": 0,
            "intstor_cp": init_intstor_cp_t0,
            "r_cp_meas": 0,
            "r_cp_swds": 0,
            "r_cp_mss": 0,
            "r_cp_up": 0,
            "int_op": 0,
            "e_atm_op": 0,
            "intstor_op": init_intstor_op_t0,
            "p_op_gw": 0,
            "r_op_meas": 0,
            "r_op_swds": 00,
            "r_op_mss": 0.0,
            "r_op_up": 0.0,
            "sum_r_up": 0,
            "init_stor_up": 0,
            "act_infilcap_up": 0,
            "tfac_up": 0,
            "e_atm_up": 0,
            "i_up_uz": 0,
            "fin_stor_up": fin_stor_up_t0,
            "r_up_meas": 0,
            "r_up_ow": 0,
            # theta_uz_t0 could be written as soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['moist_cont_eq_rz[mm]']
<<<<<<< HEAD
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
    q_ow_out_cap = 200
    k = Model(q_ow_out_cap)
=======
            "sum_i_uz": 0,
            "r_meas_uz": 0,
            "theta_h3_uz": 0,
            "t_alpha_uz": 0,
            "t_atm_uz": 0,
            "gwl_up": 0,
            "gwl_low": 0,
            "theta_eq_uz": 0,
            "capris_max_uz": 0,
            "p_uz_gw": 0,
            "theta_uz": theta_uz_t0,
            "sum_p_gw": 0,
            "r_meas_gw": 0,
            "gwl_up_1": 0,
            "gwl_low_1": 0,
            "sc_gw": soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]["stor_coef"],
            "h_gw": 0,
            "s_gw_out": 0,
            "d_gw_ow": 0,
            "gwl": init_gwl_t0,
            "gwl_sl": 0,
            "sum_r_swds": 0,
            "r_meas_swds": 0,
            "sum_r_mss": 0,
            "r_meas_mss": 0,
            "q_swds_ow": 0,
            "q_mss_out": 0,
            "q_mss_ow": 0,
            "so_swds": prev_so_swds_t0,
            "so_mss": prev_so_mss_t0,
            "stor_swds": prev_stor_swds_t0,
            "stor_mss": prev_stor_mss_t0,
            "prec_ow": P_atm[0],
            "e_atm_ow": E_pot_OW[0],
            "sum_r_ow": 0,
            "sum_d_ow": 0,
            "sum_q_ow": 0,
            "sum_so_ow": 0,
            "r_meas_ow": 0,
            "q_ow_out": 0,
            "owl": ow_level,
        }
    ]

    k = Model()
>>>>>>> 55d77f455be2621db16d1a5f9cca37019ae5a4c0

    t = 1
    while t <= iters - 1:
        lst.append(
            k.__next__(
                P_atm[t],
                E_pot_OW[t],
                Ref_grass[t],
                lst[t - 1],
                meas_uz[t],
                meas_gw[t],
                meas_swds[t],
                meas_mss[t],
                meas_ow[t],
            )
        )

<<<<<<< HEAD
        if t % 5000 == 0:
            print(f'timestep {t} / {iters}')
=======
        if t % 200 == 0:
            print(f"timestep {t} / {iters}")
>>>>>>> 55d77f455be2621db16d1a5f9cca37019ae5a4c0
        t += 1

    return lst

def savecsv(filename):
    lst = running(filename)
    df = pd.DataFrame(lst)
<<<<<<< HEAD
    df.insert(0, 'Date', date)
    outdir = Path('pysol')
    outdir.mkdir(parents=True, exist_ok=True)

=======
    df.insert(0, "Date", date)
>>>>>>> 55d77f455be2621db16d1a5f9cca37019ae5a4c0
    df.to_csv(outdir / filename, index=True)
    end = time.time()
    print(f"Model runtime: {end - start:.1f}s")


<<<<<<< HEAD
def batch_run(overridedict): # can make into args here
    para = read_parameter()
    para.update(overridedict)
    running(para)

    start = time.time()
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
        k = Model(q_ow_out_cap)
        t = 1
        while t <= iters - 1:
            lst.append(
                k.__next__(P_atm[t], E_pot_OW[t], Ref_grass[t], lst[t - 1], meas_uz[t], meas_gw[t], meas_swds[t],
                           meas_mss[t], meas_ow[t]))
            if t % 10000 == 0:
                print(f'timestep {t} / {iters}')
            t += 1
        df = pd.DataFrame(lst)
        df.insert(0, 'Date', date)
        owl_database.append(df['owl'])
    end = time.time()
    print(end - start)
    return owl_database


if __name__ == '__main__':
    # Load csv input file
    path = urbanwb.urbanwbdir / ".." / "input"
    InputData = pd.read_csv(path / 'input_csv.csv')  # input the precipitation, potential evaporation
    date = InputData['date']
    P_atm = InputData['P_atm']
    Ref_grass = InputData['Ref.grass']
    E_pot_OW = InputData['E_pot_OW']
    iters = np.shape(date)[0]

    # Parameter settings.
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
    theta_uz_t0 = soil_selector(soiltype, croptype)[gwlcal(init_gwl_t0)[2]]['moist_cont_eq_rz[mm]']
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
    meas_uz, meas_gw, meas_swds, meas_mss, meas_ow = np.zeros(iters), np.zeros(iters), np.zeros(iters), np.zeros(
        iters), np.zeros(iters)

    # test running()
    q_ow_out_cap = 200
    filename = 'test.csv'
    running(para)

    # plot SDF curve using batch_run()
    Q = np.linspace(0.1, 1, 10)
    results = []
    for q in Q:
        overridedict = {"pump_capacity": q}
        lst = batch_run(overridedict)
        results.append(lst)

    from urbanwb.SDF_curve import OWL
    storage_database = []
    for result in results:
        k = OWL(result, 5, 1.5)
        print('max', max(k.max_stor()), 'min', min(k.max_stor()))
        print('number of events', k.num_event)
        print(k.rank)
        print(k.return_time())
        storage_database.append(k.required_storage_capacity())
        print('-----' * 6)

    # print(storage_database)
    # print(np.shape(storage_database))
    # plot SDF-curve
    f = 1  # for unit conversion
    labels = ['T=1', 'T=2', 'T=5', 'T=10', 'T=20', 'T=50', 'T=100']
    plt.figure()
    for i in range(7):
        plt.plot(Q * f, [storage[i] for storage in storage_database], label=labels[i])
    plt.legend(loc='best')
    plt.xlabel('Discharge capacity')
    plt.ylabel('storage capacity')
    plt.title('SDF-curve')
    plt.grid(True)
    plt.show()

=======
if __name__ == "__main__":
    filename = "test.csv"
    running(filename)
>>>>>>> 55d77f455be2621db16d1a5f9cca37019ae5a4c0

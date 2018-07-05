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
from urbanwb.read_parameter_base import read_parameter_base
from urbanwb.read_parameter_measure import read_parameter_measure
import matplotlib.pyplot as plt


class Model(object):
    """
    A model consists of all eight components namely pavedroof, closedpaved, openpaved, unpaved, unsaturatedzone,
    groundwater, sewersystem and openwater module. Inputdata and parameters are read from the 'input.csv' and
    'static_form.ini' under the \\UWM\\input folder.
    """
    def __init__(self, dict):
        self.para = dict  # get one large dictionary of parameters
        self.pavedroof = PavedRoof(
            init_intstor_pr_t0=0,
            pr_no_meas_area=self.para["tot_pr_area"] - self.para["pr_meas_area"],
            pr_meas_area=self.para["pr_meas_area"],
            pr_meas_inflow_area=self.para["pr_meas_inflow_area"],
            intstorcap_pr=self.para["intstorcap_pr"],
            stormfrac_pr=self.para["swds_frac"],
            discfrac_pr=self.para["discfrac_pr"],
        )
        self.closedpaved = ClosedPaved(
            init_intstor_cp_t0=0,
            cp_no_meas_area=self.para["tot_cp_area"] - self.para["cp_meas_area"],
            cp_meas_area=self.para["cp_meas_area"],
            cp_meas_inflow_area=self.para["cp_meas_inflow_area"],
            intstorcap_cp=self.para["intstorcap_cp"],
            stormfrac_cp=self.para["swds_frac"],
            discfrac_cp=self.para["discfrac_cp"],
        )
        self.openpaved = OpenPaved(
            init_intstor_op_t0=0,
            op_no_meas_area=self.para["tot_op_area"] - self.para["op_meas_area"],
            op_meas_area=self.para["op_meas_area"],
            op_meas_inflow_area=self.para["op_meas_inflow_area"],
            intstorcap_op=self.para["intstorcap_op"],
            stormfrac_op=self.para["swds_frac"],
            discfrac_op=self.para["discfrac_op"],
            infilcap_op=self.para["infilcap_op"],
        )
        self.unpaved = Unpaved(
            fin_stor_up_t0=0,
            up_no_meas_area=self.para["tot_up_area"] - self.para["up_meas_area"],
            up_meas_area=self.para["up_meas_area"],
            up_meas_inflow_area=self.para["up_meas_inflow_area"],
            infilcap_up=self.para["infilcap_up"],
            intstorcap_up=self.para["intstorcap_up"],
            soiltype=self.para["soiltype"],
            croptype=self.para["croptype"],
        )
        self.unsaturatedzone = UnsaturatedZone(
            theta_uz_t0=soil_selector(self.para["soiltype"], self.para["croptype"])
                        [gwlcal(self.para["init_gwl"])[2]]["moist_cont_eq_rz[mm]"],
            uz_no_meas_area=self.para["tot_uz_area"] - self.para["uz_meas_area"],
            uz_meas_area=self.para["uz_meas_area"],
            soiltype=self.para["soiltype"],
            croptype=self.para["croptype"],
        )
        self.groundwater = Groundwater(
            init_gwl_t0=self.para["init_gwl"],
            gw_no_meas_area=self.para["tot_gw_area"] - self.para["gw_meas_area"],
            gw_meas_area=self.para["gw_meas_area"],
            seep_def=self.para["seep_def"],
            w=self.para["w"],
            vc=self.para["vc"],
            h_deepgw=self.para["h_deepgw"],
            flux=self.para["flux"],
            soiltype=self.para["soiltype"],
            croptype=self.para["croptype"],
        )
        self.sewersystem = SewerSystem(
            swds_no_meas_area=self.para["tot_swds_area"] - self.para["swds_meas_area"],
            mss_no_meas_area=self.para["tot_mss_area"] - self.para["mss_meas_area"],
            prev_stor_swds_t0=0,
            prev_so_swds_t0=0,
            prev_stor_mss_t0=0,
            prev_so_mss_t0=0,
            q_swds_ow_cap=self.para["q_swds_ow_cap"],
            q_mss_out_cap=self.para["q_mss_out_cap"],
            q_mss_ow_cap=self.para["q_mss_ow_cap"],
            stor_swds_cap=self.para["storcap_swds"],
            stor_mss_cap=self.para["storcap_mss"],
        )
        self.openwater = OpenWater(
            ow_no_meas_area=self.para["tot_ow_area"] - self.para["ow_meas_area"], ow_level=self.para["ow_level"],
            q_ow_out_cap=self.para["pump_cap"] * 8.64
        )

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
            a = self.pavedroof.sol(p_atm=p_atm, e_pot_ow=e_pot_ow)
            b = self.closedpaved.sol(p_atm=p_atm, e_pot_ow=e_pot_ow)
            c = self.openpaved.sol(p_atm=p_atm, e_pot_ow=e_pot_ow, delta_t=self.para["delta_t"])
            d = self.unpaved.sol(
                p_atm=p_atm,
                e_pot_ow=e_pot_ow,
                r_pr_up=a["r_pr_up"],
                r_cp_up=b["r_cp_up"],
                r_op_up=c["r_op_up"],
                prev_mois_uz=prev_lst["theta_uz"],
                pr_no_meas_area=self.para["tot_pr_area"]-self.para["pr_meas_area"],
                cp_no_meas_area=self.para["tot_cp_area"]-self.para["cp_meas_area"],
                op_no_meas_area=self.para["tot_op_area"]-self.para["op_meas_area"],
                ow_no_meas_area=self.para["tot_ow_area"]-self.para["ow_meas_area"],
                delta_t=self.para["delta_t"],
            )
            e = self.unsaturatedzone.sol(
                i_up_uz=d["i_up_uz"],
                meas_uz=meas_uz,
                tot_meas_area=self.para["tot_meas_area"],
                e_ref=ref_grass,
                prev_gwl=prev_lst["gwl"],
                delta_t=self.para["delta_t"],
            )
            f = self.groundwater.sol(
                p_uz_gw=e["p_uz_gw"],
                uz_no_meas_area=self.para["tot_uz_area"] - self.para["uz_meas_area"],
                p_op_gw=c["p_op_gw"],
                op_no_meas_area=self.para["tot_op_area"] - self.para["op_meas_area"],
                tot_meas_area=self.para["tot_meas_area"],
                meas_gw=meas_gw,
                prev_owl=prev_lst["owl"],
                delta_t=self.para["delta_t"],
            )
            g = self.sewersystem.sol(
                pr_no_meas_area=self.para["tot_pr_area"] - self.para["pr_meas_area"],
                cp_no_meas_area=self.para["tot_cp_area"] - self.para["cp_meas_area"],
                op_no_meas_area=self.para["tot_op_area"] - self.para["op_meas_area"],
                r_pr_swds=a["r_pr_swds"],
                r_cp_swds=b["r_cp_swds"],
                r_op_swds=c["r_op_swds"],
                r_pr_mss=a["r_pr_mss"],
                r_cp_mss=b["r_cp_mss"],
                r_op_mss=c["r_op_mss"],
                meas_swds=meas_swds,
                meas_mss=meas_mss,
                ow_no_meas_area=self.para["tot_ow_area"] - self.para["ow_meas_area"],
                tot_meas_area=self.para["tot_meas_area"],
            )
            h = self.openwater.sol(
                p_atm=p_atm,
                e_pot_ow=e_pot_ow,
                r_up_ow=d["r_up_ow"],
                d_gw_ow=f["d_gw_ow"],
                q_swds_ow=g["q_swds_ow"],
                q_mss_ow=g["q_mss_ow"],
                so_swds_ow=g["so_swds_ow"],
                so_mss_ow=g["so_mss_ow"],
                meas_ow=meas_ow,
                up_no_meas_area=self.para["tot_up_area"] - self.para["up_meas_area"],
                gw_no_meas_area=self.para["tot_gw_area"] - self.para["gw_meas_area"],
                swds_no_meas_area=self.para["tot_swds_area"] - self.para["swds_meas_area"],
                mss_no_meas_area=self.para["tot_mss_area"] - self.para['mss_meas_area'],
                tot_meas_area=self.para["tot_meas_area"],
                total_area=self.para["tot_area"],
                delta_t=self.para["delta_t"],
            )
            dictmerged = OrderedDict(dict(a, **b, **c, **d, **e, **f, **g, **h))
        except IndexError:
            raise StopIteration
        return dictmerged


def running(dict_para):
    start = time.time()
    # read general parameter and parameters for measure from static forms.
    k = Model(dict_para)
    lst = [
        {
            "int_pr": 0,
            "e_atm_pr": 0,
            "intstor_pr": 0,  # init_intstor_pr_t0
            "r_pr_meas": 0,
            "r_pr_swds": 0,
            "r_pr_mss": 0,
            "r_pr_up": 0,
            "int_cp": 0,
            "e_atm_cp": 0,
            "intstor_cp": 0,  # init_intstor_cp_t0
            "r_cp_meas": 0,
            "r_cp_swds": 0,
            "r_cp_mss": 0,
            "r_cp_up": 0,
            "int_op": 0,
            "e_atm_op": 0,
            "intstor_op": 0,  # init_intstor_op_t0
            "p_op_gw": 0,
            "r_op_meas": 0,
            "r_op_swds": 0,
            "r_op_mss": 0.0,
            "r_op_up": 0.0,
            "sum_r_up": 0,
            "init_stor_up": 0,
            "act_infilcap_up": 0,
            "tfac_up": 0,
            "e_atm_up": 0,
            "i_up_uz": 0,
            "fin_stor_up": 0, # fin_stor_up_t0
            "r_up_meas": 0,
            "r_up_ow": 0,
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
            "theta_uz": soil_selector(dict_para["soiltype"], dict_para["croptype"])
                        [gwlcal(dict_para["init_gwl"])[2]]["moist_cont_eq_rz[mm]"],
            "sum_p_gw": 0,
            "r_meas_gw": 0,
            "gwl_up_1": 0,
            "gwl_low_1": 0,
            "sc_gw": soil_selector(dict_para["soiltype"], dict_para["croptype"])[gwlcal(dict_para["init_gwl"])[2]][
                "stor_coef"
            ],
            "h_gw": 0,
            "s_gw_out": 0,
            "d_gw_ow": 0,
            "gwl": dict_para["init_gwl"],
            "gwl_sl": 0,
            "sum_r_swds": 0,
            "r_meas_swds": 0,
            "sum_r_mss": 0,
            "r_meas_mss": 0,
            "q_swds_ow": 0,
            "q_mss_out": 0,
            "q_mss_ow": 0,
            "so_swds": 0,  # prev_so_swds_t0
            "so_mss": 0,  # prev_so_mss_t0
            "stor_swds": 0,  # prev_stor_swds_t0
            "stor_mss": 0,  # prev_stor_mss_t0
            "prec_ow": P_atm[0],
            "e_atm_ow": E_pot_OW[0],
            "sum_r_ow": 0,
            "sum_d_ow": 0,
            "sum_q_ow": 0,
            "sum_so_ow": 0,
            "r_meas_ow": 0,
            "q_ow_out": 0,
            "owl": dict_para["ow_level"],
        }
    ]

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

        if t % 10000 == 0:
            print(f"timestep {t} / {iters}")
        t += 1
    end = time.time()
    print(end - start)
    return lst


def savecsv(filename, dict_para):
    lst = running(dict_para)
    df = pd.DataFrame(lst)
    df.insert(0, "Date", date)
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / filename, index=True)



# def batch_run(overridedict):  # can make into args here
#     para = read_parameter()
#     para.update(overridedict)
#     running(para)
#     start = time.time()
#     owl_database = []
#     for q in Q:
#         q_ow_out_cap = q * 8.64
#         lst = [
#             {
#                 "int_pr": 0,
#                 "e_atm_pr": 0,
#                 "intstor_pr": init_intstor_pr_t0,
#                 "r_pr_meas": 0,
#                 "r_pr_swds": 0,
#                 "r_pr_mss": 0,
#                 "r_pr_up": 0,
#                 "int_cp": 0,
#                 "e_atm_cp": 0,
#                 "intstor_cp": init_intstor_cp_t0,
#                 "r_cp_meas": 0,
#                 "r_cp_swds": 0,
#                 "r_cp_mss": 0,
#                 "r_cp_up": 0,
#                 "int_op": 0,
#                 "e_atm_op": 0,
#                 "intstor_op": init_intstor_op_t0,
#                 "p_op_gw": 0,
#                 "r_op_meas": 0,
#                 "r_op_swds": 00,
#                 "r_op_mss": 0.0,
#                 "r_op_up": 0.0,
#                 "sum_r_up": 0,
#                 "init_stor_up": 0,
#                 "act_infilcap_up": 0,
#                 "tfac_up": 0,
#                 "e_atm_up": 0,
#                 "i_up_uz": 0,
#                 "fin_stor_up": fin_stor_up_t0,
#                 "r_up_meas": 0,
#                 "r_up_ow": 0,
#                 # theta_uz_t0 could be written as soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]['moist_cont_eq_rz[mm]']
#                 "sum_i_uz": 0,
#                 "r_meas_uz": 0,
#                 "theta_h3_uz": 0,
#                 "t_alpha_uz": 0,
#                 "t_atm_uz": 0,
#                 "gwl_up": 0,
#                 "gwl_low": 0,
#                 "theta_eq_uz": 0,
#                 "capris_max_uz": 0,
#                 "p_uz_gw": 0,
#                 "theta_uz": theta_uz_t0,
#                 "sum_p_gw": 0,
#                 "r_meas_gw": 0,
#                 "gwl_up_1": 0,
#                 "gwl_low_1": 0,
#                 "sc_gw": soil_selector(soiltype, croptype)[gwlcal(init_gwl_t0)[2]][
#                     "stor_coef"
#                 ],
#                 "h_gw": 0,
#                 "s_gw_out": 0,
#                 "d_gw_ow": 0,
#                 "gwl": init_gwl_t0,
#                 "gwl_sl": 0,
#                 "sum_r_swds": 0,
#                 "r_meas_swds": 0,
#                 "sum_r_mss": 0,
#                 "r_meas_mss": 0,
#                 "q_swds_ow": 0,
#                 "q_mss_out": 0,
#                 "q_mss_ow": 0,
#                 "so_swds": prev_so_swds_t0,
#                 "so_mss": prev_so_mss_t0,
#                 "stor_swds": prev_stor_swds_t0,
#                 "stor_mss": prev_stor_mss_t0,
#                 "prec_ow": P_atm[0],
#                 "e_atm_ow": E_pot_OW[0],
#                 "sum_r_ow": 0,
#                 "sum_d_ow": 0,
#                 "sum_q_ow": 0,
#                 "sum_so_ow": 0,
#                 "r_meas_ow": 0,
#                 "q_ow_out": 0,
#                 "owl": ow_level,
#             }
#         ]
#         k = Model()
#         t = 1
#         while t <= iters - 1:
#             lst.append(
#                 k.__next__(
#                     P_atm[t],
#                     E_pot_OW[t],
#                     Ref_grass[t],
#                     lst[t - 1],
#                     meas_uz[t],
#                     meas_gw[t],
#                     meas_swds[t],
#                     meas_mss[t],
#                     meas_ow[t],
#                 )
#             )
#             if t % 10000 == 0:
#                 print(f"timestep {t} / {iters}")
#             t += 1
#         df = pd.DataFrame(lst)
#         df.insert(0, "Date", date)
#         owl_database.append(df["owl"])
#     end = time.time()
#     print(end - start)
#     return owl_database


if __name__ == "__main__":
    # read time series of precipitation and evaporation from input.csv file
    path = urbanwb.urbanwbdir / ".." / "input"
    InputData = pd.read_csv(path / "input_csv.csv")
    date = InputData["date"]
    P_atm = InputData["P_atm"]
    Ref_grass = InputData["Ref.grass"]
    E_pot_OW = InputData["E_pot_OW"]
    iters = np.shape(date)[0]
    # measure fluxes are all zeros for the time being
    meas_uz, meas_gw, meas_swds, meas_mss, meas_ow = (
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
    )

    # test

    dict_para = {**read_parameter_base(), **read_parameter_measure()}  # One large dictionary of parameters
    running(dict_para)
    savecsv("results.csv", dict_para)


    # # plot SDF curve using batch_run()
    # Q = np.linspace(0.1, 1, 10)
    # results = []
    # for q in Q:
    #     overridedict = {"pump_capacity": q}
    #     lst = batch_run(overridedict)
    #     results.append(lst)
    #
    # from urbanwb.sdf_curve import SDF_Curve
    # storage_database = []
    # for result in results:
    #     k = OWL(result, 5, 1.5)
    #     print('max', max(k.max_stor()), 'min', min(k.max_stor()))
    #     print('number of events', k.num_event)
    #     print(k.rank)
    #     print(k.return_time())
    #     storage_database.append(k.required_storage_capacity())
    #     print('-----' * 6)
    #
    # # print(storage_database)
    # # print(np.shape(storage_database))
    # # plot SDF-curve
    # f = 1  # for unit conversion
    # labels = ['T=1', 'T=2', 'T=5', 'T=10', 'T=20', 'T=50', 'T=100']
    # plt.figure()
    # for i in range(7):
    #     plt.plot(Q * f, [storage[i] for storage in storage_database], label=labels[i])
    # plt.legend(loc='best')
    # plt.xlabel('Discharge capacity')
    # plt.ylabel('storage capacity')
    # plt.title('SDF-curve')
    # plt.grid(True)
    # plt.show()

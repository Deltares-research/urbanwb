#! /usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy as np


def water_balance_checker(df, dict_param, iters):

    # Check water balance over entire area.

    # precipitation (Neerslag)
    sum_prec = sum(df["P_atm"].iloc[1:])

    # evaporation (Verdamping)
    sum_evap_pr = sum(df["e_atm_pr"].iloc[1:]) * dict_param["pr_no_meas_area"] / dict_param["tot_area"]
    sum_evap_cp = sum(df["e_atm_cp"].iloc[1:]) * dict_param["cp_no_meas_area"] / dict_param["tot_area"]
    sum_evap_op = sum(df["e_atm_op"].iloc[1:]) * dict_param["op_no_meas_area"] / dict_param["tot_area"]
    sum_evap_up = sum(df["e_atm_up"].iloc[1:]) * dict_param["up_no_meas_area"] / dict_param["tot_area"]
    sum_evap_uz = sum(df["t_atm_uz"].iloc[1:]) * dict_param["uz_no_meas_area"] / dict_param["tot_area"]
    sum_evap_ow = sum(df["e_atm_ow"].iloc[1:]) * dict_param["ow_no_meas_area"] / dict_param["tot_area"]
    sum_evap_meas = (sum(df["e_atm_meas"].iloc[1:]) * dict_param["tot_meas_area"] +
                     sum(df["t_atm_top_meas"].iloc[1:]) * dict_param["top_meas_area"] +
                     sum(df["t_atm_btm_meas"].iloc[1:]) * dict_param["btm_meas_area"]) / dict_param["tot_area"]
    evaporation = sum_evap_pr + sum_evap_cp + sum_evap_op + sum_evap_up + sum_evap_uz + sum_evap_ow + sum_evap_meas

    # discharge out (Bemaling)
    sum_q_out = (sum(df["q_ow_out"].iloc[1:]) * dict_param["ow_no_meas_area"] +
                 sum(df["q_meas_out"].iloc[1:]) * dict_param["tot_meas_area"]) / dict_param["tot_area"]

    # seepage to deep groundwater (Neerwaartse kwel)
    sum_s_deepgw = sum(df["s_gw_out"].iloc[1:]) * dict_param["gw_no_meas_area"] / dict_param["tot_area"]

    # change in storages
    sum_ds_pr = (df["intstor_pr"].iloc[-1] - df["intstor_pr"].iloc[0]) * dict_param["pr_no_meas_area"] / dict_param["tot_area"]
    sum_ds_cp = (df["intstor_cp"].iloc[-1] - df["intstor_cp"].iloc[0]) * dict_param["cp_no_meas_area"] / dict_param["tot_area"]
    sum_ds_op = (df["intstor_op"].iloc[-1] - df["intstor_op"].iloc[0]) * dict_param["op_no_meas_area"] / dict_param["tot_area"]
    sum_ds_up = (df["fin_intstor_up"].iloc[-1] - df["fin_intstor_up"].iloc[0]) * dict_param["up_no_meas_area"] / dict_param["tot_area"]
    sum_ds_uz = (df["theta_uz"].iloc[-1] - df["theta_uz"].iloc[0]) * dict_param["uz_no_meas_area"] / dict_param["tot_area"]
    storage_coef = df["sc_gw"]
    groundwater_level = df["gwl"]
    ds_gw = np.zeros_like(groundwater_level)
    for t in range(1, iters):
        ds_gw[t] = 1000 * storage_coef[t] * (groundwater_level[t-1] - groundwater_level[t])
    sum_ds_gw = sum(ds_gw) * dict_param["gw_no_meas_area"] / dict_param["tot_area"]
    sum_ds_gw_sl = 1000 * (df["gwl_sl"].iloc[-1] - df["gwl_sl"].iloc[0]) * dict_param["gw_no_meas_area"] / dict_param["tot_area"]
    sum_ds_swds = (df["stor_swds"].iloc[-1] - df["stor_swds"].iloc[0]) * dict_param["swds_no_meas_area"] / dict_param["tot_area"]
    sum_ds_mss = (df["stor_mss"].iloc[-1] - df["stor_mss"].iloc[0]) * dict_param["mss_no_meas_area"] / dict_param["tot_area"]
    # sum_ds_so
    sum_ds_ow = 1000 * (df["owl"].iloc[-1] - df["owl"].iloc[0]) * dict_param["ow_no_meas_area"] / dict_param["tot_area"]
    sum_ds_meas = ((df["intstor_meas"].iloc[-1] - df["intstor_meas"].iloc[0]) * dict_param["tot_meas_area"] +
                   (df["fin_stor_top_meas"].iloc[-1] - df["fin_stor_top_meas"].iloc[0]) * dict_param["top_meas_area"] +
                   (df["fin_stor_btm_meas"].iloc[-1] - df["fin_stor_btm_meas"].iloc[0]) * dict_param["btm_meas_area"]) / dict_param["tot_area"]
    d_storage = sum_ds_pr + sum_ds_cp + sum_ds_op + sum_ds_up + sum_ds_up + sum_ds_uz + sum_ds_gw + sum_ds_gw_sl + \
                sum_ds_swds + sum_ds_mss + sum_ds_ow + sum_ds_meas

    balance_check = sum_prec - evaporation - sum_q_out - sum_s_deepgw - d_storage
    stat = {"Precipitation": "%.2f" % sum_prec, "Evaporation": "%.2f" % evaporation, "Discharging": "%.2f" % sum_q_out, "Downward seepage": "%.2f" % sum_s_deepgw,
            "Storage change": "%.2f" % d_storage, "Water balance different": balance_check}
    print("Water balance statistics: ")
    print('---'*6)
    print("Entire model:")
    print(f"Precipitation {sum_prec:.2f} mm;   Evaporation {evaporation:.2f} mm;   Discharge outside {sum_q_out:.2f} mm; "
          f"  Seepage {sum_s_deepgw:.2f} mm;   Storage change {d_storage:.2f} mm;   Difference: {balance_check} mm")
    if math.isclose(balance_check, 0, abs_tol=0.001):
        print("Water balance is closed for entire model.")
    else:
        # pass
        raise SystemExit("Water balance is not closed. Please recheck.")
    p_meas = sum_prec
    e_meas = sum_evap_meas * dict_param["tot_area"] / dict_param["tot_meas_area"]
    r_otherarea_meas = sum(df["sum_r_meas"].iloc[1:])
    gw_recharge_meas = sum(df["q_meas_gw"].iloc[1:])
    ow_discharge_meas = sum(df["q_meas_ow"].iloc[1:])
    swds_discharge_meas = sum(df["q_meas_swds"].iloc[1:])
    mss_discharge_meas = sum(df["q_meas_mss"].iloc[1:])
    out_discharge_meas = sum(df["q_meas_mss"].iloc[1:])
    ds_meas = sum_ds_meas * dict_param["tot_area"] / dict_param["tot_meas_area"]
    measure_balance_check = p_meas - e_meas + r_otherarea_meas - gw_recharge_meas - ow_discharge_meas - \
                            swds_discharge_meas - mss_discharge_meas - out_discharge_meas - ds_meas
    print('---' * 6)
    print("Measure itself:")
    print(f"Precipitation {p_meas:.2f} mm;  Evaporation {e_meas:.2f} mm;   Runoff from inflow area {r_otherarea_meas:.2f} mm;"
          f"   Open water discharge {ow_discharge_meas:.2f} mm;   Sewer system discharge, SWDS {swds_discharge_meas:.2f} mm,  mss{mss_discharge_meas:.2f} mm;"
          f"Groundwater recharge {gw_recharge_meas:.2f} mm;   Outside discharge {out_discharge_meas} mm;  Storage changes {ds_meas} mm;"
          f"Difference {measure_balance_check} mm")
    if math.isclose(measure_balance_check, 0, abs_tol=0.001):
        print("Water balance is closed for measure itself.")
    else:
        # pass
        raise SystemExit("Water balance for measure is not closed. Please recheck.")
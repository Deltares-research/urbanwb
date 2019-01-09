#! /usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy as np
from tabulate import tabulate


def water_balance_checker(df, dict_param, iters):
    """
    checks whether water balance is closed over the entire area and over the measure itself
    """

    # Check water balance over entire area.
    print("Water balance statistics: ")

    # precipitation
    sum_prec = sum(df["P_atm"].iloc[1:])

    # evaporation
    # sum_evap_pr = sum(df["e_atm_pr"].iloc[1:])
    # sum_evap_cp = sum(df["e_atm_cp"].iloc[1:])
    # sum_evap_op = sum(df["e_atm_op"].iloc[1:])
    # sum_evap_up = sum(df["e_atm_up"].iloc[1:])
    # sum_evap_uz = sum(df["t_atm_uz"].iloc[1:])
    # sum_evap_ow = sum(df["e_atm_ow"].iloc[1:])

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
    stat = {"Precipitation": "%.2f" % sum_prec, "Evaporation": "%.2f" % evaporation, "Discharge_out": "%.2f" % sum_q_out, "Seepage": "%.2f" % sum_s_deepgw,
            "Storage_change": "%.2f" % d_storage, "Water_balance_different": balance_check}
    print("Entire model:")
    headers = ["Precipitation[mm]", "Evaporation[mm]", "Discharge_out[mm]", "Seepage[mm]", "Storage_change[mm]", "Difference[mm]"]
    table = [["%.2f" % sum_prec, "%.2f" % evaporation, "%.2f" % sum_q_out, "%.2f" % sum_s_deepgw, "%.2f" % d_storage, balance_check]]
    print(tabulate(table, headers, tablefmt="psql"))
    if math.isclose(balance_check, 0, abs_tol=0.001):
        pass
        # print("Water balance is closed for entire model.")
    else:
        # pass
        raise SystemExit("Water balance is not closed. Please recheck.")

    # water balance for measure itself
    print("Measure itself:")
    p_meas = sum(df["prec_meas"].iloc[1:])
    try:
        e_meas = sum_evap_meas * dict_param["tot_area"] / dict_param["tot_meas_area"]
        ds_meas = sum_ds_meas * dict_param["tot_area"] / dict_param["tot_meas_area"]
    except ZeroDivisionError:
        e_meas = 0
        ds_meas = 0
    r_otherarea_meas = sum(df["sum_r_meas"].iloc[1:])
    gw_recharge_meas = sum(df["q_meas_gw"].iloc[1:])
    ow_discharge_meas = sum(df["q_meas_ow"].iloc[1:])
    swds_discharge_meas = sum(df["q_meas_swds"].iloc[1:])
    mss_discharge_meas = sum(df["q_meas_mss"].iloc[1:])
    out_discharge_meas = sum(df["q_meas_mss"].iloc[1:])
    measure_balance_check = p_meas - e_meas + r_otherarea_meas - gw_recharge_meas - ow_discharge_meas - \
                            swds_discharge_meas - mss_discharge_meas - out_discharge_meas - ds_meas
    headers_m = ["Precipitation[mm]", "Evaporation[mm]", "Inflow_runoff[mm]", "Openwater_discharge[mm]",
               "SWDS_discharge[mm]", "MSS_discharge[mm]", "Outside_discharge[mm]", "Groundwater_recharge[mm]",
                "Storage_changes[mm]", "Difference[mm]"]
    table_m = [["%.2f" % p_meas, "%.2f" % e_meas, "%.2f" % r_otherarea_meas, "%.2f" % ow_discharge_meas, "%.2f" % swds_discharge_meas, "%.2f" % mss_discharge_meas,
              "%.2f" % gw_recharge_meas, "%.2f" % out_discharge_meas, "%.2f" % ds_meas, measure_balance_check]]
    print(tabulate(table_m, headers_m, tablefmt="psql"))
    if math.isclose(measure_balance_check, 0, abs_tol=0.001):
        pass
        # print("Water balance is closed for measure itself.")
    else:
        # pass
        raise SystemExit("Water balance for measure is not closed. Please recheck.")
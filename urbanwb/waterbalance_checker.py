#! /usr/bin/env python
# -*- coding: utf-8 -*-

import math

import numpy as np
from tabulate import tabulate


def water_balance_checker(df, dict_param, iters, verbose=False):
    """
    checks whether water balance is closed both over entire area and over measure itself
    """

    # check water balance over entire area:
    print("Water balance statistics: ")
    warning_msgs = []

    # precipitation over entire area
    sum_prec = sum(df["P_atm"].iloc[1:])

    # evaporation of xx over entire area
    sum_evap_pr = (
        sum(df["e_atm_pr"].iloc[1:])
        * dict_param["pr_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_evap_cp = (
        sum(df["e_atm_cp"].iloc[1:])
        * dict_param["cp_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_evap_op = (
        sum(df["e_atm_op"].iloc[1:])
        * dict_param["op_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_evap_up = (
        sum(df["e_atm_up"].iloc[1:])
        * dict_param["up_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_evap_uz = (
        sum(df["t_atm_uz"].iloc[1:])
        * dict_param["uz_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_evap_ow = (
        sum(df["e_atm_ow"].iloc[1:])
        * dict_param["ow_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_evap_meas = (
        sum(df["e_atm_meas"].iloc[1:]) * dict_param["tot_meas_area"]
        + sum(df["t_atm_top_meas"].iloc[1:]) * dict_param["top_meas_area"]
        + sum(df["t_atm_btm_meas"].iloc[1:]) * dict_param["btm_meas_area"]
    ) / dict_param["tot_area"]
    sum_evap = (
        sum_evap_pr
        + sum_evap_cp
        + sum_evap_op
        + sum_evap_up
        + sum_evap_uz
        + sum_evap_ow
        + sum_evap_meas
    )

    # discharge to outside over entire area (added discharge of combined sewer system on 4-3-2020 by Shiyang)
    sum_q_out = (
        sum(df["q_ow_out"].iloc[1:]) * dict_param["ow_no_meas_area"]
        + sum(df["q_meas_out"].iloc[1:]) * dict_param["tot_meas_area"]
        + sum(df["q_mss_out"].iloc[1:]) * dict_param["tot_mss_area"]
    ) / dict_param["tot_area"]

    # seepage to deep groundwater over entire area
    sum_s_deepgw = (
        sum(df["s_gw_out"].iloc[1:])
        * dict_param["gw_no_meas_area"]
        / dict_param["tot_area"]
    )

    # change in storages over entire area:
    # change in storages in pr, cp, op, up and uz
    sum_ds_pr = (
        (df["intstor_pr"].iloc[-1] - df["intstor_pr"].iloc[0])
        * dict_param["pr_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_ds_cp = (
        (df["intstor_cp"].iloc[-1] - df["intstor_cp"].iloc[0])
        * dict_param["cp_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_ds_op = (
        (df["intstor_op"].iloc[-1] - df["intstor_op"].iloc[0])
        * dict_param["op_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_ds_up = (
        (df["fin_intstor_up"].iloc[-1] - df["fin_intstor_up"].iloc[0])
        * dict_param["up_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_ds_uz = (
        (df["theta_uz"].iloc[-1] - df["theta_uz"].iloc[0])
        * dict_param["uz_no_meas_area"]
        / dict_param["tot_area"]
    )

    # change in groundwater storage is a bit tricky to calculate
    storage_coef = df["sc_gw"]
    groundwater_level = df["gwl"]
    ds_gw = np.zeros_like(groundwater_level)
    for t in range(1, iters):
        ds_gw[t] = (
            1000 * storage_coef[t] * (groundwater_level[t - 1] - groundwater_level[t])
        )
    sum_ds_gw = sum(ds_gw) * dict_param["gw_no_meas_area"] / dict_param["tot_area"]
    sum_ds_gw_sl = (
        1000
        * (df["gwl_sl"].iloc[-1] - df["gwl_sl"].iloc[0])
        * dict_param["gw_no_meas_area"]
        / dict_param["tot_area"]
    )  # ? mark it here: after changing (old - new), still not working.

    # change in storage in sewer system
    sum_ds_swds = (
        (df["stor_swds"].iloc[-1] - df["stor_swds"].iloc[0])
        * dict_param["swds_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_ds_mss = (
        (df["stor_mss"].iloc[-1] - df["stor_mss"].iloc[0])
        * dict_param["mss_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_ds_ow = (
        1000
        * (df["owl"].iloc[-1] - df["owl"].iloc[0])
        * dict_param["ow_no_meas_area"]
        / dict_param["tot_area"]
    )
    sum_ds_meas = (
        (df["intstor_meas"].iloc[-1] - df["intstor_meas"].iloc[0])
        * dict_param["tot_meas_area"]
        + (df["fin_stor_top_meas"].iloc[-1] - df["fin_stor_top_meas"].iloc[0])
        * dict_param["top_meas_area"]
        + (df["fin_stor_btm_meas"].iloc[-1] - df["fin_stor_btm_meas"].iloc[0])
        * dict_param["btm_meas_area"]
    ) / dict_param["tot_area"]

    sum_ds = (
        sum_ds_pr
        + sum_ds_cp
        + sum_ds_op
        + sum_ds_up
        + sum_ds_uz
        + sum_ds_gw
        + sum_ds_gw_sl
        + sum_ds_swds
        + sum_ds_mss
        + sum_ds_ow
        + sum_ds_meas
    )

    # calculate the difference in water balance to check whether water balance is closed over entire area
    balance_diff = sum_prec - sum_evap - sum_q_out - sum_s_deepgw - sum_ds

    # statistics of entire model for logging
    stat_model = {
        "rain": round(sum_prec, 2),
        "evap": round(sum_evap, 2),
        "Q_out": round(sum_q_out, 2),
        "seepage": round(sum_s_deepgw, 2),
        "storage diff": round(sum_ds, 2),
        "balance diff": balance_diff,
    }
    if verbose:
        print("\n")
        print("Entire model:")
        # display in console the table of water balance statistics over entire area
        headers = [
            "rain[mm]",
            "evap[mm]",
            "Q_out[mm]",
            "seepage[mm]",
            "storage diff[mm]",
            "balance diff[mm]",
        ]
        table = [
            [
                round(sum_prec, 2),
                round(sum_evap, 2),
                round(sum_q_out, 2),
                round(sum_s_deepgw, 2),
                round(sum_ds, 2),
                balance_diff,
            ]
        ]
        print(tabulate(table, headers, tablefmt="presto"))

    if math.isclose(balance_diff, 0, abs_tol=0.000001):
        print("Water balance for entire model is closed.")
    else:
        warning_msg_model = (
            "WARNING: Water balance for entire model is NOT closed. Please recheck!"
        )
        print(warning_msg_model)
        warning_msgs.append(warning_msg_model)
        # raise SystemExit("WARNING: Water balance is NOT closed for entire model. Please recheck.")

    # check water balance for measure itself:
    # precipitation over measure itself
    p_meas = sum(df["prec_meas"].iloc[1:])

    # evaporation and changes in storage over measure
    try:
        e_meas = sum_evap_meas * dict_param["tot_area"] / dict_param["tot_meas_area"]
        ds_meas = sum_ds_meas * dict_param["tot_area"] / dict_param["tot_meas_area"]
    except ZeroDivisionError:
        e_meas = 0
        ds_meas = 0

    # total runoff from inflow area to measure
    r_inflowarea_meas = sum(df["sum_r_meas"].iloc[1:])
    # groundwater recharge from measure
    gw_rech_meas = sum(df["q_meas_gw"].iloc[1:])
    # open water recharge from measure
    ow_rech_meas = sum(df["q_meas_ow"].iloc[1:])
    # discharge to SWDS from measure
    q_swds = sum(df["q_meas_swds"].iloc[1:])
    # discharge to MSS from measure
    q_mss = sum(df["q_meas_mss"].iloc[1:])
    # discharge to Outside from measure
    q_out = sum(df["q_meas_out"].iloc[1:])

    # calculate the difference in water balance to check whether water balance is closed over measure itself
    balance_diff_meas = (
        p_meas
        - e_meas
        + r_inflowarea_meas
        - gw_rech_meas
        - ow_rech_meas
        - q_swds
        - q_mss
        - q_out
        - (ds_meas)
    )

    # statistics of measure for logging
    stat_meas = {
        "rain": round(p_meas, 2),
        "evap": round(e_meas, 2),
        "inflow runoff": round(r_inflowarea_meas, 2),
        "GW.rech": round(gw_rech_meas, 2),
        "OW.rech": round(ow_rech_meas, 2),
        "Q_swds": round(q_swds, 2),
        "Q_mss": round(q_mss, 2),
        "Q_out": round(q_out, 2),
        "storage diff": round(ds_meas, 2),
        "balance diff": balance_diff_meas,
    }

    if verbose:
        print("\n")
        print("Measure itself:")
        # display in console the table of water balance statistics for measure itself
        headers_m = [
            "rain[mm]",
            "evap[mm]",
            "inflow runoff[mm]",
            "OW.rech[mm]",
            "Q_swds[mm]",
            "Q_mss[mm]",
            "Q_Out[mm]",
            "GW.rech[mm]",
            "storage diff[mm]",
            "balance diff[mm]",
        ]
        table_m = [
            [
                round(p_meas, 2),
                round(e_meas, 2),
                round(r_inflowarea_meas, 2),
                round(ow_rech_meas, 2),
                round(q_swds, 2),
                round(q_mss, 2),
                round(gw_rech_meas, 2),
                round(q_out, 2),
                round(ds_meas, 2),
                balance_diff_meas,
            ]
        ]
        print(tabulate(table_m, headers_m, tablefmt="presto"))

    if math.isclose(balance_diff_meas, 0, abs_tol=0.000001):
        print("Water balance is closed for measure itself.")
    else:
        warning_msg_measure = (
            "WARNING: Water balance for measure itself is NOT closed. Please recheck!"
        )
        print(warning_msg_measure)
        warning_msgs.append(warning_msg_measure)
        # raise SystemExit("Water balance for measure is not closed. Please recheck.")

    # check water balance for measure inflow area:
    try:
        # precipitation over measure inflow area
        p_mia = sum_prec

        # evaporation from measure inflow area
        e_mia = (
            sum(df["e_atm_meas"].iloc[1:]) * dict_param["tot_meas_area"]
            + sum(df["t_atm_top_meas"].iloc[1:]) * dict_param["top_meas_area"]
            + sum(df["t_atm_btm_meas"].iloc[1:] * dict_param["btm_meas_area"])
            + sum(df["e_atm_pr"].iloc[1:])
            * (dict_param["pr_meas_inflow_area"] - dict_param["pr_meas_area"])
            + sum(df["e_atm_cp"].iloc[1:])
            * (dict_param["cp_meas_inflow_area"] - dict_param["cp_meas_area"])
            + sum(df["e_atm_op"].iloc[1:])
            * (dict_param["op_meas_inflow_area"] - dict_param["op_meas_area"])
            + sum(df["e_atm_up"].iloc[1:])
            * (dict_param["up_meas_inflow_area"] - dict_param["up_meas_area"])
            + sum(df["e_atm_ow"].iloc[1:])
            * (dict_param["ow_meas_inflow_area"] - dict_param["ow_meas_area"])
        ) / dict_param["tot_meas_inflow_area"]

        # change in storages from measure inflow area
        ds_mia = (
            (df["intstor_pr"].iloc[-1] - df["intstor_pr"].iloc[0])
            * (dict_param["pr_meas_inflow_area"] - dict_param["pr_meas_area"])
            + (df["intstor_cp"].iloc[-1] - df["intstor_cp"].iloc[0])
            * (dict_param["cp_meas_inflow_area"] - dict_param["cp_meas_area"])
            + (df["intstor_op"].iloc[-1] - df["intstor_op"].iloc[0])
            * (dict_param["op_meas_inflow_area"] - dict_param["op_meas_area"])
            + (df["fin_intstor_up"].iloc[-1] - df["fin_intstor_up"].iloc[0])
            * (dict_param["up_meas_inflow_area"] - dict_param["up_meas_area"])
            + 1000
            * (df["owl"].iloc[-1] - df["owl"].iloc[0])
            * (dict_param["ow_meas_inflow_area"] - dict_param["ow_meas_area"])
            + (df["intstor_meas"].iloc[-1] - df["intstor_meas"].iloc[0])
            * (dict_param["tot_meas_area"])
            + (df["fin_stor_top_meas"].iloc[-1] - df["fin_stor_top_meas"].iloc[0])
            * (dict_param["top_meas_area"])
            + (df["fin_stor_btm_meas"].iloc[-1] - df["fin_stor_btm_meas"].iloc[0])
            * (dict_param["btm_meas_area"])
        ) / dict_param["tot_meas_inflow_area"]

        # open water recharge from measure inflow area
        ow_rech_meas_mia = (
            ow_rech_meas
            * dict_param["tot_meas_area"]
            / dict_param["tot_meas_inflow_area"]
        )
        # groundwater recharge from measure inflow area
        gw_rech_meas_mia = (
            gw_rech_meas
            * dict_param["tot_meas_area"]
            / dict_param["tot_meas_inflow_area"]
        )
        # discharge to SWDS from measure inflow area
        q_swds_meas_mia = (
            q_swds * dict_param["tot_meas_area"] / dict_param["tot_meas_inflow_area"]
        )
        # discharge to MSS from measure inflow area
        q_mss_meas_mia = (
            q_mss * dict_param["tot_meas_area"] / dict_param["tot_meas_inflow_area"]
        )
        # discharge to Outside from measure inflow area
        q_out_meas_mia = (
            q_out * dict_param["tot_meas_area"] / dict_param["tot_meas_inflow_area"]
        )

    except ZeroDivisionError:
        p_mia = e_mia = ds_mia = ow_rech_meas_mia = gw_rech_meas_mia = (
            q_swds_meas_mia
        ) = q_mss_meas_mia = q_out_meas_mia = 0.0

    # calculate the difference in water balance to check whether water balance is closed over measure inflow area
    balance_diff_mia = (
        p_mia
        - e_mia
        - ow_rech_meas_mia
        - gw_rech_meas_mia
        - q_swds_meas_mia
        - q_mss_meas_mia
        - ds_mia
        - q_out_meas_mia
    )

    stat_mia = {
        "rain": round(p_mia, 2),
        "evap": round(e_mia, 2),
        "GW.rech": round(gw_rech_meas_mia, 2),
        "OW.rech": round(ow_rech_meas_mia),
        "Q_swds": round(q_swds_meas_mia, 2),
        "Q_mss": round(q_mss_meas_mia, 2),
        "Q_Out": round(q_out_meas_mia, 2),
        "storage diff": round(ds_mia, 2),
        "balance diff": balance_diff_mia,
    }

    if verbose:
        print("\n")
        print("Measure inflow area:")
        # display in console the table of water balance statistics for measure inflow area
        headers_mia = [
            "rain[mm]",
            "evap[mm]",
            "GW.rech[mm]",
            "OW.rech[mm]",
            "Q_swds[mm]",
            "Q_mss[mm]",
            "Q_Out[mm]",
            "storage diff[mm]",
            "balance diff[mm]",
        ]
        table_mia = [
            [
                round(p_mia, 2),
                round(e_mia, 2),
                round(gw_rech_meas_mia, 2),
                round(ow_rech_meas_mia, 2),
                round(q_swds_meas_mia, 2),
                round(q_mss_meas_mia, 2),
                round(q_out_meas_mia, 2),
                round(ds_mia, 2),
                balance_diff_mia,
            ]
        ]
        print(tabulate(table_mia, headers_mia, tablefmt="presto"))

    if math.isclose(balance_diff_mia, 0, abs_tol=0.000001):
        print("Water balance is closed for measure inflow area.")
    else:
        warning_msg_mia = "WARNING: Water balance for measure inflow area is NOT closed. Please recheck!"
        print(warning_msg_mia)
        warning_msgs.append(warning_msg_mia)
        # raise SystemExit(warning_msg_mia)

    return stat_model, stat_meas, stat_mia, warning_msgs

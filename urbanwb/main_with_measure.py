#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import time
import fire
import logging
from urbanwb.setlogger import setuplog
import math
from pathlib import Path
from collections import OrderedDict
from tqdm import trange
from urbanwb.pavedroof import PavedRoof
from urbanwb.closedpaved import ClosedPaved
from urbanwb.openpaved import OpenPaved
from urbanwb.unpaved import Unpaved
from urbanwb.groundwater import Groundwater
from urbanwb.unsaturatedzone import UnsaturatedZone
from urbanwb.sewersystem import SewerSystem
from urbanwb.openwater import OpenWater
from urbanwb.selector import soil_selector
from urbanwb.gwlcalculator import gwlcalc
from urbanwb.read_parameter_base import read_parameter_base
from urbanwb.read_parameter_measure import read_parameter_measure
from urbanwb.measure import Measure
from urbanwb.waterbalance_checker import water_balance_checker
from time import sleep
from urbanwb.sdf_curve import SDF_curve2


class BasicModel(object):
    """
    Creates an instance from Basic Model (without measure) class which consists of all eight components namely paved roof, closed paved,
    open paved, unpaved, unsaturated zone, groundwater, sewer system and open water. Iterates __next__() as time
    stepping to get solutions for all time steps.

    Args:
        dict_param (dictionary): A dictionary of necessary parameters read from neighbourhood and measure configuration
        files to initialize a basic model instance
    """

    def __init__(self, dict_param):
        self.param = dict_param
        self.pavedroof = PavedRoof(**self.param)
        self.closedpaved = ClosedPaved(**self.param)
        self.openpaved = OpenPaved(**self.param)
        self.unpaved = Unpaved(**self.param)
        self.unsaturatedzone = UnsaturatedZone(
            theta_uz_t0=soil_selector(self.param["soiltype"], self.param["croptype"])[
                gwlcalc(self.param["gwl_t0"])[2]
            ]["moist_cont_eq_rz[mm]"],
            **self.param
        )
        self.groundwater = Groundwater(**self.param)
        self.sewersystem = SewerSystem(**self.param)
        self.openwater = OpenWater(**self.param)
        self.measure = Measure(k_sat_uz=self.unsaturatedzone.k_sat_uz, **self.param)

    def __iter__(self):
        return self

    def __next__(
        self,
        p_atm,
        e_pot_ow,
        ref_grass,
        prev_lst,
    ):
        """
        Calculates storage, fluxes, coefficients and other required outcomes at current time step.
        """
        try:
            # empty dictionary
            pr_sol = self.pavedroof.sol(p_atm=p_atm, e_pot_ow=e_pot_ow)
            cp_sol = self.closedpaved.sol(p_atm=p_atm, e_pot_ow=e_pot_ow)
            op_sol = self.openpaved.sol(
                p_atm=p_atm, e_pot_ow=e_pot_ow, delta_t=self.param["delta_t"]
            )
            up_sol = self.unpaved.sol(
                p_atm=p_atm,
                e_pot_ow=e_pot_ow,
                r_pr_up=pr_sol["r_pr_up"],
                r_cp_up=cp_sol["r_cp_up"],
                r_op_up=op_sol["r_op_up"],
                theta_uz_prevt=prev_lst["theta_uz"],
                pr_no_meas_area=self.param["pr_no_meas_area"],
                cp_no_meas_area=self.param["cp_no_meas_area"],
                op_no_meas_area=self.param["op_no_meas_area"],
                ow_no_meas_area=self.param["ow_no_meas_area"],
                delta_t=self.param["delta_t"],
            )
            meas_sol = self.measure.sol(p_atm=p_atm, e_pot_ow=e_pot_ow, r_pr_meas=pr_sol["r_pr_meas"], r_cp_meas=cp_sol["r_cp_meas"],
                                        r_op_meas=op_sol["r_op_meas"], r_up_meas=up_sol["r_up_meas"], pr_no_meas_area=self.param["tot_pr_area"]-self.param["pr_meas_area"],
                                        cp_no_meas_area=self.param["cp_no_meas_area"], op_no_meas_area=self.param["op_no_meas_area"],
                                        up_no_meas_area=self.param["up_no_meas_area"], gw_no_meas_area=self.param["gw_no_meas_area"],
                                        gwl_prevt=prev_lst["gwl"], delta_t=self.param["delta_t"])
            uz_sol = self.unsaturatedzone.sol(
                i_up_uz=up_sol["i_up_uz"],
                meas_uz=meas_sol["q_meas_uz"],  # meas_sol["q_meas_uz"]
                tot_meas_area=self.param["tot_meas_area"],
                e_ref=ref_grass,
                gwl_prevt=prev_lst["gwl"],
                delta_t=self.param["delta_t"],
            )
            gw_sol = self.groundwater.sol(
                p_uz_gw=uz_sol["p_uz_gw"],
                uz_no_meas_area=self.param["uz_no_meas_area"],
                p_op_gw=op_sol["p_op_gw"],
                op_no_meas_area=self.param["op_no_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
                meas_gw=meas_sol["q_meas_gw"],  # meas_sol["q_meas_gw"]
                owl_prevt=prev_lst["owl"],
                delta_t=self.param["delta_t"],
            )
            ss_sol = self.sewersystem.sol(
                pr_no_meas_area=self.param["pr_no_meas_area"],
                cp_no_meas_area=self.param["cp_no_meas_area"],
                op_no_meas_area=self.param["op_no_meas_area"],
                r_pr_swds=pr_sol["r_pr_swds"],
                r_cp_swds=cp_sol["r_cp_swds"],
                r_op_swds=op_sol["r_op_swds"],
                r_pr_mss=pr_sol["r_pr_mss"],
                r_cp_mss=cp_sol["r_cp_mss"],
                r_op_mss=op_sol["r_op_mss"],
                meas_swds=meas_sol["q_meas_swds"],  # meas_sol["q_meas_swds"]
                meas_mss=meas_sol["q_meas_mss"],  # meas_sol["q_meas_mss"]
                ow_no_meas_area=self.param["ow_no_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
            )
            ow_sol = self.openwater.sol(
                p_atm=p_atm,
                e_pot_ow=e_pot_ow,
                r_up_ow=up_sol["r_up_ow"],
                d_gw_ow=gw_sol["d_gw_ow"],
                q_swds_ow=ss_sol["q_swds_ow"],
                q_mss_ow=ss_sol["q_mss_ow"],
                so_swds_ow=ss_sol["so_swds_ow"],
                so_mss_ow=ss_sol["so_mss_ow"],
                meas_ow=meas_sol["q_meas_ow"],  #meas_sol["q_meas_ow"]
                up_no_meas_area=self.param["up_no_meas_area"],
                gw_no_meas_area=self.param["gw_no_meas_area"],
                swds_no_meas_area=self.param["swds_no_meas_area"],
                mss_no_meas_area=self.param["mss_no_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
                tot_area=self.param["tot_area"],
                delta_t=self.param["delta_t"],
            )

            dictmerged = OrderedDict(dict(pr_sol, **cp_sol, **op_sol, **up_sol, **uz_sol, **gw_sol, **ss_sol, **ow_sol, **meas_sol))  # newly added line.
        except IndexError:
            raise StopIteration
        return dictmerged


def read_inputdata(dyn_inp):
    """
    reads input data (time series of precipitation and evaporation) from dynamic input file.

    Args:
        dyn_inp (string): the filename of the input time series of precipitation and evaporation

    Returns:
        (dataframe): A dataframe of the time series of precipitation and evaporation
    """
    path = Path.cwd() / ".." / "input"

    # may add checker of the data here.
    return pd.read_csv(str(path) + "\\" + dyn_inp)


def read_parameters(stat1_inp, stat2_inp):
    """
    reads parameters for Model initialization through calling "read_parameter_base" to read parameters from
    neighbourhood configuration file and "read_parameter_measure" to read parameters from measure configuration file.

    Args:
        stat1_inp (string): filename of neighbourhood configuration file
        stat2_inp (string): filename of measure configuration file

    Returns:
        (dictionary): A dictionary of all necessary parameters to initialize a Model
    """
    parameter_base = read_parameter_base(stat1_inp)
    parameter_measure = read_parameter_measure(stat2_inp)
    d = dict(pr_no_meas_area=parameter_base["tot_pr_area"] - parameter_measure["pr_meas_area"],
             cp_no_meas_area=parameter_base["tot_cp_area"] - parameter_measure["cp_meas_area"],
             op_no_meas_area=parameter_base["tot_op_area"] - parameter_measure["op_meas_area"],
             up_no_meas_area=parameter_base["tot_up_area"] - parameter_measure["up_meas_area"],
             uz_no_meas_area=parameter_base["tot_uz_area"] - parameter_measure["uz_meas_area"],
             gw_no_meas_area=parameter_base["tot_gw_area"] - parameter_measure["gw_meas_area"],
             swds_no_meas_area=parameter_base["tot_swds_area"] - parameter_measure["swds_meas_area"],
             mss_no_meas_area=parameter_base["tot_mss_area"] - parameter_measure["mss_meas_area"],
             ow_no_meas_area=parameter_base["tot_ow_area"] - parameter_measure["ow_meas_area"],
             )
    rv = {**parameter_base, **parameter_measure, **d}
    # print(rv)
    return rv


def check_parameters(dict_param):
    """
    used in batch_run_measure() where simulations go from "with measure" cases to "without measure" baseline case in
    order to make sure all area-related parameters are correctly modified
    """
    if not dict_param["measure_applied"]:
        # update area-related parameters
        # measure inflow area
        dict_param["pr_meas_inflow_area"] = dict_param["cp_meas_inflow_area"] = dict_param["op_meas_inflow_area"] = \
            dict_param["up_meas_inflow_area"] = dict_param["ow_meas_inflow_area"] = 0.0
        # area of xx with measure
        dict_param["pr_meas_area"] = dict_param["cp_meas_area"] = dict_param["op_meas_area"] = \
            dict_param["up_meas_area"] = dict_param["uz_meas_area"] = dict_param["gw_meas_area"] = \
            dict_param["swds_meas_area"] = dict_param["mss_meas_area"] = dict_param["ow_meas_area"] = 0.0
        # area of interception layer, top storage layer and bottom storage layer of measure
        dict_param["tot_meas_area"] = dict_param["top_meas_area"] = dict_param["btm_meas_area"] = 0.0
    # print(dict_param)

    # dictionary of area of xx without measure
    d = dict(pr_no_meas_area=dict_param["tot_pr_area"] - dict_param["pr_meas_area"],
             cp_no_meas_area=dict_param["tot_cp_area"] - dict_param["cp_meas_area"],
             op_no_meas_area=dict_param["tot_op_area"] - dict_param["op_meas_area"],
             up_no_meas_area=dict_param["tot_up_area"] - dict_param["up_meas_area"],
             uz_no_meas_area=dict_param["tot_uz_area"] - dict_param["uz_meas_area"],
             gw_no_meas_area=dict_param["tot_gw_area"] - dict_param["gw_meas_area"],
             swds_no_meas_area=dict_param["tot_swds_area"] - dict_param["swds_meas_area"],
             mss_no_meas_area=dict_param["tot_mss_area"] - dict_param["mss_meas_area"],
             ow_no_meas_area=dict_param["tot_ow_area"] - dict_param["ow_meas_area"],
             )
    # update dict_param with values in d
    rv = {**dict_param, **d}
    return rv


def timer(func):
    """
    a decorator that timings the function runtime.
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        rv = func(*args, **kwargs)
        after = time.time()
        print(f"Elapsed: {after - start:.2f}s")
        return rv
    return wrapper


@timer
def running(input_data, dict_param):
    """
    takes input data from input file and parameters from configuration files to run simulation once.

    Args:
        input_data (dataframe): a fixed-format dataframe of the time series of precipitation and evaporation
        dict_param (dictionary): a dictionary of all necessary parameters to initialize a model

    Returns:
        (dataframe): A dataframe of computed results for all time steps
    """
    # global unit_list
    date = input_data["date"]
    P_atm = input_data["P_atm"]
    Ref_grass = input_data["Ref.grass"]
    E_pot_OW = input_data["E_pot_OW"]
    iters = np.shape(date)[0]
    # # print part of the dictionary
    # print("tot_area", dict_param["tot_area"])
    # print("tot_pr_area", dict_param["tot_pr_area"], "pr_no_meas_area", dict_param["pr_no_meas_area"], "pr_meas_area", dict_param["pr_meas_area"], "pr_meas_inflow_area", dict_param["pr_meas_inflow_area"])
    # print("tot_cp_area", dict_param["tot_cp_area"], "cp_no_meas_area", dict_param["cp_no_meas_area"], "cp_meas_area", dict_param["cp_meas_area"], "cp_meas_inflow_area", dict_param["cp_meas_inflow_area"])
    # print("tot_op_area", dict_param["tot_op_area"], "op_no_meas_area", dict_param["op_no_meas_area"], "op_meas_area", dict_param["op_meas_area"], "op_meas_inflow_area", dict_param["op_meas_inflow_area"])
    # print("tot_up_area", dict_param["tot_up_area"], "up_no_meas_area", dict_param["up_no_meas_area"], "up_meas_area", dict_param["up_meas_area"], "up_meas_inflow_area", dict_param["up_meas_inflow_area"])
    # print("tot_uz_area", dict_param["tot_uz_area"], "uz_no_meas_area", dict_param["uz_no_meas_area"], "uz_meas_area", dict_param["uz_meas_area"],)
    # print("tot_gw_area", dict_param["tot_gw_area"], "gw_no_meas_area", dict_param["gw_no_meas_area"], "gw_meas_area", dict_param["gw_meas_area"],)
    # print("tot_swds_area", dict_param["tot_swds_area"], "swds_no_meas_area", dict_param["swds_no_meas_area"], "swds_meas_area", dict_param["swds_meas_area"],)
    # print("tot_mss_area", dict_param["tot_mss_area"], "mss_no_meas_area", dict_param["mss_no_meas_area"], "mss_meas_area", dict_param["mss_meas_area"],)
    # print("tot_ow_area", dict_param["tot_ow_area"], "ow_no_meas_area", dict_param["ow_no_meas_area"], "ow_meas_area", dict_param["ow_meas_area"], "ow_meas_inflow_area", dict_param["ow_meas_inflow_area"])
    # print("tot_meas_area", dict_param["tot_meas_area"], "top_meas_area", dict_param["top_meas_area"], "btm_meas_area", dict_param["btm_meas_area"])
    k = BasicModel(dict_param)
    lst = [
        {
            "int_pr": np.nan,
            "e_atm_pr": np.nan,
            "intstor_pr": dict_param["intstor_pr_t0"],  # 0
            "r_pr_meas": np.nan,
            "r_pr_swds": np.nan,
            "r_pr_mss": np.nan,
            "r_pr_up": np.nan,
            "int_cp": np.nan,
            "e_atm_cp": np.nan,
            "intstor_cp": dict_param["intstor_cp_t0"],
            "r_cp_meas": np.nan,
            "r_cp_swds": np.nan,
            "r_cp_mss": np.nan,
            "r_cp_up": np.nan,
            "int_op": np.nan,
            "e_atm_op": np.nan,
            "intstor_op": dict_param["intstor_op_t0"],
            "p_op_gw": np.nan,
            "r_op_meas": np.nan,
            "r_op_swds": np.nan,
            "r_op_mss": np.nan,
            "r_op_up": np.nan,
            "sum_r_up": np.nan,
            "init_intstor_up": np.nan,
            "actl_infilcap_up": np.nan,
            "timefac_up": np.nan,
            "e_atm_up": np.nan,
            "i_up_uz": np.nan,
            "fin_intstor_up": dict_param["fin_intstor_up_t0"],
            "r_up_meas": np.nan,
            "r_up_ow": np.nan,
            "sum_i_uz": np.nan,
            "r_meas_uz": np.nan,
            "theta_h3_uz": np.nan,
            "t_alpha_uz": np.nan,
            "t_atm_uz": np.nan,
            "gwl_up": np.nan,
            "gwl_low": np.nan,
            "theta_eq_uz": np.nan,
            "capris_max_uz": np.nan,
            "p_uz_gw": np.nan,
            "theta_uz": soil_selector(dict_param["soiltype"], dict_param["croptype"])[
                gwlcalc(dict_param["gwl_t0"])[2]
            ]["moist_cont_eq_rz[mm]"],
            "sum_p_gw": np.nan,
            "r_meas_gw": np.nan,
            "sc_gw": soil_selector(dict_param["soiltype"], dict_param["croptype"])[
                gwlcalc(dict_param["gwl_t0"])[2]
            ]["stor_coef"],
            "h_gw": np.nan,
            "s_gw_out": np.nan,
            "d_gw_ow": np.nan,
            "gwl": dict_param["gwl_t0"],
            "gwl_sl": 0,
            "sum_r_swds": np.nan,
            "r_meas_swds": np.nan,
            "sum_r_mss": np.nan,
            "r_meas_mss": np.nan,
            "q_swds_ow": np.nan,
            "q_mss_out": np.nan,
            "q_mss_ow": np.nan,
            "so_swds_ow": dict_param["so_swds_t0"],
            "so_mss_ow": dict_param["so_mss_t0"],
            "stor_swds": dict_param["stor_swds_t0"],
            "stor_mss": dict_param["stor_mss_t0"],
            "prec_ow": np.nan,
            "e_atm_ow": np.nan,
            "sum_r_ow": np.nan,
            "sum_d_ow": np.nan,
            "sum_q_ow": np.nan,
            "sum_so_ow": np.nan,
            "r_meas_ow": np.nan,
            "q_ow_out": np.nan,
            "owl": dict_param["ow_level"],
            "prec_meas": np.nan,
            "sum_r_meas": np.nan,
            "int_meas": np.nan,
            "e_atm_meas": np.nan,
            "interc_down_meas": np.nan,
            "surf_runoff_meas": np.nan,
            "intstor_meas": dict_param["intstor_meas_t0"],
            "ini_stor_top_meas": np.nan,
            "t_atm_top_meas": np.nan,
            "perc_top_meas": np.nan,
            "fin_stor_top_meas": dict_param["stor_top_meas_t0"],
            "ini_stor_btm_meas": np.nan,
            "t_atm_btm_meas": np.nan,
            "p_gw_btm_meas": np.nan,
            "runoff_btm_meas": np.nan,
            "fin_stor_btm_meas": dict_param["stor_btm_meas_t0"],
            "overflow_btm_meas": np.nan,
            "q_meas_ow": np.nan,
            "q_meas_uz": np.nan,
            "q_meas_gw": np.nan,
            "q_meas_swds": np.nan,
            "q_meas_mss": np.nan,
            "q_meas_out": np.nan,
        }
    ]
    for t in trange(1, iters):  # time series first line is not relevant (initial), start from second line.
        lst.append(
            k.__next__(
            P_atm[t],
            E_pot_OW[t],
            Ref_grass[t],
            lst[t - 1],
                        )
                    )
    df = pd.DataFrame(lst)
    df.insert(0, "Date", date)
    df.insert(1, "P_atm", P_atm)
    df.insert(2, "E_pot_OW", E_pot_OW)
    df.insert(3, "Ref.grass", Ref_grass)
    wbc_results = water_balance_checker(df, dict_param, iters)
    return df, wbc_results  # df,stat

    # rv = running(inputdata, dict_param)
    # database.append(pd.DataFrame(rv[0])[variable_to_save]*dict_param["tot_meas_area"]/dict_param["tot_meas_inflow_area"])
    # logger.info(msg)
    # wbc_statistics = rv[1]
    # logger.info(f"Entire model: {wbc_statistics[0]}")
    # logger.info(f"Measure itself: {wbc_statistics[1]}")
    # logger.info(f"Measure' impact over measure inflow area: {wbc_statistics[2]}")


def save_to_csv(dyn_inp, stat1_inp, stat2_inp, output_filename, *args, save_all=True):
    """
    runs the simulation with three files (csv file of time series, configuration files of neighbourhood(base) and
    measure) and saves results in a csv file with the specified output filename under the 'pysol' folder.

    Args:
        dyn_inp (string): the filename of the dynamic input data of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        output_filename (string): the filename of the output file of solutions
        *args (strings): specified selected results to be saved
        save_all (bool): save all results when True, save specified selected results when False

    Returns:
        A csv file of all computed results
    """
    loggingfilename = ''.join(list(output_filename)[:-4]) + ".log"
    logger = setuplog(loggingfilename, "STC_logger", thelevel=logging.INFO)

    input_data = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)
    # logger.info(f"Single run, with parameters{dict_param}")  # too many parameters
    rv = running(input_data, dict_param)
    df = rv[0]
    wbc_statistics = rv[1]
    logger.info(f"Entire model: {wbc_statistics[0]}")
    logger.info(f"Measure itself: {wbc_statistics[1]}")
    if dict_param["tot_meas_area"] != 0:
        logger.info(f"Measure inflow area: {wbc_statistics[2]}")
    # print(dict_param)
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    if save_all:
        df.to_csv(outdir / output_filename, index=True)
    else:
        header = ["Date", "P_atm", "E_pot_OW", "Ref.grass"]
        header.extend([arg for arg in args])
        df.to_csv(outdir / output_filename, index=True, columns=header)


def batch_run(dyn_inp, stat1_inp, stat2_inp, dyn_out, varkey, *vararr):
    """
    this batch_run function is to batch-run specified parameter with a set of parameters and save all results in csv
    for every case.

    Args:
        dyn_inp (string): the filename of the inputdata of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        dyn_out (string): the general filename of the output file of solutions
        varkey (string): the parameter that needs to be updated in the batch run.
        vararr (float): values to update varkey.
    """
    import os
    param = {**read_parameter_base(stat1_inp), **read_parameter_measure(stat2_inp)}
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    for varval in vararr:
        param[str(varkey)] = varval
        df = run(param, dyn_inp)
        new_dyn_out = f"{varkey}={varval}_" + dyn_out
        fullname = os.path.join(outdir, new_dyn_out)
        df.to_csv(fullname, index=True)


def batch_run_save_to_csv1(dyn_inp, stat1_inp, stat2_inp, output_filename, param_to_change, *args):
    """
    this batch run function runs the model with a set of specified parameters and save all results in seperated csv"""

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    input_data = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)
    for arg in args:
        dict_param[param_to_change] = arg
        df = running(input_data, dict_param)[0]
        output = str(arg) + output_filename
        df.to_csv(outdir / output, index=True)

def batch_run_save_to_csv2(dyn_inp, stat1_inp, stat2_inp, output_filename, param_to_change, value_list, corresponding_varkey, value_list2):
    """
    this batch run function runs the model with a set of specified parameters and save all results in seperated csv"""

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    input_data = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)
    for x, y in zip(value_list, value_list2):
        dict_param[param_to_change] = x
        dict_param[corresponding_varkey] = y
        df = running(input_data, dict_param)[0]
        output = str(x) + output_filename
        df.to_csv(outdir / output, index=True)


# def batch_run2(dyn_inp, stat1_inp, stat2_inp, dyn_out, varkey, *vararr, *col, saveall=True):
#     """
#     this batch_run function is to batch-run specified parameter with a set of parameters and save all results in csv
#     for every case.
#
#     Args:
#         dyn_inp (string): the filename of the inputdata of precipitation and evaporation
#         stat1_inp (string): the filename of the static form of general parameters
#         stat2_inp (string): the filename of the static form of measure parameters
#         dyn_out (string): the general filename of the output file of solutions
#         varkey (string): the parameter that needs to be updated in the batch run.
#         vararr (float): values to update varkey.
#     """
#     import os
#     param = {**read_parameter_base(stat1_inp), **read_parameter_measure(stat2_inp)}
#     outdir = Path("pysol")
#     outdir.mkdir(parents=True, exist_ok=True)
#     for varval in vararr:
#         param[str(varkey)] = varval
#         df = run(param, dyn_inp)
#         new_dyn_out = f"{varkey}={varval}_" + dyn_out
#         fullname = os.path.join(outdir, new_dyn_out)
#         df.to_csv(fullname, index=True)


def batch_run_measure(dyn_inp, stat1_inp, stat2_inp, dyn_out, varkey, vararrlist1, correspvarkey=None, vararrlist2=None,
                      baseline_variable="r_op_swds", variable_to_save="q_meas_swds"):
    """
    batch run a series of simulations for one type of measure with various value for one parameter

    Args:
    dyn_inp (string): the filename of the inputdata of precipitation and evaporation
    stat1_inp (string): the filename of the static form of general parameters
    stat2_inp (string): the filename of the static form of measure parameters
    dyn_out (string): the filename of the output file of solutions
    varkey (float): the key parameter to be updated
    vararr (float): values to update varkey.

    Usage:
    use in the cmd: python -m urbanwb.main_with_measure batch_run_multivalue_for_one_param timeseries.csv stat1.ini stat2.ini results.csv storcap_btm_meas q_meas_swds 200 100 --inflowfac 20
    For now is is usable.
    """
    loggingfilename = ''.join(list(dyn_out)[:-4]) + ".log"
    logger = setuplog(loggingfilename, "BRM_logger", thelevel=logging.INFO)
    inputdata = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    # can delete this fraction if necessary.
    date = inputdata["date"]
    iters = np.shape(date)[0]
    dt = dict_param["delta_t"]
    num_year = round((dt * iters) / 365)
    print(f"Total year of the input time series is {num_year} year")
    print("\n")
    database = []
    if correspvarkey is not None:
        for a, b in zip(vararrlist1, vararrlist2):
            dict_param[varkey] = a
            dict_param[correspvarkey] = b
            measure_area_info = dict_param["tot_meas_area"]
            measure_inflow_area_info = dict_param["tot_meas_inflow_area"]
            msg = f"Case with measure: {varkey}={a}, {correspvarkey}={b}, measure area={measure_area_info}, " \
                f"inflow area={measure_inflow_area_info}"
            print(msg)
            rv = running(inputdata, dict_param)
            database.append(pd.DataFrame(rv[0])[variable_to_save]*dict_param["tot_meas_area"]/dict_param["tot_meas_inflow_area"])
            logger.info(msg)
            wbc_statistics = rv[1]
            logger.info(f"Entire model: {wbc_statistics[0]}")
            logger.info(f"Measure itself: {wbc_statistics[1]}")
            logger.info(f"Measure inflow area: {wbc_statistics[2]}")
            print("------" * 20)
            print("\n"*2)
            sleep(0.5)
    else:
        for a in vararrlist1:
            dict_param[varkey] = a
            measure_area_info = dict_param["tot_meas_area"]
            measure_inflow_area_info = dict_param["tot_meas_inflow_area"]
            msg = f"Case with measure: {varkey}={a},measure area={measure_area_info}, inflow area={measure_inflow_area_info}"
            print(msg)
            rv = running(inputdata, dict_param)
            database.append(pd.DataFrame(rv[0])[variable_to_save]*dict_param["tot_meas_area"]/dict_param["tot_meas_inflow_area"])
            logger.info(msg)
            wbc_statistics = rv[1]
            logger.info(f"Entire model: {wbc_statistics[0]}")
            logger.info(f"Measure itself: {wbc_statistics[1]}")
            logger.info(f"Measure inflow area: {wbc_statistics[2]}")
            print("------" * 20)
            print("\n" * 2)
            sleep(0.5)

    df = pd.DataFrame(database, index=[v for v in vararrlist1])
    df = df.T
    df.insert(0, "Date", date)
    df.insert(1, "P_atm", inputdata["P_atm"])

    dict_param["measure_applied"] = False
    # print(dict_param)
    msg = "Case without measure: Baseline"
    print(msg)
    rv = running(inputdata, check_parameters(dict_param))
    baseline_runoff = pd.DataFrame(rv[0])[baseline_variable]
    logger.info(msg)
    wbc_statistics = rv[1]
    logger.info(f"Entire model: {wbc_statistics[0]}")
    logger.info(f"Measure itself: {wbc_statistics[1]}")
    # logger.info(f"Measure' impact over measure inflow area: {wbc_statistics[2]}")
    print("------" * 20)
    sleep(0.5)
    df.insert(2, "Baseline", baseline_runoff)
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / dyn_out, index=True)


def batch_run_sdf(dyn_inp, stat1_inp, stat2_inp, dyn_out, typenumber=True, *vararr):
    """
    this batch_run function is mainly designed for getting the database for sdf_curve.

    Args:
        dyn_inp (string): the filename of the inputdata of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        dyn_out (string): the filename of the output file of solutions
        vararr (float): a list of values to update "q_ow_out_cap"

    """
    input_data = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    rank_database = []
    iters = len(input_data["date"])
    mean_daily_rainfall = np.mean(input_data["P_atm"])*24
    dt = dict_param["delta_t"]
    num_year = round((dt * iters) / 365)
    print(f"The length of input time series is around {num_year} year")
    print("First, do baseline run:")
    print(f"It is when pumping capacity equals mean daily rainfall {mean_daily_rainfall:.2f} mm/d to make fixed marks for other Q")
    dict_param["q_ow_out_cap"] = mean_daily_rainfall
    owl_data = np.append(running(input_data, dict_param)[0]["owl"], 0)
    owl_baseline = np.ones(len(owl_data)) * dict_param["ow_level"] - owl_data
    segment_marks = get_segment_index(owl_baseline)
    k_base = SDF_curve2(segment_marks, owl_data, ow_level=dict_param["ow_level"])
    rank_database.append(k_base.ranking)
    # print(segment_marks)
    print("-----"*20)
    if typenumber:
        print(vararr)
        for varval in vararr:
            dict_param["q_ow_out_cap"] = varval
            print(f"pumping capacity from open water to outside is {varval} mm/d over entire area")
            owl_data = pd.DataFrame(running(input_data, dict_param)[0])["owl"]
            k = SDF_curve2(segment_marks, owl_data, ow_level=dict_param["ow_level"])
            rank_database.append(k.ranking)
            print(f"Maximum storage height above target water level over open water for Q = {varval} mm/d is {k.ranking[0]:.4f} m")
            print("-----"*20)

        name_of_index = [f"{mean_daily_rainfall:.2f}"] + [f"{v}" for v in vararr]
        df = pd.DataFrame(rank_database, index=name_of_index)
        outdir = Path("pysol")
        outdir.mkdir(parents=True, exist_ok=True)
        df.T.to_csv(outdir / dyn_out, index=True)

    else:
        if len(vararr) != 3:
            raise SystemExit("Please type in min, max, steps.")
        array_num = np.arange(vararr[0], vararr[1]+1, (vararr[1] - vararr[0])/vararr[2])
        print(array_num)
        for val in array_num:
            dict_param["q_ow_out_cap"] = val
            print(f"pumping capacity from open water to outside is {val} mm/d over entire area")
            owl_data = pd.DataFrame(running(input_data, dict_param)[0])["owl"]
            k = SDF_curve2(segment_marks, owl_data, ow_level=dict_param["ow_level"])
            rank_database.append(k.ranking)
            print(
                f"Maximum storage height above target water level over open water for Q = {val} mm/d is {k.ranking[0]:.4f} m")
            print("-----" * 20)

        name_of_index = [f"{mean_daily_rainfall:.2f}"] + [f"{v}" for v in array_num]
        df = pd.DataFrame(rank_database, index=name_of_index)
        outdir = Path("pysol")
        outdir.mkdir(parents=True, exist_ok=True)
        df.T.to_csv(outdir / dyn_out, index=True)



from functools import reduce
from itertools import groupby

def running_counter(source_list):
    "function calculates, following the list sequence how many times a number is repeated"
    return [(k, sum(1 for i in g)) for k,g in groupby(source_list)]


def get_segment_index(owl):

    interim = np.zeros_like(owl)
    for i in range(len(owl)):
        if owl[i] != 0:
            interim[i] = 1
    count_list = running_counter(interim)

    # test numbers of timesteps match or not
    empty = []
    for element in count_list:
        empty.append(element[1])
    if reduce((lambda x, y: x + y), empty) != len(owl):
        raise SystemExit("number of time steps does not match.")

    # analyze the count_list to get the index of segments.
    t = 0
    segment_index = [0]
    base_index = 0
    while t <= len(count_list) - 1:
        if t % 2 == 0:
            segment_index.append(count_list[t][1] + base_index)
        base_index += count_list[t][1]
        t += 1
    return segment_index


if __name__ == "__main__":
    fire.Fire()


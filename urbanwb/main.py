#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from collections import OrderedDict
from pathlib import Path

import fire
import numpy as np
import pandas as pd
import toml
from tqdm import tqdm

from urbanwb.closedpaved import ClosedPaved
from urbanwb.groundwater import Groundwater
from urbanwb.gwlcalculator import gwlcalc
from urbanwb.measure import Measure
from urbanwb.openpaved import OpenPaved
from urbanwb.openwater import OpenWater
from urbanwb.pavedroof import PavedRoof
from urbanwb.read_parameter_base import read_parameter_base
from urbanwb.read_parameter_measure import (
    read_parameter_measure,
    read_parameter_measure_csv,
)
from urbanwb.sdf_curve import SDF_curve2, get_segment_index
from urbanwb.selector import soil_selector
from urbanwb.setlogger import setuplog
from urbanwb.sewersystem import SewerSystem
from urbanwb.unpaved import Unpaved
from urbanwb.unsaturatedzone import UnsaturatedZone
from urbanwb.waterbalance_checker import water_balance_checker


class UrbanwbModel(object):
    """
    Creates an instance of UrbanwbModel class which consists of all eight components namely paved roof,  closed paved,
    open paved, unpaved, unsaturated zone, groundwater, sewer system and open water together with measure module.
    Iterates __next__() as time stepping to get solutions for all time steps.

    Args:
        dict_param (dictionary): A dictionary of necessary parameters read from neighbourhood config file and measure
        config file to initialize a model instance
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
            **self.param,
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
        lst_prevt,
    ):
        """
        Calculates storage, fluxes, coefficients and other related results at current time step.
        """
        try:
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
                theta_uz_prevt=lst_prevt["theta_uz"],
                pr_no_meas_area=self.param["pr_no_meas_area"],
                cp_no_meas_area=self.param["cp_no_meas_area"],
                op_no_meas_area=self.param["op_no_meas_area"],
                ow_no_meas_area=self.param["ow_no_meas_area"],
                delta_t=self.param["delta_t"],
            )
            meas_sol = self.measure.sol(
                p_atm=p_atm,
                e_pot_ow=e_pot_ow,
                r_pr_meas=pr_sol["r_pr_meas"],
                r_cp_meas=cp_sol["r_cp_meas"],
                r_op_meas=op_sol["r_op_meas"],
                r_up_meas=up_sol["r_up_meas"],
                pr_no_meas_area=self.param["pr_no_meas_area"],
                cp_no_meas_area=self.param["cp_no_meas_area"],
                op_no_meas_area=self.param["op_no_meas_area"],
                up_no_meas_area=self.param["up_no_meas_area"],
                gw_no_meas_area=self.param["gw_no_meas_area"],
                gwl_prevt=lst_prevt["gwl"],
                delta_t=self.param["delta_t"],
            )
            uz_sol = self.unsaturatedzone.sol(
                i_up_uz=up_sol["i_up_uz"],
                meas_uz=meas_sol["q_meas_uz"],
                tot_meas_area=self.param["tot_meas_area"],
                e_ref=ref_grass,
                gwl_prevt=lst_prevt["gwl"],
                delta_t=self.param["delta_t"],
            )
            gw_sol = self.groundwater.sol(
                p_uz_gw=uz_sol["p_uz_gw"],
                uz_no_meas_area=self.param["uz_no_meas_area"],
                p_op_gw=op_sol["p_op_gw"],
                op_no_meas_area=self.param["op_no_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
                meas_gw=meas_sol["q_meas_gw"],
                owl_prevt=lst_prevt["owl"],
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
                meas_swds=meas_sol["q_meas_swds"],
                meas_mss=meas_sol["q_meas_mss"],
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
                meas_ow=meas_sol["q_meas_ow"],
                up_no_meas_area=self.param["up_no_meas_area"],
                gw_no_meas_area=self.param["gw_no_meas_area"],
                swds_no_meas_area=self.param["swds_no_meas_area"],
                mss_no_meas_area=self.param["mss_no_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
                tot_area=self.param["tot_area"],
                delta_t=self.param["delta_t"],
            )
            merged_dict = OrderedDict(
                dict(
                    **pr_sol,
                    **cp_sol,
                    **op_sol,
                    **up_sol,
                    **uz_sol,
                    **gw_sol,
                    **ss_sol,
                    **ow_sol,
                    **meas_sol,
                )
            )
        except IndexError:
            raise StopIteration
        return merged_dict


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


def read_inputdata(dyn_inp):
    """
    reads input data (time series of precipitation and evaporation) from dynamic input file.

    Args:
        dyn_inp (string): the filename of the input time series of precipitation and evaporation

    Returns:
        (dataframe): A dataframe of the time series of precipitation and evaporation
    """
    path = Path.cwd() / ".." / "input"

    # Parsing 30-year date data as datetime will takes additional 25 seconds.
    # Besides, the actual user-defined datetime format can be problematic.
    # Therefore, date is not parsed as datetime here.
    # rv = pd.read_csv(str(path) + "\\" + dyn_inp, parse_dates=["date"], dayfirst=True)
    rv = pd.read_csv(str(path) + "\\" + dyn_inp)

    # check if there is missing value in the input time series.
    num_nan = rv.isnull().sum().sum()
    if num_nan != 0:
        raise SystemExit(
            f"There are {num_nan} missing values in time series. Please recheck input time series file."
        )
    return rv


def read_parameters(stat1_inp, stat2_inp):
    """
    reads parameters for model initialization by calling "read_parameter_base" to read parameters from neighbourhood
    configuration file, calling "read_parameter_measure" to read parameters from measure configuration file, and
    computing area of xx without measure with given parameters.

    Args:
        stat1_inp (string): filename of neighbourhood configuration file
        stat2_inp (string): filename of measure configuration file

    Returns:
        (dictionary): A dictionary of all necessary parameters to initialize a model
    """
    parameter_base = read_parameter_base(stat1_inp)
    parameter_measure = read_parameter_measure(stat2_inp)
    d = dict(
        pr_no_meas_area=parameter_base["tot_pr_area"]
        - parameter_measure["pr_meas_area"],
        cp_no_meas_area=parameter_base["tot_cp_area"]
        - parameter_measure["cp_meas_area"],
        op_no_meas_area=parameter_base["tot_op_area"]
        - parameter_measure["op_meas_area"],
        up_no_meas_area=parameter_base["tot_up_area"]
        - parameter_measure["up_meas_area"],
        uz_no_meas_area=parameter_base["tot_uz_area"]
        - parameter_measure["uz_meas_area"],
        gw_no_meas_area=parameter_base["tot_gw_area"]
        - parameter_measure["gw_meas_area"],
        swds_no_meas_area=parameter_base["tot_swds_area"]
        - parameter_measure["swds_meas_area"],
        mss_no_meas_area=parameter_base["tot_mss_area"]
        - parameter_measure["mss_meas_area"],
        ow_no_meas_area=parameter_base["tot_ow_area"]
        - parameter_measure["ow_meas_area"],
    )
    rv = {**parameter_base, **parameter_measure, **d}
    return rv


def read_parameters_csv(stat1_inp, measure_id, neighbourhood_id, apply_measure=True):
    """
    reads parameters for model initialization by calling "read_parameter_base" to read parameters from neighbourhood
    configuration file, calling "read_parameter_measure" to read parameters from measure configuration file, and
    computing area of xx without measure with given parameters.

    Args:
        stat1_inp (string): filename of neighbourhood configuration file
        measure_id (string): id of measure
        neighbourhood_id (string): id of neighbourhood type

    Returns:
        (dictionary): A dictionary of all necessary parameters to initialize a model
    """
    # TODO consolidate with read_parameters above, or possibly eliminate
    path = Path.cwd() / ".." / "input"
    cf = toml.load(str(path) + "\\" + stat1_inp, _dict=dict)
    # Edit the parameters in the catchment configuration accordingly to the neighbourhood type
    # TODO remove hardcoded path
    neighbourhood_pars = pd.read_csv("../input/Parameters neighbourhoods.csv")
    idx_neighbourhood = np.where(neighbourhood_pars["id_type"] == neighbourhood_id)[0][
        0
    ]
    for key in neighbourhood_pars:
        cf[key] = neighbourhood_pars[key][idx_neighbourhood]

    parameter_base = read_parameter_base(cf)
    parameter_measure = read_parameter_measure_csv(
        measure_id, parameter_base, apply_measure
    )

    d = dict(
        pr_no_meas_area=parameter_base["tot_pr_area"]
        - parameter_measure["pr_meas_area"],
        cp_no_meas_area=parameter_base["tot_cp_area"]
        - parameter_measure["cp_meas_area"],
        op_no_meas_area=parameter_base["tot_op_area"]
        - parameter_measure["op_meas_area"],
        up_no_meas_area=parameter_base["tot_up_area"]
        - parameter_measure["up_meas_area"],
        uz_no_meas_area=parameter_base["tot_uz_area"]
        - parameter_measure["uz_meas_area"],
        gw_no_meas_area=parameter_base["tot_gw_area"]
        - parameter_measure["gw_meas_area"],
        swds_no_meas_area=parameter_base["tot_swds_area"]
        - parameter_measure["swds_meas_area"],
        mss_no_meas_area=parameter_base["tot_mss_area"]
        - parameter_measure["mss_meas_area"],
        ow_no_meas_area=parameter_base["tot_ow_area"]
        - parameter_measure["ow_meas_area"],
    )
    rv = {**parameter_base, **parameter_measure, **d}
    return rv


def read_parameters_exception(
    stat1_inp, measure_title, neighbourhood_id, apply_measure
):
    """
    reads parameters for model initialization by calling "read_parameter_base" to read parameters from neighbourhood
    configuration file, calling "read_parameter_measure" to read parameters from measure configuration file, and
    computing area of xx without measure with given parameters.

    Args:
        stat1_inp (string): filename of neighbourhood configuration file
        stat2_inp (string): filename of measure configuration file

    Returns:
        (dictionary): A dictionary of all necessary parameters to initialize a model
    """
    # TODO consolidate with read_parameters above, or possibly eliminate
    path = Path.cwd() / ".." / "input"
    cf = toml.load(str(path) + "\\" + stat1_inp, _dict=dict)
    # Edit the parameters in the catchment configuration accordingly to the neighbourhood type
    # TODO remove hardcoded path
    neighbourhood_pars = pd.read_csv("../input/Parameters neighbourhoods.csv")
    idx_neighbourhood = np.where(neighbourhood_pars["id_type"] == neighbourhood_id)[0][
        0
    ]
    for key in neighbourhood_pars:
        cf[key] = neighbourhood_pars[key][idx_neighbourhood]

    measures_exception = pd.read_excel(
        "../input/Parameters measures exception.xlsx", sheet_name=None
    )
    for key in measures_exception[measure_title]:
        if key == "title":
            pass
        else:
            if key in cf:
                cf[key] = measures_exception[measure_title][key][0]
            elif key == "change_op_to_up":
                if measures_exception[measure_title][key][0] == True:
                    cf["up_frac"] += cf["op_frac"]
                    cf["op_frac"] = 0
                else:
                    pass
            elif key == "extra_ow_height":
                cf["storcap_ow"] += measures_exception[measure_title][key][0]
            elif key == "extra_ow_frac":
                cf["up_frac"] -= measures_exception[measure_title][key][0]
                cf["ow_frac"] += measures_exception[measure_title][key][0]

    parameter_base = read_parameter_base(cf)
    parameter_measure = read_parameter_measure_csv(
        measure_title, parameter_base, apply_measure
    )
    parameter_measure["title"] = measures_exception[measure_title]["title"][0]

    d = dict(
        pr_no_meas_area=parameter_base["tot_pr_area"]
        - parameter_measure["pr_meas_area"],
        cp_no_meas_area=parameter_base["tot_cp_area"]
        - parameter_measure["cp_meas_area"],
        op_no_meas_area=parameter_base["tot_op_area"]
        - parameter_measure["op_meas_area"],
        up_no_meas_area=parameter_base["tot_up_area"]
        - parameter_measure["up_meas_area"],
        uz_no_meas_area=parameter_base["tot_uz_area"]
        - parameter_measure["uz_meas_area"],
        gw_no_meas_area=parameter_base["tot_gw_area"]
        - parameter_measure["gw_meas_area"],
        swds_no_meas_area=parameter_base["tot_swds_area"]
        - parameter_measure["swds_meas_area"],
        mss_no_meas_area=parameter_base["tot_mss_area"]
        - parameter_measure["mss_meas_area"],
        ow_no_meas_area=parameter_base["tot_ow_area"]
        - parameter_measure["ow_meas_area"],
    )
    rv = {**parameter_base, **parameter_measure, **d}
    return rv


def check_parameters(dict_param):
    """
    especially used in batch_run_measure() when the simulation switches from "with measure" cases to "without measure",
    i.e. the baseline case, in order to make sure all area-related parameters are correctly modified accordingly.

    Args:
        dict_param (dictionary): a dictionary of parameters to initialize a model, which needs to be checked.

    Returns:
        (dictionary): A dictionary of all necessary parameters to initialize a model
    """
    if dict_param["measure_applied"]:
        return dict_param
    else:
        # update area-related parameters:
        # measure inflow area
        dict_param["pr_meas_inflow_area"] = dict_param[
            "cp_meas_inflow_area"
        ] = dict_param["op_meas_inflow_area"] = dict_param[
            "up_meas_inflow_area"
        ] = dict_param[
            "ow_meas_inflow_area"
        ] = 0.0
        dict_param["tot_meas_inflow_area"] = 0.0
        # area of xx with measure
        dict_param["pr_meas_area"] = dict_param["cp_meas_area"] = dict_param[
            "op_meas_area"
        ] = dict_param["up_meas_area"] = dict_param["uz_meas_area"] = dict_param[
            "gw_meas_area"
        ] = dict_param[
            "swds_meas_area"
        ] = dict_param[
            "mss_meas_area"
        ] = dict_param[
            "ow_meas_area"
        ] = 0.0
        # area of interception layer, top storage layer, and bottom storage layer of measure
        dict_param["tot_meas_area"] = dict_param["top_meas_area"] = dict_param[
            "btm_meas_area"
        ] = 0.0
        # print(dict_param)

        # dictionary of area of xx without measure
        d = dict(
            pr_no_meas_area=dict_param["tot_pr_area"] - dict_param["pr_meas_area"],
            cp_no_meas_area=dict_param["tot_cp_area"] - dict_param["cp_meas_area"],
            op_no_meas_area=dict_param["tot_op_area"] - dict_param["op_meas_area"],
            up_no_meas_area=dict_param["tot_up_area"] - dict_param["up_meas_area"],
            uz_no_meas_area=dict_param["tot_uz_area"] - dict_param["uz_meas_area"],
            gw_no_meas_area=dict_param["tot_gw_area"] - dict_param["gw_meas_area"],
            swds_no_meas_area=dict_param["tot_swds_area"]
            - dict_param["swds_meas_area"],
            mss_no_meas_area=dict_param["tot_mss_area"] - dict_param["mss_meas_area"],
            ow_no_meas_area=dict_param["tot_ow_area"] - dict_param["ow_meas_area"],
        )
        # updates dict_param with values in d
        rv = {**dict_param, **d}
        return rv


def running(input_data, dict_param):
    """
    a basic running unit, which takes the forcing from input_data and the parameters from a dictionary of parameters to
    run the simulation once and returns all the results in a dataframe. After calculation, the water balance for the
    entire model, measure itself, and measure inflow area is checked and the corresponding statistics is returned.

    Args:
        input_data (dataframe): a fixed-format dataframe of time series of forcing (precipitation and evaporation)
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
    # # print area-related parameters in the dictionary for checking. Uncomment it when necessary.
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

    # create an instance of the UrbanwbModel class
    k = UrbanwbModel(dict_param)
    # first row of dataframe that stores initial values
    lst = [
        {
            "int_pr": np.nan,
            "e_atm_pr": np.nan,
            "intstor_pr": dict_param["intstor_pr_t0"],
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
            # "uncontrolled_runoff": np.nan,
            # "controlled_runoff": np.nan,
            # "total_runoff": np.nan
        }
    ]
    # time series first line is not relevant, computation starts from the second line.
    for t in tqdm(range(1, iters)):
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
    return df, wbc_results


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
        A csv file of all (or part of) computed results
    """
    loggingfilename = "".join(list(output_filename)[:-4]) + ".log"
    logger = setuplog(loggingfilename, "STC_logger", thelevel=logging.INFO)

    input_data = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)
    rv = running(input_data, dict_param)
    df = rv[0]
    wbc_statistics = rv[1]
    # logging the water balance for entire model
    logger.info(f"Entire model: {wbc_statistics[0]}")
    # logging the water balance for measure itself
    logger.info(f"Measure itself: {wbc_statistics[1]}")

    # if measure is applied, logging the water balance for measure inflow area
    if dict_param["tot_meas_area"] != 0:
        logger.info(f"Measure inflow area: {wbc_statistics[2]}")

    # if warning messages is not empty, logging the warning message
    if len(wbc_statistics[3]) != 0:
        logger.warning(wbc_statistics[3])

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    # logging the info regarding saving
    if save_all:
        msg = f"Saving all results to {output_filename}..."
    else:
        msg = f"Saving results {args} to {output_filename}..."
    logger.info(msg)
    print(msg)

    if save_all:
        df.to_csv(outdir / output_filename, index=True)
    else:
        header = ["Date", "P_atm", "E_pot_OW", "Ref.grass"]
        header.extend([arg for arg in args])
        df.to_csv(outdir / output_filename, index=True, columns=header)


def batch_run_measure(
    dyn_inp,
    stat1_inp,
    stat2_inp,
    dyn_out,
    varkey,
    vararrlist1,
    correspvarkey=None,
    vararrlist2=None,
    baseline_variable="r_op_swds",
    variable_to_save="q_meas_swds",
):
    """
    for one type of measure, run a batch of simulations with different values for one (or two) parameter(s)

    Args:
    dyn_inp (string): the filename of the inputdata of precipitation and evaporation
    stat1_inp (string): the filename of the static form of general parameters
    stat2_inp (string): the filename of the static form of measure parameters
    dyn_out (string): the filename of the output file of solutions
    varkey (float): the key parameter to be updated
    vararr (float): values to update varkey

    Usage:
    use in the cmd: python -m urbanwb.main batch_run_measure timeseries.csv stat1.ini stat2.ini results.csv storcap_btm_meas [20,30,40]
    """
    loggingfilename = "".join(list(dyn_out)[:-4]) + ".log"
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
    nameofmeasure = dict_param["title"]
    msg_nameofmeasure = f"Current running {nameofmeasure}"
    logger.info(msg_nameofmeasure)
    print(msg_nameofmeasure)
    print("\n")
    database = []
    if correspvarkey is not None:
        for a, b in zip(vararrlist1, vararrlist2):
            dict_param[varkey] = a
            dict_param[correspvarkey] = b
            measure_area_info = dict_param["tot_meas_area"]
            measure_inflow_area_info = dict_param["tot_meas_inflow_area"]
            msg = (
                f"Case with measure: {varkey}={a}, {correspvarkey}={b}, measure area={measure_area_info}, "
                f"inflow area={measure_inflow_area_info}"
            )
            print(msg)
            rv = running(inputdata, dict_param)
            database.append(
                pd.DataFrame(rv[0])[variable_to_save]
                * dict_param["tot_meas_area"]
                / dict_param["tot_meas_inflow_area"]
            )
            logger.info(msg)
            wbc_statistics = rv[1]
            logger.info(f"Entire model: {wbc_statistics[0]}")
            logger.info(f"Measure itself: {wbc_statistics[1]}")
            logger.info(f"Measure inflow area: {wbc_statistics[2]}")
            print("------" * 20)
            print("\n" * 2)
    else:
        for a in vararrlist1:
            dict_param[varkey] = a
            measure_area_info = dict_param["tot_meas_area"]
            measure_inflow_area_info = dict_param["tot_meas_inflow_area"]
            msg = f"Case with measure: {varkey}={a},measure area={measure_area_info}, inflow area={measure_inflow_area_info}"
            print(msg)
            rv = running(inputdata, dict_param)
            database.append(
                pd.DataFrame(rv[0])[variable_to_save]
                * dict_param["tot_meas_area"]
                / dict_param["tot_meas_inflow_area"]
            )
            logger.info(msg)
            wbc_statistics = rv[1]
            logger.info(f"Entire model: {wbc_statistics[0]}")
            logger.info(f"Measure itself: {wbc_statistics[1]}")
            logger.info(f"Measure inflow area: {wbc_statistics[2]}")
            print("------" * 20)
            print("\n" * 2)

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
    df.insert(2, "Baseline", baseline_runoff)
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / dyn_out, index=True)
    return df


def batch_run_sdf(
    dyn_inp,
    stat1_inp,
    stat2_inp,
    dyn_out,
    q_list,
    baseline_q=None,
    arithmetic_progression=False,
):
    """
    this batch_run function is mainly designed for getting the database for sdf_curve.

    Args:
        dyn_inp (string): the filename of the inputdata of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        dyn_out (string): the filename of the output file of solutions
        q_list (float): a list of values to update "q_ow_out_cap"
        baseline_q (float): default baseline q is mean daily rainfall if baseline_q not explicitly defined
        arithmetic_progression (bool): default is False meaning q_list is a list of random number; when explicitly
        defined True, q_list is (min,max,steps)

    """
    # TODO reduce printing
    # determine logfile name based on outputfile name
    loggingfilename = "".join(list(dyn_out)[:-4]) + ".log"
    logger = setuplog(loggingfilename, "BRSDF_logger", thelevel=logging.INFO)
    input_data = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    rank_database = []
    iters = len(input_data["date"])
    dt = dict_param["delta_t"]
    mean_daily_rainfall = np.mean(input_data["P_atm"]) / dt
    num_year = round((dt * iters) / 365)
    print(f"The length of input time series is around {num_year} year")
    print(f"Mean daily rainfall is {mean_daily_rainfall:.2f} mm/d")
    print("First, do baseline run:")

    if baseline_q is None:
        dict_param["q_ow_out_cap"] = mean_daily_rainfall
        msg0 = f"Baseline pumping capacity is by default set as mean daily rainfall {mean_daily_rainfall:.2f} mm/d to make fixed marks"
        logger.info(msg0)
        print(msg0)
    else:
        msg0 = f"Baseline pumping capacity is {baseline_q} mm/d to make fixed marks"
        dict_param["q_ow_out_cap"] = baseline_q
        logger.info(msg0)
        print(msg0)

    # perform baseline run
    owl_data = np.append(
        running(input_data, dict_param)[0]["owl"], 0
    )  # extra 0 at the end
    owl_baseline = np.ones(len(owl_data)) * dict_param["ow_level"] - owl_data
    segment_marks = get_segment_index(owl_baseline)
    k_base = SDF_curve2(segment_marks, owl_data, ow_level=dict_param["ow_level"])
    rank_database.append(k_base.ranking)
    # print(segment_marks)
    print("-----" * 50)
    if not arithmetic_progression:  # if it is random number to type in.
        print(f"q value to batch run: {q_list}")
        for q in q_list:
            dict_param["q_ow_out_cap"] = q
            msg1 = f"Running: pumping capacity from open water to outside is {q} mm/d over entire area"
            print(msg1)
            logger.info(msg1)
            rv = running(input_data, dict_param)
            wbc_statistics = rv[1]
            # logging the water balance for entire model
            logger.info(f"Entire model: {wbc_statistics[0]}")
            # logging the water balance for measure itself
            logger.info(f"Measure itself: {wbc_statistics[1]}")
            # if measure is applied, logging the water balance for measure inflow area
            if dict_param["tot_meas_area"] != 0:
                logger.info(f"Measure inflow area: {wbc_statistics[2]}")
            # if warning messages is not empty, logging the warning message
            if len(wbc_statistics[3]) != 0:
                logger.warning(wbc_statistics[3])
            owl_data = pd.DataFrame(rv[0])["owl"]
            k = SDF_curve2(segment_marks, owl_data, ow_level=dict_param["ow_level"])
            rank_database.append(k.ranking)
            msg2 = f"Maximum storage height above target water level over open water for Q = {q} mm/d is {k.ranking[0]:.4f} m"
            print(msg2)
            logger.info(msg2)
            print("-----" * 50)
        if baseline_q is None:
            name_of_index = [f"{mean_daily_rainfall:.2f}"] + [f"{v}" for v in q_list]
        else:
            name_of_index = [f"{baseline_q:.2f}"] + [f"{v}" for v in q_list]
        df = pd.DataFrame(rank_database, index=name_of_index)
        outdir = Path("pysol")
        outdir.mkdir(parents=True, exist_ok=True)
        df.T.to_csv(outdir / dyn_out, index=True)
        return df

    else:  # if we type in an arithmetic progression
        if len(q_list) != 3:
            raise SystemExit("Please type in min, max, steps.")
        array_q = np.arange(
            q_list[0], q_list[1] + 1, (q_list[1] - q_list[0]) / q_list[2]
        )
        print(f"q value to batch run are {array_q}")
        for q in array_q:
            dict_param["q_ow_out_cap"] = q
            msg1 = f"Running: pumping capacity from open water to outside is {q} mm/d over entire area"
            print(msg1)
            logger.info(msg1)
            rv = running(input_data, dict_param)
            wbc_statistics = rv[1]
            # logging the water balance for entire model
            logger.info(f"Entire model: {wbc_statistics[0]}")
            # logging the water balance for measure itself
            logger.info(f"Measure itself: {wbc_statistics[1]}")
            # if measure is applied, logging the water balance for measure inflow area
            if dict_param["tot_meas_area"] != 0:
                logger.info(f"Measure inflow area: {wbc_statistics[2]}")
            # if warning messages is not empty, logging the warning message
            if len(wbc_statistics[3]) != 0:
                logger.warning(wbc_statistics[3])
            owl_data = pd.DataFrame(rv[0])["owl"]
            k = SDF_curve2(segment_marks, owl_data, ow_level=dict_param["ow_level"])
            rank_database.append(k.ranking)
            msg2 = f"Maximum storage height above target water level over open water for Q = {q} mm/d is {k.ranking[0]:.4f} m"
            print(msg2)
            logger.info(msg2)
            print("-----" * 40)

        if baseline_q is None:
            name_of_index = [f"{mean_daily_rainfall:.2f}"] + [f"{v}" for v in array_q]
        else:
            name_of_index = [f"{baseline_q:.2f}"] + [f"{v}" for v in array_q]

        df = pd.DataFrame(rank_database, index=name_of_index)
        outdir = Path("pysol")
        outdir.mkdir(parents=True, exist_ok=True)
        df.T.to_csv(outdir / dyn_out, index=True)
        return df


if __name__ == "__main__":
    # provide an auto generated cli based on the functions in this file
    fire.Fire()

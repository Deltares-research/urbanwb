#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math
import time
from collections import OrderedDict
from pathlib import Path
from time import sleep

import fire
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import toml
from tqdm import trange

from urbanwb.closedpaved import ClosedPaved
from urbanwb.groundwater import Groundwater
from urbanwb.gwlcalculator import gwlcalc
from urbanwb.main import (UrbanwbModel, batch_run_measure, batch_run_sdf,
                          check_parameters, read_inputdata, read_parameters,
                          running, save_to_csv)
from urbanwb.measure import Measure
from urbanwb.openpaved import OpenPaved
from urbanwb.openwater import OpenWater
from urbanwb.pavedroof import PavedRoof
from urbanwb.read_parameter_base import read_parameter_base
from urbanwb.read_parameter_measure import (read_parameter_measure,
                                            read_parameter_measure_csv)
from urbanwb.sdf_curve import SDF_curve2, get_segment_index
from urbanwb.selector import soil_selector
from urbanwb.setlogger import setuplog
from urbanwb.sewersystem import SewerSystem
from urbanwb.unpaved import Unpaved
from urbanwb.unsaturatedzone import UnsaturatedZone
from urbanwb.waterbalance_checker import water_balance_checker

# =============================================================================
# Following part is all for the function 'getconstants'
#
# Edited: Added an 'if' that when the runoff reduction factor exceeds the 1000,
# it will give give 1000.
# =============================================================================


def making_marks(precipitation):
    """
    Make the marks by separating rainfall events by six consecutive hours without precipitation

    Args:
        precipitation (series): a series ("P_atm" column) of the dataframe

    Return:
        (numpy.ndarray): an array of corresponding marks for separating precipitation time series
    """
    # Create an empty array.
    mark = np.zeros_like(precipitation)
    # Specify values to this mark array.
    for i in range(len(precipitation)):
        if i < 6:
            mark[i] = 0
        else:
            if precipitation[i] > 0:
                if sum(precipitation[i - 6 : i]) > 0:
                    mark[i] = mark[i - 1]
                else:
                    mark[i] = mark[i - 1] + 1
            else:
                mark[i] = mark[i - 1]
    return mark


def ranking(df, x, num):
    """
    According to the event mark, get the sum of x for each event, and then rank the sum from highest to lowest.

    Args:
        df (dataframe): a dataframe to do computations on
        x (string): a header of the dataframe
        num (integer): the total number of events

    Returns:
        (numpy.ndarray): an array of values ranked in a descending order
    """
    rank = np.zeros(num)
    for i in range(num):
        rank[i] = sum(df[df.mark == i][x])
    return sorted(rank, reverse=True)


def removekey(d, *keys):
    """
    Remove keys in the dictionary

    Args:
        d (dictionary): a dictionary to be modified
        keys (string): keys in the dictionary to be removed

    Returns:
        (dictionary): a modified dictionary
    """
    r = dict(d)
    for _ in keys:
        del r[_]
    return r


def find_corresponding_T_for_array(
    t_array, array, vararr=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]
):
    """
    Compute corresponding return period T (i.e. T=1/P, P is the probability of exceedance) for a certain return value in
    an array through linear interpolation, in order to compute an averaged value as runoff frequency reduction factor
    (The algorithm can be modified with the new code in the jupyter notebook despite the same results)

    Args:
        t_array ()
    Returns:
    """
    database = []
    for var in vararr:
        # print(var, 'case:')
        t_value = 0.0
        try:
            for counter, value in enumerate(array):
                if value < var:
                    # print(value)
                    v_below = array[counter]
                    v_above = array[counter - 1]
                    # print('v-above', counter-1, v_above)
                    # print('v-below', counter, v_below)
                    # print('---'*6)
                    t_up = t_array[counter - 1]
                    t_below = t_array[counter]
                    # print('T-up', t_up)
                    # print('T-below', t_below)
                    t_value = t_up - (v_above - var) / (v_above - v_below) * (
                        t_up - t_below
                    )
                    # print('T_value', t_value)
                    break
        except KeyError:
            # print('below',counter, array[counter])
            # print('above',counter, array[counter])
            t_value = math.inf
        finally:
            database.append(t_value)
    return database


def getconstants_measures(data, num_year=30):
    """
    Get the constant --- Runoff frequency reduction factor averaged over several specified runoff return value.

    Args:
        inputfilename (string): filename of the runoff time series resulted from the urbanwb model
        num_year (integer): total number of years of the time series
    """
    m = Analyse(data, num_year=num_year)
    results = m.getconstants()
    mean_constants = []
    for key in results.keys():
        new_var_array = []
        var_array = results[key]
        for var in var_array:
            if var < 2000:
                new_var_array.append(var)
        if new_var_array is not None:
            mean_constants.append(np.round(np.mean(new_var_array), 2))
    for i in range(len(mean_constants)):
        if np.isnan(mean_constants[i]) == True or mean_constants[i] > 1000:
            mean_constants[i] = 1000
        else:
            pass
    else:
        pass

    # if there is no change in runoff, then reduction factor = 0 (e.g. at implementing on unpaved when he unpaved area already has no runoff)
    if data[data.keys()[3]].sum() == data["Baseline"].sum():
        mean_constants = [1]
    return results, mean_constants


class Analyse(object):
    """
    Integrate all functions, basically functioning, requiring further development
    """

    def __init__(
        self,
        data,
        num_year=30,
    ):
        self.output_name = "results_measures.csv"
        self.df = data
        self.df = self.df.fillna(0)
        self.dictionary = self.df.to_dict("list")
        self.num_year = num_year

        # making event marks according to precipitation (6 consective zeros as separation)
        self.df["mark"] = making_marks(self.df["P_atm"])
        self.measure_dictionary = removekey(
            self.dictionary, "Date", "P_atm", "Baseline"
        )
        self.makingranks = self.makingranks()

    def getconstants(
        self,
    ):  # consider changing function name to avoid confusion.
        pass
        #        print(["storage cap mm", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50])
        emp = dict()
        baseT = find_corresponding_T_for_array(
            t_array=self.makingranks["T_list"], array=self.makingranks["Rank_baseline"]
        )
        for key in self.makingranks.keys():
            if key not in ["Rank_P", "T_list", "Rank_baseline"]:
                a = find_corresponding_T_for_array(
                    t_array=self.makingranks["T_list"], array=self.makingranks[key]
                )
                c = [y / x for x, y in zip(baseT, a)]
                emp[key] = c
                np.mean(c)
        return emp

    def save_constants(self):
        pass

    def makingranks(
        self,
    ):
        # unchanged, I made a mistake here, should be self.emp rather than emp. Not a big problem.
        emp = dict()
        emp["Rank_P"] = ranking(self.df, "P_atm", int(max(self.df.mark) + 1))
        # create T list (30 yr, thus starting from (30+1/1) according to Weibull formula)
        emp["T_list"] = [
            (self.num_year + 1) / m for m in range(1, len(emp["Rank_P"]) + 1)
        ]
        # rank runoff on the baseline case
        emp["Rank_baseline"] = ranking(self.df, "Baseline", int(max(self.df.mark) + 1))
        for key in self.measure_dictionary.keys():
            emp[key] = ranking(self.df, key, int(max(self.df.mark) + 1))
        data = pd.DataFrame.from_dict(emp)
        return data

    def save_to_csv(
        self,
    ):
        self.makingranks.to_csv(self.output_name)

    def plotting(
        self,
        measure_name,
        addition_name,
        xlim_down=0,
        xlim_up=40,
    ):
        self.data = self.makingranks

        plt.figure(figsize=(9, 6))
        plt.semilogy(
            self.data.Rank_P, self.data.T_list, "b--", label="Precipitation", ms=2
        )
        plt.semilogy(
            self.data.Rank_baseline, self.data.T_list, "k-", label="Baseline", ms=2
        )
        measures_rank_dictionary = removekey(
            self.data.to_dict("list"), "Rank_P", "Rank_baseline", "T_list"
        )

        for key in measures_rank_dictionary.keys():
            plt.semilogy(
                measures_rank_dictionary[key], self.data.T_list, label=key, ms=2
            )

        x = np.linspace(0, 100, 200)
        # plt.legend(loc='best',frameon=False)
        plt.legend(loc="upper right", frameon=True)
        plt.xlabel("Runoff (mm)")
        plt.ylabel("T (year)")
        plt.title(measure_name + "(1981-2011)")
        plt.xlim(xlim_down, xlim_up)

        # add grid
        ax = plt.gca()
        ax.yaxis.grid(linestyle="--", linewidth=0.5, which="both")
        ax.xaxis.grid(linestyle="--", linewidth=0.5, which="both")

        # plt.savefig("figures/" + addition_name + measure_name + ".png")


# =============================================================================
# The following functions are edited from 'uwbmb_functions.py'
#
# Mainly, the functions have been edited to read .csv files instead of .ini.
# This allows for the user to give a list of measures as input in one overview.
# =============================================================================


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

    path = Path.cwd() / ".." / "input"
    cf = toml.load(str(path) + "\\" + stat1_inp, _dict=dict)
    # Edit the parameters in the catchment configuration accordingly to the neighbourhood type
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
    # print(rv)
    return rv


@timer
def run_measures(
    dyn_inp,
    stat1_inp,
    measure_id,
    neighbourhood_id,
    dyn_out,
    base_run,
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

    inputdata = read_inputdata(dyn_inp)
    dict_param = read_parameters_csv(stat1_inp, measure_id, neighbourhood_id)

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    date = inputdata["date"]

    nameofmeasure = dict_param["title"]
    msg_nameofmeasure = (
        f"Currently running Neighbourhood {str(neighbourhood_id)} - {nameofmeasure}"
    )
    print(msg_nameofmeasure)

    database_runoff = []
    database_gw = []
    database_evap = []
    if correspvarkey is not None:
        for a, b in zip(vararrlist1, vararrlist2):
            dict_param[varkey] = a
            dict_param[correspvarkey] = b

            rv = running(inputdata, dict_param)
            results = pd.DataFrame(rv[0])  # Model variables results
            wbc_results = rv[
                1
            ]  # Water Balance values: rv[1][0] = entire model, rv[1][1] = measure itself, rv[1][2] = measure inflow area

            avg_p_gw = (
                results["p_op_gw"].sum() * dict_param["op_no_meas_area"]
                + results["q_meas_gw"].sum() * dict_param["tot_meas_area"]
                + results["p_uz_gw"].sum() * dict_param["tot_uz_area"]
            ) / dict_param["tot_gw_area"]

            # Obtain the values of runoff, evaporation and gw recharge of the measure
            database_runoff.append(
                results[variable_to_save]
                * dict_param["tot_meas_area"]
                / dict_param["tot_meas_inflow_area"]
            )
            database_gw.append(avg_p_gw)
            database_evap.append(wbc_results[0]["evap"])
    else:
        for a in vararrlist1:
            dict_param[varkey] = a

            rv = running(inputdata, dict_param)
            results = pd.DataFrame(rv[0])  # Model variables results
            wbc_results = rv[
                1
            ]  # Water Balance values: rv[1][0] = entire model, rv[1][1] = measure itself, rv[1][2] = measure inflow area

            avg_p_gw = (
                results["p_op_gw"].sum() * dict_param["op_no_meas_area"]
                + results["q_meas_gw"].sum() * dict_param["tot_meas_area"]
                + results["p_uz_gw"].sum() * dict_param["tot_uz_area"]
            ) / dict_param["tot_gw_area"]

            # Obtain the values of runoff, evaporation and gw recharge of the measure
            runoff = (
                results[variable_to_save]
                * dict_param["tot_meas_area"]
                / dict_param["tot_meas_inflow_area"]
            )
            database_runoff.append(runoff)
            database_gw.append(avg_p_gw)
            database_evap.append(wbc_results[0]["evap"])

    # Dataframe: runoff
    df_runoff = pd.DataFrame(database_runoff, index=[v for v in vararrlist1])
    df_runoff = df_runoff.T
    df_runoff.insert(0, "Date", date)
    df_runoff.insert(1, "P_atm", inputdata["P_atm"])

    # Dataframe: groundwater recharge
    df_gw = pd.DataFrame(database_gw, index=[v for v in vararrlist1])
    df_gw = df_gw.T

    # Dataframe: evaporation
    df_evap = pd.DataFrame(database_evap, index=[v for v in vararrlist1])
    df_evap = df_evap.T

    results_base = pd.DataFrame(base_run[0])  # Model variables results
    wbc_results_base = base_run[1]  # Water Balance values for the entire model

    # Obtain the values of runoff, evaporation and gw recharge of the baseline
    baseline_runoff = results_base[baseline_variable]
    baseline_gw = results_base["sum_p_gw"].sum()
    baseline_evap = wbc_results_base[0]["evap"]

    df_runoff.insert(2, "Baseline", baseline_runoff)
    df_gw.insert(0, "Baseline", baseline_gw)
    df_evap.insert(0, "Baseline", baseline_evap)

    return df_runoff, df_gw, df_evap


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
    path = Path.cwd() / ".." / "input"
    cf = toml.load(str(path) + "\\" + stat1_inp, _dict=dict)
    # Edit the parameters in the catchment configuration accordingly to the neighbourhood type
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
    # print(rv)
    return rv


# This function implements the measure by changing the catchment properties instead of using measure parameters as input
def run_measures_exception(
    dyn_inp,
    stat1_inp,
    measure_title,
    neighbourhood_id,
    base_run,
    baseline_variable,
    variable_to_save,
):
    inputdata = read_inputdata(dyn_inp)
    dict_param = read_parameters_exception(
        stat1_inp, measure_title, neighbourhood_id, apply_measure=False
    )  # Apply measure is False here, as we change the catchment properties rather than implement an extra measure element

    date = inputdata["date"]
    nameofmeasure = dict_param["title"]
    msg_nameofmeasure = (
        f"Currently running Neighbourhood {str(neighbourhood_id)} - {nameofmeasure}"
    )
    print(msg_nameofmeasure)

    # Run the model with the new catchment properties
    rv = running(inputdata, dict_param)
    results = rv[0]
    wbc_results = rv[1]

    # Obtain runoff. In case of an urban forest, the open pavement is changed to unpaved. In order to compare the runoff values,
    # the added runoff to the unpaved needs to be calculated. This is then compared to the open paved runoff
    runoff = results[variable_to_save]

    # Dataframe: runoff
    df_runoff = pd.DataFrame(runoff)
    df_runoff.insert(0, "Date", date)
    df_runoff.insert(1, "P_atm", inputdata["P_atm"])

    # Dataframe: groundwater recharge
    gw = rv[0]["sum_p_gw"].sum()
    df_gw = pd.DataFrame([gw], columns=["alt"])

    # Dataframe: evaporation
    evap = wbc_results[0]["evap"]
    df_evap = pd.DataFrame([evap], columns=["alt"])

    # Baseline results for comparison
    results_base = pd.DataFrame(base_run[0])  # Model variables results
    wbc_results_base = base_run[1]  # Water Balance values for the entire model

    # Obtain the values of runoff, evaporation and gw recharge of the baseline
    baseline_runoff = results_base[baseline_variable]
    baseline_gw = results_base["sum_p_gw"].sum()
    baseline_evap = wbc_results_base[0]["evap"]

    # Place the baseline values in the dataframes of the effectivity variables
    df_runoff.insert(2, "Baseline", baseline_runoff)
    df_gw.insert(0, "Baseline", baseline_gw)
    df_evap.insert(0, "Baseline", baseline_evap)

    return df_runoff, df_gw, df_evap


if __name__ == "__main__":
    fire.Fire()

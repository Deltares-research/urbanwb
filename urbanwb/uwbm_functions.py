#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import pandas as pd

from urbanwb.main import (
    read_inputdata,
    read_parameters_csv,
    read_parameters_exception,
    running,
)


def run_measures(
    dyn_inp,
    stat1_inp,
    measure_id,
    neighbourhood_id,
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
    # TODO consolidate and posibly eliminate with the other run_measures functions
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

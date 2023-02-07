#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import fire
import numpy as np
import pandas as pd

from urbanwb.getconstants import getconstants_measures
from urbanwb.main import (
    read_inputdata,
    read_parameters_csv,
    read_parameters_exception,
    running,
)


def run_measures(
    dyn_inp,
    stat1_inp,
    measures_path,
    neighbourhood_pars_path,
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
    For one type of measure, run a batch of simulations with different values for one (or two) parameter(s)

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
    dict_param = read_parameters_csv(
        stat1_inp, measures_path, neighbourhood_pars_path, measure_id, neighbourhood_id
    )

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
    measures_path,
    measures_exception_path,
    neighbourhood_pars_path,
    measure_title,
    neighbourhood_id,
    base_run,
    baseline_variable,
    variable_to_save,
):
    # TODO consolidate and posibly eliminate with the other run_measures functions
    inputdata = read_inputdata(dyn_inp)
    dict_param = read_parameters_exception(
        stat1_inp,
        measures_path,
        measures_exception_path,
        neighbourhood_pars_path,
        measure_title,
        neighbourhood_id,
        apply_measure=False,
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


def run_all(
    # Rainfall & evaporation timeseries
    input_csv,
    # Catchment properties .ini file for the initial parameters
    catchment_properties,
    # Output file name (.xlsx (defined at bottom) gets added to it in the script, so this should be left out here)
    output_name,
    # .csv with the parameters for the measures (this file needs to be called exactly: Parameters measures.csv)
    measures_path,
    # .xlsx with the parameters for the measures which are implemented by adjusting the catchment properties
    measures_exception_path,
    # .csv with the parameters for the neighbourhood types (this file needs to be called exactly: Parameters neighbourhoods.csv)
    # (= possibilty to add different neighbourhoods, unlimited nr)
    neighbourhood_pars_path,
    D_eff=[5, 10, 20, 30, 40, 50, 100],
):
    # read files into dataframes
    measures = pd.read_csv(measures_path, index_col=0)
    measures_exception = pd.read_excel(measures_exception_path, sheet_name=None)
    neighbourhood_pars = pd.read_csv(neighbourhood_pars_path)

    D_eff_str = list(map(str, D_eff))
    # Create a list will all measures: '.csv measures' and the exceptions
    total_measures = list(measures.index)
    total_measures_titles = list(measures["title"])
    for i in measures_exception:
        total_measures.append(measures_exception[i]["id"][0])
        total_measures_titles.append(measures_exception[i]["title"][0])

    # Create DataFrames to store the results in
    df = pd.DataFrame(columns=["id", "Measure", *map(str, D_eff)])
    df["id"] = total_measures
    df["Measure"] = total_measures_titles

    df_runoff = df.copy()
    df_Ftot = df.copy()
    df_gw = df.copy()
    df_evap = df.copy()
    df_gw.insert(2, "Baseline", np.zeros(len(df_gw.index)))
    df_evap.insert(2, "Baseline", np.zeros(len(df_evap.index)))

    # Loop for each neighbourhood type in the 'Parameters neighbourhoods' file
    for n in range(len(neighbourhood_pars)):
        print("\n")
        neighbourhood_id = neighbourhood_pars["id_type"][n]

        # Base run: run the model without any measure implemented yet. This is needed to do a comparison between base and measure run.
        print("Currently running Neighbourhood " + str(n + 1) + " - Base run")
        inputdata = read_inputdata(input_csv)
        dict_param = read_parameters_csv(
            catchment_properties,
            measures_path,
            neighbourhood_pars_path,
            str(measures.index[0]),
            neighbourhood_id,
            apply_measure=False,
        )
        if dict_param["tot_up_area"] == 0 and np.any(measures["up_meas_area"] == 1):
            print(
                "error: measure"
                + str(measures[measures["up_meas_area"] == 1].title.values)
                + "cannot be applied in zero sized unpaved area!"
            )
            break
        if dict_param["tot_cp_area"] == 0 and np.any(measures["cp_meas_area"] == 1):
            print(
                "error: measure "
                + str(measures[measures["cp_meas_area"] == 1].title.values)
                + "cannot be applied in zero sized closed paved area!"
            )
            break
        if dict_param["tot_op_area"] == 0 and np.any(measures["op_meas_area"] == 1):
            print(
                "error: measure"
                + str(measures[measures["op_meas_area"] == 1].title.values)
                + "cannot be applied in zero sized open paved area!"
            )
            break
        if dict_param["tot_pr_area"] == 0 and np.any(measures["pr_meas_area"] == 1):
            print(
                "error: measure "
                + str(measures[measures["pr_meas_area"] == 1].title.values)
                + "cannot be applied in zero sized paved roof area!"
            )
            break
        base_run = running(inputdata, dict_param)

        # Calculate amount of paved- and unpaved area, required for the Ftot calculation
        Ap = (
            dict_param["tot_pr_area"]
            + dict_param["tot_cp_area"]
            + dict_param["tot_op_area"]
        )
        Aup = dict_param["tot_up_area"]

        # Fraction of runoff from unpaved compared to paved, required for the Ftot calculation.
        # This needs adjustments as the runoff sum difference may not be a good indication for the difference in peak runoff
        sum_Rp = (
            base_run[0]["r_cp_meas"].sum()
            + base_run[0]["r_cp_swds"].sum()
            + base_run[0]["r_cp_mss"].sum()
            + base_run[0]["r_cp_up"].sum()
        )
        sum_Rup = base_run[0]["r_up_ow"].sum() + base_run[0]["r_up_meas"].sum()
        frac_Rup_Rp = sum_Rup / sum_Rp

        # Loop for each measure in the 'Parameters measures' file
        for i in measures.index:
            measure_id = str(i)

            # Calculate depth measure based on the inflow factor and the effective depth. Currently, the default values for inflow factor are used.
            inflow_factor = measures["Ain_def"][i]
            D_meas = [x * inflow_factor for x in D_eff]

            # Measures with an base storage, such as wet ponds, should have the extra depth added to this base storage.
            if measures["stor_btm_meas_t0"][i] > 0:
                D_meas = [
                    x * inflow_factor + measures["stor_btm_meas_t0"][i] for x in D_eff
                ]

            # Determine the storage capacity parameter which needs to be changed depending on the amount of storage layers in the measure.
            # Green roofs (extensive) consists of three layers, however, are an exception where the top layer storage needs to be adjusted instead of the bottom layer storage.
            if int(measures["num_stor_lvl"][i]) == 1:
                varkey = "storcap_int_meas"
            elif measure_id in ["15", "16"]:
                varkey = "storcap_top_meas"
            elif int(measures["num_stor_lvl"][i]) > 1:
                varkey = "storcap_btm_meas"
            else:
                raise ValueError("Unknown measure id")

            # Determine the runoff variable which acts as a baseline. This is based on the source of the inflow for the measure: pr, cp, op, up, ow.
            if measures["pr_meas_inflow_area"][i] > 0:
                baseline_variable = "r_pr_swds"
                Ami = dict_param["tot_pr_area"]
            elif measures["cp_meas_inflow_area"][i] > 0:
                baseline_variable = "r_cp_swds"
                Ami = dict_param["tot_cp_area"]
            elif measures["op_meas_inflow_area"][i] > 0:
                baseline_variable = "r_op_swds"
                Ami = dict_param["tot_op_area"]
            elif measures["up_meas_inflow_area"][i] > 0:
                baseline_variable = "r_up_ow"
                Ami = dict_param["tot_up_area"]
            elif measures["ow_meas_inflow_area"][i] > 0:
                baseline_variable = "r_ow_swds"
                Ami = dict_param["tot_ow_area"]
            else:
                raise ValueError("Unknown measure area")

            # Determine variable_to_save for runoff based on the area where the uncontrolled runoff is discharged to
            if measures["surf_runoff_meas_OW"][i] == 1:
                variable_to_save = "q_meas_ow"
            elif measures["surf_runoff_meas_UZ"][i] == 1:
                variable_to_save = "q_meas_uz"
            elif measures["surf_runoff_meas_GW"][i] == 1:
                variable_to_save = "q_meas_gw"
            elif measures["surf_runoff_meas_SWDS"][i] == 1:
                variable_to_save = "q_meas_swds"
            elif measures["surf_runoff_meas_MSS"][i] == 1:
                variable_to_save = "q_meas_mss"
            elif measures["surf_runoff_meas_Out"][i] == 1:
                variable_to_save = "q_meas_out"
            else:
                raise ValueError("Unknown measure area")

            # Runoffcap_stor_dependent checks whether the runoff capacity of the measure depends on the storage capacity, e.g. in an underground storage or rain barrel
            if measures.loc[i]["runoffcap_stor_dependent"] == 1:
                runoffcap_factor = measures.loc[i]["runoffcap_stor_factor"]
                runoffcap_meas = [x * runoffcap_factor for x in D_meas]
                runoff, gw, evap = run_measures(
                    input_csv,
                    catchment_properties,
                    measures_path,
                    neighbourhood_pars_path,
                    measure_id,
                    neighbourhood_id,
                    base_run,
                    varkey=varkey,
                    vararrlist1=D_meas,
                    correspvarkey="runoffcap_btm_meas",
                    vararrlist2=runoffcap_meas,
                    baseline_variable=baseline_variable,
                    variable_to_save=variable_to_save,
                )
            else:
                runoff, gw, evap = run_measures(
                    input_csv,
                    catchment_properties,
                    measures_path,
                    neighbourhood_pars_path,
                    measure_id,
                    neighbourhood_id,
                    base_run,
                    varkey=varkey,
                    vararrlist1=D_meas,
                    correspvarkey=None,
                    vararrlist2=None,
                    baseline_variable=baseline_variable,
                    variable_to_save=variable_to_save,
                )

            num_years = (
                pd.to_datetime(runoff.Date[len(runoff.Date) - 1])
                - pd.to_datetime(runoff.Date[0])
            ).days / 365
            num_years = round(num_years)

            # 'getconstants_measures' calculates the runoff reduction factors for the measures at each effective depth
            constants_runoff, mean_constants_runoff = getconstants_measures(
                runoff, num_year=num_years
            )
            gw = round(gw / num_years, 2)
            evap = round(evap / num_years, 2)

            idx_measure = np.where(df_runoff.id == i)[0][0]
            df_runoff.loc[idx_measure, D_eff_str] = mean_constants_runoff
            df_gw.loc[idx_measure, ["Baseline"] + D_eff_str] = gw.values[0]
            df_gw.loc[idx_measure, D_eff_str] -= gw["Baseline"].values[0]
            df_evap.loc[idx_measure, ["Baseline"] + D_eff_str] = evap.values[0]
            df_evap.loc[idx_measure, D_eff_str] -= evap["Baseline"].values[0]

            # =============================================================================
            #     Calculate Ftot: Runoff reduction factor over the total area
            # =============================================================================

            # Calculate the Ftot according to the inflow area of the measure, assuming no measures are taken on unpaved or open water
            Fmeas = mean_constants_runoff
            df_Ftot.loc[idx_measure, D_eff_str] = np.round(
                (Ap * np.exp(Ami * np.log(Fmeas) / Ap) + frac_Rup_Rp * Aup)
                / (Ap + frac_Rup_Rp * Aup),
                2,
            )

        # Loop for the exception measures, which are implemented by altering the catchment itself, rather than implemented as a separate measure.
        for title in measures_exception:
            measure_title = title

            baseline_variable = measures_exception[measure_title]["baseline_variable"][
                0
            ]
            variable_to_save = measures_exception[measure_title]["variable_to_save"][0]

            runoff, gw, evap = run_measures_exception(
                input_csv,
                catchment_properties,
                measures_path,
                measures_exception_path,
                neighbourhood_pars_path,
                measure_title,
                neighbourhood_id,
                base_run,
                baseline_variable,
                variable_to_save,
            )

            num_years = (
                pd.to_datetime(runoff.Date[len(runoff.Date) - 1])
                - pd.to_datetime(runoff.Date[0])
            ).days / 365
            num_years = round(num_years)

            constants_runoff, mean_constants_runoff = getconstants_measures(
                runoff, num_year=num_years
            )
            gw = round(gw / num_years, 2)
            evap = round(evap / num_years, 2)

            idx_measure = np.where(
                df_runoff.id == measures_exception[measure_title]["id"][0]
            )[0][0]
            df_runoff.loc[idx_measure, D_eff_str] = mean_constants_runoff[0]

            df_gw.loc[idx_measure, "Baseline"] = gw["Baseline"].values[0]
            df_gw.loc[idx_measure, D_eff_str] = gw["alt"].values[0]

            df_evap.loc[idx_measure, "Baseline"] = evap["Baseline"].values[0]
            df_evap.loc[idx_measure, D_eff_str] = evap["alt"].values[0]

            # Calculate Ftot
            Fmeas = mean_constants_runoff[0]
            Inflow_area = measures_exception[measure_title]["inflow_area"][0]
            Ami = dict_param[f"tot_{Inflow_area}_area"]
            df_Ftot.loc[idx_measure, D_eff_str] = np.round(
                (Ap * np.exp(Ami * np.log(Fmeas) / Ap) + frac_Rup_Rp * Aup)
                / (Ap + frac_Rup_Rp * Aup),
                2,
            )

        # Sort the values on measure id
        df_runoff = df_runoff.sort_values(by="id").reset_index(drop=True)
        df_Ftot = df_Ftot.sort_values(by="id").reset_index(drop=True)
        df_gw = df_gw.sort_values(by="id").reset_index(drop=True)
        df_evap = df_evap.sort_values(by="id").reset_index(drop=True)

        neighbourhood_name = neighbourhood_pars["title"][n]
        output_file = output_name + " - %s.xlsx" % neighbourhood_name
        outdir = Path(output_file).parent
        outdir.mkdir(parents=True, exist_ok=True)

        # Save the results in a .xsls (Excel workbook) file
        with pd.ExcelWriter(output_file) as writer:
            df_runoff.to_excel(writer, sheet_name="Runoff factor", index=0)
            df_Ftot.to_excel(writer, sheet_name="Ftot", index=0)
            df_gw.to_excel(writer, sheet_name="Groundwater recharge", index=0)
            df_evap.to_excel(writer, sheet_name="Evaporation", index=0)


if __name__ == "__main__":
    # provide an auto generated cli based on the functions in this file
    fire.Fire()

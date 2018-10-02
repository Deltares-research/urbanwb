#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import time
import fire
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
from urbanwb.gwlcalculator import gwlcal
from urbanwb.read_parameter_base import read_parameter_base
from urbanwb.read_parameter_measure import read_parameter_measure
from urbanwb.sdf_curve import SDF_Curve
from urbanwb.measure import Measure


class Model(object):
    """
    Creates an instance of Model class which consists of consists of all eight components namely pavedroof, closedpaved,
    openpaved, unpaved, unsaturatedzone, groundwater, sewersystem and openwater module. Iterates __next__() over time
    steps to get solutions at each time step.

    Args:
        dict (dictionary): A dictionary of general parameters and parameters for measure which are read from dynamic
        input (.csv) and configuration file (.ini)
    """

    def __init__(self, dict):
        self.param = dict  # get one large dictionary of parameters
        self.pavedroof = PavedRoof(
            init_intstor_pr_t0=0,  # This initial value can be thrown into ini.file later.
            pr_no_meas_area=self.param["tot_pr_area"] - self.param["pr_meas_area"],
            pr_meas_area=self.param["pr_meas_area"],
            pr_meas_inflow_area=self.param["pr_meas_inflow_area"],
            intstorcap_pr=self.param["intstorcap_pr"],
            stormfrac_pr=self.param["swds_frac"],
            discfrac_pr=self.param["discfrac_pr"],
        )
        self.closedpaved = ClosedPaved(
            init_intstor_cp_t0=0,
            cp_no_meas_area=self.param["tot_cp_area"] - self.param["cp_meas_area"],
            cp_meas_area=self.param["cp_meas_area"],
            cp_meas_inflow_area=self.param["cp_meas_inflow_area"],
            intstorcap_cp=self.param["intstorcap_cp"],
            stormfrac_cp=self.param["swds_frac"],
            discfrac_cp=self.param["discfrac_cp"],
        )
        self.openpaved = OpenPaved(
            init_intstor_op_t0=0,
            op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
            op_meas_area=self.param["op_meas_area"],
            op_meas_inflow_area=self.param["op_meas_inflow_area"],
            intstorcap_op=self.param["intstorcap_op"],
            stormfrac_op=self.param["swds_frac"],
            discfrac_op=self.param["discfrac_op"],
            infilcap_op=self.param["infilcap_op"],
        )
        self.unpaved = Unpaved(
            fin_stor_up_t0=0,
            up_no_meas_area=self.param["tot_up_area"] - self.param["up_meas_area"],
            up_meas_area=self.param["up_meas_area"],
            up_meas_inflow_area=self.param["up_meas_inflow_area"],
            infilcap_up=self.param["infilcap_up"],
            intstorcap_up=self.param["intstorcap_up"],
            soiltype=self.param["soiltype"],
            croptype=self.param["croptype"],
        )
        self.unsaturatedzone = UnsaturatedZone(
            theta_uz_t0=soil_selector(self.param["soiltype"], self.param["croptype"])[
                gwlcal(self.param["init_gwl"])[2]
            ]["moist_cont_eq_rz[mm]"],
            uz_no_meas_area=self.param["tot_uz_area"] - self.param["uz_meas_area"],
            uz_meas_area=self.param["uz_meas_area"],
            soiltype=self.param["soiltype"],
            croptype=self.param["croptype"],
        )
        self.groundwater = Groundwater(
            init_gwl_t0=self.param["init_gwl"],
            gw_no_meas_area=self.param["tot_gw_area"] - self.param["gw_meas_area"],
            gw_meas_area=self.param["gw_meas_area"],
            seep_def=self.param["seep_def"],
            w=self.param["w"],
            vc=self.param["vc"],
            h_deepgw=self.param["h_deepgw"],
            flux=self.param["flux"],
            soiltype=self.param["soiltype"],
            croptype=self.param["croptype"],
        )
        self.sewersystem = SewerSystem(
            swds_no_meas_area=self.param["tot_swds_area"]
            - self.param["swds_meas_area"],
            mss_no_meas_area=self.param["tot_mss_area"] - self.param["mss_meas_area"],
            prev_stor_swds_t0=0,
            prev_so_swds_t0=0,
            prev_stor_mss_t0=0,
            prev_so_mss_t0=0,
            q_swds_ow_cap=self.param["q_swds_ow_cap"],
            q_mss_out_cap=self.param["q_mss_out_cap"],
            q_mss_ow_cap=self.param["q_mss_ow_cap"],
            stor_swds_cap=self.param["storcap_swds"],
            stor_mss_cap=self.param["storcap_mss"],
        )
        self.openwater = OpenWater(
            ow_no_meas_area=self.param["tot_ow_area"] - self.param["ow_meas_area"],
            ow_level=self.param["ow_level"],
            q_ow_out_cap=self.param["pump_cap"]
            * 8.64  # using "pump_cap" [liter/s/ha] instead of q_ow_out_cap [mm/d]"
            # may need modifications later, or provide choices
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
        """
        Calculates storage, fluxes, coefficients and other required outcomes at current time step.
        """
        try:
            # empty dictionary
            a = self.pavedroof.sol(p_atm=p_atm, e_pot_ow=e_pot_ow)
            b = self.closedpaved.sol(p_atm=p_atm, e_pot_ow=e_pot_ow)
            c = self.openpaved.sol(
                p_atm=p_atm, e_pot_ow=e_pot_ow, delta_t=self.param["delta_t"]
            )
            d = self.unpaved.sol(
                p_atm=p_atm,
                e_pot_ow=e_pot_ow,
                r_pr_up=a["r_pr_up"],
                r_cp_up=b["r_cp_up"],
                r_op_up=c["r_op_up"],
                prev_mois_uz=prev_lst["theta_uz"],
                pr_no_meas_area=self.param["tot_pr_area"] - self.param["pr_meas_area"],
                cp_no_meas_area=self.param["tot_cp_area"] - self.param["cp_meas_area"],
                op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
                ow_no_meas_area=self.param["tot_ow_area"] - self.param["ow_meas_area"],
                delta_t=self.param["delta_t"],
            )
            e = self.unsaturatedzone.sol(
                i_up_uz=d["i_up_uz"],
                meas_uz=meas_uz,
                tot_meas_area=self.param["tot_meas_area"],
                e_ref=ref_grass,
                prev_gwl=prev_lst["gwl"],
                delta_t=self.param["delta_t"],
            )
            f = self.groundwater.sol(
                p_uz_gw=e["p_uz_gw"],
                uz_no_meas_area=self.param["tot_uz_area"] - self.param["uz_meas_area"],
                p_op_gw=c["p_op_gw"],
                op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
                meas_gw=meas_gw,
                prev_owl=prev_lst["owl"],
                delta_t=self.param["delta_t"],
            )
            g = self.sewersystem.sol(
                pr_no_meas_area=self.param["tot_pr_area"] - self.param["pr_meas_area"],
                cp_no_meas_area=self.param["tot_cp_area"] - self.param["cp_meas_area"],
                op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
                r_pr_swds=a["r_pr_swds"],
                r_cp_swds=b["r_cp_swds"],
                r_op_swds=c["r_op_swds"],
                r_pr_mss=a["r_pr_mss"],
                r_cp_mss=b["r_cp_mss"],
                r_op_mss=c["r_op_mss"],
                meas_swds=meas_swds,
                meas_mss=meas_mss,
                ow_no_meas_area=self.param["tot_ow_area"] - self.param["ow_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
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
                up_no_meas_area=self.param["tot_up_area"] - self.param["up_meas_area"],
                gw_no_meas_area=self.param["tot_gw_area"] - self.param["gw_meas_area"],
                swds_no_meas_area=self.param["tot_swds_area"]
                - self.param["swds_meas_area"],
                mss_no_meas_area=self.param["tot_mss_area"]
                - self.param["mss_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
                total_area=self.param["tot_area"],
                delta_t=self.param["delta_t"],
            )
            dictmerged = OrderedDict(dict(a, **b, **c, **d, **e, **f, **g, **h))
        except IndexError:
            raise StopIteration
        return dictmerged


def running(dyn_inp, stat1_inp, stat2_inp):
    """
    takes input data from input file and parameters from configuration file to run one calculation

    Args:
        dyn_inp (string): the filename of the inputdata of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters

    Returns:
        (dataframe): A dataframe of all desired results for all time steps
    """

    start = time.time()
    # read inputdata(P, Ep and Er) from dyn_inp
    path = Path.cwd() / ".." / "input"
    InputData = pd.read_csv(str(path) + "\\" + dyn_inp)
    # check if there is NaN in dynamic input. or replace it with automatically changing data for user?
    NoNaN = InputData.isnull().sum().sum()
    if NoNaN != 0:
        raise SystemExit(f"The No. of NaN in the dynamic input is {NoNaN}, Please recheck it.")
    date = InputData["date"]
    P_atm = InputData["P_atm"]
    Ref_grass = InputData["Ref.grass"]
    E_pot_OW = InputData["E_pot_OW"]
    iters = np.shape(date)[0]
    # measure fluxes are all zeros if measure excluded
    meas_uz, meas_gw, meas_swds, meas_mss, meas_ow = (
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
    )
    # read general parameter and parameters for measure from static forms.
    dict_para = {
        **read_parameter_base(stat1_inp),
        **read_parameter_measure(stat2_inp),
    }  # One large dictionary of parameters
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
            "fin_stor_up": 0,  # fin_stor_up_t0
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
            "theta_uz": soil_selector(dict_para["soiltype"], dict_para["croptype"])[
                gwlcal(dict_para["init_gwl"])[2]
            ]["moist_cont_eq_rz[mm]"],
            "sum_p_gw": 0,
            "r_meas_gw": 0,
            "gwl_up_1": 0,
            "gwl_low_1": 0,
            "sc_gw": soil_selector(dict_para["soiltype"], dict_para["croptype"])[
                gwlcal(dict_para["init_gwl"])[2]
            ]["stor_coef"],
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
            "so_swds_ow": 0,  # prev_so_swds_t0
            "so_mss_ow": 0,  # prev_so_mss_t0
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
    for t in trange(1, iters):
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

    df = pd.DataFrame(lst)
    df.insert(0, "Date", date)
    end = time.time()
    print(f"Model runtime: {end - start:.1f}s")
    return df


def savecsv(dyn_inp, stat1_inp, stat2_inp, dyn_out):
    """
    takes input args to run running function and saves results into the specified outputfile under the 'pysol' folder

    Args:
        dyn_inp (string): the filename of the dynamic input data of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        dyn_out (string): the filename of the output file of solutions
    """
    df = running(dyn_inp, stat1_inp, stat2_inp)
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / dyn_out, index=True)


def saverun(dyn_inp, stat1_inp, stat2_inp, dyn_out, *args, saveall=True):
    """
    saverun function can save all (by default) results or selected results to the outputfile

    Args:
        dyn_inp (string): the filename of the dynamic input data of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        dyn_out (string): the filename of the output file of solutions
        *args (string): the name(s) of column(s) to be saved
        saveall (bool): whether to save all results or part of results
    """
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    df = running(dyn_inp, stat1_inp, stat2_inp)
    if saveall:
        df.to_csv(outdir / dyn_out, index=True)
    else:
        header = ["Date"]
        header.extend([arg for arg in args])
        df.to_csv(outdir / dyn_out, index=True, columns=header)


def run(param, dyn_inp):
    """
    This function is only used when the batch_run() function is called, repetition of running function,
    may needs further modifications
    """
    start = time.time()
    path = Path.cwd() / ".." / "input"
    InputData = pd.read_csv(path / dyn_inp)  # can change to input_csv_30yr
    NoNaN = InputData.isnull().sum().sum()
    if NoNaN != 0:
        raise SystemExit(f"The No. of NaN in the dynamic input is {NoNaN}, Please recheck it.")
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
    # read general parameter and parameters for measure from static forms.
    dict_para = param  # One large dictionary of parameters
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
            "fin_stor_up": 0,  # fin_stor_up_t0
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
            "theta_uz": soil_selector(dict_para["soiltype"], dict_para["croptype"])[
                gwlcal(dict_para["init_gwl"])[2]
            ]["moist_cont_eq_rz[mm]"],
            "sum_p_gw": 0,
            "r_meas_gw": 0,
            "gwl_up_1": 0,
            "gwl_low_1": 0,
            "sc_gw": soil_selector(dict_para["soiltype"], dict_para["croptype"])[
                gwlcal(dict_para["init_gwl"])[2]
            ]["stor_coef"],
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
            "so_swds_ow": 0,  # prev_so_swds_t0
            "so_mss_ow": 0,  # prev_so_mss_t0
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
    for t in trange(1, iters):
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

    df = pd.DataFrame(lst)
    df.insert(0, "Date", date)
    end = time.time()
    print(f"Model runtime: {end - start:.1f}s")
    return df


def batch_run_sdf(dyn_inp, stat1_inp, stat2_inp, dyn_out, *vararr):
    """
    this batch_run function is mainly designed for getting the database for sdf_curve.

    Args:
        dyn_inp (string): the filename of the inputdata of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        dyn_out (string): the filename of the output file of solutions
        vararr (float): the list of values to update "pump_cap".

    """
    rank_database = []
    param = {**read_parameter_base(stat1_inp), **read_parameter_measure(stat2_inp)}
    path = Path.cwd() / ".." / "input"
    InputData = pd.read_csv(path / dyn_inp)
    date = InputData["date"]
    iters = np.shape(date)[0]
    dt = param["delta_t"]
    num_year = round((dt * iters) / 365)
    print(f"The number of year of the input time series is around {num_year} year")
    for varval in vararr:
        param["pump_cap"] = varval
        owl_data = pd.DataFrame(run(param, dyn_inp))["owl"]
        print(f"pump_capacity = {varval} l/s/ha")
        k = SDF_Curve(owl_data, num_year=num_year, ow_level=param["ow_level"])
        rank_database.append(k.rank)
        print(f"Maximum height above target water level is {k.rank[0]}")
    df = pd.DataFrame(rank_database, index=[f"{v*8.64}" for v in vararr])
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    df.T.to_csv(outdir / dyn_out, index=True)


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


if __name__ == "__main__":
    fire.Fire()
    # batch_run("input_csv.csv", "static_form.ini", "static_form_measure.ini", "myresults.csv", 30, "pump_cap", 1)
    # savecsv("input_csv.csv", "static_form.ini", "static_form_measure.ini", "resultstry.csv")
    # saverun(
    #     "input_csv.csv",
    #     "static_form.ini",
    #     "static_form_measure.ini",
    #     "resultstry0.csv",
    #     "int_pr",
    #     "int_cp",
    #     saveall=False,
    # )
    # saverun("input_csv.csv", "static_form.ini", "static_form_measure.ini", "resultstry1.csv")

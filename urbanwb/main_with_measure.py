#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import time
import fire
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
from urbanwb.waterbalance_checker import WaterBalanceChecker
from time import sleep
from urbanwb.sdf_curve import SDF_curve2


class Model(object):
    """
    Creates an instance from Model class which consists of all eight components namely paved roof, closed paved,
    open paved, unpaved, unsaturated zone, groundwater, sewer system and open water. Iterates __next__() as time
    stepping to get solutions for all time steps.

    Args:
        dict_param (dictionary): A dictionary of necessary parameters read from neighbourhood and measure configuration
        files to initialize the model
    """

    def __init__(self, dict_param):
        self.param = dict_param  # get one large dictionary of parameters
        self.pavedroof = PavedRoof(
            pr_no_meas_area=self.param["tot_pr_area"] - self.param["pr_meas_area"],
            **self.param
        )
        self.closedpaved = ClosedPaved(
            cp_no_meas_area=self.param["tot_cp_area"] - self.param["cp_meas_area"],
            **self.param
        )
        self.openpaved = OpenPaved(
            op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
            **self.param
        )
        self.unpaved = Unpaved(
            up_no_meas_area=self.param["tot_up_area"] - self.param["up_meas_area"],
            **self.param
        )
        self.unsaturatedzone = UnsaturatedZone(
            theta_uz_t0=soil_selector(self.param["soiltype"], self.param["croptype"])[
                gwlcalc(self.param["gwl_t0"])[2]
            ]["moist_cont_eq_rz[mm]"],
            uz_no_meas_area=self.param["tot_uz_area"] - self.param["uz_meas_area"],
            **self.param
        )
        self.groundwater = Groundwater(
            gw_no_meas_area=self.param["tot_gw_area"] - self.param["gw_meas_area"],
            **self.param
        )
        self.sewersystem = SewerSystem(
            swds_no_meas_area=self.param["tot_swds_area"] - self.param["swds_meas_area"],
            mss_no_meas_area=self.param["tot_mss_area"] - self.param["mss_meas_area"],
            **self.param
        )
        self.openwater = OpenWater(
            ow_no_meas_area=self.param["tot_ow_area"] - self.param["ow_meas_area"],
            **self.param
        )
        # it takes too many parameters to initialise a measure instance.

        # k_sat_uz = 10 * soil_selector(soiltype, croptype)[0]["k_sat"]
        # k_sat_uz=10*soil_selector(self.param["soiltype"],self.param["croptype"])[0]["k_sat"]
        # self.measure = Measure(meas_area=self.param["meas_area"], runoff_to_stor_layer=self.param["runoff_to_stor_layer"],
        #                        intstor_meas_t0=self.param["intstor_meas_t0"], ev_evaporation=self.param["ev_evaporation"],
        #                        num_stor_lvl=self.param["num_stor_lvl"], infil_cap_meas=self.param["infil_cap_meas"],
        #                        top_storcap_meas=self.param["top_storcap_meas"],
        #                        bot_storcap_meas=self.param["bot_storcap_meas"],
        #                        top_stor_meas_t0=self.param["top_stor_meas_t0"],
        #                        bot_stor_meas_t0=self.param["bot_stor_meas_t0"],
        #                        int_cap_meas=self.param["int_cap_meas"], ts_area_meas=self.param["ts_area_meas"],
        #                        et_transpiration=self.param["et_transpiration"], e_fac_meas=self.param["e_fac_meas"],
        #                        in_infiltration=self.param["in_infiltration"], tinf_cap_meas=self.param["tinf_cap_meas"],
        #                        bs_area_meas=self.param["bs_area_meas"], btm_et_transpiration=self.param["btm_et_transpiration"],
        #                        connection_to_gw=self.param["connection_to_gw"], gwl_limit_meas=self.param["gwl_limit_meas"],
        #                        k_sat_uz=100+10*soil_selector(self.param["soiltype"],self.param["croptype"])[0]["k_sat"],b_level_meas=self.param["b_level_meas"],
        #                        btm_discharge_type=self.param["btm_discharge_type"], br_cap_meas=self.param["br_cap_meas"],
        #                        bdl_meas=self.param["bdl_meas"], bdr_meas=self.param["bdr_meas"],
        #                        surf_runoff_meas_ow=self.param["surf_runoff_meas_ow"], ctrl_runoff_meas_ow=self.param["ctrl_runoff_meas_ow"], overflow_meas_ow=self.param["overflow_meas_ow"],
        #                        surf_runoff_meas_uz=self.param["surf_runoff_meas_uz"], ctrl_runoff_meas_uz=self.param["ctrl_runoff_meas_uz"], overflow_meas_uz=self.param["overflow_meas_uz"],
        #                        surf_runoff_meas_gw=self.param["surf_runoff_meas_gw"], ctrl_runoff_meas_gw=self.param["ctrl_runoff_meas_gw"], overflow_meas_gw=self.param["overflow_meas_gw"],
        #                        surf_runoff_meas_swds=self.param["surf_runoff_meas_swds"], ctrl_runoff_meas_swds=self.param["ctrl_runoff_meas_swds"], overflow_meas_swds=self.param["overflow_meas_swds"],
        #                        surf_runoff_meas_mss=self.param["surf_runoff_meas_mss"], ctrl_runoff_meas_mss=self.param["ctrl_runoff_meas_mss"], overflow_meas_mss=self.param["overflow_meas_mss"],
        #                        surf_runoff_meas_out=self.param["surf_runoff_meas_out"], ctrl_runoff_meas_out=self.param["ctrl_runoff_meas_out"], overflow_meas_out=self.param["overflow_meas_out"], isgreenroofdd=self.param["isgreenroofdd"])
        # if self.param["waterbalance_check"]:
        #         self.waterbalancechecker = WaterBalanceChecker(tot_area=self.param["tot_area"], pr_no_meas_area=self.param["tot_pr_area"]-self.param["pr_meas_area"],
        #                                                cp_no_meas_area=self.param["tot_cp_area"]-self.param["cp_meas_area"], op_no_meas_area=self.param["tot_op_area"]-self.param["op_meas_area"],
        #                                                up_no_meas_area=self.param["tot_up_area"]-self.param["up_meas_area"], ow_no_meas_area=self.param["tot_ow_area"]-self.param["ow_meas_area"],
        #                                                uz_no_meas_area=self.param["tot_uz_area"]-self.param["uz_meas_area"], gw_no_meas_area=self.param["tot_gw_area"]-self.param["gw_meas_area"],
        #                                                swds_no_meas_area=self.param["tot_swds_area"]-self.param["swds_meas_area"],mss_no_meas_area=self.param["tot_mss_area"]-self.param["mss_meas_area"],
        #                                                meas_area=self.param["meas_area"],meas_top_area=self.param["ts_area_meas"],meas_bot_area=self.param["bs_area_meas"],meas_inflow_area=self.param["op_meas_inflow_area"],inflowareaIsoparea=True)  # need to make this op_meas_inflow_area adaptive, not just open paved but it is applicable to other area.

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
                pr_no_meas_area=self.param["tot_pr_area"] - self.param["pr_meas_area"],
                cp_no_meas_area=self.param["tot_cp_area"] - self.param["cp_meas_area"],
                op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
                ow_no_meas_area=self.param["tot_ow_area"] - self.param["ow_meas_area"],
                delta_t=self.param["delta_t"],
            )
            # meas_sol = self.measure.sol(p_atm=p_atm, e_pot_ow=e_pot_ow, r_pr_meas=pr_sol["r_pr_meas"], r_cp_meas=cp_sol["r_cp_meas"],
            #                             r_op_meas=op_sol["r_op_meas"], r_up_meas=up_sol["r_up_meas"], pr_no_meas_area=self.param["tot_pr_area"]-self.param["pr_meas_area"],
            #                             cp_no_meas_area=self.param["tot_cp_area"]-self.param["cp_meas_area"], op_no_meas_area=self.param["tot_op_area"]-self.param["op_meas_area"],
            #                             up_no_meas_area=self.param["tot_up_area"]-self.param["up_meas_area"], gw_no_meas_area=self.param["tot_gw_area"]-self.param["gw_meas_area"],
            #                             prev_gwl_gw=prev_lst["gwl"], delta_t=self.param["delta_t"])
            uz_sol = self.unsaturatedzone.sol(
                i_up_uz=up_sol["i_up_uz"],
                meas_uz=0,  # meas_sol["q_meas_uz"]
                tot_meas_area=self.param["tot_meas_area"],
                e_ref=ref_grass,
                gwl_prevt=prev_lst["gwl"],
                delta_t=self.param["delta_t"],
            )
            gw_sol = self.groundwater.sol(
                p_uz_gw=uz_sol["p_uz_gw"],
                uz_no_meas_area=self.param["tot_uz_area"] - self.param["uz_meas_area"],
                p_op_gw=op_sol["p_op_gw"],
                op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
                tot_meas_area=self.param["tot_meas_area"],
                meas_gw=0,  # meas_sol["q_meas_gw"]
                owl_prevt=prev_lst["owl"],
                delta_t=self.param["delta_t"],
            )
            ss_sol = self.sewersystem.sol(
                pr_no_meas_area=self.param["tot_pr_area"] - self.param["pr_meas_area"],
                cp_no_meas_area=self.param["tot_cp_area"] - self.param["cp_meas_area"],
                op_no_meas_area=self.param["tot_op_area"] - self.param["op_meas_area"],
                r_pr_swds=pr_sol["r_pr_swds"],
                r_cp_swds=cp_sol["r_cp_swds"],
                r_op_swds=op_sol["r_op_swds"],
                r_pr_mss=pr_sol["r_pr_mss"],
                r_cp_mss=cp_sol["r_cp_mss"],
                r_op_mss=op_sol["r_op_mss"],
                meas_swds=0,  # meas_sol["q_meas_swds"]
                meas_mss=0,  # meas_sol["q_meas_mss"]
                ow_no_meas_area=self.param["tot_ow_area"] - self.param["ow_meas_area"],
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
                meas_ow=0,  # meas_sol["q_meas_ow"]
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
            # if self.param["waterbalance_check"]:
            #     wbc = self.waterbalancechecker.sol(P_atm=p_atm, e_atm_pr=pr_sol["e_atm_pr"],e_atm_cp=cp_sol["e_atm_cp"],e_atm_op=op_sol["e_atm_op"],
            #                                    e_atm_up=up_sol["e_atm_up"],e_atm_ow=ow_sol["e_atm_ow"], t_atm_uz=uz_sol["t_atm_uz"],e_atm_meas=meas_sol["e_atm_meas"],
            #                                    tt_atm_meas=meas_sol["tt_atm_meas"],tb_atm_meas=meas_sol["tb_atm_meas"],s_gw_out=gw_sol["s_gw_out"],d_gw_ow=gw_sol["d_gw_ow"],
            #                                    q_swds_ow=ss_sol["q_swds_ow"],q_mss_ow=ss_sol["q_mss_ow"],sum_so_ow=ow_sol["sum_so_ow"],q_mss_out=ss_sol["q_mss_out"],q_ow_out=ow_sol["q_ow_out"],
            #                                    q_meas_out=meas_sol["q_meas_out"],intstor_pr=pr_sol["intstor_pr"],intstor_pr_prevt=prev_lst["intstor_pr"],intstor_cp=cp_sol["intstor_cp"],
            #                                    intstor_cp_prevt=prev_lst["intstor_cp"],intstor_op=op_sol["intstor_op"],intstor_op_prevt=prev_lst["intstor_op"],
            #                                    intstor_up=up_sol["fin_intstor_up"],intstor_up_prevt=prev_lst["fin_intstor_up"],theta_uz=uz_sol["theta_uz"],theta_uz_prevt=prev_lst["theta_uz"],
            #                                    sc_gw=gw_sol["sc_gw"],gwl_prevt=prev_lst["gwl"],gwl=gw_sol["gwl"],gwl_sl=gw_sol["gwl_sl"],gwl_sl_prevt=prev_lst["gwl_sl"],
            #                                    so_swds=ss_sol["so_swds_ow"],so_swds_prevt=prev_lst["so_swds_ow"],so_mss=ss_sol["so_mss_ow"],so_mss_prevt=prev_lst["so_mss_ow"],
            #                                    stor_swds=ss_sol["stor_swds"],stor_swds_prevt=prev_lst["stor_swds"],stor_mss=ss_sol["stor_mss"],stor_mss_prevt=prev_lst["stor_mss"],
            #                                    owl_prevt=prev_lst["owl"],owl=ow_sol["owl"],intstor_meas=meas_sol["intstor_meas"],intstor_meas_prevt=prev_lst["intstor_meas"],top_stor_meas=meas_sol["top_stor_meas"],
            #                                    top_stor_meas_prevt=prev_lst["top_stor_meas"],bot_stor_meas=meas_sol["bot_stor_meas"],bot_stor_meas_prevt=prev_lst["bot_stor_meas"],
            #                                    meas_ow=meas_sol["q_meas_ow"],meas_gw=meas_sol["q_meas_gw"],meas_swds=meas_sol["q_meas_swds"]) # the last part about measure should be kindof adapative.
            #     dictmerged = OrderedDict(dict(pr_sol, **cp_sol, **op_sol, **up_sol, **uz_sol, **gw_sol, **ss_sol, **ow_sol, **meas_sol, **wbc))
            # else:
            #     dictmerged = OrderedDict(dict(pr_sol, **cp_sol, **op_sol, **up_sol, **uz_sol, **gw_sol, **ss_sol, **ow_sol, **meas_sol))
            dictmerged = OrderedDict(dict(pr_sol, **cp_sol, **op_sol, **up_sol, **uz_sol, **gw_sol, **ss_sol, **ow_sol,))  # newly added line.
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

    # add checker of the data here.
    return pd.read_csv(str(path) + "\\" + dyn_inp)


def read_parameters(stat1_inp, stat2_inp):
    """
    reads parameters for Model initialization through calling "read_parameter_base" to read parameters from
    neighbourhood  configuration file and "read_parameter_measure" to read parameters from measure configuration file.

    Args:
        stat1_inp (string): filename of neighbourhood configuration file
        stat2_inp (string): filename of measure configuration file

    Returns:
        (dictionary): A dictionary of all necessary parameters to initialize a Model
    """
    return {**read_parameter_base(stat1_inp), **read_parameter_measure(stat2_inp)}


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
    date = input_data["date"]
    P_atm = input_data["P_atm"]
    Ref_grass = input_data["Ref.grass"]
    E_pot_OW = input_data["E_pot_OW"]
    iters = np.shape(date)[0]
    k = Model(dict_param)
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
            "init_intstor_up": 0,
            "actl_infilcap_up": 0,
            "timefac_up": 0,
            "e_atm_up": 0,
            "i_up_uz": 0,
            "fin_intstor_up": 0,  # fin_stor_up_t0
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
            "theta_uz": soil_selector(dict_param["soiltype"], dict_param["croptype"])[
                gwlcalc(dict_param["gwl_t0"])[2]
            ]["moist_cont_eq_rz[mm]"],
            # "moist_cont_uz":soil_selector(dict_param["soiltype"], dict_param["croptype"])[
            #     gwlcalc(dict_param["gwl_t0"])[2]
            # ]["moist_cont_eq_rz[mm]"],
            "sum_p_gw": 0,
            "r_meas_gw": 0,
            # "gwl_up_1": 0,
            # "gwl_low_1": 0,
            "sc_gw": soil_selector(dict_param["soiltype"], dict_param["croptype"])[
                gwlcalc(dict_param["gwl_t0"])[2]
            ]["stor_coef"],
            "h_gw": 0,
            "s_gw_out": 0,
            "d_gw_ow": 0,
            "gwl": dict_param["gwl_t0"],
            "gwl_sl": 0,
            "sum_r_swds": 0,
            "r_meas_swds": 0,
            "sum_r_mss": 0,
            "r_meas_mss": 0,
            "q_swds_ow": 0,
            "q_mss_out": 0,
            "q_mss_ow": 0,
            "so_swds_ow": dict_param["so_swds_t0"],  # prev_so_swds_t0
            "so_mss_ow": dict_param["so_mss_t0"],  # prev_so_mss_t0
            "stor_swds": dict_param["stor_swds_t0"],  # prev_stor_swds_t0
            "stor_mss": dict_param["stor_mss_t0"],  # prev_stor_mss_t0
            "prec_ow": P_atm[0],
            "e_atm_ow": E_pot_OW[0],
            "sum_r_ow": 0,
            "sum_d_ow": 0,
            "sum_q_ow": 0,
            "sum_so_ow": 0,
            "r_meas_ow": 0,
            "q_ow_out": 0,
            "owl": dict_param["ow_level"],
            "prec_meas": 0,
            "sum_r_meas": 0,
            "int_meas": 0,
            "e_atm_meas": 0,
            "int_down_meas": 0,
            "sr_meas": 0,
            "intstor_meas": dict_param["intstor_meas_t0"],
            "ts_ini_meas": 0,
            "tt_atm_meas": 0,
            "pt_meas": 0,
            "top_stor_meas": dict_param["top_stor_meas_t0"],  # top_stor_meas_t0
            "bs_ini_meas": 0,
            "tb_atm_meas": 0,
            "pb_meas_gw": 0,
            "br_meas": 0,
            "bot_stor_meas": dict_param["bot_stor_meas_t0"],  # bot_stor_meas_t0
            "bo_meas": 0,
            "q_meas_ow": 0,
            "q_meas_uz": 0,
            "q_meas_gw": 0,
            "q_meas_swds": 0,
            "q_meas_mss": 0,
            "q_meas_out": 0,
            "rainfall_tot": 0,  # waterbalance checker lst from here on
            "evaporation_tot": 0,
            "seepage_tot": 0,
            "drainage_tot": 0,
            "sewerflow_tot": 0,
            "toWWTP_tot": 0,
            "OWtoOut_tot": 0,
            "StorChange_tot": 0,
            "BalanceClosed_tot": 0,
            "rainfall_mia": 0,
            "evaporation_mia": 0,
            "storage_mia": 0,  # "op_meas_inflow_area" - needs to be adaptive here, modify later, #(dict_param["intstor_meas_t0"]*dict_param["meas_area"] + dict_param["bot_stor_meas_t0"] *
                            #dict_param["bs_area_meas"] + dict_param["top_stor_meas_t0"] * dict_param["ts_area_meas"] + 0 *
                            #(dict_param["tot_op_area"] - dict_param["op_meas_area"])
                            #)/dict_param["op_meas_inflow_area"]  # another way to modify it is to use another (new) waterbalance check method to avoid this divzero.
            "toOW_mia": 0,
            "toGW_mia": 0,
            "runofftoSWDS_mia": 0,
        }
    ]
    start = time.time()
    for t in trange(1, iters):  # time series first line is not relevant (initial), start from second line.
        lst.append(
            k.__next__(
            P_atm[t],
            E_pot_OW[t],
            Ref_grass[t],
            lst[t - 1],
                        )
                    )
    end = time.time()
    print(f"Model runtime: {end - start:.1f}s")
    df = pd.DataFrame(lst)
    df.insert(0, "Date", date)
    df.insert(1, "P_atm", P_atm)
    df.insert(2, "E_pot_OW", E_pot_OW)
    df.insert(3, "Ref.grass", Ref_grass)

    # water balance check.
    # sum_prec = sum(df["prec_meas"].iloc[1:])
    # sum_evap = sum(df["evaporation_mia"].iloc[1:])
    # intstor_change = df["storage_mia"].iloc[-1] - df["storage_mia"].iloc[0]
    # ow_recharge = sum(df["toOW_mia"].iloc[1:])
    # gw_recharge = sum(df["toGW_mia"].iloc[1:])
    # discharge = sum(df["runofftoSWDS_mia"].iloc[1:])
    # balance_check = sum_prec - sum_evap - intstor_change - ow_recharge - gw_recharge - discharge
    # stat = {"sum_prec": sum_prec, "sum_evap": sum_evap, "intstor_change": intstor_change,"ow_recharge": ow_recharge,
    #         "gw_recharge": gw_recharge, "discharge": discharge, "balance_check": balance_check}
    # print("results statistics", stat)
    # print("Water balance is closed? ", math.isclose(balance_check, 0, abs_tol=0.001))
    return df  # df,stat


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

    input_data = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)
    df = running(input_data, dict_param)  # [0]
    # print(dict_param)
    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)

    if save_all:
        df.to_csv(outdir / output_filename, index=True)
    else:
        header = ["Date", "P_atm", "E_pot_OW", "Ref.grass"]
        header.extend([arg for arg in args])
        df.to_csv(outdir / output_filename, index=True, columns=header)


def batch_run_multivalue_for_one_param(dyn_inp, stat1_inp, stat2_inp, dyn_out, varkey, *vararrs, corresponding_varkey=None,
                                       baseline_variable="r_op_swds", variable_to_save="runofftoSWDS_mia"):
    """
    this batch_run function is mainly for getting the database for different values for different parameters.

    Args:
        dyn_inp (string): the filename of the inputdata of precipitation and evaporation
        stat1_inp (string): the filename of the static form of general parameters
        stat2_inp (string): the filename of the static form of measure parameters
        dyn_out (string): the filename of the output file of solutions
        varkey (float): the key parameter to be updated
        vararr (float): values to update varkey.

    Usage:
        use in the cmd: python -m urbanwb.main_with_measure batch_run_multivalue_for_one_param timeseries.csv stat1.ini stat2.ini results.csv bot_storcap_meas q_meas_swds 200 100 --inflowfac 20
        For now is is usable.
    for now doesn't enable the matrix checker cause some parameters are just correlated.
    """

    inputdata = read_inputdata(dyn_inp)
    dict_param = read_parameters(stat1_inp, stat2_inp)

    # can delete this fraction if necessary.
    date = inputdata["date"]
    iters = np.shape(date)[0]
    dt = dict_param["delta_t"]
    num_year = round((dt * iters) / 365)
    print(f"Total year of the input time series is {num_year} year")
    database = []
    statsbase = []
    for varval in vararrs:
        dict_param[varkey] = varval
        if corresponding_varkey is not None:
            dict_param[corresponding_varkey] = varval/2  # if change bot_stor --> sometimes the discharge down_seepage_flux will change accordingly /2, if change measure area, sometimes bot_area change accordingly. need more thinking here
            print(varval/2)
        rv = running(inputdata, dict_param)
        df2 = pd.DataFrame(rv[0])
        print("variable to save: ", variable_to_save)
        database.append(df2[variable_to_save])
        statsbase.append(rv[1])
        print("------"*20)
        sleep(0.5)

    df = pd.DataFrame(database, index=[v for v in vararrs])
    df = df.T
    df.insert(0, "Date", date)
    df.insert(1, "P_atm", inputdata["P_atm"])

    # run no measure baseline:
    dict_param["choice"] = 0
    dict_param["op_meas_inflow_area"] = 0
    dict_param["op_meas_area"] = 0
    dict_param["waterbalance_check"] = False
    print("---"*3)
    # print(dict_param)
    print("Baseline (No measure)")
    baseline_runoff = pd.DataFrame(running3(dyn_inp, dict_param))["r_op_swds"]  # need to be adaptive, besides, running3 function needs to be refreshed.
    print("------" * 20)
    sleep(0.5)
    df.insert(2, "Baseline", baseline_runoff)

    outdir = Path("pysol")
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / dyn_out, index=True)
    dyn_out_stat = "stats_" + ''.join(list(dyn_out)[:-4]) + ".txt"
    np.savetxt(outdir / dyn_out_stat, statsbase, delimiter=",", fmt='%s')


def running3(dyn_inp, param):
    """ Run without measure ----.
    This is a temporary function, will be modified later. I think running function should neither contain dynamic input file name or static input file name.
    Just contains parameter matrix, dataframe of dynamic timeseries. So simply a running function.
    takes input data from input file and parameters from configuration file to run one calculation

    Args:
        dyn_inp (string): the filename of the inputdata of precipitation and evaporation
        param: One large dictionary of parameters

    Returns:
        (dataframe): A dataframe of all desired results for all time steps
    """

    start = time.time()
    # read inputdata(P, Ep and Er) from dyn_inp
    path = Path.cwd() / ".." / "input"
    InputData = pd.read_csv(str(path) + "\\" + dyn_inp)
    date = InputData["date"]
    P_atm = InputData["P_atm"]
    Ref_grass = InputData["Ref.grass"]
    E_pot_OW = InputData["E_pot_OW"]
    iters = np.shape(date)[0]

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
            "actl_infilcap_up": 0,
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
                gwlcalc(dict_para["gwl_t0"])[2]
            ]["moist_cont_eq_rz[mm]"],
            # "moist_cont_uz": soil_selector(dict_para["soiltype"], dict_para["croptype"])[gwlcalc(dict_para["gwl_t0"])[2]]
            # ["moist_cont_eq_rz[mm]"],
            "sum_p_gw": 0,
            "r_meas_gw": 0,
            # "gwl_up_1": 0,
            # "gwl_low_1": 0,
            "sc_gw": soil_selector(dict_para["soiltype"], dict_para["croptype"])[
                gwlcalc(dict_para["gwl_t0"])[2]
            ]["stor_coef"],
            "h_gw": 0,
            "s_gw_out": 0,
            "d_gw_ow": 0,
            "gwl": dict_para["gwl_t0"],
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
            "prec_meas": 0,
            "sum_r_meas": 0,
            "int_meas": 0,
            "e_atm_meas": 0,
            "int_down_meas": 0,
            "sr_meas": 0,
            "intstor_meas": 0,
            "ts_ini_meas": 0,
            "tt_atm_meas": 0,
            "pt_meas": 0,
            "top_stor_meas": dict_para["top_stor_meas_t0"],  # top_stor_meas_t0
            "bs_ini_meas": 0,
            "tb_atm_meas": 0,
            "pb_meas_gw": 0,
            "br_meas": 0,
            "bot_stor_meas": dict_para["bot_stor_meas_t0"],  # bot_stor_meas_t0
            "bo_meas": 0,
            "q_meas_ow": 0,
            "q_meas_uz": 0,
            "q_meas_gw": 0,
            "q_meas_swds": 0,
            "q_meas_mss": 0,
            "q_meas_out": 0,
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
            )
        )

    df = pd.DataFrame(lst)
    df.insert(0, "Date", date)
    df.insert(1, "P_atm", P_atm)
    df.insert(2, "E_pot_OW", E_pot_OW)
    df.insert(3, "Ref.grass", Ref_grass)

    end = time.time()
    print(f"Model runtime: {end - start:.1f}s")
    return df


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
    owl_data = np.append(running(input_data, dict_param)["owl"], 0)
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
            owl_data = pd.DataFrame(running(input_data, dict_param))["owl"]
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
            owl_data = pd.DataFrame(running(input_data, dict_param))["owl"]
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
    # batch_run("input_csv.csv", "static_form.ini", "static_form_measure.ini", "myresults.csv", 30, "pump_cap", 1)
    # savecsv("input_csv_for_build_measure.csv", "static_form_base_for_measure.ini", "static_form_measure_for_measure.ini", "results_measure_build.csv")


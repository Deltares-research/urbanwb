# from urbanwb.main import running
from urbanwb.SDF_curve import OWL
from urbanwb.read_parameter_no_section import read_parameter
from pathlib import Path
import pandas as pd
import numpy as np
from urbanwb.gwlcalculator import gwlcal
from urbanwb.selector import soil_selector
from urbanwb.main import running, Model

# Load csv file
indir = Path("input")
outdir = Path("pysol")
outdir.mkdir(parents=True, exist_ok=True)
InputData = pd.read_csv(
    indir / "input_csv.csv"
)  # input the precipitation, potential evaporation
date = InputData["date"]
P_atm = InputData["P_atm"]
Ref_grass = InputData["Ref.grass"]
E_pot_OW = InputData["E_pot_OW"]
iters = np.shape(date)[0]


def batch_run(Q):
    para = read_parameter("input/static_form_for_batchrun.ini")
    # general parameters
    delta_t = para["delta_t"]
    total_area = para["tot_area"]
    soiltype, croptype = para["soiltype"], para["croptype"]
    # paved roof
    tot_pr_area, pr_meas_area = para["tot_pr_area"], 0
    pr_no_meas_area, pr_meas_inflow_area, init_intstor_pr_t0 = (
        tot_pr_area - pr_meas_area,
        0,
        0,
    )
    # closed paved
    tot_cp_area, cp_meas_area = para["tot_cp_area"], 0
    cp_no_meas_area, cp_meas_inflow_area, init_intstor_cp_t0 = (
        tot_cp_area - cp_meas_area,
        0,
        0,
    )
    # open paved
    tot_op_area, op_meas_area = para["tot_op_area"], 0
    op_no_meas_area, op_meas_inflow_area, init_intstor_op_t0 = (
        tot_op_area - op_meas_area,
        0,
        0,
    )
    # unpaved
    tot_up_area, up_meas_area = para["tot_up_area"], 0
    up_no_meas_area, up_meas_inflow_area, fin_stor_up_t0 = (
        tot_up_area - up_meas_area,
        0,
        0,
    )
    # openwater
    tot_ow_area, ow_meas_area = para["tot_ow_area"], 0
    ow_no_meas_area, ow_level = tot_ow_area - ow_meas_area, para["ow_level"]
    # unsaturated zone
    init_gwl_t0 = 1.5
    theta_uz_t0 = soil_selector(2, 1)[gwlcal(init_gwl_t0)[2]]["moist_cont_eq_rz[mm]"]
    tot_uz_area, uz_meas_area = para["tot_uz_area"], 0
    uz_no_meas_area = tot_uz_area - uz_meas_area
    # groundwater
    tot_gw_area, gw_meas_area = para["tot_gw_area"], 0
    gw_no_meas_area = tot_gw_area - gw_meas_area
    # swds
    tot_swds_area, swds_meas_area, tot_mss_area, mss_meas_area = (
        para["tot_swds_area"],
        0,
        para["tot_mss_area"],
        0,
    )
    swds_no_meas_area, mss_no_meas_area = (
        tot_swds_area - swds_meas_area,
        tot_mss_area - mss_meas_area,
    )
    prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0, prev_so_mss_t0 = 0, 0, 0, 0
    # measure inflow:
    tot_meas_area = 0
    meas_uz, meas_gw, meas_swds, meas_mss, meas_ow = (
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
        np.zeros(iters),
    )

    for q in Q:
        filename = "test" + str(q) + ".csv"
        running(filename)


if __name__ == "__main__":
    batchrun([3, 4, 5, 6])

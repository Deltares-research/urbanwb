import toml
import fire
from pathlib import Path


def read_parameter_measure(stat2_inp):
    """
    reads parameters from the TOML-formated static form for measure.

    Args:
        stat2_inp (string): filename of the static form of general parameters

    Returns:
        (dictionary): A dictionary of parameters for measure.
    """
    path = Path.cwd() / ".." / "input"
    cf = toml.load(str(path) + "\\" + stat2_inp, _dict=dict)
    choice = cf["choice"]
    validinput = False
    while not validinput:
        if choice == 0:  # input choice: no measure
            pr_meas_area = (
                cp_meas_area
            ) = (
                op_meas_area
            ) = (
                up_meas_area
            ) = (
                uz_meas_area
            ) = gw_meas_area = swds_meas_area = mss_meas_area = ow_meas_area = 0
            validinput = True
        elif choice == 1:  # input choice: there is measure
            pr_meas_area = cf["pr_meas_area"]
            cp_meas_area = cf["cp_meas_area"]
            op_meas_area = cf["op_meas_area"]
            up_meas_area = cf["up_meas_area"]
            uz_meas_area = cf["uz_meas_area"]
            gw_meas_area = cf["gw_meas_area"]
            swds_meas_area = cf["swds_meas_area"]
            mss_meas_area = cf["mss_meas_area"]
            ow_meas_area = cf["ow_meas_area"]
            validinput = True
        else:
            raise ValueError("Error: Choice can only be 0 or 1.")
    # these parameters are parameters for measure. As you can see in the configuration file,
    # these so many parameters are confusing and overview of parameters is not as good as excel.
    # Hence, it may be possible that we build a GUI to handle this problem. But for the time being,
    # we just build like this to make it run first.

    # meas_area -- predefined measure area [m^2]
    # Button_BW17 --- predefined selection at which measure layer runoff from other areas is stored (1 or 3), Inflow from other areas can only take place at interception level (1) or at the bottom storage level (3).
    # * prev_intstor_meas --- interception storage on the measure at previous time step [mm]
    # intstor_meas_t0 --- predefined interception storage on the measure at t=0 [mm]
    # ev_evaporation --- predefined selection if evaporation from measure is possible (1) or not (0)
    # num_stor_lvl --- predefined number of storage levels (1, 2 or 3)
    # infil_cap_meas --- predefined infiltration capacity of measure [mm/d] (4800mm/d)
    # top_storcap_meas --- predefined storage capacity in top layer of measure (76.2mm)
    # bot_storcap_meas --- predefined storage capacity in bottom layer of measure (182.88mm)
    # * prev_top_stor_meas --- top layer storage at the end of previous time step [mm]
    # top_stor_meas_t0 --- top layer storage at t = 0 [mm] (0 mm)
    # * prev_bot_stor_meas --- bottom layer storage at the end of previous time step [mm]
    # bot_stor_meas_t0 --- bottom layer storage at t = 0 [mm] (0 mm)

    # int_cap_meas --- predefined interception storage capacity of measure [mm] (20mm)
    # ts_area_meas --- predefined area of top layer storage area of measure [m^2]
    # et_transpiration --- predefined selection if transpiration from measure is possible (1) or not (0)
    # e_fac_meas --- predefined evaporation factor of measure [-]
    # tinf_cap_meas --- predefined infiltration capacity of top layer of measure [mm/d] (480mm/d)

    # bs_area_meas --- predefined area of bottom layer storage area of measure [m^2]
    # btm_et_transpiration --- predefined selection if transpiration from bottom layer of measure is possible (1) or not (0)
    # connection_to_gw --- predefined selection if percolation (connection) from measure to groundwater is possible (1) or not (0)
    # gwl_limit_meas --- predefined limitation of percolation from measure to groundwater if groundwater level is below measure bottom level (1=yes; 0=no)
    # b_level_meas --- predefined bottom level of measure [m -SL] (0.6858)
    # btm_discharge_type --- predefined definition of discharge type from bottom layer of measure (0 = flux limited, 1 = level difference over resistance)
    # br_cap_meas --- predefined runoff capacity from bottom layer of measure [mm/d] (flux=15mm/d)
    # bdl_meas --- predefined discharge level from bottom layer of measure [mm]
    # bdr_meas --- predefined hydraulic resistance for level induced discharge from bottom layer of measure [d]

    # surf_runoff_meas_ow --- predefined definition of surface runoff from measure to open water (0 = no, 1 = yes)
    # ctrl_runoff_meas_ow --- predefined definition of controlled runoff from measure to open water (0 = no, 1 = yes)
    # overflow_meas_ow --- predefined definition of overflow from measure to open water (0 = no, 1 = yes)
    # surf_runoff_meas_uz --- predefined definition of surface runoff from measure to unsaturated zone (0 = no, 1 = yes)
    # ctrl_runoff_meas_uz --- predefined definition of controlled runoff from measure to unsaturated zone (0 = no, 1 = yes)
    # overflow_meas_uz --- predefined definition of overflow from measure to unsaturated zone (0 = no, 1 = yes)
    # surf_runoff_meas_gw --- predefined definition of surface runoff from measure to groundwater (0 = no, 1 = yes)
    # ctrl_runoff_meas_gw --- predefined definition of controlled runoff from measure to groundwater (0 = no, 1 = yes)
    # overflow_meas_gw --- predefined definition of overflow from measure to groundwater (0 = no, 1 = yes)
    # surf_runoff_meas_swds --- predefined definition of surface runoff from measure to storm water drainage system (0 = no, 1 = yes)
    # ctrl_runoff_meas_swds --- predefined definition of controlled runoff from measure to storm water drainage system (0 = no, 1 = yes)
    # overflow_meas_gw --- predefined definition of overflow from measure to storm water drainage system (0 = no, 1 = yes)
    # surf_runoff_meas_mss --- predefined definition of surface runoff from measure to mixed sewer system (0 = no, 1 = yes)
    # ctrl_runoff_meas_mss --- predefined definition of controlled runoff from measure to mixed sewer system (0 = no, 1 = yes)
    # overflow_meas_gw--- predefined definition of overflow from measure to mixed sewer system (0 = no, 1 = yes)
    # surf_runoff_meas_out --- predefined definition of surface runoff from measure to outside water (0 = no, 1 = yes)
    # ctrl_runoff_meas_out --- predefined definition of controlled runoff from measure to outside water (0 = no, 1 = yes)
    # overflow_meas_out --- predefined definition of overflow from measure to outside water (0 = no, 1 = yes)

    meas_area = cf["meas_area"]
    runoff_to_stor_layer = cf["runoff_to_stor_layer"]
    intstor_meas_t0 = cf["intstor_meas_t0"]
    ev_evaporation = cf["ev_evaporation"]
    num_stor_lvl = cf["num_stor_lvl"]
    infil_cap_meas = cf["infil_cap_meas"]
    top_storcap_meas = cf["top_storcap_meas"]
    bot_storcap_meas = cf["bot_storcap_meas"]
    top_stor_meas_t0 = cf["top_stor_meas_t0"]
    bot_stor_meas_t0 = cf["bot_stor_meas_t0"]
    int_cap_meas = cf["int_cap_meas"]
    ts_area_meas = cf["ts_area_meas"]
    et_transpiration = cf["et_transpiration"]
    e_fac_meas = cf["e_frac_meas"]
    in_infiltration = cf["in_infiltration"]
    tinf_cap_meas = cf["tinf_cap_meas"]
    bs_area_meas = cf["bs_area_meas"]
    btm_et_transpiration = cf["btm_et_transpiration"]
    connection_to_gw = cf["connection_to_gw"]
    gwl_limit_meas = cf["gwl_limit_meas"]
    b_level_meas = cf["b_level_meas"]
    btm_discharge_type = cf["btm_discharge_type"]
    br_cap_meas = cf["br_cap_meas"]
    bdl_meas = cf["bdl_meas"]
    bdr_meas = cf["bdr_meas"]
    # temporary
    waterbalance_check = cf["waterbalance_check"]

    # Buttons:
    surf_runoff_meas_ow = cf["surf_runoff_meas_ow"]
    ctrl_runoff_meas_ow = cf["ctrl_runoff_meas_ow"]
    overflow_meas_ow = cf["overflow_meas_ow"]
    surf_runoff_meas_uz = cf["surf_runoff_meas_uz"]
    ctrl_runoff_meas_uz = cf["ctrl_runoff_meas_uz"]
    overflow_meas_uz = cf["overflow_meas_uz"]
    surf_runoff_meas_gw = cf["surf_runoff_meas_gw"]
    ctrl_runoff_meas_gw = cf["ctrl_runoff_meas_gw"]
    overflow_meas_gw = cf["overflow_meas_gw"]
    surf_runoff_meas_swds = cf["surf_runoff_meas_swds"]
    ctrl_runoff_meas_swds = cf["ctrl_runoff_meas_swds"]
    overflow_meas_swds = cf["overflow_meas_swds"]
    surf_runoff_meas_mss = cf["surf_runoff_meas_mss"]
    ctrl_runoff_meas_mss = cf["ctrl_runoff_meas_mss"]
    overflow_meas_mss = cf["overflow_meas_mss"]
    surf_runoff_meas_out = cf["surf_runoff_meas_out"]
    ctrl_runoff_meas_out = cf["ctrl_runoff_meas_out"]
    overflow_meas_out = cf["overflow_meas_out"]

    # Note that pr_meas_inflow_area should be within the range (pr_meas_area, tot_pr_area), it should be specified.
    # But for the time being we assume it is equal to pr_meas_area.
    # Assume for the time being, measure inflow area = component_area
    pr_meas_inflow_area = cf["pr_meas_inflow_area"]
    cp_meas_inflow_area = cf["cp_meas_inflow_area"]
    op_meas_inflow_area = cf["op_meas_inflow_area"]
    up_meas_inflow_area = cf["up_meas_inflow_area"]
    tot_meas_area = (
        pr_meas_area
        + cp_meas_area
        + op_meas_area
        + up_meas_area
        + uz_meas_area
        + gw_meas_area
        + swds_meas_area
        + mss_meas_area
        + ow_meas_area
    )
    isgreenroofdd = cf["isgreenroofdd"]
    # 0 or 1 check. check some parameters (some buttons) which can only be selected from 0 or 1
    k = [surf_runoff_meas_ow, ctrl_runoff_meas_ow, overflow_meas_ow, surf_runoff_meas_uz, ctrl_runoff_meas_uz, overflow_meas_uz, surf_runoff_meas_gw, ctrl_runoff_meas_gw, overflow_meas_gw,
         surf_runoff_meas_swds, ctrl_runoff_meas_swds, overflow_meas_swds, surf_runoff_meas_mss, ctrl_runoff_meas_mss, overflow_meas_mss, surf_runoff_meas_out, ctrl_runoff_meas_out, overflow_meas_out,
         gwl_limit_meas, connection_to_gw, btm_et_transpiration, btm_discharge_type]
    check = [n for n in k if n != 0 and n != 1]
    if len(check) != 0:
        print(check)
        raise ValueError("Error: Button Parameter can only be 0 or 1.")
    if num_stor_lvl != 1 and num_stor_lvl != 2 and num_stor_lvl != 3:
        # print(num_stor_lvl)
        raise ValueError("Error: Number of storage levels can only be (1, 2 or 3) (integer)")
    if runoff_to_stor_layer !=1 and runoff_to_stor_layer != 3:
        raise ValueError("Error: runoff_to_stor_layer (Runoff from other areas into storage layer) can only be (1 or 3)")
    return {
        "pr_meas_area": pr_meas_area,
        "cp_meas_area": cp_meas_area,
        "op_meas_area": op_meas_area,
        "up_meas_area": up_meas_area,
        "uz_meas_area": uz_meas_area,
        "gw_meas_area": gw_meas_area,
        "swds_meas_area": swds_meas_area,
        "mss_meas_area": mss_meas_area,
        "ow_meas_area": ow_meas_area,
        "tot_meas_area": tot_meas_area,
        "pr_meas_inflow_area": pr_meas_inflow_area,
        "cp_meas_inflow_area": cp_meas_inflow_area,
        "op_meas_inflow_area": op_meas_inflow_area,
        "up_meas_inflow_area": up_meas_inflow_area,
        "meas_area": meas_area,
        "runoff_to_stor_layer": runoff_to_stor_layer,
        "intstor_meas_t0": intstor_meas_t0,
        "ev_evaporation": ev_evaporation,
        "num_stor_lvl": num_stor_lvl,
        "infil_cap_meas": infil_cap_meas,
        "top_storcap_meas": top_storcap_meas,
        "bot_storcap_meas": bot_storcap_meas,
        "top_stor_meas_t0": top_stor_meas_t0,
        "bot_stor_meas_t0": bot_stor_meas_t0,
        "int_cap_meas": int_cap_meas,
        "ts_area_meas": ts_area_meas,
        "et_transpiration": et_transpiration,
        "e_fac_meas": e_fac_meas,
        "in_infiltration": in_infiltration,
        "tinf_cap_meas": tinf_cap_meas,
        "bs_area_meas": bs_area_meas,
        "btm_et_transpiration": btm_et_transpiration,
        "connection_to_gw": connection_to_gw,
        "gwl_limit_meas": gwl_limit_meas,
        "b_level_meas": b_level_meas,
        "btm_discharge_type": btm_discharge_type,
        "br_cap_meas": br_cap_meas,
        "bdl_meas": bdl_meas,
        "bdr_meas": bdr_meas,
        "surf_runoff_meas_ow": surf_runoff_meas_ow,
        "ctrl_runoff_meas_ow": ctrl_runoff_meas_ow,
        "overflow_meas_ow": overflow_meas_ow,
        "surf_runoff_meas_uz": surf_runoff_meas_uz,
        "ctrl_runoff_meas_uz": ctrl_runoff_meas_uz,
        "overflow_meas_uz": overflow_meas_uz,
        "surf_runoff_meas_gw": surf_runoff_meas_gw,
        "ctrl_runoff_meas_gw": ctrl_runoff_meas_gw,
        "overflow_meas_gw": overflow_meas_gw,
        "surf_runoff_meas_swds": surf_runoff_meas_swds,
        "ctrl_runoff_meas_swds": ctrl_runoff_meas_swds,
        "overflow_meas_swds": overflow_meas_swds,
        "surf_runoff_meas_mss": surf_runoff_meas_mss,
        "ctrl_runoff_meas_mss": ctrl_runoff_meas_swds,
        "overflow_meas_mss": overflow_meas_mss,
        "surf_runoff_meas_out": surf_runoff_meas_out,
        "ctrl_runoff_meas_out": ctrl_runoff_meas_out,
        "overflow_meas_out": overflow_meas_out,
        "waterbalance_check": waterbalance_check,
        "isgreenroofdd": isgreenroofdd
    }


if __name__ == "__main__":
    print(read_parameter_measure("static_form_measure_for_measure.ini"))
    # fire.Fire(read_parameter_measure)

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
    choice = cf["measure_applied"]

    tot_meas_area = cf["tot_meas_area"]
    top_meas_area = cf["top_meas_area"]
    btm_meas_area = cf["btm_meas_area"]

    pr_meas_inflow_area = cf["pr_meas_inflow_area"]
    cp_meas_inflow_area = cf["cp_meas_inflow_area"]
    op_meas_inflow_area = cf["op_meas_inflow_area"]
    up_meas_inflow_area = cf["up_meas_inflow_area"]
    ow_meas_inflow_area = cf["ow_meas_inflow_area"]
    tot_meas_inflow_area = (
        pr_meas_inflow_area
        + cp_meas_inflow_area
        + op_meas_inflow_area
        + up_meas_inflow_area
        + ow_meas_inflow_area
    )
    # deal with initial values here later
    validinput = False
    while not validinput:
        if not choice:  # input choice: no measure
            # to make it as foolproof as possible, when measure is not applied, measure-related area will all be set as
            # zeros regardless of what is in the configuration file.

            tot_meas_area = (
                pr_meas_area
            ) = (
                cp_meas_area
            ) = (
                op_meas_area
            ) = (
                up_meas_area
            ) = (
                uz_meas_area
            ) = (
                gw_meas_area
            ) = (
                swds_meas_area
            ) = mss_meas_area = ow_meas_area = top_meas_area = btm_meas_area = 0.0

            pr_meas_inflow_area = (
                cp_meas_inflow_area
            ) = (
                op_meas_inflow_area
            ) = up_meas_inflow_area = ow_meas_inflow_area = tot_meas_inflow_area = 0.0

            validinput = True
        elif choice:  # input choice: there is measure
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
            raise ValueError("Error: Choice can only be true or false.")
    # these parameters are parameters for measure. As you can see in the configuration file,
    # these so many parameters are confusing and overview of parameters is not as good as excel.
    # Hence, it may be possible that we build a GUI to handle this problem. But for the time being,
    # we just build like this to make it run first.

    # tot_meas_area -- predefined measure area [m^2]
    # Button_BW17 --- predefined selection at which measure layer runoff from other areas is stored (1 or 3), Inflow from other areas can only take place at interception level (1) or at the bottom storage level (3).
    # * intstor_meas_prevt --- interception storage on the measure at previous time step [mm]
    # intstor_meas_t0 --- predefined interception storage on the measure at t=0 [mm]
    # EV_evaporation --- predefined selection if evaporation from measure is possible (1) or not (0)
    # num_stor_lvl --- predefined number of storage levels (1, 2 or 3)
    # infilcap_int_meas --- predefined infiltration capacity of measure [mm/d] (4800mm/d)
    # storcap_top_meas --- predefined storage capacity in top layer of measure (76.2mm)
    # storcap_btm_meas --- predefined storage capacity in bottom layer of measure (182.88mm)
    # * stor_top_meas_prevt --- top layer storage at the end of previous time step [mm]
    # top_stor_meas_t0 --- top layer storage at t = 0 [mm] (0 mm)
    # * stor_btm_meas_prevt --- bottom layer storage at the end of previous time step [mm]
    # bot_stor_meas_t0 --- bottom layer storage at t = 0 [mm] (0 mm)

    # storcap_int_meas --- predefined interception storage capacity of measure [mm] (20mm)
    # top_meas_area --- predefined area of top layer storage area of measure [m^2]
    # ET_transpiration --- predefined selection if transpiration from measure is possible (1) or not (0)
    # evaporation_factor_meas --- predefined evaporation factor of measure [-]
    # infilcap_top_meas --- predefined infiltration capacity of top layer of measure [mm/d] (480mm/d)

    # btm_meas_area --- predefined area of bottom layer storage area of measure [m^2]
    # btm_meas_transpiration --- predefined selection if transpiration from bottom layer of measure is possible (1) or not (0)
    # connection_to_gw --- predefined selection if percolation (connection) from measure to groundwater is possible (1) or not (0)
    # limited_by_gwl --- predefined limitation of percolation from measure to groundwater if groundwater level is below measure bottom level (1=yes; 0=no)
    # btm_level_meas --- predefined bottom level of measure [m -SL] (0.6858)
    # btm_discharge_type --- predefined definition of discharge type from bottom layer of measure (0 = down_seepage_flux limited, 1 = level difference over resistance)
    # runoffcap_btm_meas --- predefined runoff capacity from bottom layer of measure [mm/d] (down_seepage_flux=15mm/d)
    # dischlvl_btm_meas --- predefined discharge level from bottom layer of measure [mm]
    # c_btm_meas --- predefined hydraulic resistance for level induced discharge from bottom layer of measure [d]

    # surf_runoff_meas_OW --- predefined definition of surface runoff from measure to open water (0 = no, 1 = yes)
    # ctrl_runoff_meas_OW --- predefined definition of controlled runoff from measure to open water (0 = no, 1 = yes)
    # overflow_meas_OW --- predefined definition of overflow from measure to open water (0 = no, 1 = yes)
    # surf_runoff_meas_UZ --- predefined definition of surface runoff from measure to unsaturated zone (0 = no, 1 = yes)
    # ctrl_runoff_meas_UZ --- predefined definition of controlled runoff from measure to unsaturated zone (0 = no, 1 = yes)
    # overflow_meas_UZ --- predefined definition of overflow from measure to unsaturated zone (0 = no, 1 = yes)
    # surf_runoff_meas_GW --- predefined definition of surface runoff from measure to groundwater (0 = no, 1 = yes)
    # ctrl_runoff_meas_GW --- predefined definition of controlled runoff from measure to groundwater (0 = no, 1 = yes)
    # overflow_meas_GW --- predefined definition of overflow from measure to groundwater (0 = no, 1 = yes)
    # surf_runoff_meas_SWDS --- predefined definition of surface runoff from measure to storm water drainage system (0 = no, 1 = yes)
    # ctrl_runoff_meas_SWDS --- predefined definition of controlled runoff from measure to storm water drainage system (0 = no, 1 = yes)
    # overflow_meas_GW --- predefined definition of overflow from measure to storm water drainage system (0 = no, 1 = yes)
    # surf_runoff_meas_MSS --- predefined definition of surface runoff from measure to mixed sewer system (0 = no, 1 = yes)
    # ctrl_runoff_meas_MSS --- predefined definition of controlled runoff from measure to mixed sewer system (0 = no, 1 = yes)
    # overflow_meas_GW--- predefined definition of overflow from measure to mixed sewer system (0 = no, 1 = yes)
    # surf_runoff_meas_Out --- predefined definition of surface runoff from measure to outside water (0 = no, 1 = yes)
    # ctrl_runoff_meas_Out --- predefined definition of controlled runoff from measure to outside water (0 = no, 1 = yes)
    # overflow_meas_Out --- predefined definition of overflow from measure to outside water (0 = no, 1 = yes)

    runoff_to_stor_layer = cf["runoff_to_stor_layer"]
    intstor_meas_t0 = cf["intstor_meas_t0"]
    EV_evaporation = cf["EV_evaporation"]
    num_stor_lvl = cf["num_stor_lvl"]
    infilcap_int_meas = cf["infilcap_int_meas"]
    storcap_top_meas = cf["storcap_top_meas"]
    storcap_btm_meas = cf["storcap_btm_meas"]
    stor_top_meas_t0 = cf["stor_top_meas_t0"]
    stor_btm_meas_t0 = cf["stor_btm_meas_t0"]
    storcap_int_meas = cf["storcap_int_meas"]
    ET_transpiration = cf["ET_transpiration"]
    evaporation_factor_meas = cf["evaporation_factor_meas"]
    IN_infiltration = cf["IN_infiltration"]
    infilcap_top_meas = cf["infilcap_top_meas"]
    btm_meas_transpiration = cf["btm_meas_transpiration"]
    connection_to_gw = cf["connection_to_gw"]
    limited_by_gwl = cf["limited_by_gwl"]
    btm_level_meas = cf["btm_level_meas"]
    btm_discharge_type = cf["btm_discharge_type"]
    runoffcap_btm_meas = cf["runoffcap_btm_meas"]
    dischlvl_btm_meas = cf["dischlvl_btm_meas"]
    c_btm_meas = cf["c_btm_meas"]

    # Buttons:
    surf_runoff_meas_OW = cf["surf_runoff_meas_OW"]
    ctrl_runoff_meas_OW = cf["ctrl_runoff_meas_OW"]
    overflow_meas_OW = cf["overflow_meas_OW"]
    surf_runoff_meas_UZ = cf["surf_runoff_meas_UZ"]
    ctrl_runoff_meas_UZ = cf["ctrl_runoff_meas_UZ"]
    overflow_meas_UZ = cf["overflow_meas_UZ"]
    surf_runoff_meas_GW = cf["surf_runoff_meas_GW"]
    ctrl_runoff_meas_GW = cf["ctrl_runoff_meas_GW"]
    overflow_meas_GW = cf["overflow_meas_GW"]
    surf_runoff_meas_SWDS = cf["surf_runoff_meas_SWDS"]
    ctrl_runoff_meas_SWDS = cf["ctrl_runoff_meas_SWDS"]
    overflow_meas_SWDS = cf["overflow_meas_SWDS"]
    surf_runoff_meas_MSS = cf["surf_runoff_meas_MSS"]
    ctrl_runoff_meas_MSS = cf["ctrl_runoff_meas_MSS"]
    overflow_meas_MSS = cf["overflow_meas_MSS"]
    surf_runoff_meas_Out = cf["surf_runoff_meas_Out"]
    ctrl_runoff_meas_Out = cf["ctrl_runoff_meas_Out"]
    overflow_meas_Out = cf["overflow_meas_Out"]

    # Note that pr_meas_inflow_area should be within the range (pr_meas_area, tot_pr_area), it should be specified.
    # But for the time being we assume it is equal to pr_meas_area.
    # Assume for the time being, measure inflow area = component_area

    if tot_meas_area != (
        pr_meas_area
        + cp_meas_area
        + op_meas_area
        + up_meas_area
        + uz_meas_area
        + gw_meas_area
        + swds_meas_area
        + mss_meas_area
        + ow_meas_area
    ):
        raise ValueError("Error: Measure area info error")
    greenroof_type_measure = cf["greenroof_type_measure"]
    # 0 or 1 check. check some parameters (some buttons) which can only be selected from 0 or 1
    k = [
        surf_runoff_meas_OW,
        ctrl_runoff_meas_OW,
        overflow_meas_OW,
        surf_runoff_meas_UZ,
        ctrl_runoff_meas_UZ,
        overflow_meas_UZ,
        surf_runoff_meas_GW,
        ctrl_runoff_meas_GW,
        overflow_meas_GW,
        surf_runoff_meas_SWDS,
        ctrl_runoff_meas_SWDS,
        overflow_meas_SWDS,
        surf_runoff_meas_MSS,
        ctrl_runoff_meas_MSS,
        overflow_meas_MSS,
        surf_runoff_meas_Out,
        ctrl_runoff_meas_Out,
        overflow_meas_Out,
        limited_by_gwl,
        connection_to_gw,
        btm_meas_transpiration,
        btm_discharge_type,
    ]
    check = [n for n in k if n != 0 and n != 1]
    if len(check) != 0:
        print(check)
        raise ValueError("Error: Button Parameter can only be 0 or 1.")
    if num_stor_lvl != 1 and num_stor_lvl != 2 and num_stor_lvl != 3:
        # print(num_stor_lvl)
        raise ValueError(
            "Error: Number of storage levels can only be (1, 2 or 3) (integer)"
        )
    if runoff_to_stor_layer != 1 and runoff_to_stor_layer != 3:
        raise ValueError(
            "Error: runoff_to_stor_layer (Runoff from other areas into storage layer) can only be (1 or 3)"
        )

    title = cf["title"]
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
        "ow_meas_inflow_area": ow_meas_inflow_area,
        "runoff_to_stor_layer": runoff_to_stor_layer,
        "intstor_meas_t0": intstor_meas_t0,
        "EV_evaporation": EV_evaporation,
        "num_stor_lvl": num_stor_lvl,
        "infilcap_int_meas": infilcap_int_meas,
        "storcap_top_meas": storcap_top_meas,
        "storcap_btm_meas": storcap_btm_meas,
        "stor_top_meas_t0": stor_top_meas_t0,
        "stor_btm_meas_t0": stor_btm_meas_t0,
        "storcap_int_meas": storcap_int_meas,
        "top_meas_area": top_meas_area,
        "ET_transpiration": ET_transpiration,
        "evaporation_factor_meas": evaporation_factor_meas,
        "IN_infiltration": IN_infiltration,
        "infilcap_top_meas": infilcap_top_meas,
        "btm_meas_area": btm_meas_area,
        "btm_meas_transpiration": btm_meas_transpiration,
        "connection_to_gw": connection_to_gw,
        "limited_by_gwl": limited_by_gwl,
        "btm_level_meas": btm_level_meas,
        "btm_discharge_type": btm_discharge_type,
        "runoffcap_btm_meas": runoffcap_btm_meas,
        "dischlvl_btm_meas": dischlvl_btm_meas,
        "c_btm_meas": c_btm_meas,
        "surf_runoff_meas_OW": surf_runoff_meas_OW,
        "ctrl_runoff_meas_OW": ctrl_runoff_meas_OW,
        "overflow_meas_OW": overflow_meas_OW,
        "surf_runoff_meas_UZ": surf_runoff_meas_UZ,
        "ctrl_runoff_meas_UZ": ctrl_runoff_meas_UZ,
        "overflow_meas_UZ": overflow_meas_UZ,
        "surf_runoff_meas_GW": surf_runoff_meas_GW,
        "ctrl_runoff_meas_GW": ctrl_runoff_meas_GW,
        "overflow_meas_GW": overflow_meas_GW,
        "surf_runoff_meas_SWDS": surf_runoff_meas_SWDS,
        "ctrl_runoff_meas_SWDS": ctrl_runoff_meas_SWDS,
        "overflow_meas_SWDS": overflow_meas_SWDS,
        "surf_runoff_meas_MSS": surf_runoff_meas_MSS,
        "ctrl_runoff_meas_MSS": ctrl_runoff_meas_MSS,
        "overflow_meas_MSS": overflow_meas_MSS,
        "surf_runoff_meas_Out": surf_runoff_meas_Out,
        "ctrl_runoff_meas_Out": ctrl_runoff_meas_Out,
        "overflow_meas_Out": overflow_meas_Out,
        "greenroof_type_measure": greenroof_type_measure,
        "tot_meas_inflow_area": tot_meas_inflow_area,  # note
        "title": title,
    }


if __name__ == "__main__":
    print(read_parameter_measure("static_form_measure_for_measure.ini"))
    # fire.Fire(read_parameter_measure)

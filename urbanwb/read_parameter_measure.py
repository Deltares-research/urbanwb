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
    # Button_BQ19 --- predefined selection if evaporation from measure is possible (1) or not (0)
    # Button_BQ18 --- predefined number of storage levels (1, 2 or 3)
    # infil_cap_meas --- predefined infiltration capacity of measure [mm/d] (4800mm/d)
    # top_storcap_meas --- predefined storage capacity in top layer of measure (76.2mm)
    # bot_storcap_meas --- predefined storage capacity in bottom layer of measure (182.88mm)
    # * prev_top_stor_meas --- top layer storage at the end of previous time step [mm]
    # top_stor_meas_t0 --- top layer storage at t = 0 [mm] (0 mm)
    # * prev_bot_stor_meas --- bottom layer storage at the end of previous time step [mm]
    # bot_stor_meas_t0 --- bottom layer storage at t = 0 [mm] (0 mm)

    # int_cap_meas --- predefined interception storage capacity of measure [mm] (20mm)
    # ts_area_meas --- predefined area of top layer storage area of measure [m^2]
    # Button_BQ20 --- predefined selection if transpiration from measure is possible (1) or not (0)
    # e_fac_meas --- predefined evaporation factor of measure [-]
    # tinf_cap_meas --- predefined infiltration capacity of top layer of measure [mm/d] (480mm/d)

    # bs_area_meas --- predefined area of bottom layer storage area of measure [m^2]
    # Button_CL21 --- predefined selection if transpiration from bottom layer of measure is possible (1) or not (0)
    # Button_CL17 --- predefined connection from measure to groundwater (1 = yes. 0 = no)
    # gwl_limit_meas --- predefined limitation of percolation from measure to groundwater if groundwater level is below measure bottom level (1=yes; 0=no)
    # k_sat_uz --- saturation permeability of soil [mm/d]
    # b_level_meas --- predefined bottom level of measure [m -SL] (0.6858)
    # Button_CP14 --- predefined definition of discharge type from bottom layer of measure (0 = flux limited, 1 = level difference over resistance)
    # br_cap_meas --- predefined runoff capacity from bottom layer of measure [mm/d] (flux=15mm/d)
    # bdl_meas --- predefined discharge level from bottom layer of measure [mm]
    # bdr_meas --- predefined hydraulic resistance for level induced discharge from bottom layer of measure [d]

    # button_BW25 --- predefined definition of surface runoff from measure to open water (0 = no, 1 = yes)
    # button_BW26 --- predefined definition of controlled runoff from measure to open water (0 = no, 1 = yes)
    # button_BW27 --- predefined definition of overflow from measure to open water (0 = no, 1 = yes)
    # button_BX25 --- predefined definition of surface runoff from measure to unsaturated zone (0 = no, 1 = yes)
    # button_BX26 --- predefined definition of controlled runoff from measure to unsaturated zone (0 = no, 1 = yes)
    # button_BX27 --- predefined definition of overflow from measure to unsaturated zone (0 = no, 1 = yes)
    # button_BY25 --- predefined definition of surface runoff from measure to groundwater (0 = no, 1 = yes)
    # button_BY26 --- predefined definition of controlled runoff from measure to groundwater (0 = no, 1 = yes)
    # button_BY27 --- predefined definition of overflow from measure to groundwater (0 = no, 1 = yes)
    # button_BZ25 --- predefined definition of surface runoff from measure to storm water drainage system (0 = no, 1 = yes)
    # button_BZ26 --- predefined definition of controlled runoff from measure to storm water drainage system (0 = no, 1 = yes)
    # button_BZ27 --- predefined definition of overflow from measure to storm water drainage system (0 = no, 1 = yes)
    # button_CA25 --- predefined definition of surface runoff from measure to mixed sewer system (0 = no, 1 = yes)
    # button_CA26 --- predefined definition of controlled runoff from measure to mixed sewer system (0 = no, 1 = yes)
    # button_CA27 --- predefined definition of overflow from measure to mixed sewer system (0 = no, 1 = yes)
    # button_CB25 --- predefined definition of surface runoff from measure to outside water (0 = no, 1 = yes)
    # button_CB26 --- predefined definition of controlled runoff from measure to outside water (0 = no, 1 = yes)
    # button_CB27 --- predefined definition of overflow from measure to outside water (0 = no, 1 = yes)

    meas_area = cf["meas_area"]
    Button_BW17 = cf["Button_BW17"]
    intstor_meas_t0 = cf["intstor_meas_t0"]
    Button_BQ19 = cf["Button_BQ19"]
    Button_BQ18 = cf["Button_BQ18"]
    infil_cap_meas = cf["infil_cap_meas"]
    top_storcap_meas = cf["top_storcap_meas"]
    bot_storcap_meas = cf["bot_storcap_meas"]
    top_stor_meas_t0 = cf["top_stor_meas_t0"]
    bot_stor_meas_t0 = cf["bot_stor_meas_t0"]
    int_cap_meas = cf["int_cap_meas"]
    ts_area_meas = cf["ts_area_meas"]
    Button_BQ20 = cf["Button_BQ20"]
    e_fac_meas = cf["e_frac_meas"]
    tinf_cap_meas = cf["tinf_cap_meas"]
    bs_area_meas = cf["bs_area_meas"]
    Button_CL21 = cf["Button_CL21"]
    Button_CL17 = cf["Button_CL17"]
    gwl_limit_meas = cf["gwl_limit_meas"]
    k_sat_uz = cf["k_sat_uz"]
    b_level_meas = cf["b_level_meas"]
    Button_CP14 = cf["Button_CP14"]
    br_cap_meas = cf["br_cap_meas"]
    bdl_meas = cf["bdl_meas"]
    bdr_meas = cf["bdr_meas"]

    # Buttons:
    Button_BW25 = cf["Button_BW25"]
    Button_BW26 = cf["Button_BW26"]
    Button_BW27 = cf["Button_BW27"]
    Button_BX25 = cf["Button_BX25"]
    Button_BX26 = cf["Button_BX26"]
    Button_BX27 = cf["Button_BX27"]
    Button_BY25 = cf["Button_BY25"]
    Button_BY26 = cf["Button_BY26"]
    Button_BY27 = cf["Button_BY27"]
    Button_BZ25 = cf["Button_BZ25"]
    Button_BZ26 = cf["Button_BZ26"]
    Button_BZ27 = cf["Button_BZ27"]
    Button_CA25 = cf["Button_CA25"]
    Button_CA26 = cf["Button_CA26"]
    Button_CA27 = cf["Button_CA27"]
    Button_CB25 = cf["Button_CB25"]
    Button_CB26 = cf["Button_CB26"]
    Button_CB27 = cf["Button_CB27"]

    # Note that pr_meas_inflow_area should be within the range (pr_meas_area, tot_pr_area), it should be specified.
    # But for the time being we assume it is equal to pr_meas_area.
    pr_meas_inflow_area = pr_meas_area
    cp_meas_inflow_area = cp_meas_area
    op_meas_inflow_area = op_meas_area
    up_meas_inflow_area = up_meas_area
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

    # 0 or 1 check. check some parameters (some buttons) which can only be selected from 0 or 1
    k = [Button_BW25, Button_BW26, Button_BW27, Button_BX25, Button_BX26, Button_BX27, Button_BY25, Button_BY26, Button_BY27,
         Button_BZ25, Button_BZ26, Button_BZ27, Button_CA25, Button_CA26, Button_CA27, Button_CB25, Button_CB26, Button_CB27,
         gwl_limit_meas, Button_CL17, Button_CL21, Button_CP14]
    check = [n for n in k if n != 0 and n != 1]
    if len(check) != 0:
        print(check)
        raise ValueError("Error: Button Parameter can only be 0 or 1.")
    if Button_BQ18 != 1 and Button_BQ18 != 2 and Button_BQ18 != 3:
        print(Button_BQ18)
        raise ValueError("Error: Number of storage levels can only be (1, 2 or 3) (integer)")
    if Button_BW17 !=1 and Button_BW17 != 3:
        print(Button_BW17)
        raise ValueError("Error: Runoff from other areas into storage layer can only be (1 or 3)")
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
        "Button_BW17": Button_BW17,
        "intstor_meas_t0": intstor_meas_t0,
        "Button_BQ19": Button_BQ19,
        "Button_BQ18": Button_BQ18,
        "infil_cap_meas": infil_cap_meas,
        "top_storcap_meas": top_storcap_meas,
        "bot_storcap_meas": bot_storcap_meas,
        "top_stor_meas_t0": top_stor_meas_t0,
        "bot_stor_meas_t0": bot_stor_meas_t0,
        "int_cap_meas": int_cap_meas,
        "ts_area_meas": ts_area_meas,
        "Button_BQ20": Button_BQ20,
        "e_fac_meas": e_fac_meas,
        "tinf_cap_meas": tinf_cap_meas,
        "bs_area_meas": bs_area_meas,
        "Button_CL21": Button_CL21,
        "Button_CL17": Button_CL17,
        "gwl_limit_meas": gwl_limit_meas,
        "k_sat_uz": k_sat_uz, # this will later be thrown into stat1.ini
        "b_level_meas": b_level_meas,
        "Button_CP14": Button_CP14,
        "br_cap_meas": br_cap_meas,
        "bdl_meas": bdl_meas,
        "bdr_meas": bdr_meas,
        "Button_BW25": Button_BW25,
        "Button_BW26": Button_BW26,
        "Button_BW27": Button_BW27,
        "Button_BX25": Button_BX25,
        "Button_BX26": Button_BX26,
        "Button_BX27": Button_BX27,
        "Button_BY25": Button_BY25,
        "Button_BY26": Button_BY26,
        "Button_BY27": Button_BY27,
        "Button_BZ25": Button_BZ25,
        "Button_BZ26": Button_BZ26,
        "Button_BZ27": Button_BZ27,
        "Button_CA25": Button_CA25,
        "Button_CA26": Button_CA26,
        "Button_CA27": Button_CA27,
        "Button_CB25": Button_CB25,
        "Button_CB26": Button_CB26,
        "Button_CB27": Button_CB27,
    }


if __name__ == "__main__":
    print(read_parameter_measure("static_form_measure.ini"))
    # fire.Fire(read_parameter_measure)

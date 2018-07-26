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
    Button_CB27 = cf["Button_CB26"]

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
        "k_sat_uz": k_sat_uz, # this will later thrown into stat1.ini
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

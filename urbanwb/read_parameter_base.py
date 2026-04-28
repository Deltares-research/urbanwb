import math
from collections.abc import Mapping

import fire
import toml


def read_parameter_base(arg):
    """Reads parameters from the TOML-formated static form.

    Args:
        arg (string): path of the static form of parameters for measures
        arg (mapping): an already parsed mapping

    Returns:
        (dictionary): A dictionary of general parameters

    """
    if isinstance(arg, Mapping):
        cf = arg
    else:
        stat1_inp = arg
        cf = toml.load(stat1_inp, _dict=dict)

    delta_t = (
        cf["timestep"] / 86400
    )  # length of timestep, converted from second (s) to day (d)
    tot_area = cf["tot_area"]  # total area of study area (model) [m^2]
    soiltype = cf["soiltype"]  # soil type
    croptype = cf["croptype"]  # crop type
    area_type = cf["area_type"]  # area input type [0: fraction, 1: area]
    validinput = False
    while not validinput:
        if area_type == 0:  # input area type: fraction
            pr_frac = cf["pr_frac"]  # paved roof fraction of total [-]
            cp_frac = cf["cp_frac"]  # closed paved fraction of total [-]
            op_frac = cf["op_frac"]  # open paved fraction of total [-]
            up_frac = cf["up_frac"]  # unpaved fraction of total [-]
            ow_frac = cf["ow_frac"]  # open water fraction of total [-]
            tot_pr_area = pr_frac * tot_area  # total area of paved roof [m^2]
            frac_pr_aboveGW = cf[
                "frac_pr_aboveGW"
            ]  # part of buildings (PR) above GW [-]
            tot_cp_area = cp_frac * tot_area  # total area of closed paved [m^2]
            tot_op_area = op_frac * tot_area  # total area of open paved [m^2]
            tot_up_area = up_frac * tot_area  # total area of unpaved [m^2]
            tot_ow_area = ow_frac * tot_area  # total area of open water [m^2]
            frac_ow_aboveGW = cf["frac_ow_aboveGW"]  # part of open water above GW [-]
            tot_uz_area = tot_up_area  # total area of unsaturated zone (Assumed equal to total area of unpaved) [m^2]
            gw_frac = (
                pr_frac * frac_pr_aboveGW
                + cp_frac
                + op_frac
                + up_frac
                + ow_frac * frac_ow_aboveGW
            )  # groundwater fraction of total [-]
            tot_gw_area = gw_frac * tot_area  # total area of groundwater [m^2]
            if math.isclose(
                pr_frac + cp_frac + op_frac + up_frac + ow_frac,
                1,
                rel_tol=1e-9,
                abs_tol=0.0,
            ):
                validinput = True
            else:
                raise ValueError("Error: Land use fractions do not add up to 1.")
        elif area_type == 1:  # input area type: area
            tot_pr_area = cf["tot_pr_area"]
            pr_frac = tot_pr_area / tot_area
            frac_pr_aboveGW = cf["frac_pr_aboveGW"]
            tot_cp_area = cf["tot_cp_area"]
            cp_frac = tot_cp_area / tot_area
            tot_op_area = cf["tot_op_area"]
            op_frac = tot_op_area / tot_area
            tot_up_area = cf["tot_up_area"]
            up_frac = tot_up_area / tot_area
            tot_ow_area = cf["tot_ow_area"]
            ow_frac = tot_ow_area / tot_area
            frac_ow_aboveGW = cf["frac_ow_aboveGW"]
            tot_uz_area = tot_up_area
            gw_frac = (
                pr_frac * frac_pr_aboveGW
                + cp_frac
                + op_frac
                + up_frac
                + ow_frac * frac_ow_aboveGW
            )
            tot_gw_area = gw_frac * tot_area
            if math.isclose(
                tot_pr_area + tot_cp_area + tot_op_area + tot_up_area + tot_ow_area,
                tot_area,
                rel_tol=1e-9,
                abs_tol=0.0,
            ):
                validinput = True
            else:
                raise ValueError("Error: land use areas do not add up to total area.")
        else:
            raise ValueError("Error: Input area type can only be 0-fraction or 1-area.")

    # part of paved area disconnected from sewer system
    discfrac_pr = cf[
        "discfrac_pr"
    ]  # part of paved roof disconnected from sewer system [-]
    discfrac_cp = cf[
        "discfrac_cp"
    ]  # part of closed paved disconnected from sewer system [-]
    discfrac_op = cf[
        "discfrac_op"
    ]  # part of open paved disconnected from sewer system [-]

    # interception storage capacity
    intstorcap_pr = cf[
        "intstorcap_pr"
    ]  # interception storage capacity on paved roof [mm]
    intstorcap_cp = cf[
        "intstorcap_cp"
    ]  # interception storage capacity on closed paved [mm]
    intstorcap_op = cf[
        "intstorcap_op"
    ]  # interception storage capacity on open paved [mm]
    intstorcap_up = cf["intstorcap_up"]  # interception storage capacity on unpaved [mm]
    storcap_ow = cf["storcap_ow"]  # storage capacity of open water [mm]

    # infiltration capacity
    infilcap_op = cf["infilcap_op"]  # infiltration capacity of open paved [mm/d]
    infilcap_up = cf["infilcap_up"]  # infiltration capacity of unpaved [mm/d]

    # rainfall statistics
    rainfall_swds_so = cf[
        "rainfall_swds_so"
    ]  # rainfall intensity when sewer overflow occurs on the street, in NL, it is T=2yr rainfall intensity [mm/dt]
    rainfall_mss_ow = cf[
        "rainfall_mss_ow"
    ]  # rainfall intensity when combined sewer overflow to open water occurs, in NL, it is T=1/6yr rainfall intensity [mm/dt]

    # sewer system parameters
    swds_frac = cf["swds_frac"]  # storm water drainage system fraction [-]
    mss_frac = 1.0 - swds_frac  # combined sewer system fraction [-]
    tot_disc_area = (
        tot_pr_area * discfrac_pr
        + tot_cp_area * discfrac_cp
        + tot_op_area * discfrac_op
    )
    tot_swds_area = swds_frac * (
        tot_pr_area + tot_cp_area + tot_op_area - tot_disc_area
    )
    tot_mss_area = mss_frac * (tot_pr_area + tot_cp_area + tot_op_area - tot_disc_area)
    storcap_swds = cf[
        "storcap_swds"
    ]  # storage capacity of storm water drainage system [mm]
    storcap_mss = cf["storcap_mss"]  # storage capacity of combined sewer system [mm]
    # discharge capacity of SWDS to open water [mm/dt], i.e. sewer discharge capacity of SWDS above which sewer overflow
    # onto street occurs, in NL, the design standard is it occurs once every two year.
    q_swds_ow_cap = rainfall_swds_so - intstorcap_cp - storcap_swds
    # discharge capacity of MSS to open water [mm/dt], i.e. sewer discharge capacity of MSS above which sewer overflow
    # onto street occurs, in NL, the design standard is it occurs once every two year.
    q_mss_ow_cap = rainfall_swds_so - intstorcap_cp - storcap_mss
    # discharge capacity of MSS to WWTP [mm/dt], i.e. sewer discharge capacity of MSS above which combined sewer
    # overflow to open water through CSO weir occurs, in NL, the design standard is it occurs six times per year.
    q_mss_out_cap = rainfall_mss_ow - intstorcap_cp

    # groundwater parameters
    w = cf["w"]  # drainage resistance w from groundwater to open water [d]
    seepage_define = cf["seepage_define"]  # defined seepage [0: flux, 1: level]
    if seepage_define == 0 or seepage_define == 1:
        down_seepage_flux = cf[
            "down_seepage_flux"
        ]  # constant downward flux from shallow groundwater to deep groundwater [mm/d] (negative means upward)
        gwl_t0 = cf["gwl_t0"]
        head_deep_gw = cf["head_deep_gw"]  # hydraulic head of deep groundwater [m-SL]
        vc = cf[
            "vc"
        ]  # vertical flow resistance from shallow groundwater to deep groundwater vc [d]
    else:
        raise ValueError(
            "Error: Seepage to deep groundwater can only be defined as either 0-flux or 1-level."
        )

    # open water parameters.
    q_ow_out_qh = cf.get("q_ow_out_qh", None)  # Q(h) relation: list of {h, q} dicts
    if q_ow_out_qh is not None:
        if "q_ow_out_cap" in cf:
            raise ValueError("Error: Cannot specify both q_ow_out_cap and q_ow_out_qh.")
        for entry in q_ow_out_qh:
            if not isinstance(entry, dict) or "h" not in entry or "q" not in entry:
                raise ValueError(
                    "Error: Each entry in q_ow_out_qh must have 'h' and 'q' keys."
                )
        q_ow_out_cap = None
    else:
        q_ow_out_cap = cf[
            "q_ow_out_cap"
        ]  # discharge capacity from open water to outside water over entire area [mm/d]
    q_ow_in_cap = cf.get(
        "q_ow_in_cap", float("inf")
    )  # inlet capacity from outside water to open water over entire area [mm/d], default unlimited
    ow_level = (
        storcap_ow / 1000.0
    )  # predefined target open water level, also initial open water level (at t=0) [m-Sl]

    # Non-negative check
    list1 = [
        delta_t,
        tot_area,
        soiltype,
        croptype,
        area_type,
        tot_pr_area,
        tot_cp_area,
        tot_op_area,
        tot_up_area,
        tot_ow_area,
        tot_uz_area,
        tot_gw_area,
        frac_pr_aboveGW,
        frac_ow_aboveGW,
        discfrac_pr,
        discfrac_cp,
        discfrac_op,
        intstorcap_pr,
        intstorcap_cp,
        intstorcap_op,
        intstorcap_up,
        infilcap_op,
        infilcap_up,
        swds_frac,
        storcap_swds,
        storcap_mss,
        rainfall_swds_so,
        rainfall_mss_ow,
        q_swds_ow_cap,
        q_mss_ow_cap,
        q_mss_out_cap,
        w,
        seepage_define,
        gwl_t0,
        head_deep_gw,
        vc,
        q_ow_in_cap,
    ]  # note that: down_seepage_flux can be negative(when upward down_seepage_flux)
    if q_ow_out_cap is not None:
        list1.append(q_ow_out_cap)
    if q_ow_out_qh is not None:
        for entry in q_ow_out_qh:
            list1.append(entry["q"])

    # Fraction within [0,1] check
    list2 = [
        pr_frac,
        cp_frac,
        op_frac,
        up_frac,
        ow_frac,
        gw_frac,
        frac_pr_aboveGW,
        frac_ow_aboveGW,
        discfrac_pr,
        discfrac_cp,
        discfrac_op,
        swds_frac,
    ]

    k1 = [n for n in list1 if n < 0]
    k2 = [n for n in list2 if n > 1 or n < 0]
    if len(k1) != 0:
        print(k1)
        raise ValueError("Error: Parameter is negative.")
    if len(k2) != 0:
        print(k2)
        raise ValueError("Error: Fraction is over 1 or negative.")

    intstor_pr_t0 = cf["intstor_pr_t0"]
    intstor_cp_t0 = cf["intstor_cp_t0"]
    intstor_op_t0 = cf["intstor_op_t0"]
    fin_intstor_up_t0 = cf["fin_intstor_up_t0"]
    stor_swds_t0 = cf["stor_swds_t0"]
    so_swds_t0 = cf["so_swds_t0"]
    stor_mss_t0 = cf["stor_mss_t0"]
    so_mss_t0 = cf["so_mss_t0"]

    return {
        "delta_t": delta_t,
        "tot_area": tot_area,
        "soiltype": soiltype,
        "croptype": croptype,
        "tot_pr_area": tot_pr_area,
        "tot_cp_area": tot_cp_area,
        "tot_op_area": tot_op_area,
        "tot_up_area": tot_up_area,
        "tot_ow_area": tot_ow_area,
        "tot_uz_area": tot_uz_area,
        "tot_gw_area": tot_gw_area,
        "discfrac_pr": discfrac_pr,
        "discfrac_cp": discfrac_cp,
        "discfrac_op": discfrac_op,
        "swds_frac": swds_frac,
        "tot_swds_area": tot_swds_area,
        "tot_mss_area": tot_mss_area,
        "storcap_swds": storcap_swds,
        "storcap_mss": storcap_mss,
        "intstorcap_pr": intstorcap_pr,
        "intstorcap_cp": intstorcap_cp,
        "intstorcap_op": intstorcap_op,
        "intstorcap_up": intstorcap_up,
        "infilcap_op": infilcap_op,
        "infilcap_up": infilcap_up,
        "w": w,
        "seepage_define": seepage_define,
        "down_seepage_flux": down_seepage_flux,
        "gwl_t0": gwl_t0,
        "head_deep_gw": head_deep_gw,
        "vc": vc,
        "q_swds_ow_cap": q_swds_ow_cap,
        "q_mss_ow_cap": q_mss_ow_cap,
        "q_mss_out_cap": q_mss_out_cap,
        "q_ow_out_cap": q_ow_out_cap,
        "q_ow_out_qh": q_ow_out_qh,
        "q_ow_in_cap": q_ow_in_cap,
        "ow_level": ow_level,
        "intstor_pr_t0": intstor_pr_t0,
        "intstor_cp_t0": intstor_cp_t0,
        "intstor_op_t0": intstor_op_t0,
        "fin_intstor_up_t0": fin_intstor_up_t0,
        "stor_swds_t0": stor_swds_t0,
        "so_swds_t0": so_swds_t0,
        "stor_mss_t0": stor_mss_t0,
        "so_mss_t0": so_mss_t0,
    }


if __name__ == "__main__":
    fire.Fire(read_parameter_base)

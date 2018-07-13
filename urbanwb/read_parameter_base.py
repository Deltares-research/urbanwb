import math
import toml
import fire
from pathlib import Path


def read_parameter_base(stat1_inp):
    """
    reads parameters from the TOML-formated static form.
    # stat1_inp --- filename of the static form of parameters for measures.
    """
    path = Path.cwd() / ".." / "input"
    cf = toml.load(str(path) + "\\" + stat1_inp, _dict=dict)
    delta_t = cf["timestep"] / 86400  # delta_t, converted from second to day
    tot_area = cf["tot_area"]  # total area
    soiltype = cf["soiltype"]  # soil type
    croptype = cf["croptype"]  # crop type
    choice = cf["type"]
    validinput = False
    while not validinput:
        if choice == 0:  # input type: fraction
            pr_frac = cf["pr_frac"]  # Paved roof fraction of total [-]
            cp_frac = cf["cp_frac"]  # closed paved fraction of total [-]
            op_frac = cf["op_frac"]  # open paved fraction of total [-]
            up_frac = cf["up_frac"]  # unpaved fraction of total [-]
            ow_frac = cf["ow_frac"]  # open water fraction of total [-]
            tot_pr_area = pr_frac * tot_area
            frac_pr_aboveGW = cf["frac_pr_aboveGW"]  # part of buildings above GW [-]
            tot_cp_area = cp_frac * tot_area
            tot_op_area = op_frac * tot_area
            tot_up_area = up_frac * tot_area
            tot_ow_area = ow_frac * tot_area
            frac_ow_aboveGW = cf["frac_ow_aboveGW"]  # part of open water above GW [-]
            tot_uz_area = (
                tot_up_area
            )  # total area of unsaturated zone [m^2] (Assumed to be equal to area of unpaved)
            gw_frac = (
                pr_frac * frac_pr_aboveGW
                + cp_frac
                + op_frac
                + up_frac
                + ow_frac * frac_ow_aboveGW
            )
            tot_gw_area = gw_frac * tot_area  # total area of groundwater [m^2]
            if math.isclose(
                pr_frac + cp_frac + op_frac + up_frac + ow_frac,
                1,
                rel_tol=1e-9,
                abs_tol=0.0,
            ):
                validinput = True
            else:
                raise ValueError("Error: Area fractions do not add up to 1 (type = 0).")
                # print('Area fractions do not add up to 1.')
                # return
        elif choice == 1:  # input type: area
            tot_pr_area = cf["tot_pr_area"]  # total area of paved roof [m^2]
            pr_frac = tot_pr_area / tot_area
            frac_pr_aboveGW = cf["frac_pr_aboveGW"]
            tot_cp_area = cf["tot_cp_area"]  # total area of closed paved [m^2]
            cp_frac = tot_cp_area / tot_area
            tot_op_area = cf["tot_op_area"]  # total area of open paved [m^2]
            op_frac = tot_op_area / tot_area
            tot_up_area = cf["tot_up_area"]  # total area of unpaved [m^2]
            up_frac = tot_up_area / tot_area
            tot_ow_area = cf["tot_ow_area"]  # total area of open water [m^2]
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
                raise ValueError(
                    "Error: Areas do not sum up to the total area (type = 1)."
                )
                # print('Areas do not sum up to the total area.')
                # return
        else:
            raise ValueError("Error: Type can only be 0 or 1.")
            # print("The input 'type' can only be 0 or 1.")
            # return

    # fraction of area that is disconnected from the sewer [-]
    discfrac_pr = cf[
        "discfrac_pr"
    ]  # fraction of paved roof area disconnected from sewer [-]
    discfrac_cp = cf[
        "discfrac_cp"
    ]  # fraction of closed paved area disconnected from sewer [-]
    discfrac_op = cf[
        "discfrac_op"
    ]  # fraction of open paved area disconnected from sewer [-]

    # interception storage capacity [mm]
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
    storcap_ow = cf["storcap_ow"]  # open water storage capacity [mm]

    # infiltration capacity parameters
    infilcap_op = cf[
        "infilcap_op"
    ]  # infiltration capacity of the open paved area [mm/d]
    infilcap_up = cf["infilcap_up"]  # infiltration capacity of the unpaved area [mm/d]

    # rainfall statistics
    rainfall_swds_so = cf[
        "rainfall_swds_so"
    ]  # rainfall intensity (when swds overflow on the street [mm/dt])
    rainfall_mss_ow = cf[
        "rainfall_mss_ow"
    ]  # rainfall intensity (when mss overflow to open water [mm/dt])

    # sewer system parameters
    swds_frac = cf["swds_frac"]  # storm water drainage system fraction [-]
    mss_frac = 1 - swds_frac  # mixed sewer system fraction [-]
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
    storcap_mss = cf["storcap_mss"]  # storage capacity of mixed sewer system [mm]
    pump_cap = cf["pump_cap"]  # pump capacity [lt/s/ha]
    discharge_cap = pump_cap * 8.64  # discharge capacity for total area [mm/d]
    q_swds_ow_cap = (
        rainfall_swds_so - intstorcap_cp - storcap_swds
    )  # discharge cap of SWDS to open water [mm/dt]
    q_mss_ow_cap = (
        rainfall_swds_so - intstorcap_cp - storcap_mss
    )  # discharge cap of MSS to open water [mm/dt]
    q_mss_out_cap = (
        rainfall_mss_ow - intstorcap_cp
    )  # discharge capacity of MSS to WWTP [mm/dt]

    # groundwater calculation parameters
    w = cf["w"]  # groundwater drainage resistance w [d]
    seep_def = cf["seep_def"]  # defined seepage [type: 0=flux, 1=level]
    if seep_def == 0 or seep_def == 1:
        flux = cf[
            "flux"
        ]  # defined constant downward seepage flux [mm/d] (can be negative [upward])
        init_gwl = cf["init_gwl"]
        h_deepgw = cf["h_deepgw"]  # defined hydraulic head of deep groundwater [m-SL]
        vc = cf["vc"]  # flow resistance between deep and shallow groundwater vc [d]
    else:
        raise ValueError(
            "Error: 'seep_def' (defined seepage) can only be 0(flux) or 1(level)."
        )

    # open water calculation parameters.
    # q_ow_out_cap needs to be dealt with carefully as it can be problematic in the batch run.
    q_ow_out_cap = (
        discharge_cap
    )  # predefined discharge capacity from open water to outside water [mm/d]
    ow_level = (
        storcap_ow / 1000
    )  # predefined target open water level/ initial open water level [m-Sl]

    # Non-negative check
    list1 = [
        delta_t,
        tot_area,
        soiltype,
        croptype,
        choice,
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
        ow_level,
        infilcap_op,
        infilcap_up,
        swds_frac,
        storcap_swds,
        storcap_mss,
        rainfall_swds_so,
        rainfall_mss_ow,
        pump_cap,
        q_swds_ow_cap,
        q_mss_ow_cap,
        q_mss_out_cap,
        w,
        seep_def,
        init_gwl,
        h_deepgw,
        vc,
        q_ow_out_cap,
        ow_level,
    ]  # note that: flux can be negative(when upward flux)

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
        "pump_cap": pump_cap,
        "intstorcap_pr": intstorcap_pr,
        "intstorcap_cp": intstorcap_cp,
        "intstorcap_op": intstorcap_op,
        "intstorcap_up": intstorcap_up,
        "infilcap_op": infilcap_op,
        "infilcap_up": infilcap_up,
        "w": w,
        "seep_def": seep_def,
        "flux": flux,
        "init_gwl": init_gwl,
        "h_deepgw": h_deepgw,
        "vc": vc,
        "q_swds_ow_cap": q_swds_ow_cap,
        "q_mss_ow_cap": q_mss_ow_cap,
        "q_mss_out_cap": q_mss_out_cap,
        "q_ow_out_cap": q_ow_out_cap,
        "ow_level": ow_level,
    }


if __name__ == "__main__":
    # print(read_parameter_base("static_form.ini"))
    fire.Fire(read_parameter_base)


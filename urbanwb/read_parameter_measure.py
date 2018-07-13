import toml
import fire
from pathlib import Path


def read_parameter_measure(stat2_inp):
    """
    reads parameters from the TOML-formated static form for measure.
    # stat2_inp --- filename of the static form of general parameters
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
    }


if __name__ == "__main__":
    # print(read_parameter_measure("static_form_measure.ini"))
    fire.Fire(read_parameter_measure)

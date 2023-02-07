import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

import urbanwb
from urbanwb.sewersystem import SewerSystem

path = urbanwb.urbanwbdir / ".." / "input"
InputData = pd.read_csv(path / "integration_test" / "input_csv.csv")
date = InputData["date"]
Ref_grass = InputData["Ref.grass"]
iters = np.shape(date)[0]
meas_swds = meas_mss = np.zeros(iters)


def validate(a, b, c, d, e, f, g, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match
    """
    # a --- area of storm water drainage system (without a measure)
    # b --- area of mixed sewer system (without a measure)
    # c --- q_swds_ow_cap predefined discharge capacity of storm water drainage system [mm/dt]
    # d --- q_mss_out_cap predefined discharge capacity of mixed sewer system to WWTP [mm/dt]
    # e --- q_mss_ow_cap predefined discharge capacity of mixed sewer system to open water [mm/dt]
    # f --- storcap_swds predefined storage capacity of storm water drainage system [mm]
    # g --- storcap_mss predefined storage capacity of mixed sewer system [mm]
    # Dec --- Desired precision, default is 6.
    # Num --- No. of test to locate excel file.

    m = SewerSystem(
        swds_no_meas_area=a,
        mss_no_meas_area=b,
        stor_swds_t0=0,
        so_swds_t0=0,
        stor_mss_t0=0,
        so_mss_t0=0,
        q_swds_ow_cap=c,
        q_mss_out_cap=d,
        q_mss_ow_cap=e,
        storcap_swds=f,
        storcap_mss=g,
    )
    data_py = [
        {
            "sum_r_swds": 0,
            "r_meas_swds": 0,
            "sum_r_mss": 0,
            "r_meas_mss": 0,
            "q_swds_ow": 0,
            "q_mss_out": 0,
            "q_mss_ow": 0,
            "so_swds_ow": 0,
            "so_mss_ow": 0,
            "stor_swds": 0,
            "stor_mss": 0,
        }
    ]

    R_swds = pd.read_csv(path / "integration_test" / "r_swds.csv")
    r_pr_swds = R_swds["r_pr_swds_" + str(Num)]
    r_cp_swds = R_swds["r_cp_swds_" + str(Num)]
    r_op_swds = R_swds["r_op_swds_" + str(Num)]
    R_mss = pd.read_csv(path / "integration_test" / "r_mss.csv")
    r_pr_mss = R_mss["r_pr_mss_" + str(Num)]
    r_cp_mss = R_mss["r_cp_mss_" + str(Num)]
    r_op_mss = R_mss["r_op_mss_" + str(Num)]
    (
        pr_no_meas_area,
        cp_no_meas_area,
        op_no_meas_area,
        ow_no_meas_area,
        tot_meas_area,
    ) = (
        1560,
        803.39,
        481.61,
        300,
        0,
    )

    t = 1
    while t <= iters - 1:
        data_py.append(
            m.sol(
                pr_no_meas_area,
                cp_no_meas_area,
                op_no_meas_area,
                r_pr_swds[t],
                r_cp_swds[t],
                r_op_swds[t],
                r_pr_mss[t],
                r_cp_mss[t],
                r_op_mss[t],
                meas_swds[t],
                meas_mss[t],
                ow_no_meas_area,
                tot_meas_area,
            )
        )
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = "ss_it_exsol_" + str(Num) + ".csv"
    data_ex = pd.read_csv(path / "integration_test" / filename_excel)
    keys = data_py.keys()
    none_list = []
    for key in keys:
        none_list.append(
            npt.assert_array_almost_equal(
                data_py[key][1:], data_ex[key][1:], decimal=Dec
            )
        )
        # assert_array_almost_equal is used to compare two arrays. If true, it returns None.
        # default decimal is 6.
        # comparison excludes first row (where there are NaNs in excel)
    return none_list


@pytest.fixture
def ss_1():
    return SewerSystem(
        2845,
        0,
        0,
        0,
        0,
        0,
        q_swds_ow_cap=55.1,
        q_mss_out_cap=26.3,
        q_mss_ow_cap=48.1,
        storcap_swds=2,
        storcap_mss=9,
    )


def test_sol(ss_1):
    """
    test the 'sol' in the SewerSystem class. Better carefully select values that can coverage all the
    process threshold
    """
    # time level t = 1/4/1986 11:00
    ss_1.stor_swds_prevt = 0
    ss_1.so_swds_prevt = 0
    ss_1.stor_mss_prevt = 0
    ss_1.so_mss_prevt = 0
    assert ss_1.sol(
        1560,
        803.390641,
        481.6093594,
        6.766687196,
        6.766687196,
        6.725020529,
        0,
        0,
        0,
        0,
        0,
        300,
        0,
    )["sum_r_swds"] == pytest.approx(6.7596337490)

    # # time level t = 1/4/1986 12:00
    ss_1.stor_swds_prevt = 0
    ss_1.so_swds_prevt = 0
    ss_1.stor_mss_prevt = 0
    ss_1.so_mss_prevt = 0
    assert ss_1.sol(
        1560,
        803.390641,
        481.6093594,
        0.670687196,
        0.670687196,
        0.629020529,
        0,
        0,
        0,
        0,
        0,
        300,
        0,
    )["q_swds_ow"] == pytest.approx(0.663633749)


def test_integration():
    """
    runs integration tests (validate with excel using different coefficient sets for all time steps)
    """
    for n in validate(2845, 0, 55.1, 26.3, 48.1, 2, 9, Dec=7, Num=0):  # default
        assert n is None
    for n in validate(
        2845, 0, 551, 26.3, 48.1, 2, 9, Dec=7, Num=1
    ):  # q_swds_ow_cap = 551
        assert n is None
    for n in validate(2845, 0, 0, 26.3, 48.1, 2, 9, Dec=7, Num=2):  # q_swds_ow_cap = 0
        assert n is None
    for n in validate(
        2845, 0, 55.1, 263, 48.1, 2, 9, Dec=7, Num=3
    ):  # q_mss_out_cap = 263
        assert n is None
    for n in validate(2845, 0, 55.1, 0, 48.1, 2, 9, Dec=7, Num=4):  # q_mss_out_cap = 0
        assert n is None
    for n in validate(
        2845, 0, 55.1, 26.3, 481, 2, 9, Dec=7, Num=5
    ):  # q_mss_ow_cap = 481
        assert n is None
    for n in validate(2845, 0, 55.1, 26.3, 0, 2, 9, Dec=7, Num=6):  # q_mss_ow_cap = 0
        assert n is None
    for n in validate(
        2845, 0, 37.1, 26.3, 48.1, 20, 9, Dec=7, Num=7
    ):  # q_swds_ow_cap = 37.1, storcap_swds = 20
        assert n is None
    for n in validate(
        2845, 0, 57.1, 26.3, 48.1, 0, 9, Dec=7, Num=8
    ):  # q_swds_ow_cap = 57.1, storcap_swds = 0
        assert n is None
    for n in validate(
        2845, 0, 55.1, 26.3, 48.1, 2, 90, Dec=7, Num=9
    ):  # storcap_mss = 90
        assert n is None
    for n in validate(
        2845, 0, 55.1, 26.3, 48.1, 2, 0, Dec=7, Num=10
    ):  # storcap_mss = 0
        assert n is None

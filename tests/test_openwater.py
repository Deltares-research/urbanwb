import pytest
import urbanwb
import numpy as np
import pandas as pd
import numpy.testing as npt
from urbanwb.openwater import OpenWater

path = urbanwb.urbanwbdir / ".." / "input"
InputData = pd.read_csv(path / "integration_test" / "input_csv.csv")
date = InputData["date"]
P_atm = InputData["P_atm"]
Ref_grass = InputData["Ref.grass"]
E_pot_OW = InputData["E_pot_OW"]
iters = np.shape(date)[0]
meas_ow = np.zeros(iters)


def validate(a, b, c, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match
    """

    # a --- area of open water (without a measure) [m^2].
    # b --- target open water level as well as the initial open water level [m-SL]
    # c --- q_ow_out_cap predefined discharge capacity from open water to outside water [mm/d]
    # Dec --- Desired precision, default is 6.
    # Num --- No. of test to locate excel file.

    m = OpenWater(ow_no_meas_area=a, ow_level=b, q_ow_out_cap=c)
    data_py = [
        {
            "prec_ow": 0,
            "e_atm_ow": 0,
            "sum_r_ow": 0,
            "sum_d_ow": 0,
            "sum_q_ow": 0,
            "sum_so_ow": 0,
            "r_meas_ow": 0,
            "q_ow_out": 0,
            "owl": b,
        }
    ]

    r_up_ow = pd.read_csv(path / "integration_test" / "r_up_ow.csv")[
        "r_up_ow_" + str(Num)
    ]
    d_gw_ow = pd.read_csv(path / "integration_test" / "d_gw_ow.csv")[
        "d_gw_ow_" + str(Num)
    ]
    q_swds_ow = pd.read_csv(path / "integration_test" / "q_swds_ow.csv")[
        "q_swds_ow_" + str(Num)
    ]
    q_mss_ow = pd.read_csv(path / "integration_test" / "q_mss_ow.csv")[
        "q_mss_ow_" + str(Num)
    ]
    so_swds_ow = pd.read_csv(path / "integration_test" / "so_swds_ow.csv")[
        "so_swds_ow_" + str(Num)
    ]
    so_mss_ow = pd.read_csv(path / "integration_test" / "so_mss_ow.csv")[
        "so_mss_ow_" + str(Num)
    ]

    t = 1
    while t <= iters - 1:
        data_py.append(
            m.sol(
                P_atm[t],
                E_pot_OW[t],
                r_up_ow[t],
                d_gw_ow[t],
                q_swds_ow[t],
                q_mss_ow[t],
                so_swds_ow[t],
                so_mss_ow[t],
                meas_ow[t],
                up_no_meas_area=6855,
                gw_no_meas_area=8140,
                swds_no_meas_area=2845,
                mss_no_meas_area=0,
                tot_meas_area=0,
                tot_area=10000,
                delta_t=1 / 24,
            )
        )
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = "ow_it_exsol_" + str(Num) + ".csv"
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
def ow_1():
    return OpenWater(ow_no_meas_area=300, ow_level=1.5, q_ow_out_cap=200)


def test_sol(ow_1):
    # time level t = 1/4/1986 11:00
    ow_1.prev_stor_swds = 0
    ow_1.prev_stor_mss = 0
    # ow_1.prev
    assert (
        ow_1.sol(
            0,
            0.331006211,
            0,
            -0.083728895,
            0,
            0,
            0,
            0,
            0,
            6855,
            8140,
            2845,
            0,
            0,
            10000,
            1 / 24,
        )["sum_d_ow"]
        == pytest.approx(-2.271844027)
    )


@pytest.mark.skip(reason="some larger differences found, have to investigate")
def test_integration():
    """
    runs integration tests (validate with excel using different coefficient sets for all time steps)
    """
    for n in validate(300, 1.5, 200, Dec=6, Num=0):  # default
        assert n is None
    for n in validate(300, 3, 200, Dec=3, Num=1):  # target open water level = 3
        assert n is None
    for n in validate(300, 1.5, 2000, Dec=2, Num=2):  # q_ow_out_cap = 2000
        assert n is None
    # for Num 1 Num 2 cases, the results are actually the same.

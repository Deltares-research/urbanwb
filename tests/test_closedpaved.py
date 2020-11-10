import pytest
import urbanwb
import numpy as np
import pandas as pd
import numpy.testing as npt
from urbanwb.closedpaved import ClosedPaved


def validate(a, b, c, d, e, f, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match
    """
    # a --- area of closed paved (without a measure)
    # b --- area of closed paved (with a measure)
    # c --- area of closed paved measure inflow area.
    # d --- interception storage capacity on closed paved.
    # e --- fraction of closed paved area with storm water drainage system.
    # f --- fraction of closed paved area that is disconnected to the sewer system.
    # Dec --- Desired precision, default is 6.
    # Num --- No. of test to locate excel file.

    path = urbanwb.urbanwbdir / ".." / "input"
    InputData = pd.read_csv(path / "input_csv.csv")
    date = InputData["date"]
    P_atm = InputData["P_atm"]
    E_pot_OW = InputData["E_pot_OW"]
    iters = np.shape(date)[0]

    m = ClosedPaved(
        intstor_cp_t0=0,
        cp_no_meas_area=a,
        cp_meas_area=b,
        cp_meas_inflow_area=c,
        intstorcap_cp=d,
        swds_frac=e,
        discfrac_cp=f,
    )
    data_py = [
        {
            "int_cp": 0,
            "e_atm_cp": 0,
            "intstor_cp": 0,
            "r_cp_meas": 0,
            "r_cp_swds": 0,
            "r_cp_mss": 0,
            "r_cp_up": 0,
        }
    ]
    t = 1
    while t <= iters - 1:
        data_py.append(m.sol(P_atm[t], E_pot_OW[t]))
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = "cp_it_exsol_" + str(Num) + ".csv"
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
def cp_1():
    return ClosedPaved(
        0, 803.3906406, 0, 0, intstorcap_cp=1.6, stormfrac_cp=1.0, discfrac_cp=0.0
    )


def test_inflowfac(cp_1):
    assert cp_1.inflowfac() == pytest.approx(0.0)


def test_sol(cp_1):
    # time level t = 4/22/1990 19:00
    cp_1.init_intstor_cp = 0  # update state
    assert cp_1.sol(8.89, 0.111267176)["int_cp"] == pytest.approx(1.6)

    # time level t = 4/22/1990 20:00
    cp_1.init_intstor_cp = 1.488732824  # update state
    assert cp_1.sol(0.254, 0)["r_cp_swds"] == pytest.approx(0.142732824)


def test_integration():
    """
    runs integration tests (validate with excel using different coefficient sets for all time steps)
    """
    for n in validate(803.39, 0, 0, 1.6, 1, 0, Dec=8, Num=0):  # default
        assert n is None
    for n in validate(0, 803.39, 0, 1.6, 1.0, 0.0, Dec=8, Num=1):  # cp_no_meas_area = 0
        assert n is None
    for n in validate(803.39, 0, 0, 0, 1, 0, Dec=8, Num=2):  # intstorcap_cp = 0
        assert n is None
    for n in validate(803.39, 0, 0, 1600, 1, 0, Dec=6, Num=3):  # intstorcap_cp = 1600
        assert n is None
    for n in validate(803.39, 0, 0, 1.6, 0, 0, Dec=8, Num=4):  # stormfrac = 0
        assert n is None
    for n in validate(803.39, 0, 0, 1.6, 0.37, 0, Dec=8, Num=5):  # stormfrac = 0.37
        assert n is None
    for n in validate(803.39, 0, 0, 1.6, 1, 1, Dec=8, Num=6):  # discfrac = 1
        assert n is None
    for n in validate(803.39, 0, 0, 1.6, 1, 0.37, Dec=8, Num=7):  # discfrac = 0.37
        assert n is None

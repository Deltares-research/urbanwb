import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

import urbanwb
from urbanwb.openpaved import OpenPaved


def validate(a, b, c, d, e, f, g, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match.
    """

    # a --- area of open paved (without a measure) [m^2].
    # b --- area of open paved(with a measure) [m^2].
    # c --- area of open paved measure inflow area [m^2].
    # d --- interception storage capacity on open paved [mm].
    # e --- fraction of open paved area with storm water drainage system [-].
    # f --- fraction of open paved area that is disconnected to the sewer system [-].
    # g --- predefined infiltration capacity on open paved area [mm/d]
    # Num --- No. of test to locate excel file.
    # Dec --- Desired precision, default is 6.

    path = urbanwb.urbanwbdir / ".." / "input"
    InputData = pd.read_csv(path / "integration_test" / "input_csv.csv")
    date = InputData["date"]
    P_atm = InputData["P_atm"]
    E_pot_OW = InputData["E_pot_OW"]
    iters = np.shape(date)[0]

    m = OpenPaved(
        intstor_op_t0=0,
        op_no_meas_area=a,
        op_meas_area=b,
        op_meas_inflow_area=c,
        intstorcap_op=d,
        swds_frac=e,
        discfrac_op=f,
        infilcap_op=g,
    )
    data_py = [
        {
            "int_op": 0,
            "e_atm_op": 0,
            "intstor_op": 0,
            "p_op_gw": 0,
            "r_op_meas": 0,
            "r_op_swds": 0,
            "r_op_mss": 0,
            "r_op_up": 0,
        }
    ]
    t = 1
    while t <= iters - 1:
        data_py.append(m.sol(P_atm[t], E_pot_OW[t], delta_t=1 / 24))
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = "op_it_exsol_" + str(Num) + ".csv"
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
def op_1():
    return OpenPaved(
        0, 481.6093594, 0, 0, intstorcap_op=1.6, stormfrac_op=1.0, discfrac_op=0.0
    )


def test_inflowfac(op_1):
    op_1.inflowfac() == pytest.approx(0.0)


def test_sol(op_1):
    # time level t = 12/23/1990 6:00
    op_1.intstor_op_prevt = 0  # update state
    assert op_1.sol(2.286, 0.02145677, 1 / 24)["int_op"] == pytest.approx(1.6)

    # time level t = 12/23/1990 7:00
    op_1.intstor_op_prevt = 0.02145677  # update state
    assert op_1.sol(12.7, 0.183915171, 1 / 24)["e_atm_op"] == pytest.approx(0.183915171)


def test_integration():
    """
    runs integration tests (validate with excel using different coefficient sets for all time steps)
    """
    for n in validate(481.61, 0, 0, 1.6, 1.0, 0, 1, Dec=8, Num=0):  # default
        assert n is None
    for n in validate(481.61, 0, 0, 0, 1, 0, 1, Dec=8, Num=1):  # intstorcap_op = 0
        assert n is None
    for n in validate(
        481.61, 0, 0, 1600, 1, 0, 1, Dec=6, Num=2
    ):  # intstorcap_op = 1600
        assert n is None
    for n in validate(481.61, 0, 0, 1.6, 0, 0, 1, Dec=8, Num=3):  # stormfrac = 0
        assert n is None
    for n in validate(481.61, 0, 0, 1.6, 0.37, 0, 1, Dec=8, Num=4):  # stormfrac = 0.37
        assert n is None
    for n in validate(481.61, 0, 0, 1.6, 1, 1, 1, Dec=8, Num=5):  # discfrac = 1
        assert n is None
    for n in validate(481.61, 0, 0, 1.6, 1, 0.37, 1, Dec=8, Num=6):  # discfrac = 0.37
        assert n is None
    for n in validate(481.61, 0, 0, 1.6, 1, 0, 0, Dec=8, Num=7):  # infilcap_op = 0
        assert n is None
    for n in validate(481.61, 0, 0, 1.6, 1, 0, 100, Dec=8, Num=8):  # infilcap_op = 100
        assert n is None
    for n in validate(
        0, 481.61, 481.61, 1.6, 1, 0, 1, Dec=8, Num=9
    ):  # op_no_meas_area = 0
        assert n is None

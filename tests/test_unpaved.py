import unittest
import urbanwb
import numpy as np
import pandas as pd
import numpy.testing as npt
from urbanwb.unpaved import Unpaved
from urbanwb.selector import soil_selector

path = urbanwb.urbanwbdir / ".." / "input"


def validate(a, b, c, d, e, f, g, h, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match
    """
    # a --- area of unpaved (without a measure) [m^2].
    # b --- area of unpaved (with a measure) [m^2].
    # c --- area of unpaved measure inflow area [m^2].
    # d --- predefined infiltration capacity of unpaved area [mm/d].
    # e --- maximum water volume in the root zone [mm].
    # f --- predefined saturated permeability of unsaturated zone [mm/d].
    # g --- predefined storage capacity on unpaved area [mm].
    # h --- area of open water (without a measure) [m^2].
    # Dec --- Desired precision, default is 6.
    # Num --- No. of test to locate excel file.

    InputData = pd.read_csv(path / "integration_test" / "input_csv.csv")
    date = InputData["date"]
    P_atm = InputData["P_atm"]
    E_pot_OW = InputData["E_pot_OW"]
    iters = np.shape(date)[0]

    r_up = pd.read_csv(path / "integration_test" / "r_up.csv")
    theta_rz = pd.read_csv(path / "integration_test" / "theta_rz.csv")
    r_pr_up = r_up["r_pr_up_" + str(Num)]
    r_cp_up = r_up["r_cp_up_" + str(Num)]
    r_op_up = r_up["r_op_up_" + str(Num)]
    theta_rz = theta_rz["theta_rz_" + str(Num)]

    m = Unpaved(
        fin_intstor_up_t0=0,
        up_no_meas_area=a,
        up_meas_area=b,
        up_meas_inflow_area=c,
        infilcap_up=d,
        intstorcap_up=e,
        soiltype=f,
        croptype=g,
    )
    data_py = [
        {
            "sum_r_up": 0,
            "init_stor_up": 0,
            "act_infilcap_up": 0,
            "tfac_up": 0,
            "e_atm_up": 0,
            "i_up_uz": 0,
            "fin_stor_up": 0,
            "r_up_meas": 0,
            "r_up_ow": 0,
        }
    ]
    t = 1
    while t <= iters - 1:
        data_py.append(
            m.sol(
                P_atm[t],
                E_pot_OW[t],
                r_pr_up[t],
                r_cp_up[t],
                r_op_up[t],
                theta_rz[t - 1],
                pr_no_meas_area=1560,
                cp_no_meas_area=803.39,
                op_no_meas_area=481.61,
                ow_no_meas_area=h,
                delta_t=1 / 24,
            )
        )
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = "up_it_exsol_" + str(Num) + ".csv"
    data_ex = pd.read_csv(path / "integration_test" / filename_excel)
    keys = data_py.keys()
    none_list = []
    for key in keys:
        none_list.append(
            npt.assert_array_almost_equal(
                data_py[key][1:], data_ex[key][1:], decimal=Dec
            )
        )
    return none_list


class TestOpenPaved(unittest.TestCase):
    def setUp(self):
        """
        runs the code before every single test
        """
        self.up_1 = Unpaved(
            0, 6855, 0, 0, infilcap_up=48, intstorcap_up=20, soiltype=2, croptype=1
        )

    def test_inflowfac(self):
        """
        test the 'inflowfac' in the Unpaved class
        """
        self.assertEqual(self.up_1.inflowfac(), 0)

    def test_sol(self):
        """
        test the 'sol' in the Unpaved class
        """

        # time level t = 8/1/1988 13:00
        self.up_1.fin_intstor_up_prevt = 0  # update state
        self.assertAlmostEqual(
            self.up_1.sol(
                0,
                0.346642066,
                0,
                0,
                0,
                175.7714344,
                1560,
                803.3906406,
                481.6093594,
                300,
                1 / 24,
            )["act_infilcap_up"],
            2,
        )

        # time level t = 8/1/1988 14:00
        self.up_1.fin_intstor_up_prevt = 0  # update state
        self.assertAlmostEqual(
            self.up_1.sol(
                4.826,
                0.346642066,
                0,
                0,
                0,
                175.5165721,
                1560,
                803.3906406,
                481.6093594,
                300,
                1 / 24,
            )["init_stor_up"],
            4.826,
        )

    def test_integration(self):
        """
        runs integration tests (validate with excel using different coefficient sets for all time steps)
        """
        for n in validate(6855, 0, 0, 48, 20, 2, 1, 300, Dec=8, Num=0):  # default
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 48, 0, 2, 1, 300, Dec=8, Num=1
        ):  # intstorcap_up = 0
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 48, 2000, 2, 1, 300, Dec=6, Num=2
        ):  # intstorcap_up = 2000
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 0, 20, 2, 1, 300, Dec=8, Num=3
        ):  # infilcap_up = 0
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 4800, 20, 2, 1, 300, Dec=6, Num=4
        ):  # infilcap_up = 4800
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 48, 20, 3, 1, 300, Dec=8, Num=5
        ):  # soiltype = 3, croptype = 1
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 48, 20, 4, 1, 300, Dec=8, Num=6
        ):  # soiltype = 4, croptype = 1
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 48, 20, 2, 1, 300, Dec=6, Num=7
        ):  # discfrac = 0.37 for all three paved areas.
            self.assertIsNone(n)
        for n in validate(
            0, 6855, 0, 48, 20, 2, 1, 300, Dec=8, Num=8
        ):  # up_no_meas_area = 0
            self.assertIsNone(n)
        for n in validate(
            6855, 0, 0, 48, 20, 2, 1, 0, Dec=6, Num=9
        ):  # ow_no_meas_area = 0
            self.assertIsNone(n)


if __name__ == "__main__":
    unittest.main()

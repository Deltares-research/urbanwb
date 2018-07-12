import unittest
import urbanwb
import numpy as np
import pandas as pd
import numpy.testing as npt
from urbanwb.unsaturatedzone import UnsaturatedZone
from urbanwb.selector import soil_selector
from urbanwb.gwlcalculator import gwlcal

path = urbanwb.urbanwbdir / ".." / "input"
InputData = pd.read_csv(path / "integration_test" / "input_csv.csv")
date = InputData["date"]
Ref_grass = InputData["Ref.grass"]
iters = np.shape(date)[0]
meas_uz = np.zeros(iters)


def validate(a, b, c, d, e, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match
    """
    # a --- theta_uz_t0, which depends on the initial GWL.
    # b --- area of unsaturated zone (without a measure).
    # c --- area of unsaturated zone (with a measure).
    # d --- soil type.
    # e --- crop type.
    # Dec --- Desired precision, default is 6.
    # Num --- No. of test to locate excel file.
    init_GWL = a
    theta_uz_t0 = soil_selector(d, e)[gwlcal(init_GWL)[2]]["moist_cont_eq_rz[mm]"]
    m = UnsaturatedZone(
        theta_uz_t0, uz_no_meas_area=b, uz_meas_area=c, soiltype=d, croptype=e
    )
    data_py = [
        {
            "sum_i_uz": 0,
            "r_meas_uz": 0,
            "theta_h3_uz": 0,
            "t_alpha_uz": 0,
            "t_atm_uz": 0,
            "gwl_up": 0,
            "gwl_low": 0,
            "theta_eq_uz": 0,
            "capris_max_uz": 0,
            "p_uz_gw": 0,
            "theta_uz": theta_uz_t0,
        }
    ]

    i_up_uz = pd.read_csv(path / "integration_test" / "i_up_uz.csv")[
        "i_up_uz_" + str(Num)
    ]
    gwl = pd.read_csv(path / "integration_test" / "gwl.csv")["gwl_" + str(Num)]
    tot_meas_area = 0

    t = 1
    while t <= iters - 1:
        data_py.append(
            m.sol(
                i_up_uz[t],
                meas_uz[t],
                tot_meas_area,
                Ref_grass[t],
                prev_gwl=gwl[t - 1],
                delta_t=1 / 24,
            )
        )
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = "uz_it_exsol_" + str(Num) + ".csv"
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


class TestOpenPaved(unittest.TestCase):
    def setUp(self):
        """
        runs the code before every single test
        """
        self.uz_1 = UnsaturatedZone(194.1, 6855, 0, soiltype=2, croptype=1)

    def test_sol(self):
        """
        test the 'sol' in the Unpaved class. Better carefully select values that can coverage all the
        process threshold
        """
        # uz_1 --- default setting
        # uz_2 --- setting 2

        # time level t = 1/7/1986 10:00
        self.uz_1.init_theta_uz = 193.4439006  # update state
        self.assertAlmostEqual(
            self.uz_1.sol(1.830653459, 0, 0, 0.081752162, 1.52326266, 1 / 24)[
                "t_atm_uz"
            ],
            0.081752162,
            places=8,
        )

        # time level t = 1/4/1986 12:00
        self.uz_1.init_theta_uz = 193.6718515310  # update state
        self.assertAlmostEqual(
            self.uz_1.sol(2.00000000, 0, 0, 0.082017161, 1.5151371876, 1 / 24)[
                "capris_max_uz"
            ],
            1.5102715093,
            places=8,
        )

        # time level t = 1/4/1986 12:00
        self.uz_1.init_theta_uz = 193.6718515310  # update state
        self.assertAlmostEqual(
            self.uz_1.sol(2.00000000, 0, 0, 0.0820171606, 1.5151371876, 0.041666667)[
                "capris_max_uz"
            ],
            1.5102715093,
            places=8,
        )

    def test_integration(self):
        """
        runs integration tests (validate with excel using different coefficient sets for all time steps)
        """
        for n in validate(1.5, 6855, 0, 2, 1, Dec=6, Num=0):  # default
            self.assertIsNone(n)
        for n in validate(
            1.5, 6855, 0, 3, 1, Dec=7, Num=1
        ):  # soiltype = 3, croptype = 1
            self.assertIsNone(n)
        for n in validate(
            1.5, 6855, 0, 7, 1, Dec=4, Num=2
        ):  # soiltype = 7, croptype = 1
            self.assertIsNone(n)
        for n in validate(3.0, 6855, 0, 2, 1, Dec=4, Num=3):  # initial gwl = 3.0
            self.assertIsNone(n)
        for n in validate(0.0, 6855, 0, 2, 1, Dec=3, Num=4):  # initial gwl = 0
            self.assertIsNone(n)
        # there is -0.0004256 difference in col 9, error is caused by copy-pasting excel solution
        for n in validate(1.5, 0, 6855, 2, 1, Dec=8, Num=5):  # uz_no_meas_area = 0
            self.assertIsNone(n)


if __name__ == "__main__":
    unittest.main()

import unittest
import urbanwb
import numpy as np
import pandas as pd
import numpy.testing as npt
from urbanwb.groundwater import Groundwater


path = urbanwb.urbanwbdir / ".." / "input"
InputData = pd.read_csv(path / "integration_test" / "input_csv.csv")
date = InputData["date"]
iters = np.shape(date)[0]
meas_gw = np.zeros(iters)


def validate(a, b, c, d, e, f, g, h, i, j, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match
    """
    # a --- initial GWL
    # b --- area of groundwater (without a measure)
    # c --- area of groundwater (with a measure)
    # d --- defined seepage (0 or 1)
    # e --- groundwater drainage resistance [d]
    # f --- flow resistance between deep and shallow groundwater [d]
    # g --- defined hydraulic head of deep groundwater [m-SL]
    # h --- defined constant downward seepage down_seepage_flux [mm/d]
    # i --- soil type
    # j --- crop type
    # Dec --- Desired precision, default is 6.
    # Num --- No. of test to locate excel file.

    m = Groundwater(
        gwl_t0=a,
        gw_no_meas_area=b,
        gw_meas_area=c,
        seepage_define=d,
        w=e,
        vc=f,
        head_deep_gw=g,
        down_seepage_flux=h,
        soiltype=i,
        croptype=j,
    )
    data_py = [
        {
            "sum_p_gw": 0,
            "r_meas_gw": 0,
            "gwl_up_1": 0,
            "gwl_low_1": 0,
            "sc_gw": 0,
            "h_gw": 0,
            "s_gw_out": 0,
            "d_gw_ow": 0,
            "gwl": a,
            "gwl_sl": 0,
        }
    ]

    p_uz_gw = pd.read_csv(path / "integration_test" / "p_uz_gw.csv")[
        "p_uz_gw_" + str(Num)
    ]
    p_op_gw = pd.read_csv(path / "integration_test" / "p_op_gw.csv")[
        "p_op_gw_" + str(Num)
    ]
    owl = pd.read_csv(path / "integration_test" / "owl.csv")["owl_" + str(Num)]
    uz_no_meas_area = 6855

    t = 1
    while t <= iters - 1:
        data_py.append(
            m.sol(
                p_uz_gw=p_uz_gw[t],
                uz_no_meas_area=uz_no_meas_area,
                p_op_gw=p_op_gw[t],
                op_no_meas_area=300,
                tot_meas_area=c,
                meas_gw=meas_gw[t],
                owl_prevt=owl[t - 1],
                delta_t=1 / 24,
            )
        )
        # it is assumed here tot_meas_area = gw_meas_area
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = "gw_it_exsol_" + str(Num) + ".csv"
    data_ex = pd.read_csv(path / "integration_test" / filename_excel)
    keys = data_ex.keys()
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


class TestGroundwater(unittest.TestCase):
    def setUp(self):
        """runs the code before every single test"""
        self.gw_1 = Groundwater(
            1.5,
            8140,
            0,
            seepage_define=0,
            w=100,
            vc=20000,
            head_deep_gw=21.5,
            down_seepage_flux=1,
            soiltype=2,
            croptype=1,
        )

    def test_sol(self):
        """test the 'sol' in the Unpaved class. Better carefully select values that can coverage all the
        process threshold"""
        # time level t = 12/17/1989 15:00
        self.gw_1.gwl_prevt = 1.5589210852  # update state
        self.gw_1.gwl_sl_prevt = 0
        self.assertAlmostEqual(
            self.gw_1.sol(0.8231929258, 6855, 0, 481.6093594, 0, 0, 1.5, 1 / 24)[
                "sc_gw"
            ],
            0.21189210852,
            places=8,
        )

        # time level t = 12/17/1989 15:00
        self.gw_1.gwl_prevt = 1.5589210852  # update state
        self.gw_1.gwl_sl_prevt = 0
        self.assertAlmostEqual(
            self.gw_1.sol(0.8231929258, 6855, 0, 481.6093594, 0, 0, 1.5, 1 / 24)[
                "sum_p_gw"
            ],
            0.6932417084,
            places=8,
        )

        # time level t = 12/17/1989 16:00
        self.gw_1.gwl_prevt = 1.5588655980  # update state
        self.gw_1.gwl_sl_prevt = 0
        self.assertAlmostEqual(
            self.gw_1.sol(
                0.3826862970, 6855, 0.041666667, 481.6093594, 0, 0, 1.5, 1 / 24
            )["gwl"],
            1.5588826117,
            places=9,
        )

    # def test_integration(self):
    #     """
    #      runs integration tests (validate with excel using different coefficient sets for all time steps)
    #      """
    #     for n in validate(
    #         1.5, 8140, 0, 0, 100, 20000, 21.5, 1, 2, 1, Dec=3, Num=0
    #     ):  # default
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 0, 100, 20000, 21.5, 1, 3, 1, Dec=3, Num=1
    #     ):  # soiltype = 3 croptype = 1
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 0, 100, 20000, 21.5, 1, 7, 1, Dec=3, Num=2
    #     ):  # soiltype = 7 croptype = 1
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 1, 100, 20000, 21.5, 1, 2, 1, Dec=3, Num=3
    #     ):  # seepage_define = 1
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 0, 10000, 20000, 21.5, 1, 2, 1, Dec=3, Num=4
    #     ):  # w = 10000
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 0, 0.1, 20000, 21.5, 1, 2, 1, Dec=2, Num=5
    #     ):  # w = 0.1 (cannot be 0 otherwise DIV0 ERROR)
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 0, 100, 2000000, 21.5, 1, 2, 1, Dec=3, Num=6
    #     ):  # vc = 2000000
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 0, 100, 0, 21.5, 1, 2, 1, Dec=3, Num=7
    #     ):  # vc = 0
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 1, 100, 20000, 215, 1, 2, 1, Dec=3, Num=8
    #     ):  # head_deep_gw = 215, seepage_define = 1
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 8140, 0, 1, 100, 20000, 0, 1, 2, 1, Dec=3, Num=9
    #     ):  # head_deep_gw = 0, seepage_define = 1
    #         self.assertIsNone(n)
    #     for n in validate(
    #         1.5, 0, 8140, 0, 100, 20000, 21.5, 1, 2, 1, Dec=3, Num=10
    #     ):  # gw_no_meas_area = 0
    #         self.assertIsNone(n)
    #     # The difference between the summations of all values in solution matrix for python and excel is from 0.0001 to 0.001.


if __name__ == "__main__":
    unittest.main()

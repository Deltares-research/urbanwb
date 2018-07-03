import unittest
import urbanwb
import numpy as np
import pandas as pd
import numpy.testing as npt
from urbanwb.pavedroof import PavedRoof

path = urbanwb.urbanwbdir / ".." / "input"
InputData = pd.read_csv(path / "integration_test" / 'input_csv.csv')
date = InputData['date']
P_atm = InputData['P_atm']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]


def validate(a, b, c, d, e, f, Dec, Num):
    """
    Integration test function. Compares python solutions with excel's for all columns for all time steps to see
    whether the results match
    """

    # a --- area of paved roof (without a measure)
    # b --- area of paved roof(with a measure)
    # c --- area of paved roof measure inflow area.
    # d --- interception storage capacity on paved roof.
    # e --- fraction of paved roof area with storm water drainage system.
    # f --- fraction of paved roof area that is disconnected to the sewer system.
    # Dec --- Desired precision, default is 6.
    # Num --- No. of test to locate excel file.

    m = PavedRoof(init_intstor_pr_t0=0, pr_no_meas_area=a, pr_meas_area=b, pr_meas_inflow_area=c,
                  intstorcap_pr=d, stormfrac_pr=e, discfrac_pr=f)
    data_py = [{'int_pr': 0, 'e_atm_pr': 0, 'intstor_pr': 0, 'r_pr_meas': 0, 'r_pr_swds': 0,
                'r_pr_mss': 0, 'r_pr_up': 0}]  # initial condition (first row)
    t = 1
    while t <= iters - 1:
        data_py.append(m.sol(P_atm[t], E_pot_OW[t]))
        t += 1
    data_py = pd.DataFrame(data_py)
    filename_excel = 'pr_it_exsol_' + str(Num) + '.csv'
    data_ex = pd.read_csv(path / "integration_test" / filename_excel)
    keys = data_py.keys()
    none_list = []
    for key in keys:
        none_list.append(npt.assert_array_almost_equal(data_py[key][1:], data_ex[key][1:], decimal=Dec))
        # assert_array_almost_equal is used to compare two arrays. If true, it returns None.
        # default decimal is 6.
        # comparison excludes first row (where there are NaNs in excel)
    return none_list


class TestPavedRoof(unittest.TestCase):
    @ classmethod
    def setUpClass(cls):
        print('setupClass')

    @ classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        """runs the code before every single test"""
        print('Setup')
        self.pr_1 = PavedRoof(0, 1560, 0, 0, intstorcap_pr=1.6, stormfrac_pr=1.0, discfrac_pr=0.0)

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_inflowfac(self):
        """tests the 'inflowfac' in the PavedRoof class"""
        self.assertAlmostEqual(self.pr_1.inflowfac(), 0, places=8)

    def test_sol(self):
        """tests the 'sol' in the PavedRoof class"""
        # time level t = 4/20/1990 15:00
        self.pr_1.init_intstor_pr = 0  # update state
        self.assertAlmostEqual(self.pr_1.sol(0.508, 0.215938697)['int_pr'], 0.508, places=7)

        # time level t = 4/20/1990 16:00
        self.pr_1.init_intstor_pr = 0.292061303  # update state
        self.assertAlmostEqual(self.pr_1.sol(20.32, 0.215938697)['int_pr'], 1.6, places=7)

    def test_integration(self):
        """runs integration tests (validate with excel using different coefficient sets for all time steps)"""
        for n in validate(1560, 0, 0, 1.6, 1, 0, Dec=8, Num=0):  # default
            self.assertIsNone(n)
        for n in validate(0, 1560, 0, 1.6, 1.0, 0.0, Dec=10, Num=1):  # pr_no_meas_area = 0
            self.assertIsNone(n)
        for n in validate(1560, 0, 0, 0, 1, 0, Dec=10, Num=2):  # intstorcap_pr = 0
            self.assertIsNone(n)
        for n in validate(1560, 0, 0, 1600, 1, 0, Dec=6, Num=3):  # intstorcap_pr = 1600
            self.assertIsNone(n)
        for n in validate(1560, 0, 0, 1.6, 0, 0, Dec=8, Num=4):  # stormfrac = 0
            self.assertIsNone(n)
        for n in validate(1560, 0, 0, 1.6, 0.37, 0, Dec=8, Num=5):  # stormfrac = 0.37
            self.assertIsNone(n)
        for n in validate(1560, 0, 0, 1.6, 1, 1, Dec=8, Num=6):  # discfrac = 1
            self.assertIsNone(n)
        for n in validate(1560, 0, 0, 1.6, 1, 0.37, Dec=8, Num=7):  # discfrac = 0.37
            self.assertIsNone(n)


if __name__ == '__main__':
    unittest.main()

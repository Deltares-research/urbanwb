import unittest
from urbanwb.unpaved import Unpaved


class TestOpenPaved(unittest.TestCase):
    @ classmethod
    def setUpClass(cls):
        print('setupClass')

    @ classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        """runs the code before every single test"""
        print('Setup')
        # added here.
        self.up_1 = Unpaved(0, 6855, 0, 0, infilcap_up=48, intstorcap_up=20, soiltype=2, croptype=1)
        # self.up_2 = Unpaved()
        # not applicable for now.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the Unpaved class. Better carefully select values that can coverage all the
        process threshold"""
        # up_1 --- default setting
        # up_2 --- setting 2
        # not applicable for now
        # (self, p_atm, e_pot_ow, r_pr_up, r_cp_up, r_op_up, prev_mois_uz, pr_no_meas_area, cp_no_meas_area,
        #             op_no_meas_area, ow_no_meas_area, delta_t=1 / 24):

        # time level t = 8/1/1988 13:00
        self.up_1.prev_fin_stor_up = 0  # update state
        self.assertEqual(self.up_1.sol(0, 0.346642066, 0, 0, 0, 175.7714344, 1560, 803.3906406, 481.6093594, 300,
                                       1/24)[2], 2)

        # time level t = 8/1/1988 14:00
        self.up_1.prev_fin_stor_up = 0  # update state
        self.assertEqual(self.up_1.sol(4.826, 0.346642066, 0, 0, 0, 175.5165721, 1560, 803.3906406, 481.6093594, 300,
                                       1/24)[1], 4.826)

    def test_inflowfac(self):
        """test the 'inflowfac' in the PavedRoof class. Actually not very necessary as it is already included in sol"""

        self.assertEqual(self.up_1.inflowfac(), 0)


if __name__ == '__main__':
    unittest.main()

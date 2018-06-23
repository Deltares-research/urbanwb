import unittest
from urbanwb.unsaturatedzone import UnsaturatedZone


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
        # added here. (theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=2, croptype=1)
        self.uz_1 = UnsaturatedZone(194.1, 6855, 0, soiltype=2, croptype=1)
        # self.uz_2 = Unpaved()
        # not applicable for now.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the Unpaved class. Better carefully select values that can coverage all the
        process threshold"""
        # uz_1 --- default setting
        # uz_2 --- setting 2
        # not applicable for now

        # (i_up_uz, meas_uz, tot_meas_area, e_ref, prev_gwl, delta_t=1 / 24)

        # time level t = 1/7/1986 10:00
        self.uz_1.init_theta_uz = 193.4439006  # update state
        self.assertEqual(self.uz_1.sol(1.830653459, 0, 0, 0.081752162, 1.52326266, 1/24)[4], 0.081752162)

        # time level t = 1/4/1986 12:00
        self.uz_1.init_theta_uz = 193.6718515310  # update state
        self.assertAlmostEqual(self.uz_1.sol(2.00000000, 0, 0, 0.082017161, 1.5151371876, 1/24)[8], 1.5102715093, places=8)

        # time level t = 1/4/1986 12:00
        self.uz_1.init_theta_uz = 193.6718515310  # update state
        self.assertEqual(self.uz_1.sol(2.00000000, 0, 0, 0.0820171606, 1.5151371876, 0.041666667)[8], 1.5102715093)
        # float causing cannot "assertequal" after 8 digits for eq. moisture content, maximum capillary rise.


if __name__ == '__main__':
    unittest.main()

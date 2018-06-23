import unittest
from urbanwb.openwater import OpenWater


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
        # added here. init_owl_t0, ow_no_meas_area, ow_level, q_ow_out_cap=200
        self.ow_1 = OpenWater(300, 1.5, q_ow_out_cap=200)
        # self.ow_2 = OpenWater()
        # not applicable for now.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the OpenWater class. Better carefully select values that can coverage all the
        process threshold"""
        # ow_1 --- default setting
        # ow_2 --- setting 2
        # not applicable for now

        # time level t = 1/4/1986 11:00
        self.ow_1.prev_stor_swds = 0
        self.ow_1.prev_stor_mss = 0
        # self.ow_1.prev
        self.assertAlmostEqual(self.ow_1.sol(0, 0.331006211, 0, -0.083728895, 0, 0, 0, 0, 0, 6855, 8140,
                                             2845, 0, 0, 10000, 1/24)[3], -2.271844027, places=7)
        # time level t = 1/4/1986 12:00
        self.ow_1.prev_stor_swds = 0
        # self.ow_
        self.assertAlmostEquals(self.ow_1.sol(),a,b,c,places=9)


if __name__ == '__main__':
    unittest.main()

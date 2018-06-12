import unittest
from groundwater import Groundwater


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
        # added here. (init_gwl_t0, gw_no_meas_area, gw_meas_area, seep_def=0, w=100, vc=20000,
        # h_deepgw=21.5, flux=1, soiltype=2, croptype=1):
        self.gw_1 = Groundwater(1.5, 8140, 0, seep_def=0, w=100, vc=20000, h_deepgw=21.5, flux=1,
                                soiltype=2, croptype=1)
        # self.gw_2 = Groundwater()
        # not applicable for now.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the Unpaved class. Better carefully select values that can coverage all the
        process threshold"""
        # gw_1 --- default setting
        # gw_2 --- setting 2
        # not applicable for now

        # (p_uz_gw, uz_no_meas_area, p_op_gw, op_no_meas_area, tot_meas_area, meas_gw,
        #             prev_owl,  delta_t=1 / 24)

        # time level t = 12/17/1989 15:00

        # time level t = 12/17/1989 15:00
        self.gw_1.prev_gwl = 1.5589210852  # update state
        self.gw_1.prev_gwl_sl = 0  # update state
        self.assertEqual(self.gw_1.sol(0.8231929258, 6855, 0, 481.6093594, 0, 0, 1.5, 1 / 24)[4], 0.21189210852)

        # time level t = 12/17/1989 15:00
        self.gw_1.prev_gwl = 1.5589210852  # update state
        self.gw_1.prev_gwl_sl = 0  # update state
        self.assertAlmostEqual(self.gw_1.sol(0.8231929258, 6855, 0, 481.6093594, 0, 0, 1.5, 1/24)[0], 0.6932417084, places=9)

        # time level t = 12/17/1989 16:00
        self.gw_1.prev_gwl = 1.5588655980  # update state
        self.gw_1.prev_gwl_sl = 0  # update state
        self.assertAlmostEqual(self.gw_1.sol(0.3826862970, 6855, 0.041666667, 481.6093594, 0, 0, 1.5, 1/24)[8], 1.5588826117, places=9)
